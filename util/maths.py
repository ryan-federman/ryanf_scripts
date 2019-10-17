import maya.cmds as cmds
import maya.api.OpenMaya as om


def get_normal_of_plane(first_loc, second_loc, third_loc):
    # get vectors of plane
    root_pos = cmds.xform(first_loc, q=True, ws=True, t=True)
    mid_pos = cmds.xform(second_loc, q=True, ws=True, t=True)
    end_pos = cmds.xform(third_loc, q=True, ws=True, t=True)

    root_vec = om.MVector(root_pos[0], root_pos[1], root_pos[2])
    mid_vec = om.MVector(mid_pos[0], mid_pos[1], mid_pos[2])
    end_vec = om.MVector(end_pos[0], end_pos[1], end_pos[2])

    upper_vec = (mid_vec - root_vec).normal()
    line_vec = (end_vec - mid_vec).normal()

    normalVector = (upper_vec ^ line_vec).normal()

    return normalVector


def create_matrix(x_vec, y_vec, z_vec, pos):
    matrix = (x_vec[0], x_vec[1], x_vec[2], 0,
              y_vec[0], y_vec[1], y_vec[2], 0,
              z_vec[0], z_vec[1], z_vec[2], 0,
              pos[0], pos[1], pos[2], 0)
    return matrix


def plane_matrix(vectors):
    norm_vec = get_normal_of_plane(vectors[0], vectors[1], vectors[2])

    vec1 = om.MVector(cmds.xform(vectors[0], t=True, ws=True, q=True))
    vec2 = om.MVector(cmds.xform(vectors[1], t=True, ws=True, q=True))

    up_vec = (vec1 - vec2).normal()

    side_vec = norm_vec ^ up_vec

    pos_x = 0
    pos_y = 0
    pos_z = 0
    for each in vectors:
        pos = cmds.xform(each, t=True, ws=True, q=True)
        pos_x += pos[0]
        pos_y += pos[1]
        pos_z += pos[2]
    pos_x = pos_x/4.0
    pos_y = pos_y/4.0
    pos_z = pos_z/4.0
    pos = [pos_x, pos_y, pos_z]

    mtx = create_matrix(up_vec, norm_vec, side_vec, pos)

    return mtx


def point_to_plane(pointA, pointB, pointC, project_point):
        A = om.MVector(pointA)
        B = om.MVector(pointB)
        C = om.MVector(pointC)
        D = om.MVector(project_point)

        v1 = B - A
        v2 = B - C
        n = (v1 ^ v2).normal()

        d = ((n.x * B.x) + (n.y * B.y) + (n.z * B.z)) * -1.0

        distance = (n.x * D.x) + (n.y * D.y) + (n.z * D.z) + d
        scaled_normal = n * distance

        final_point = D - scaled_normal

        return final_point


def axis_in_matrix(matrix, axis='+x'):
    ''' Gets the position of a vector within a given matrix
    Args:
        matrix (om.MMatrix()): matrix to get vector from
        axis (str): +x, -x, +y, -y, +z, -z
    Returns:
        om.MVector(): point within matrix
    '''
    point = None

    x = om.MVector(matrix[0], matrix[1], matrix[2])
    y = om.MVector(matrix[4], matrix[5], matrix[6])
    z = om.MVector(matrix[8], matrix[9], matrix[10])
    pos = om.MVector(matrix[12], matrix[13], matrix[14])

    if axis == '+x':
        point = x + pos
    elif axis == '-x':
        point = -x + pos
    elif axis == '+y':
        point = y + pos
    elif axis == '-y':
        point = -y + pos
    elif axis == '+z':
        point = z + pos
    elif axis == '-z':
        point = -z + pos

    return point
