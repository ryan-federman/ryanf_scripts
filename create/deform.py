import maya.cmds as cmds

import millrigger.modules.NY.misc.ryanf_scripts.util.control_shapes as ctrls
import millrigger.modules.NY.misc.ryanf_scripts.util.component as component
import millrigger.modules.NY.misc.ryanf_scripts.util.maths as math
import millrigger.modules.NY.misc.ryanf_scripts.create.nurbs as nrb

from rigging_utils import constraint
from rigging_utils import skin
from rigging_utils import cluster


def create_softmod(name, face):
    # create plane for follicle
    plane = cmds.polyPlane(name=name + '_foll_GEO')
    cmds.setAttr(plane[1] + '.sw', 1)
    cmds.setAttr(plane[1] + '.sh', 1)
    cmds.setAttr(plane[0] + '.s', .01, .01, .01)

    cmds.delete(plane[0], ch=True)
    cmds.makeIdentity(plane[0], apply=True)

    # move plane to face
    vertices = component.face_to_vertex([face])
    pos_vtx_list = []
    for each in vertices:
        pos = cmds.xform(each, t=True, ws=True, q=True)
        pos = (pos[0], pos[1], pos[2])
        pos_vtx_list.append(pos)

    mtx = math.plane_matrix(vertices)
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
    try:
        skin.copy_skincluster(geo, [plane_geo])
    except:
        constraint.simple_constraint(geo, plane[0], snap=False)

    # create controls
    soft_mod_ctrl = ctrls.diamond_shape(name + '_SOFT_CTRL')
    soft_mod_ctrl_pivot = ctrls.sphere_shape(name + '_SOFT_PIV_CTRL')
    soft_mod_ctrl_pivot_zero = cmds.createNode('transform', name=soft_mod_ctrl_pivot + '_ZERO')

    cmds.setAttr(soft_mod_ctrl + '.s', 0.4, 0.4, 0.4)
    cmds.makeIdentity(soft_mod_ctrl, apply=True)
    cmds.addAttr(soft_mod_ctrl, ln='falloff', at='double', min=0, keyable=True)
    cmds.addAttr(soft_mod_ctrl, ln='falloffMode', at='enum', en='volume:surface', keyable=True)
    cmds.parent(soft_mod_ctrl, soft_mod_ctrl_pivot)
    cmds.parent(soft_mod_ctrl_pivot, soft_mod_ctrl_pivot_zero)
    constraint.simple_constraint(transform, soft_mod_ctrl_pivot_zero, snap=True)

    # create soft mod
    sm = cluster.create(geo, name + '_softMod', soft=True)
    constraint.simple_constraint(soft_mod_ctrl_pivot, sm[0], snap=True)
    constraint.simple_constraint(soft_mod_ctrl, sm[1], snap=True)
    cmds.connectAttr(soft_mod_ctrl + '.falloff', sm[1] + '.falloff')
    cmds.connectAttr(soft_mod_ctrl + '.falloffMode', sm[1] + '.falloffMode')


def lattice_clusters(lattice, surface=None, divisions='s', scale=False):
    ''' Creates clusters to control a lattice
    Args:
        lattice (str): name of lattice to control with clusters
        surface (str): if given attaches clusters to a nurbs surface
        divisions (str): s, t, u, or all, how to attach points to clusters
    '''

    s_divisions = cmds.getAttr(lattice + '.sDivisions')
    t_divisions = cmds.getAttr(lattice + '.tDivisions')
    u_divisions = cmds.getAttr(lattice + '.uDivisions')

    clusters = []
    if divisions == 's':
        for i in range(s_divisions):
            pts = cmds.ls('{}.pt[{}][*][*]'.format(lattice, i), fl=True)
            cls = cmds.cluster(pts, name='{}_{}_CLS'.format(lattice, i))[1]
            clusters.append(cls)
    elif divisions == 't':
        for i in range(t_divisions):
            pts = cmds.ls('{}.pt[*][{}][*]'.format(lattice, i), fl=True)
            cls = cmds.cluster(pts, name='{}_{}_CLS'.format(lattice, i))[1]
            clusters.append(cls)
    elif divisions == 'u':
        for i in range(u_divisions):
            pts = cmds.ls('{}.pt[*][*][{}]'.format(lattice, i), fl=True)
            cls = cmds.cluster(pts, name='{}_{}_CLS'.format(lattice, i))[1]
            clusters.append(cls)
    else:
        pts = cmds.ls('{}.pt[{}][{}][{}]'.format(lattice, s_divisions, t_divisions, u_divisions), fl=True)
        for i, pt in enumerate(pts):
            cls = cmds.cluster([pt], name='{}_{}_CLS'.format(lattice, i))[1]
            clusters.append(cls)

    # attach all clusters to surface
    if surface:
        for cls in clusters:
            cls_grp = cmds.createNode('transform', name=cls + '_GRP')
            shape = cls + 'Shape'
            pos = cmds.getAttr(shape + '.origin')[0]
            cmds.xform(cls_grp, t=pos, ws=True)
            cmds.parent(cls, cls_grp)
            nrb.attach_to_surface(surface, cls_grp, snap=False, scale=scale)

