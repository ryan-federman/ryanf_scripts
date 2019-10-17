import numpy as np

import maya.cmds as cmds
import maya.api.OpenMaya as om

import millrigger.modules.NY.misc.ryanf_scripts.util.component as component
import millrigger.modules.NY.misc.ryanf_scripts.create.dag as dg


from rigging_utils.create import curves
from rigging_utils import constraint
from rigging_utils import shape
from rigging_utils import attribute
from rigging_utils import maths


def nurbs_plane(dag_pos, name='generic', sections=30, width=1):
    """Creates a nurbs plane based on two given positions
    Args:
        dag_pos (list[tuple(float)]): Positions that are used for the beginning
                                      and end of the vector
        name (str): Base name for the plane that is created
        sections (int): Amount of sections on the plane
    Returns:
        list[str]: Plane object name and node name
    """
    crvs = []
    pos1 = om.MVector(dag_pos[0])
    pos2 = om.MVector(dag_pos[1])

    for x in range(2):
        mtx1 = om.MMatrix()
        mtx1.setElement(3, 2, width)

        mtx2 = om.MMatrix()
        mtx2.setElement(3, 2, (width) * -1)

        crv = curves.curve_from_matrices([mtx1, mtx2], degree=1)
        crvs.append(crv)

    cmds.xform(crvs[0], t=pos1, ws=True)
    cmds.xform(crvs[1], t=pos2, ws=True)

    plane = cmds.loft(crvs[0], crvs[1],
                      name=name,
                      ch=True,
                      uniform=True,
                      sectionSpans=sections,
                      range=False,
                      polygon=0,
                      rsn=True)
    cmds.delete(crvs)

    return plane


def birail_nurbs_plane(dags, name, side_vector):
    """
    Args:
        dags[(str)]: dag nodes to control plane
        name (str): base name of plane
        side_vector (om.MVector()): side vector to orient/create plane

    Returns:
        str: nurbs plane
    """
    mtxs = []
    side_vector = side_vector * 2
    other_side_vector = side_vector * -1
    for each in dags:
        mtx = cmds.xform(each, matrix=True, ws=True, q=True)
        mtxs.append(mtx)
    mtx1 = om.MMatrix()
    mtx1.setElement(3, 0, side_vector[0])
    mtx1.setElement(3, 1, side_vector[1])
    mtx1.setElement(3, 2, side_vector[2])
    mtx2 = om.MMatrix()
    mtx2.setElement(3, 0, other_side_vector[0])
    mtx2.setElement(3, 1, other_side_vector[1])
    mtx2.setElement(3, 2, other_side_vector[2])

    prof_crv1 = curves.curve_from_matrices(mtxs, name=name + '_prof1_CRV', degree=2)
    prof_crv2 = curves.curve_from_matrices(mtxs, name=name + '_prof2_CRV', degree=2)

    rail_crv1 = curves.curve_from_matrices([mtx1, mtx2], name=name + '_rail1_CRV', degree=1)
    rail_crv2 = curves.curve_from_matrices([mtx1, mtx2], name=name + '_rail2_CRV', degree=1)

    cmds.rebuildCurve(prof_crv1, ch=1, rpo=1, kr=0, kcp=1, kt=0, s=30, d=2, tol=0.01)
    cmds.rebuildCurve(prof_crv2, ch=1, rpo=1, kr=0, kcp=1, kt=0, s=30, d=2, tol=0.01)

    plane = cmds.doubleProfileBirailSurface(prof_crv1,
                                            prof_crv2,
                                            rail_crv1,
                                            rail_crv2,
                                            po=0,
                                            name=name)

    constraint.simple_constraint(dags[0], rail_crv1)
    constraint.simple_constraint(dags[-1], rail_crv2)

    for x, each in enumerate(dags):
        scon1 = cmds.createNode("millSimpleConstraint", name=prof_crv1 + '_MSC')
        scon2 = cmds.createNode("millSimpleConstraint", name=prof_crv1 + '_MSC')

        cmds.connectAttr(each + '.worldMatrix[0]', scon1 + '.inMatrix')
        cmds.connectAttr(prof_crv1 + '.parentInverseMatrix[0]', scon1 + '.parentInverseMatrix')

        cmds.connectAttr(each + '.worldMatrix[0]', scon2 + '.inMatrix')
        cmds.connectAttr(prof_crv2 + '.parentInverseMatrix[0]', scon2 + '.parentInverseMatrix')

        cmds.setAttr(scon1 + '.translateOffset', side_vector[0], side_vector[1], side_vector[2])
        cmds.setAttr(scon2 + '.translateOffset', side_vector[0], side_vector[1], side_vector[2])

        cmds.connectAttr(scon1 + '.outTranslate', prof_crv1 + '.cv[{}]'.format(x))
        cmds.connectAttr(scon2 + '.outTranslate', prof_crv2 + '.cv[{}]'.format(x))

    return plane


