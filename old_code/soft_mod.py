import maya.cmds as cmds
import maya.api.OpenMaya as om
from rigging_utils import skin
from rigging_utils import constraint
from rigging_utils import cluster


def diamond_shape(name):
    ctrl1 = cmds.circle(name=name + '_01Shape')
    cmds.setAttr(ctrl1[1] + '.degree', 1)
    cmds.setAttr(ctrl1[1] + '.sections', 4)
    ctrl2 = cmds.duplicate(ctrl1[0], name=name + '_02Shape')[0]
    cmds.setAttr(ctrl2 + '.rx', 90)
    ctrl3 = cmds.duplicate(ctrl2, name=name + '_03Shape')[0]
    cmds.setAttr(ctrl3 + '.rz', 90)

    cmds.makeIdentity(ctrl1, apply=True)
    cmds.makeIdentity(ctrl2, apply=True)
    cmds.makeIdentity(ctrl3, apply=True)

    transform = cmds.createNode('transform', name=name)

    shape1 = cmds.listRelatives(ctrl1, s=True)[0]
    shape2 = cmds.listRelatives(ctrl2, s=True)[0]
    shape3 = cmds.listRelatives(ctrl3, s=True)[0]

    cmds.parent(shape1, transform, r=True, shape=True)
    cmds.parent(shape2, transform, r=True, shape=True)
    cmds.parent(shape3, transform, r=True, shape=True)

    cmds.delete(ctrl1)
    cmds.delete(ctrl2)
    cmds.delete(ctrl3)

    return transform


def sphere_shape(name):
    ctrl1 = cmds.circle(name=name + '_01Shape')
    ctrl2 = cmds.duplicate(ctrl1[0], name=name + '_02Shape')[0]
    cmds.setAttr(ctrl2 + '.rx', 90)
    ctrl3 = cmds.duplicate(ctrl2, name=name + '_03Shape')[0]
    cmds.setAttr(ctrl3 + '.rz', 90)

    cmds.makeIdentity(ctrl1, apply=True)
    cmds.makeIdentity(ctrl2, apply=True)
    cmds.makeIdentity(ctrl3, apply=True)

    transform = cmds.createNode('transform', name=name)

    shape1 = cmds.listRelatives(ctrl1, s=True)[0]
    shape2 = cmds.listRelatives(ctrl2, s=True)[0]
    shape3 = cmds.listRelatives(ctrl3, s=True)[0]

    cmds.parent(shape1, transform, r=True, shape=True)
    cmds.parent(shape2, transform, r=True, shape=True)
    cmds.parent(shape3, transform, r=True, shape=True)

    cmds.delete(ctrl1)
    cmds.delete(ctrl2)
    cmds.delete(ctrl3)

    return transform


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


def face_to_vtx(faces):
    vertices = cmds.polyListComponentConversion(faces, ff=True, tv=True)
    vertices = cmds.ls(vertices, fl=True)

    return vertices


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


def create_softmod(name, face):
    # create plane for follicle
    plane = cmds.polyPlane(name=name + '_foll_GEO')
    cmds.setAttr(plane[1] + '.sw', 1)
    cmds.setAttr(plane[1] + '.sh', 1)
    cmds.setAttr(plane[0] + '.s', .01, .01, .01)

    cmds.delete(plane[0], ch=True)
    cmds.makeIdentity(plane[0], apply=True)

    # move plane to face
    vertices = face_to_vtx(face)
    pos_vtx_list = []
    for each in vertices:
        pos = cmds.xform(each, t=True, ws=True, q=True)
        pos = (pos[0], pos[1], pos[2])
        pos_vtx_list.append(pos)

    mtx = plane_matrix(vertices)
    cmds.xform(plane[0], matrix=mtx)

    # create follicle
    plane_geo = cmds.listRelatives(plane[0], s=True)[0]
    transform = cmds.createNode('transform', name=name + '_foll')
    foll = cmds.createNode('follicle', name=name + '_follShape', parent=transform)
    cmds.connectAttr(foll + ".outTranslate", transform + ".t", force=True)
    cmds.connectAttr(foll + ".outRotate", transform + ".r", force=True)
    cmds.setAttr(foll + ".visibility", False)
    cmds.connectAttr(plane_geo + '.outMesh', foll + '.inputMesh')
    cmds.connectAttr(plane_geo + '.worldMatrix[0]', foll + '.inputWorldMatrix')
    cmds.setAttr(foll + '.parameterU', 0.5)
    cmds.setAttr(foll + '.parameterV', 0.5)

    # copy skin weights to plane
    geo = face.split('.')[0]
    skin.copy_skincluster(geo, [plane_geo])

    # create controls
    soft_mod_ctrl = diamond_shape(name + '_SOFT_CTRL')
    soft_mod_ctrl_pivot = sphere_shape(name + '_SOFT_PIV_CTRL')
    soft_mod_ctrl_pivot_zero = cmds.createNode('transform', name=soft_mod_ctrl_pivot + '_ZERO')

    cmds.setAttr(soft_mod_ctrl + '.s', 0.4, 0.4, 0.4)
    cmds.makeIdentity(soft_mod_ctrl, apply=True)
    cmds.addAttr(soft_mod_ctrl, ln='falloff', at='double', min=0, keyable=True)
    cmds.parent(soft_mod_ctrl, soft_mod_ctrl_pivot)
    cmds.parent(soft_mod_ctrl_pivot, soft_mod_ctrl_pivot_zero)
    constraint.simple_constraint(transform, soft_mod_ctrl_pivot_zero, snap=True)

    # create soft mod
    sm = cluster.create(geo, name + 'softMod', soft=True)
    constraint.simple_constraint(soft_mod_ctrl_pivot, sm[0], snap=True)
    constraint.simple_constraint(soft_mod_ctrl, sm[1], snap=True)
    cmds.connectAttr(soft_mod_ctrl + '.falloff', sm[1] + '.falloff')
