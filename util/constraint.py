import maya.cmds as cmds
import maya.api.OpenMaya as om

from rigging_utils import constraint


def attach_to_surface(surface, dag):
    """Takes a dag node and attaches it to the nearest point on a surface,
       replacement for a follicle
    Args:
         surface (str): name of the transform of the nurbs surface that the dag
                        node will be attached to
         dag (str): name of the dag node which will be attached
    Returns:
        str: Name of transform that follows the surface
    """

    # nodes to attach dag to surface
    POSI = cmds.createNode('pointOnSurfaceInfo', name=dag + '_POSI')
    matrix_node = cmds.createNode('fourByFourMatrix', name=dag + '_4X4')
    foll = cmds.createNode('transform', name=dag + '_custom_foll')
    foll_MSC = cmds.createNode('millSimpleConstraint', name=foll + '_MSC')
    MM = cmds.createNode('multMatrix', name=dag + '_MM')

    # find closest point on surface and it's UV values
    sel = om.MSelectionList()
    sel.add(surface)

    plane = om.MFnNurbsSurface()
    plane.setObject(sel.getDagPath(0))

    point = om.MPoint(om.MVector(cmds.xform(dag, t=True, ws=True, q=True)))

    pos, parU, parV = plane.closestPoint(point)

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

    cmds.connectAttr(matrix_node + '.output', MM + '.matrixIn[0]')
    cmds.connectAttr(surface + '.worldMatrix[0]', MM + '.matrixIn[1]')

    cmds.connectAttr(MM + '.matrixSum', foll_MSC + '.inMatrix')
    cmds.connectAttr(foll + '.parentInverseMatrix[0]', foll_MSC + '.parentInverseMatrix')

    cmds.connectAttr(foll_MSC + '.outTranslate', foll + '.translate')
    cmds.connectAttr(foll_MSC + '.outRotate', foll + '.rotate')

    constraint.simple_constraint(foll, dag)

    return foll


def matrix_constraint(source, target, maintain_offset=True, connect='srt'):
    """
    Args:
        object (str): object that will be constraining an object
        target (str): object being constrained
        maintain_offset (bool): maintains the offset between the objects
        connect (str): connects scale, rotation, translation
    Returns:
        str: name of node that outputs translation and rotation values
    """

    if maintain_offset:
        # get matrix of target within the space of the source object
        proxy = cmds.duplicate(target)[0]
        cmds.parent(proxy, source)

        target_mtx = cmds.xform(proxy, matrix=True, ws=False, q=True)

        cmds.delete(proxy)

        # get vectors of matrix
        target_x = om.MVector((target_mtx[0], target_mtx[1], target_mtx[2]))
        target_y = om.MVector((target_mtx[4], target_mtx[5], target_mtx[6]))
        target_z = om.MVector((target_mtx[8], target_mtx[9], target_mtx[10]))
        pos_ofs = om.MVector((target_mtx[12], target_mtx[13], target_mtx[14]))

        x_ofs = pos_ofs + target_x
        y_ofs = pos_ofs + target_y
        z_ofs = pos_ofs + target_z

        # create the vectors of the target matrix
        x_vp = cmds.createNode('vectorProduct', name=source + '_xvec_VP')
        y_vp = cmds.createNode('vectorProduct', name=source + '_yvec_VP')
        z_vp = cmds.createNode('vectorProduct', name=source + '_zvec_VP')
        pos_vp = cmds.createNode('vectorProduct', name=source + '_posvec_VP')

        x_pma = cmds.createNode('plusMinusAverage', name=source + '_xvec_PMA')
        y_pma = cmds.createNode('plusMinusAverage', name=source + '_yvec_PMA')
        z_pma = cmds.createNode('plusMinusAverage', name=source + '_zvec_PMA')
        mtx = cmds.createNode('fourByFourMatrix', name=source + '_MTX')
        dm = cmds.createNode('decomposeMatrix', name=source + '_DM')

        cmds.setAttr(x_vp + '.input1', x_ofs[0], x_ofs[1], x_ofs[2])
        cmds.connectAttr(source + '.worldMatrix[0]', x_vp + '.matrix')
        cmds.setAttr(x_vp + '.operation', 4)

        cmds.setAttr(y_vp + '.input1', y_ofs[0], y_ofs[1], y_ofs[2])
        cmds.connectAttr(source + '.worldMatrix[0]', y_vp + '.matrix')
        cmds.setAttr(y_vp + '.operation', 4)

        cmds.setAttr(z_vp + '.input1', z_ofs[0], z_ofs[1], z_ofs[2])
        cmds.connectAttr(source + '.worldMatrix[0]', z_vp + '.matrix')
        cmds.setAttr(z_vp + '.operation', 4)

        cmds.setAttr(pos_vp + '.input1', pos_ofs[0], pos_ofs[1], pos_ofs[2])
        cmds.connectAttr(source + '.worldMatrix[0]', pos_vp + '.matrix')
        cmds.setAttr(pos_vp + '.operation', 4)

        cmds.setAttr(x_pma + '.operation', 2)
        cmds.connectAttr(x_vp + '.output', x_pma + '.input3D[0]')
        cmds.connectAttr(pos_vp + '.output', x_pma + '.input3D[1]')

        cmds.setAttr(y_pma + '.operation', 2)
        cmds.connectAttr(y_vp + '.output', y_pma + '.input3D[0]')
        cmds.connectAttr(pos_vp + '.output', y_pma + '.input3D[1]')

        cmds.setAttr(z_pma + '.operation', 2)
        cmds.connectAttr(z_vp + '.output', z_pma + '.input3D[0]')
        cmds.connectAttr(pos_vp + '.output', z_pma + '.input3D[1]')

        cmds.connectAttr(x_pma + '.output3Dx', mtx + '.in00')
        cmds.connectAttr(x_pma + '.output3Dy', mtx + '.in01')
        cmds.connectAttr(x_pma + '.output3Dz', mtx + '.in02')
        cmds.connectAttr(y_pma + '.output3Dx', mtx + '.in10')
        cmds.connectAttr(y_pma + '.output3Dy', mtx + '.in11')
        cmds.connectAttr(y_pma + '.output3Dz', mtx + '.in12')
        cmds.connectAttr(z_pma + '.output3Dx', mtx + '.in20')
        cmds.connectAttr(z_pma + '.output3Dy', mtx + '.in21')
        cmds.connectAttr(z_pma + '.output3Dz', mtx + '.in22')
        cmds.connectAttr(pos_vp + '.outputX', mtx + '.in30')
        cmds.connectAttr(pos_vp + '.outputY', mtx + '.in31')
        cmds.connectAttr(pos_vp + '.outputZ', mtx + '.in32')

        # connect matrix to target
        cmds.connectAttr(mtx + '.output', dm + '.inputMatrix')
        cmds.connectAttr(dm + '.outputTranslate', target + '.translate')
        cmds.connectAttr(dm + '.outputRotate', target + '.rotate')