def replace_shape(dag, curve_type):
    '''Replaces a nurbscurve under a control

    Args:
        dag (str): dag node in which the new shape node will be put under
        new_shape (str): type of nurbscurve being created
    Returns:
        (str): new shape node
    '''

    new_shape = shape.create_nurbscurve(curve_type)
    old_shape = cmds.listRelatives(dag, s=True)

    cmds.parent(new_shape, dag, r=True, s=True)
    cmds.delete(old_shape)

    return new_shape


def modify_shape(dag, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1), rotationOrder='xyz'):
    '''Modify a shape node without affecting transforms

    Args:
        dag (str): dag node of shape node
        translate
    '''
    rotate_dict = {}
    rotate_dict['x'] = rotate[0]
    rotate_dict['y'] = rotate[1]
    rotate_dict['z'] = rotate[2]

    cvs = cmds.ls('{}.cv[*]'.format(dag))
    cmds.select(cvs)

    cmds.move(*translate, relative=True)
    for each in rotationOrder:
        if each == 'x':
            cmds.rotate(rotate[0], 0, 0)
        elif each == 'y':
            cmds.rotate(0, rotate[1], 0)
        elif each == 'z':
            cmds.rotate(0, 0, rotate[2])
    cmds.scale(*scale)

    cmds.select(clear=True)


def closest_point_on_surface(surface, point):
    ''' find closest point on surface and it's UV values

    Args:
        surface (str): nurbs surface
        point tuple(float, float, float): position to reference
    Return:
         tuple(float, float, float), (int), (int): position, u param, v param
    '''
    sel = om.MSelectionList()
    sel.add(surface)

    plane = om.MFnNurbsSurface()
    plane.setObject(sel.getDagPath(0))

    point = om.MPoint(om.MVector(point))

    pos, parU, parV = plane.closestPoint(point)

    return pos, parU, parV


