import maya.cmds as cmds
import maya.api.OpenMaya as om

from rigging_utils import constraint
from rigging_utils import attribute
from rigging_utils import shape

import util.control_shapes as cs

import util.attribute as local_attr


# mirror an object over the x axis
def mirror_object(object, mirrored_object):
    mtx = cmds.xform(object, matrix=True, ws=True, q=True)
    x = [mtx[0], mtx[1] * -1, mtx[2] * -1]
    y = [mtx[4], mtx[5] * -1, mtx[6] * -1]
    z = [mtx[8], mtx[9] * -1, mtx[10] * -1]
    p = [mtx[12] * -1, mtx[13], mtx[14]]
    new_mtx = [x[0], x[1], x[2], 0,
               y[0], y[1], y[2], 0,
               z[0], z[1], z[2], 0,
               p[0], p[1], p[2], 1]
    cmds.xform(mirrored_object, matrix=new_mtx, ws=True)


def create_dag(name, source=None, connect='srt', snap=True, position=None, type='bone', ctrl_type='circle', size=1.0, offset=True):
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

    zero = cmds.createNode('transform', name=dag + '_ZERO')
    if offset:
        ofs = cmds.createNode('transform', name=dag + '_OFS')
        cmds.parent(dag, ofs)
        cmds.parent(ofs, zero)
    else:
        cmds.parent(dag, zero)

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


def dags_on_curve(up_curve, curve, name, dag_type, num_dags=10):
    attribute.add_generic_blend(curve, 'parameter')
    par_increment = 1.0/float(num_dags)
    par = 0.0 - par_increment
    for x in range(num_dags + 1):
        par += par_increment
        if par > 1.0:
            par = 1.0
        cmds.select(clear=True)

        if dag_type == 'bone':
            dag = cmds.joint(name=name + '_{}_BONE'.format(x))
        elif dag_type == 'locator':
            dag = cmds.spaceLocator(name=name + '_{}_LOC'.format(x))[0]
        zero = cmds.createNode('transform', name=dag + '_ZERO')
        poci = cmds.createNode('pointOnCurveInfo', name=dag + '_POCI')
        up_poci = cmds.createNode('pointOnCurveInfo', name=dag + '_up_POCI')
        sub_vec = cmds.createNode('math_SubtractVector', name=dag + '_upvec_SV')
        up_vec_normal = cmds.createNode('vectorProduct', name=dag + '_upvec_VP')
        cp = cmds.createNode('vectorProduct', name=poci + 'cross_VP')
        mtx = cmds.createNode('fourByFourMatrix', name=poci + '_MTX')
        param_add = cmds.createNode('math_Add', name=dag + '_param_ADD')
        msc = cmds.createNode('millSimpleConstraint', name=dag + '_MSC')

        param_sub = cmds.createNode('math_Subtract', name=dag + '_param_SUB')
        param_cond = cmds.createNode('condition', name=dag + '_param_COND')

        attribute.add_generic_blend(dag, 'parameter')
        cmds.setAttr(dag + '.parameter', par)

        cmds.parent(dag, zero)

        cmds.connectAttr(dag + '.parameter', param_add + '.input1')
        cmds.connectAttr(curve + '.parameter', param_add + '.input2')

        # condition for if the parameter goes over one
        cmds.connectAttr(param_add + '.output', param_sub + '.input1')
        cmds.setAttr(param_sub + '.input2', 1)

        cmds.setAttr(param_cond + '.operation', 2)
        cmds.connectAttr(param_add + '.output', param_cond + '.firstTerm')
        cmds.setAttr(param_cond + '.secondTerm', 1)
        cmds.connectAttr(param_sub + '.output', param_cond + '.colorIfTrueR')
        cmds.connectAttr(param_add + '.output', param_cond + '.colorIfFalseR')

        # connect curves to POCIs
        cmds.connectAttr(curve + '.worldSpace[0]', poci + '.inputCurve')
        cmds.connectAttr(param_cond + '.outColorR', poci + '.parameter')

        cmds.connectAttr(up_curve + '.worldSpace[0]', up_poci + '.inputCurve')
        cmds.connectAttr(param_cond + '.outColorR', up_poci + '.parameter')

        # x vector
        cmds.connectAttr(poci + '.normalizedTangentX', mtx + '.in00')
        cmds.connectAttr(poci + '.normalizedTangentY', mtx + '.in01')
        cmds.connectAttr(poci + '.normalizedTangentZ', mtx + '.in02')

        # y vector
        cmds.connectAttr(up_poci + '.position', sub_vec + '.input1')
        cmds.connectAttr(poci + '.position', sub_vec + '.input2')

        cmds.setAttr(up_vec_normal + '.operation', 0)
        cmds.setAttr(up_vec_normal + '.normalizeOutput', 1)
        cmds.connectAttr(sub_vec + '.output', up_vec_normal + '.input1')

        cmds.connectAttr(up_vec_normal + '.outputX', mtx + '.in10')
        cmds.connectAttr(up_vec_normal + '.outputY', mtx + '.in11')
        cmds.connectAttr(up_vec_normal + '.outputZ', mtx + '.in12')

        # z vector
        cmds.setAttr(cp + '.operation', 2)
        cmds.setAttr(cp + '.normalizeOutput', 1)
        cmds.connectAttr(up_vec_normal + '.output', cp + '.input1')
        cmds.connectAttr(poci + '.normalizedTangent', cp + '.input2')

        cmds.connectAttr(cp + '.outputX', mtx + '.in20')
        cmds.connectAttr(cp + '.outputY', mtx + '.in21')
        cmds.connectAttr(cp + '.outputZ', mtx + '.in22')

        # position of matrix
        cmds.connectAttr(poci + '.positionX', mtx + '.in30')
        cmds.connectAttr(poci + '.positionY', mtx + '.in31')
        cmds.connectAttr(poci + '.positionZ', mtx + '.in32')

        # constrain loc to matrix
        cmds.connectAttr(mtx + '.output', msc + '.inMatrix')
        cmds.connectAttr(zero + '.parentInverseMatrix[0]', msc + '.parentInverseMatrix')

        cmds.connectAttr(msc + '.outTranslate', zero + '.translate')
        cmds.connectAttr(msc + '.outRotate', zero + '.rotate')


