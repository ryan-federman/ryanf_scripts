import maya.cmds as cmds
import maya.api.OpenMaya as om


def face_to_vertex(faces):
    vertices = []
    for face in faces:
        vtxs = cmds.ls(cmds.polyListComponentConversion(face, tv=True), fl=True)
        for vtx in vtxs:
            vertices.append(vtx)

    return vertices


def move_points_to_geo(points, geo):
    """ Moves selected points to a piece of geometry with matching point order
    Args:
        points [str]: list of selected points to move
        geo (str): geometry to move the points to
    """

    for point in points:
        vtx_num = point.split('.')[-1]
        vtx = geo + '.' + vtx_num

        pos = cmds.xform(vtx, t=True, ws=True, q=True)
        cmds.xform(point, t=pos, ws=True)


def closest_vtx_on_mesh(geo, point):
    obj = om.MSelectionList()
    obj.add(geo)
    mesh = om.MFnMesh(obj.getComponent(0)[0])

    pos = om.MPoint(point[0], point[1], point[2])
    point, face = mesh.getClosestPoint(pos, space=4)
    face = '{}.f[{}]'.format(geo, face)
    vertices = cmds.polyListComponentConversion(face, tv=True)
    vertices = cmds.ls(vertices, fl=True)
    start_pos = om.MVector(point[0], point[1], point[2])
    # find which vertex has the same position as the given point
    shortest_distance = None
    closest_vtx = None
    print vertices
    for i, vtx in enumerate(vertices):
        pos = cmds.xform(vtx, t=True, ws=True, q=True)
        end_pos = om.MVector(pos[0], pos[1], pos[2])
        distance = (start_pos - end_pos).length()
        if not closest_vtx:
            shortest_distance = distance
            closest_vtx = vtx
        elif distance < shortest_distance:
            shortest_distance = distance
            closest_vtx = vtx
        if distance == 0:
            break
        print i
    return closest_vtx
