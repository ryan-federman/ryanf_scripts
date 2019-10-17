import maya.cmds as cmds
import maya.api.OpenMaya as om

from rigging_utils import shape
from rigging_utils.create import curves
from rigging_utils import constraint
from rigging_utils import attribute


def dag_on_vector(dag_pos, dag_num, dag_type, name='generic',
                  control_type='box', scale=1.0):
    """ Creates an even distribution of DAG nodes along a vector

    Args:
        dag_pos (list[tuple(float)]): Positions that are used for the beginning
                                      and end of the vector
        dag_num (int): Number of DAG nodes created
        dag_type (str): Type of DAG node created,
                        inputs can be either 'CTRL' or 'BONE'
        name (str): base name for DAG nodes
        control_type (str): If the dag type is 'CTRL' then this is the type
                            of control created
        scale (float): How big the controls are created

    Returns:
        list[str]: List of DAG nodes created
    """

    # get aim vector for DAGs to be positioned along
    pos1 = om.MVector(dag_pos[0])
    pos2 = om.MVector(dag_pos[1])
    aim_vec = pos2 - pos1

    # create DAGs along vector
    dags = []
    for x in range(0, dag_num):
        x1 = float(x)
        num_str = str(x)
        if x < 10:
            num_str = '0' + num_str
        pos = ((1.0/float((dag_num-1))) * (aim_vec)) * x1 + pos1
        zero = cmds.createNode('transform', name='C_{}_{}_{}_ZERO'.format(name, num_str, dag_type))
        ofs = cmds.createNode('transform', name='C_{}_{}_{}_OFS'.format(name, num_str, dag_type))
        cmds.select(clear=True)
        if dag_type == 'CTRL':
            dag = shape.create_nurbscurve(control_type)
            dag = cmds.listRelatives(dag, p=True)
            dag = cmds.rename(dag, 'C_{}_{}_CTRL'.format(name, num_str))
        elif dag_type == 'BONE':
            dag = cmds.joint(name='C_{}_{}_BONE'.format(name, num_str))
        dags.append(dag)

        cmds.parent(ofs, zero)
        cmds.parent(dag, ofs)
        cmds.xform(zero, t=pos, ws=True)

        cmds.select(clear=True)
        if dag_type != 'BONE':
            cmds.setAttr(dag + '.s', scale, scale, scale)
            cmds.makeIdentity(dag, apply=True)
    return dags


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

