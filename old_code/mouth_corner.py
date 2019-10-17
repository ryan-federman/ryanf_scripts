import maya.cmds as cmds
import maya.api.OpenMaya as om


class mouthCornerSetup:

    def __init__(self, side):
        self.side = side
        self.parts = []
        self.controls = []
        self.bones = []
        self.jaw = []

    def build(self):
        self.create_ctrls()
        self.create_curve('top', self.top_beg_ctrl, self.top_end_ctrl)
        self.create_curve('bot', self.bot_beg_ctrl, self.bot_end_ctrl)

        parts_grp = cmds.createNode('transform', name=self.side + '_lips_parts_GRP')
        bones_grp = cmds.createNode('transform', name=self.side + '_lips_bones_GRP')
        controls_grp = cmds.createNode('transform', name=self.side + '_lips_ctrls_GRP')

        for each in self.parts:
            cmds.parent(each, parts_grp)
        for each in self.controls:
            cmds.parent(each, controls_grp)
        for each in self.bones:
            cmds.parent(each, bones_grp)
        for each in self.jaw:
            cmds.parentConstraint('jaw', each, mo=True)

    def create_ctrls(self):
        self.init_loc_list = cmds.ls(sl=True)
        if len(self.init_loc_list) != 4:
            cmds.error('Select 4 locators')

        self.top_beg_ctrl = self.basic_ctrl('top_beg')
        self.bot_beg_ctrl = self.basic_ctrl('bot_beg', scale=.8)
        self.top_end_ctrl = self.basic_ctrl('top_end')
        self.bot_end_ctrl = self.basic_ctrl('bot_end', scale=.8)
        main_lip_ctrl = self.basic_ctrl('main', scale=1.5, rot=(0, 90, 0))
        bot_null = cmds.createNode('transform', name='{}_lip_bot_null'.format(self.side))

        PMA = cmds.createNode('plusMinusAverage', name=self.side + 'bot_end_CTRL_translate_PMA')

        self.controls.append(self.top_beg_ctrl[1])
        self.controls.append(self.bot_beg_ctrl[1])
        self.controls.append(main_lip_ctrl[1])
        self.jaw.append(bot_null)
        self.jaw.append(self.bot_beg_ctrl[1])

        pos_beg = cmds.xform(self.init_loc_list[0], t=True, ws=True, q=True)
        pos_end = cmds.xform(self.init_loc_list[-1], t=True, ws=True, q=True)

        cmds.xform(self.top_beg_ctrl[1], t=pos_beg, ws=True)
        cmds.xform(self.bot_beg_ctrl[1], t=pos_beg, ws=True)
        cmds.xform(self.top_end_ctrl[1], t=pos_end, ws=True)
        cmds.xform(bot_null, t=pos_end, ws=True)
        cmds.xform(main_lip_ctrl[1], t=pos_end, ws=True)

        cmds.connectAttr(bot_null + '.rotate', self.bot_end_ctrl[1] + '.rotate')
        cmds.connectAttr(bot_null + '.translate', PMA + '.input3D[0]')
        cmds.connectAttr(main_lip_ctrl[0] + '.translate', PMA + '.input3D[1]')
        cmds.connectAttr(PMA + '.output3D', self.bot_end_ctrl[1] + '.translate')

        cmds.parent(self.top_end_ctrl[1], main_lip_ctrl[0])
        cmds.parent(self.bot_end_ctrl[1], main_lip_ctrl[0])
        cmds.parent(bot_null, main_lip_ctrl[0])

    def basic_ctrl(self, topBot, scale=1.0, rot=(0, 0, 0)):
        ctrl = cmds.circle(name='{}_{}_lip_CTRL'.format(self.side, topBot))[0]
        cmds.setAttr(ctrl + '.scale', scale, scale, scale)
        cmds.setAttr(ctrl + '.rotate', rot[0], rot[1], rot[2])
        cmds.makeIdentity(ctrl, apply=True)

        cmds.delete(ch=True)
        srt = cmds.createNode('transform', name=ctrl + '_srt')
        cmds.parent(ctrl, srt)

        return (ctrl, srt)

    def create_bones(self, crv, topBot, amt_bones):
        par_add = 1.0/amt_bones

        srt_list = []
        for x in range(0, amt_bones + 1):
            par = par_add * x
            # get names of the bones
            if x == 0:
                part = 'beg'
            elif x > 0 and x < 3:
                part = 'mid' + str(x)
            elif x == 3:
                part = 'end'

            # if side == 'L':
            #     up_vec_cp = self.up_vec_CP_list[0]
            # elif side == 'R':
            #     up_vec_cp = self.up_vec_CP_list[1]
            # else:
            #     up_vec_cp = self.up_vec_CP_list[2]

            cmds.select(clear=True)
            bone = cmds.joint(name='{}_{}_{}_lip_BONE'.format(self.side, topBot, part))
            srt = cmds.createNode('transform', name='{}_srt'.format(bone))
            srt_list.append(srt)
            cmds.parent(bone, srt)

            PCI = cmds.createNode('pointOnCurveInfo', name=str(bone) + '_PCI')
            z_cross_product = cmds.createNode('vectorProduct', name=bone + '_z_CP')
            y_cross_product = cmds.createNode('vectorProduct', name=bone + '_y_CP')
            z_cp_reverse = cmds.createNode('multiplyDivide', name=bone + '_z_CP_MULT')
            fbf_matrix = cmds.createNode('fourByFourMatrix', name=bone + '_fbfMtx')
            dec_matrix = cmds.createNode('decomposeMatrix', name=bone + '_DM')

            cmds.connectAttr(crv + '.worldSpace[0]', PCI + '.inputCurve')

            cmds.setAttr(PCI + '.parameter', par)

            cmds.setAttr(z_cross_product + '.operation', 2)
            cmds.setAttr(z_cross_product + '.normalizeOutput', 1)
            # cmds.connectAttr(up_vec_cp + '.output', z_cross_product + '.input2')
            cmds.setAttr(z_cross_product + '.input2', 0, 1, 0)
            cmds.connectAttr(PCI + '.normalizedTangent', z_cross_product + '.input1')

            cmds.setAttr(z_cp_reverse + '.input2', -1, -1, -1)
            cmds.connectAttr(z_cross_product + '.output', z_cp_reverse + '.input1')

            cmds.setAttr(y_cross_product + '.operation', 2)
            cmds.setAttr(y_cross_product + '.normalizeOutput', 1)
            cmds.connectAttr(PCI + '.normalizedTangent', y_cross_product + '.input1')
            cmds.connectAttr(z_cp_reverse + '.output', y_cross_product + '.input2')

            cmds.connectAttr(PCI + '.normalizedTangentX', fbf_matrix + '.in00')
            cmds.connectAttr(PCI + '.normalizedTangentY', fbf_matrix + '.in01')
            cmds.connectAttr(PCI + '.normalizedTangentZ', fbf_matrix + '.in02')

            cmds.connectAttr(y_cross_product + '.outputX', fbf_matrix + '.in10')
            cmds.connectAttr(y_cross_product + '.outputY', fbf_matrix + '.in11')
            cmds.connectAttr(y_cross_product + '.outputZ', fbf_matrix + '.in12')

            cmds.connectAttr(z_cp_reverse + '.outputX', fbf_matrix + '.in20')
            cmds.connectAttr(z_cp_reverse + '.outputY', fbf_matrix + '.in21')
            cmds.connectAttr(z_cp_reverse + '.outputZ', fbf_matrix + '.in22')

            cmds.connectAttr(PCI + '.positionX', fbf_matrix + '.in30')
            cmds.connectAttr(PCI + '.positionY', fbf_matrix + '.in31')
            cmds.connectAttr(PCI + '.positionZ', fbf_matrix + '.in32')

            cmds.connectAttr(fbf_matrix + '.output', dec_matrix + '.inputMatrix')

            cmds.connectAttr(dec_matrix + '.outputTranslate', srt + '.translate')
            cmds.connectAttr(dec_matrix + '.outputRotate', srt + '.rotate')

        for each in srt_list:
            self.bones.append(each)

        return srt_list

    def create_curve(self, topBot, beg_ctrl, end_ctrl):

        # create curve with a cv at each vertex
        pos_list = []
        for each in self.init_loc_list:
            v = cmds.xform(each, t=1, ws=1, query=1)
            pos_list.append(v)

        crv1 = cmds.curve(d=3,
                          name='{}_{}_lip_CRV'.format(self.side, topBot),
                          p=[(pos_list[0]), (pos_list[1]), (pos_list[2]),  (pos_list[3])])
        self.parts.append(crv1)

        # create curve and attach cvs to second list of locators
        pos_list = []
        for each in self.init_loc_list:
            v = cmds.xform(each, t=1, ws=1, query=1)
            pos_list.append(v)

        loc_list = []
        # create locators to attach cvs to
        for each in self.init_loc_list:
            loc = cmds.spaceLocator(name='{}_{}_{}'.format(self.side, topBot, each))
            pos = cmds.xform(each, t=1, ws=1, q=1)
            cmds.xform(loc, t=pos, ws=1)
            loc_list.append(loc[0])

            self.parts.append(loc[0])

        # connect cvs of curve to locators
        shape = cmds.listRelatives(crv1, s=True)[0]

        cmds.connectAttr('{}.translate'.format(loc_list[0]), '{}.controlPoints[0]'.format(shape))
        cmds.connectAttr('{}.translate'.format(loc_list[1]), '{}.controlPoints[1]'.format(shape))
        cmds.connectAttr('{}.translate'.format(loc_list[2]), '{}.controlPoints[2]'.format(shape))
        cmds.connectAttr('{}.translate'.format(loc_list[3]), '{}.controlPoints[3]'.format(shape))

        cmds.parentConstraint(beg_ctrl, loc_list[0])
        cmds.parentConstraint(end_ctrl, loc_list[3])

        if topBot == 'bot':
            self.jaw.append(loc_list[1])
            self.jaw.append(loc_list[2])
        self.create_bones(crv1, topBot, 3)
        return crv1