def get_parent(dag, level=None):
    """Queries the parent of a node

    Args:
        dag (str): node to get the parent of
        level (int): amount of parents above node to query, 'top' will get
                     the top node of the hierarchy
    Return:
        (str): parent node
    """

    if not level or level == 0:
        parent = cmds.listRelatives(dag, p=True)[0]
    elif level == 'top':
        parent = cmds.listRelatives(dag, ap=True)[-1]
    else:
        parents = cmds.listRelatives(dag, ap=True)
        if level >= len(parents):
            parent = parents[-1]
        else:
            parent = parents[level]

    return parent


def section_controls(follow, side, name, default_pos=(0.0, 3.0, 0.0), function_attrs=None, **kwargs):
    '''

    Args:
        follow (str): control/dag node that the section control follows
        side (str): C/L/R side control is on, influences color
        name (str): base name for control
        default_pos tuple(float, float, float): default position for positioning
                                                of control in world space above
                                                followed control
        function_attrs list[(str)]: attributes to create proxy attributes of
        **kwargs: key is the attribute name, value is a list of the objects
                  whose visibility is being driven. If value is an attribute
                  then the section attribute will be proxy to that attribute.
    Return:
         str: node name for section control
    '''
    # get color of control
    if side == 'L':
        color = 18
    elif side == 'R':
        color = 13
    else:
        color = 17

    zero, ofs, ctrl = cs.gear_ctrl('{}_{}_section_CTRL'.format(side, name))

    # set color
    cmds.setAttr(ctrl + '.overrideEnabled', 1)
    cmds.setAttr(ctrl + '.overrideColor', color)

    # visibility attributes
    attribute.add_headline(ctrl, 'show')
    for attr, attr_list in kwargs.items():
        # make sure item is a list
        obj_type = type(attr_list)
        if obj_type != 'list':
            ValueError('Keyword values must be a list')
        local_attr.force_visibility_attr(ctrl, attr, items=attr_list)

    # function attributes
    if function_attrs:
        attribute.add_headline(ctrl, 'function')
        for attr in function_attrs:
            # create proxy attribute to attribute
            attr_name = attr.split('.')[1]
            local_attr.proxy_attribute(ctrl, attr, attr_name)

    # constrain control to follow control
    pos = cmds.xform(follow, t=True, ws=True, q=True)
    cmds.xform(zero, t=pos, ws=True)
    constraint.simple_constraint(follow, zero, snap=False, connect='t')

    # set offset from follow control
    cmds.setAttr(ofs + '.translate', default_pos[0], default_pos[1], default_pos[2])