def attach_to_surface(surface, dag, snap=False, scale=False):
    # nodes to attach dag to surface
    POSI = cmds.createNode('pointOnSurfaceInfo', name=dag + '_POSI')
    matrix_node = cmds.createNode('fourByFourMatrix', name=dag + '_4X4')
    foll = cmds.createNode('transform', name=dag + '_custom_foll')
    foll_MSC = cmds.createNode('millSimpleConstraint', name=foll + '_MSC')

    # find closest point on surface and it's UV values
    dag_pos = cmds.xform(dag, t=True, ws=True, q=True)
    pos, parU, parV = closest_point_on_surface(surface, dag_pos)

    cmds.xform(dag, t=(pos[0], pos[1], pos[2]), ws=True)

    # attach dag to surface
    cmds.connectAttr(surface + '.local', POSI + '.inputSurface')
    cmds.setAttr(POSI + '.parameterU', parU)
    cmds.setAttr(POSI + '.parameterV', parV)

    # create matrix from POSI node
    cmds.connectAttr(POSI + '.normalizedTangentVX', matrix_node + '.in00')
    cmds.connectAttr(POSI + '.normalizedTangentVY', matrix_node + '.in01')
    cmds.connectAttr(POSI + '.normalizedTangentVZ', matrix_node + '.in02')
    cmds.connectAttr(POSI + '.normalizedNormalX', matrix_node + '.in10')
    cmds.connectAttr(POSI + '.normalizedNormalY', matrix_node + '.in11')
    cmds.connectAttr(POSI + '.normalizedNormalZ', matrix_node + '.in12')
    cmds.connectAttr(POSI + '.normalizedTangentUX', matrix_node + '.in20')
    cmds.connectAttr(POSI + '.normalizedTangentUY', matrix_node + '.in21')
    cmds.connectAttr(POSI + '.normalizedTangentUZ', matrix_node + '.in22')
    cmds.connectAttr(POSI + '.positionX', matrix_node + '.in30')
    cmds.connectAttr(POSI + '.positionY', matrix_node + '.in31')
    cmds.connectAttr(POSI + '.positionZ', matrix_node + '.in32')

    cmds.connectAttr(matrix_node + '.output', foll_MSC + '.inMatrix')
    cmds.connectAttr(foll + '.parentInverseMatrix[0]', foll_MSC + '.parentInverseMatrix')

    cmds.connectAttr(foll_MSC + '.outTranslate', foll + '.translate')
    cmds.connectAttr(foll_MSC + '.outRotate', foll + '.rotate')

    constraint.simple_constraint(foll, dag, snap=snap)

    if scale:
        POSI0 = cmds.createNode('pointOnSurfaceInfo', name=dag + '_scale0_POSI')
        POSI1 = cmds.createNode('pointOnSurfaceInfo', name=dag + '_scale1_POSI')
        dist = cmds.createNode('math_DistancePoints', name=dag + '_DIST')
        div = cmds.createNode('math_Divide', name=dag + '_DIV')

        cmds.connectAttr(surface + '.local', POSI0 + '.inputSurface')
        cmds.connectAttr(surface + '.local', POSI1 + '.inputSurface')
        cmds.setAttr(POSI0 + '.parameterU', 0)
        cmds.setAttr(POSI1 + '.parameterU', 1)
        cmds.setAttr(POSI0 + '.parameterV', parV)
        cmds.setAttr(POSI1 + '.parameterV', parV)

        cmds.connectAttr(POSI0 + '.position', dist + '.input1')
        cmds.connectAttr(POSI1 + '.position', dist + '.input2')

        init_distance = cmds.getAttr(dist + '.output')
        cmds.setAttr(div + '.input2', init_distance)
        cmds.connectAttr(dist + '.output', div + '.input1')

        cmds.connectAttr(div + '.output', foll + '.sz')

    return foll


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
    par_attr = attribute.add_generic_blend(dag, 'curveDistance', max_value=max_param)
    cmds.connectAttr(par_attr, ctrl_poci + '.parameter')
    cmds.connectAttr(par_attr, dag_poci + '.parameter')

    # connect dag to curve
    cmds.connectAttr(dag + '_ZERO.parentInverseMatrix[0]', msc + '.parentInverseMatrix')
    cmds.connectAttr(msc + '.outTranslate', dag + '_ZERO.translate')
    cmds.connectAttr(msc + '.outRotate', dag + '_ZERO.rotate')


def linspace_curve(curve, num):
    ''' Provide matrices that are an equal distribution along a curve

    Args:
        curve (str): name of curve to get information from
        num (int): number of matrices to be returned
    Return:
         list[om.MMatrix()]: list of matrices
    '''
    sel = om.MSelectionList()
    sel.add(curve)

    crv = om.MFnNurbsCurve()
    crv.setObject(sel.getDagPath(0))

    curve_length = crv.length()
    lengths = np.linspace(0, curve_length, num)
    matrices = []
    # create instance to control pos and rot of controls being attached
    for length in lengths:
        param = crv.findParamFromLength(length)
        if param == 0:
            param = .001
        if length == lengths[-1]:
            param -= .001

        aim_vec = crv.tangent(param)
        side_vec = crv.normal(param)
        up_vec = aim_vec ^ side_vec
        pos = crv.getPointAtParam(param)

        mtx = maths.vectors_to_matrix(row1=aim_vec.normal(),
                                      row2=up_vec.normal(),
                                      row3=side_vec.normal(),
                                      row4=pos)
        matrices.append(mtx)

    return matrices
