import numpy as np

import maya.api.OpenMaya as om
import maya.cmds as cmds

from rigging_utils import constraint


def populate_among_plane(surface, dag, num):
    sel = om.MSelectionList()
    sel.add(surface)

    plane = om.MFnNurbsSurface()
    plane.setObject(sel.getDagPath(0))

    params = np.linspace(0, 1, num)

    new_dags = []
    for par in params:
        new_dag = cmds.duplicate(dag)[0]
        pos = plane.getPointAtParam(0.5, par)
        cmds.xform(new_dag, t=(pos[0], pos[1], pos[2]), ws=True)
        new_dags.append(new_dag)

    for dag in new_dags:
        attach_to_surface(surface, dag, snap=True)


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