def movable_pivot(ctrl, ctrl_type='box'):
    '''Creates a movable pivot under a given control

    Args:
         ctrl (str): control to make a movable pivot under
         ctrl_type (str): type of control that will be created
    '''
    scnd_ctrl = ctrl.split('CTRL')[0] + 'SCND_CTRL'
    pivot = ctrl.split('CTRL')[0] + 'PIV_CTRL'

    shape.create_nurbscurve(ctrl_type, name=scnd_ctrl)
    shape.create_nurbscurve('locator', name=pivot)

    ctrl_zero = cmds.createNode('transform', name=scnd_ctrl + '_ZERO')
    pivot_zero = cmds.createNode('transform', name=pivot + '_ZERO')

    reverse = cmds.createNode('math_MultiplyVector', name=pivot + '_MVEC')

    cmds.parent(scnd_ctrl, ctrl_zero)
    cmds.parent(pivot, pivot_zero)
    cmds.parent(ctrl_zero, pivot)
    cmds.parent(pivot_zero, ctrl)

    cmds.setAttr(pivot_zero + '.t', 0, 0, 0)
    cmds.setAttr(pivot_zero + '.rotate', 0, 0, 0)

    cmds.setAttr(reverse + '.input2', -1)
    cmds.connectAttr(pivot + '.t', reverse + '.input1')

    cmds.connectAttr(reverse + '.output', ctrl_zero + '.t')


def dag_to_geo(dag, geo):
    position_attr = attribute.add_generic_blend(dag, 'meshPosition')
    geo_shape = cmds.listRelatives(geo, s=True)[0]

    sel = om.MSelectionList()
    sel.add(geo_shape)

    plane = om.MFnMesh()
    plane.setObject(sel.getDagPath(0))

    foll = cmds.createNode('follicle', name=dag + '_FOLL')
    foll_grp = cmds.listRelatives(foll, p=True)
    foll_grp = cmds.rename(foll_grp, foll + '_GRP')

    pos = cmds.xform(dag, t=True, ws=True, q=True)
    point = om.MPoint(om.MVector(pos))

    parU, parV, face = plane.getUVAtPoint(point, space=4)

    cmds.connectAttr(foll + '.outTranslate', foll_grp + '.translate')
    cmds.connectAttr(foll + '.outRotate', foll_grp + '.rotate')
    cmds.connectAttr(geo_shape + '.outMesh', foll + '.inputMesh')
    cmds.connectAttr(geo_shape + '.worldMatrix', foll + '.inputWorldMatrix')
    cmds.setAttr(foll + '.parameterU', parU)
    cmds.setAttr(position_attr, parV)
    cmds.connectAttr(position_attr, foll + '.parameterV')

    constraint.simple_constraint(foll_grp, dag, snap=False)
