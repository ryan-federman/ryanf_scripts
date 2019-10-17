import maya.cmds as cmds
import maya.api.OpenMaya as om


class PointsToGeo():

    def __init__(self):
        self.source_geo = None
        self.target_geo = None

    def point_check(self, target_geo):
        source_vtxs = cmds.ls('{}.vtx[*]'.format(self.source_geo), fl=True)
        target_vtxs = cmds.ls('{}.vtx[*]'.format(target_geo), fl=True)

        if len(source_vtxs) != len(target_vtxs):
            cmds.warning('Geos do not have the same amount of vertices')

    def geo_check(self, dag):
        shape = cmds.listRelatives(dag, s=True)[0]
        shape_type = cmds.nodeType(shape)
        if shape_type != 'mesh':
            raise ValueError('Select a piece of geometry')

    def get_geo(self, dag, shape=False):
        self.geo_check(dag)
        if shape:
            geo = cmds.listRelatives(dag, s=True)
        else:
            geo = dag
        return geo

    def get_source(self):
        self.source_geo = self.get_geo(cmds.ls(sl=True)[0])

    def closest_point_on_mesh(self, geo, point):
        obj = om.MSelectionList()
        obj.add(geo)
        mesh = om.MFnMesh(obj.getComponent(0)[0])

        pos = om.MPoint(point[0], point[1], point[2])
        point = mesh.getClosestPoint(pos, space=4)

        return point

    def match_point_order(self):
        selection = cmds.ls(sl=True, fl=True)
        if 'vtx' in selection[0]:
            target_geo = selection[0].split('.')[0]
            self.point_check(target_geo)
            for target_vtx in selection:
                source_vtx = '{}.{}'.format(self.source_geo, target_vtx.split('.')[1])
                pos = cmds.xform(source_vtx, t=True, ws=True, q=True)
                cmds.move(pos[0], pos[1], pos[2], [target_vtx], ws=True)
        else:
            self.geo_check(selection[0])
            vtxs = cmds.ls('{}.vtx[*]'.format(selection[0]), fl=True)
            for i, target_vtx in enumerate(vtxs):
                source_vtx = '{}.vtx[{}]'.format(self.source_geo, i)
                pos = cmds.xform(source_vtx, t=True, ws=True, q=True)
                cmds.move(pos[0], pos[1], pos[2], [target_vtx], ws=True)

    def match_closest_point(self):
        selection = cmds.ls(sl=True, fl=True)
        if 'vtx' in selection[0]:
            target_geo = selection[0].split('.')[0]
            self.point_check(target_geo)
            for target_vtx in selection:
                target_pos = cmds.xform(target_vtx, t=True, ws=True, q=True)
                pos = self.closest_point_on_mesh(self.source_geo, target_pos)[0]
                cmds.move(pos[0], pos[1], pos[2], [target_vtx], ws=True)
        else:
            self.geo_check(selection[0])
            vtxs = cmds.ls('{}.vtx[*]'.format(selection[0]), fl=True)
            for target_vtx in vtxs:
                target_pos = cmds.xform(target_vtx, t=True, ws=True, q=True)
                pos = self.closest_point_on_mesh(self.source_geo, target_pos)[0]
                cmds.move(pos[0], pos[1], pos[2], [target_vtx], ws=True)
