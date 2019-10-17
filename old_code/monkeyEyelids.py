import pymel.core as pm
import maya.cmds as cmds
import maya.api.OpenMaya as om


class eyeLidSetup:

    def __init__(self, rig_name):
        self.locList = []
        self.locNum = 0

        self.jntList = []

        self.mainCtrlJnt = ''
        self.mainCtrlJntSrt = ''

        self.midACtrlJnt = ''
        self.midACtrlJntSrt = ''

        self.midBCtrlJntSrt = ''
        self.midBCtrlJnt = ''

        self.begCtrlJntSrt = ''
        self.begCtrlJnt = ''

        self.endCtrlJntSrt = ''
        self.endCtrlJnt = ''

        self.rig_name = rig_name

    def create_starter_locs(self):
        self.starter_loc_list = []
        list = cmds.ls(sl=True, fl=True)
        for each in list:
            pos = cmds.xform(each, t=True, ws=True, query=True)
            loc = cmds.spaceLocator()[0]
            cmds.xform(loc, t=(pos[0], pos[1], pos[2]))
            self.starter_loc_list.append(loc)

    def create_curve(self):
        vtx_list = cmds.ls(sl=True)

        # create curve with a cv at each vertex
        pos_list = []
        self.crv_list = []
        for each in vtx_list:
            v = cmds.xform(each, t=1, ws=1, query=1)
            pos_list.append(v)
        end_curve = len(pos_list) - 1

        crv1 = cmds.curve(d=1,
                          name=self.rig_name + '_EL_HD_CRV',
                          p=[(pos_list[0]), (pos_list[1])])
        for x in range(2, end_curve + 1):
            pos = pos_list[x]
            print pos
            cmds.curve(crv1, os=True, a=True, p=(pos[0], pos[1], pos[2]))
        self.crv_list.append(crv1)
        cmds.select(clear=True)

        # define end points and mid points for next curve
        self.second_loc_list = []
        num_locs = len(vtx_list)

        self.beg_loc = vtx_list[0]
        self.end_loc = vtx_list[num_locs - 1]
        self.mid_loc = vtx_list[num_locs/2]
        self.beg_mid_loc = vtx_list[num_locs/4]
        self.end_mid_loc = vtx_list[(num_locs * 3)/4]

        self.second_loc_list.append(self.beg_loc)
        self.second_loc_list.append(self.beg_mid_loc)
        self.second_loc_list.append(self.mid_loc)
        self.second_loc_list.append(self.end_mid_loc)
        self.second_loc_list.append(self.end_loc)

        for each in self.second_loc_list:
            self.starter_loc_list.remove(each)

        for each in self.starter_loc_list:
            cmds.delete(each)

        cmds.select(clear=True)

        # create curve and attach cvs to second list of locators
        pos_list = []
        for each in self.second_loc_list:
            v = cmds.xform(each, t=1, ws=1, query=1)
            pos_list.append(v)
        end_curve = len(self.second_loc_list) - 1

        crv2 = cmds.curve(d=1,
                          name=self.rig_name + '_EL_LD_CRV',
                          p=[(pos_list[0]), (pos_list[1])])
        for x in range(2, end_curve + 1):
            pos = pos_list[x]
            print pos
            cmds.curve(crv2, os=True, a=True, p=(pos[0], pos[1], pos[2]))
        cmds.rebuildCurve(crv2, ch=1, rpo=1, end=1, kr=0, kt=1, s=5, d=2)

        # connect cvs of rebuilt curve to locators
        shape = cmds.listRelatives(crv2, s=True)[0]
        cmds.connectAttr('{}.translate'.format(self.beg_loc), '{}.controlPoints[0]'.format(shape))
        cmds.connectAttr('{}.translate'.format(self.beg_loc), '{}.controlPoints[1]'.format(shape))

        cmds.connectAttr('{}.translate'.format(self.beg_mid_loc), '{}.controlPoints[2]'.format(shape))

        cmds.connectAttr('{}.translate'.format(self.mid_loc), '{}.controlPoints[3]'.format(shape))

        cmds.connectAttr('{}.translate'.format(self.end_mid_loc), '{}.controlPoints[4]'.format(shape))

        cmds.connectAttr('{}.translate'.format(self.end_loc), '{}.controlPoints[5]'.format(shape))
        cmds.connectAttr('{}.translate'.format(self.end_loc), '{}.controlPoints[6]'.format(shape))

        self.crv_list.append(crv2)
        cmds.select(clear=True)

        self.driver_jnt_list = []
        # create joints that will control the curves
        for x in range(0, 5):
            if x == 0:
                jnt_part = 'beg'
            if x == 1:
                jnt_part = 'beg_mid'
            if x == 2:
                jnt_part = 'mid'
            if x == 3:
                jnt_part = 'end_mid'
            if x == 4:
                jnt_part = 'end'
            jnt = cmds.joint(name='{}_EL_{}_driver_jnt'.format(self.rig_name, jnt_part))
            self.driver_jnt_list.append(jnt)
            srt = cmds.createNode('transform', name=jnt + '_srt')
            cmds.parent(jnt, srt)

            pos = cmds.xform(self.second_loc_list[x], t=1, ws=1, query=1)
            cmds.xform(srt, t=(pos[0], pos[1], pos[2]), ws=1)
            cmds.select(clear=True)

    # create locators for each cv
    def create_bones(self):
        self.locNum = 0
        crv = self.crv_list[0]
        degs = pm.getAttr(crv + '.degree')
        spans = pm.getAttr(crv + '.spans')
        cvs = degs+spans
        self.locList = []

        for x in range(0, cvs):
            cmds.select(clear=True)
            cv = crv + '.cv[' + str(x) + ']'
            bone = cmds.joint(name='{}_EL_{}_BONE'.format(self.rig_name, self.locNum))
            srt = cmds.createNode('transform', name='{}_srt'.format(bone))
            cmds.parent(bone, srt)

            pos = cmds.xform(cv, t=True, ws=True, query=True)
            loc = cmds.spaceLocator(name=self.rig_name + str(self.locNum) + '_LOC')[0]
            self.locNum += 1
            self.locList.append(loc)

            nPCI = cmds.createNode('nearestPointOnCurve', name=str(loc) + '_nPCI')
            PCI = cmds.createNode('pointOnCurveInfo', name=str(loc) + '_PCI')

            cmds.setAttr(nPCI + '.inPositionX', pos[0])
            cmds.setAttr(nPCI + '.inPositionY', pos[1])
            cmds.setAttr(nPCI + '.inPositionZ', pos[2])

            cmds.connectAttr(crv + '.worldSpace[0]', nPCI + '.inputCurve')
            cmds.connectAttr(crv + '.worldSpace[0]', PCI + '.inputCurve')

            cmds.connectAttr(nPCI + '.parameter', PCI + '.parameter')
            cmds.connectAttr(PCI + '.position', loc + '.translate')

            par = cmds.getAttr(PCI + '.parameter')
            cmds.delete(nPCI)
            cmds.setAttr(PCI + '.parameter', par)

            cmds.parent(srt, loc)
            cmds.setAttr(srt + '.translate', 0, 0, 0)
            cmds.setAttr(bone + '.translate', 0, 0, 0)

    def get_normal_of_plane(self, first_loc, second_loc, third_loc):
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

    def basic_ctrl(self, ctrl_type):
        ctrl = cmds.circle(name='{}_EL_{}_CTRL'.format(self.rig_name, ctrl_type))[0]
        cmds.delete(ch=True)
        srt = cmds.createNode('transform', name=ctrl + '_srt')
        cmds.parent(ctrl, srt)

        return (ctrl, srt)

    def create_matrix(self, x_vec, y_vec, z_vec, pos):
        matrix = (x_vec[0], x_vec[1], x_vec[2], 0,
                  y_vec[0], y_vec[1], y_vec[2], 0,
                  z_vec[0], z_vec[1], z_vec[2], 0,
                  pos[0], pos[1], pos[2], 0)
        return matrix

    def finish_rig(self):
        cmds.select(clear=True)
        for each in self.driver_jnt_list:
            cmds.select(each, add=True)
        cmds.skinCluster(self.driver_jnt_list, self.crv_list[1])
        cmds.wire(self.crv_list[0], li=1.000000, w=self.crv_list[1], dds=(0, 10.0000))
        self.create_bones()

        ctrl_list = []
        srt_list = []

        # create controls
        beg_ctrl, beg_ctrl_srt = self.basic_ctrl('beg')
        ctrl_list.append(beg_ctrl)
        srt_list.append(beg_ctrl_srt)

        beg_mid_ctrl, beg_mid_ctrl_srt = self.basic_ctrl('beg_mid')
        ctrl_list.append(beg_mid_ctrl)
        srt_list.append(beg_mid_ctrl_srt)

        mid_ctrl, mid_ctrl_srt = self.basic_ctrl('mid')
        ctrl_list.append(mid_ctrl)
        srt_list.append(mid_ctrl_srt)

        end_mid_ctrl, end_mid_ctrl_srt = self.basic_ctrl('end_mid')
        ctrl_list.append(end_mid_ctrl)
        srt_list.append(end_mid_ctrl_srt)

        end_ctrl, end_ctrl_srt = self.basic_ctrl('end')
        ctrl_list.append(end_ctrl)
        srt_list.append(end_ctrl_srt)

        # create vectors for the rotation of each control in space
        normal_vector1 = self.get_normal_of_plane(self.second_loc_list[0], self.second_loc_list[2], self.second_loc_list[4])
        y_vector = om.MVector(0, 1, 0)
        x_vector = (y_vector ^ normal_vector1).normal()
        # create a y vector that is orthogonal to both the x and z vectors
        # instead of the world space y vector you used to create the x
        y_vector = (x_vector ^ normal_vector1).normal()

        # create offset for controls off of their original position
        normal_vector2 = normal_vector1 * 2

        # position controls
        for x in range(0, 5):
            pos = cmds.xform(self.second_loc_list[x], t=True, ws=True, query=True)
            pos = (pos[0] - normal_vector2[0],
                   pos[1] - normal_vector2[1],
                   pos[2] - normal_vector2[2])
            matrix = self.create_matrix((x_vector * -1), (y_vector * -1), (normal_vector1 * -1), pos)
            print matrix
            cmds.xform(srt_list[x], m=matrix, ws=True)
            cmds.pointConstraint(ctrl_list[x], self.driver_jnt_list[x], mo=True)

        # connect mid controls to the positions of the main controls
        cmds.select(clear=True)
        cmds.select(ctrl_list[0])
        cmds.select(ctrl_list[2], add=True)
        cmds.select(srt_list[1], add=True)
        cmds.pointConstraint(mo=True)

        cmds.select(clear=True)
        cmds.select(ctrl_list[2])
        cmds.select(ctrl_list[4], add=True)
        cmds.select(srt_list[3], add=True)
        cmds.pointConstraint(mo=True)

        # delete leftover locators
        for each in self.second_loc_list:
            cmds.delete(each)

