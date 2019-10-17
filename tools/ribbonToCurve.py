import numpy as np
import copy

import maya.cmds as cmds
import maya.api.OpenMaya as om

from rigging_utils import constraint
from rigging_utils import shape
from rigging_utils.create import curves


def lock_attributes(dag, attrs, channelbox=False):
    """Wrapper for locking attributes

    Args:
        dag (str): dag to lock attributes on
        attrs list[(str)]: attributes to lock
        channelbox (bool): whether to hide the attributes being locked from the channelbox
    """

    for attr in attrs:
        attribute = '{}.{}'.format(dag, attr)
        cmds.setAttr(attribute, keyable=channelbox, lock=True)


def remap_values(OldMin, OldMax, NewMin, NewMax, input):
    OldRange = (OldMax - OldMin)
    NewRange = (NewMax - NewMin)
    NewValue = (((input - OldMin) * NewRange) / OldRange) + NewMin

    return NewValue


def create_dag(name, source=None, connect='srt', snap=True, position=None, type='bone', ctrl_type='circle', size=1.0):
    '''Creates a dag object of the given type

    Args:
         name (str): base name of node
         source (str): source dag object for constraining the object to
         connect (str): connect scale, translation, rotation of new dag to source
         snap (bool): whether the object will be moved to the source object
         position (om.MMatrix): matrix for object to be positioned at
         type (str): type of dag object created
         size (float): how large the dag will be
    Returns:
        (str): dag object created
    '''
    cmds.select(clear=True)

    # create dag based on the type flag
    dag = None
    if type == 'bone':
        dag = cmds.joint(name=name + '_BONE')
        cmds.setAttr(dag + '.radius', size)
    if type == 'control':
        dag = shape.create_nurbscurve(ctrl_type, name=name + '_CTRL', size=size)
        dag = cmds.listRelatives(dag, p=True)[0]
    if type == 'locator':
        dag = cmds.spaceLocator(name=name + '_CTRL')[0]
    ofs = cmds.createNode('transform', name=dag + '_OFS')
    zero = cmds.createNode('transform', name=dag + '_ZERO')
    cmds.parent(dag, ofs)
    cmds.parent(ofs, zero)

    # position and constrain the dag accordingly
    if position:
        cmds.xform(zero, matrix=position, ws=True)
    if source:
        if snap:
            snap_to_dag(source, zero)
        if connect:
            constraint.simple_constraint(source, zero, connect=connect)

    return dag


def snap_to_dag(source, target):
    '''Moves one dag object to the position and rotation of another

    Args:
         source (str): object to reference for transforms
         target (str): object to move to source object
    '''

    pos = cmds.xform(source, t=True, ws=True, q=True)
    rot = cmds.xform(source, ro=True, ws=True, q=True)

    cmds.xform(target, t=pos, ws=True)
    cmds.xform(target, ro=rot, ws=True)


def add_enum(node, name, *args):
    '''Wrapper for making an enum attribute

    Args:
        node (str): node to add attribute to
        name (str): name of attribute
        *args: arguments that will be the enum names of the attribute
    Return:
         (str): attribute name
    '''

    enum_names = ''
    for i, arg in enumerate(args):
        if arg != args[-1]:
            enum_names += arg + ':'
        else:
            enum_names += arg

    cmds.addAttr(node,
                 shortName=name,
                 attributeType='enum',
                 enumName=enum_names,
                 keyable=True)

    return '{}.{}'.format(node, name)


def linspace_bones(curve, bones):
    ''' Provide matrices that are an equal distribution along a curve

    Args:
        curve (str): name of curve to get information from
        bones (list[str]): number of controls to be created for up vec of curve
    '''
    sel = om.MSelectionList()
    sel.add(curve)

    crv = om.MFnNurbsCurve()
    crv.setObject(sel.getDagPath(0))

    curve_length = crv.length()
    lengths = np.linspace(0, curve_length, len(bones))

    # create instance to control pos and rot of controls being attached
    for i, length in enumerate(lengths):
        bone = bones[i]
        poci = cmds.createNode('pointOnCurveInfo', name=bone + '_POCI')

        param = crv.findParamFromLength(length)
        if param == 0:
            param = .001
        if length == lengths[-1]:
            param -= .001

        cmds.connectAttr(curve + '.worldSpace[0]', poci + '.inputCurve')
        cmds.setAttr(poci + '.parameter', param)
        cmds.connectAttr(poci + '.position', bone + '.translate')


