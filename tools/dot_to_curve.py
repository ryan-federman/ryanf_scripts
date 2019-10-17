import numpy as np

import maya.cmds as cmds
import maya.api.OpenMaya as om

import millrigger.modules.NY.misc.ryanf_scripts.create.dag as dg

from rigging_utils.create import curves
from rigging_utils import constraint
from rigging_utils import shape


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


def dag_to_curve(dag, curve):
    ''' Provide matrices that are an equal distribution along a curve

    Args:
        dag (str): name of dag node to attach to curve
        curve (str): name of curve to attach to
    '''
    sel = om.MSelectionList()
    sel.add(curve)

    crv = om.MFnNurbsCurve()
    crv.setObject(sel.getDagPath(0))

    curve_length = crv.length()
    max_param = crv.findParamFromLength(curve_length)

    mscs = []
    up_vecs = []
    ctrl_params = []

    # create control to control up vector of curve
    ctrl_height = curve_length/10.0
    param = 0.001
    ctrl = dg.create_dag('C_crv_upvec', type='control', ctrl_type='triangle', offset=True)
    ctrl_ofs = ctrl + '_OFS'
    ctrl_zero = ctrl + '_ZERO'
    line_loc = cmds.spaceLocator(name='C_crv_upvec_LOC')[0]
    ctrl_poci = cmds.createNode('pointOnCurveInfo', name=ctrl + '_POCI')
    dm = cmds.createNode('decomposeMatrix', name=ctrl + '_DM')
    sub_vec = cmds.createNode('math_SubtractVector', name=ctrl + '_SV')
    normalize = cmds.createNode('math_NormalizeVector', name=ctrl + '_NV')
    ctrl_params.append(param)

    cmds.connectAttr(curve + '.worldSpace[0]', ctrl_poci + '.inputCurve')
    cmds.setAttr(ctrl_poci + '.parameter', param)

    cmds.connectAttr(ctrl_poci + '.position', ctrl_zero + '.translate')
    cmds.connectAttr(ctrl_poci + '.position', line_loc + '.translate')

    cmds.setAttr(ctrl_ofs + '.ty', ctrl_height)
    cmds.connectAttr(ctrl + '.worldMatrix[0]', dm + '.inputMatrix')

    cmds.connectAttr(dm + '.outputTranslate', sub_vec + '.input1')
    cmds.connectAttr(line_loc + '.translate', sub_vec + '.input2')

    cmds.connectAttr(sub_vec + '.output', normalize + '.input')

    line_curve = curves.curve_from_objects([ctrl, line_loc], name=ctrl + '_vec_CRV')
    cmds.setAttr(line_curve + '.overrideEnabled', 1)
    cmds.setAttr(line_curve + '.overrideDisplayType', 2)

    up_vecs.append(normalize)

    # create instance to control pos and rot of controls being attached
    dag_poci = cmds.createNode('pointOnCurveInfo')
    fbf = cmds.createNode('fourByFourMatrix')
    msc = cmds.createNode('millSimpleConstraint')
    z_vec = cmds.createNode('vectorProduct')
    mscs.append(msc)

    # connect vecs to pair blend
    cmds.setAttr(z_vec + '.operation', 2)
    cmds.connectAttr(normalize + '.output', z_vec + '.input1')
    cmds.connectAttr(dag_poci + '.normalizedTangent', z_vec + '.input2')

    cmds.connectAttr(curve + '.worldSpace[0]', dag_poci + '.inputCurve')
    cmds.setAttr(dag_poci + '.parameter', param)
    cmds.connectAttr(dag_poci + '.normalizedTangentX', fbf + '.in00')
    cmds.connectAttr(dag_poci + '.normalizedTangentY', fbf + '.in01')
    cmds.connectAttr(dag_poci + '.normalizedTangentZ', fbf + '.in02')
    cmds.connectAttr(normalize + '.outputX', fbf + '.in10')
    cmds.connectAttr(normalize + '.outputY', fbf + '.in11')
    cmds.connectAttr(normalize + '.outputZ', fbf + '.in12')
    cmds.connectAttr(z_vec + '.outputX', fbf + '.in20')
    cmds.connectAttr(z_vec + '.outputY', fbf + '.in21')
    cmds.connectAttr(z_vec + '.outputZ', fbf + '.in22')
    cmds.connectAttr(dag_poci + '.positionX', fbf + '.in30')
    cmds.connectAttr(dag_poci + '.positionY', fbf + '.in31')
    cmds.connectAttr(dag_poci + '.positionZ', fbf + '.in32')
    cmds.connectAttr(fbf + '.output', msc + '.inMatrix')

    # attribute on dag to control the position along the curve
    par_attr = cmds.ls(dag + '.curveDistance')
    if par_attr:
        par_attr = par_attr[0]
    else:
        cmds.addAttr(dag, longName='curveDistance', at='float', maxValue=max_param, minValue=0, defaultValue=0, keyable=True)
        par_attr = dag + '.curveDistance'
    cmds.connectAttr(par_attr, ctrl_poci + '.parameter')
    cmds.connectAttr(par_attr, dag_poci + '.parameter')

    # connect dag to curve
    cmds.connectAttr(dag + '_ZERO.parentInverseMatrix[0]', msc + '.parentInverseMatrix')
    cmds.connectAttr(msc + '.outTranslate', dag + '_ZERO.translate')
    cmds.connectAttr(msc + '.outRotate', dag + '_ZERO.rotate')

    # connect parameter attribute to rotation of dot
    mult = dag.split('CTRL')[0] + 'rot_MULT'
    cmds.connectAttr(par_attr, mult + '.input2')