def linspace_curve(curve, num, num_ctrls):
    ''' Provide matrices that are an equal distribution along a curve

    Args:
        curve (str): name of curve to get information from
        num (int): number of matrices to be returned
        num_ctrls (int): number of controls to be created for up vec of curve
    Return:
         list[om.MMatrix()]: list of matrices
    '''
    top_grp = cmds.createNode('transform', name=curve + '_ribbon_GRP')
    add_enum(top_grp, 'ribbonGRP', 'exists')

    sel = om.MSelectionList()
    sel.add(curve)

    crv = om.MFnNurbsCurve()
    crv.setObject(sel.getDagPath(0))

    curve_length = crv.length()
    lengths = np.linspace(0, curve_length, num)
    ctrl_lengths = np.linspace(0, curve_length, num_ctrls)

    mscs = []
    up_vecs = []
    ctrl_params = []

    # create controls to control up vector of curve
    for i, length in enumerate(ctrl_lengths):
        ctrl_height = curve_length/10.0
        param = crv.findParamFromLength(length)
        ctrl = create_dag('C_crv_{}'.format(str(i)), type='control', ctrl_type='triangle')
        lock_attributes(ctrl, ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
        ctrl_ofs = ctrl + '_OFS'
        ctrl_zero = ctrl + '_ZERO'
        line_loc = cmds.spaceLocator(name='C_crv_{}_LOC'.format(str(i)))[0]
        poci = cmds.createNode('pointOnCurveInfo', name=ctrl + '_POCI')
        dm = cmds.createNode('decomposeMatrix', name=ctrl + '_DM')
        sub_vec = cmds.createNode('math_SubtractVector', name=ctrl + '_SV')
        normalize = cmds.createNode('math_NormalizeVector', name=ctrl + '_NV')
        ctrl_params.append(param)

        cmds.connectAttr(curve + '.worldSpace[0]', poci + '.inputCurve')
        cmds.setAttr(poci + '.parameter', param)

        cmds.connectAttr(poci + '.position', ctrl_zero + '.translate')
        cmds.connectAttr(poci + '.position', line_loc + '.translate')

        cmds.setAttr(ctrl_ofs + '.ty', ctrl_height)
        cmds.connectAttr(ctrl + '.worldMatrix[0]', dm + '.inputMatrix')

        cmds.connectAttr(dm + '.outputTranslate', sub_vec + '.input1')
        cmds.connectAttr(line_loc + '.translate', sub_vec + '.input2')

        cmds.connectAttr(sub_vec + '.output', normalize + '.input')

        line_curve = curves.curve_from_objects([ctrl, line_loc], name=ctrl + '_vec_CRV')
        cmds.setAttr(line_curve + '.overrideEnabled', 1)
        cmds.setAttr(line_curve + '.overrideDisplayType', 2)

        up_vecs.append(normalize)

        cmds.parent(ctrl_zero, top_grp)
        cmds.parent(line_loc, top_grp)
        cmds.parent(line_curve, top_grp)

    # create instance to control pos and rot of controls being attached
    for length in lengths:
        poci = cmds.createNode('pointOnCurveInfo')
        fbf = cmds.createNode('fourByFourMatrix')
        msc = cmds.createNode('millSimpleConstraint')
        pblnd = cmds.createNode('pairBlend')
        z_vec = cmds.createNode('vectorProduct')
        mscs.append(msc)

        param = crv.findParamFromLength(length)

        # find the two up vecs the current param is between
        param_differences = []
        par_list = copy.deepcopy(ctrl_params)
        vec_list = copy.deepcopy(up_vecs)
        closest_vecs = {}
        for par in par_list:
            par_dif = abs(param - par)
            param_differences.append(par_dif)

        # iterate through the parameter list twice to get the two closest pars
        def closest_vec():
            closest_par = None
            close_index = None
            for i, par in enumerate(param_differences):
                if i == 0:
                    closest_par = par
                    close_index = i
                elif par < closest_par:
                    closest_par = par
                    close_index = i

            closest_vecs[par_list[close_index]] = vec_list[close_index]
            param_differences.remove(closest_par)
            par_list.remove(par_list[close_index])
            vec_list.remove(vec_list[close_index])

        closest_vec()
        closest_vec()

        close_pars = []
        close_vecs = []
        for key, value in closest_vecs.items():
            close_pars.append(key)
            close_vecs.append(value)

        blend_value = remap_values(close_pars[0], close_pars[1], 0, 1, param)

        # connect vecs to pair blend
        cmds.connectAttr(close_vecs[0] + '.output', pblnd + '.inTranslate1')
        cmds.connectAttr(close_vecs[1] + '.output', pblnd + '.inTranslate2')
        cmds.setAttr(pblnd + '.weight', blend_value)

        cmds.setAttr(z_vec + '.operation', 2)
        cmds.connectAttr(pblnd + '.outTranslate', z_vec + '.input1')
        cmds.connectAttr(poci + '.normalizedTangent', z_vec + '.input2')

        cmds.connectAttr(curve + '.worldSpace[0]', poci + '.inputCurve')
        cmds.setAttr(poci + '.parameter', param)
        cmds.connectAttr(poci + '.normalizedTangentX', fbf + '.in00')
        cmds.connectAttr(poci + '.normalizedTangentY', fbf + '.in01')
        cmds.connectAttr(poci + '.normalizedTangentZ', fbf + '.in02')
        cmds.connectAttr(pblnd + '.outTranslateX', fbf + '.in10')
        cmds.connectAttr(pblnd + '.outTranslateY', fbf + '.in11')
        cmds.connectAttr(pblnd + '.outTranslateZ', fbf + '.in12')
        cmds.connectAttr(z_vec + '.outputX', fbf + '.in20')
        cmds.connectAttr(z_vec + '.outputY', fbf + '.in21')
        cmds.connectAttr(z_vec + '.outputZ', fbf + '.in22')
        cmds.connectAttr(poci + '.positionX', fbf + '.in30')
        cmds.connectAttr(poci + '.positionY', fbf + '.in31')
        cmds.connectAttr(poci + '.positionZ', fbf + '.in32')
        cmds.connectAttr(fbf + '.output', msc + '.inMatrix')

    return mscs


def gather_controls():
    namespace_ctrls = cmds.ls('*:*CTRL')
    regular_ctrls = cmds.ls('*CTRL')
    grps = cmds.ls('*GRP')
    grps = cmds.ls('*:*GRP') + grps
    bones = cmds.ls('C_ribbon_*_CRV_BONE')
    bones = cmds.ls('*:C_ribbon_*_CRV_BONE') + bones
    all_controls = namespace_ctrls + regular_ctrls
    num_ctrls = None
    ribbon_ctrls = []
    ribbon_grps = []
    ctrl_order = {}
    for ctrl in all_controls:
        if 'bank' or 'sub' not in ctrl:
            if cmds.ls(ctrl + '.ribbonCtrl'):
                i = cmds.getAttr(ctrl + '.ribbonCtrl')
                ctrl_order[i] = ctrl
            elif cmds.ls(ctrl + '.ribbonRoot'):
                num_ctrls = cmds.getAttr(ctrl + '.numControls')
    for i in range(len(ctrl_order)):
        if 'bank' or 'sub' not in ctrl_order[i]:
            ribbon_ctrls.append(ctrl_order[i])
    for grp in grps:
        if cmds.ls(grp + '.ribbonGRP'):
            ribbon_grps.append(grp)
    return ribbon_ctrls, num_ctrls, ribbon_grps, bones


def reset_controls():
    ctrls, num_dags, grps, bones = gather_controls()

    # reset curve bones
    for bone in bones:
        poci = cmds.listConnections(bone + '.translate', source=True)
        cmds.delete(poci)
    lengths = np.linspace(0, 68.853, len(bones))
    for i, each in enumerate(lengths):
        cmds.xform(bones[i], t=(0, 0, each))

    # reset controls
    for i, dag in enumerate(ctrls):
        ofs = dag + '_OFS'
        if cmds.ls(ofs + '.curveMSC'):
            msc = cmds.getAttr(ofs + '.curveMSC', asString=True)
            cmds.deleteAttr(ofs + '.curveMSC')
            cmds.delete(msc)
        cmds.setAttr(ofs + '.t', 0, 0, 0)
        cmds.setAttr(ofs + '.r', 0, 0, 0)
        cmds.setAttr(dag + '.r', 0, 0, 0)
    for dag in grps:
        cmds.delete(dag)


def move_to_curve(curve, num_ctrls):
    ctrls, num_dags, grps, bones = gather_controls()
    rig_crv = cmds.ls('C_ribbon_CRV')
    rig_crv = (cmds.ls('*:C_ribbon_CRV') + rig_crv)[0]
    dags = []
    for i in range(num_dags):
        dags.append(ctrls[i])
    linspace_bones(curve, bones)

    mscs = linspace_curve(rig_crv, num_dags, num_ctrls)

    if cmds.ls(ctrls[0] + '_OFS.curveMSC'):
        reset_controls()

    for i, dag in enumerate(dags):
        ofs = dag + '_OFS'
        cmds.connectAttr(ofs + '.parentInverseMatrix[0]', mscs[i] + '.parentInverseMatrix')
        cmds.connectAttr(mscs[i] + '.outTranslate', ofs + '.translate')
        cmds.connectAttr(mscs[i] + '.outRotate', ofs + '.rotate')

        add_enum(ofs, 'curveMSC', mscs[i])
