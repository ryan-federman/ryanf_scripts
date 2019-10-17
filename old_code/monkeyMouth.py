import pymel.core as pm
import maya.cmds as cmds
import maya.api.OpenMaya as om
import math
import copy


class MouthSetup:

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

    def starter_loc_positions(self, num):
        degrees_add = 90.0/float(num + 1)
        pos_list = []
        L_locs = []
        R_locs = []

        degree = 0
        for y in range(0, num):
            degree = degree + degrees_add
            rad = math.radians(degree)
            z = 4 * math.sin(rad)
            x = 4 * math.cos(rad)
            pos = (x, 0, z)
            L_locs.append(pos)
        degree = 90
        for y in range(0, num):
            degree = degree + degrees_add
            rad = math.radians(degree)
            z = 4 * math.sin(rad)
            x = 4 * math.cos(rad)
            pos = (x, 0, z)
            R_locs.append(pos)

        pos_list.append((4, 0, 0))
        for each in L_locs:
            pos_list.append(each)
        pos_list.append((0, 0, 4))
        for each in R_locs:
            pos_list.append(each)
        pos_list.append((-4, 0, 0))

        return pos_list

    def create_starter_locs(self, num_mid_ctrls=1):
        self.loc_list = []
        pos_list = self.starter_loc_positions(num_mid_ctrls)

        mid_of_list = (len(pos_list)/2)
        for x in range(0, len(pos_list)):
            if x == mid_of_list:
                side = 'C'
                part = 'main'
            elif x < mid_of_list:
                side = 'L'
                part = 'mid' + str(x)
            elif x > mid_of_list:
                side = 'R'
                y = x - mid_of_list
                part_num = mid_of_list - y
                part = 'mid' + str(part_num)
            if x == 0 or x == (len(pos_list)-1):
                part = 'main'

            loc = cmds.spaceLocator(name='{}_{}_{}_LOC'.format(side, part, self.rig_name))
            cmds.xform(loc, t=pos_list[x], ws=True)
            self.loc_list.append(loc[0])

    def mirror_locs(self):
        mirror_loc_list = copy.copy(self.loc_list)

        for each in mirror_loc_list:
            side = (each.split('_'))[0]
            if side == 'L':
                mirrored_loc_list = each.split('_')
                mirrored_loc = 'R'
                for x in range(1, len(mirrored_loc_list)):
                    mirrored_loc += '_' + mirrored_loc_list[x]
                pos = cmds.xform(each, t=1, ws=1, q=1)
                new_pos = (pos[0] * -1, pos[1], pos[2])
                cmds.xform(mirrored_loc, t=new_pos, ws=1)

    def create_curve(self, locs, name, cvs=2, rebuild=True, degree=3):
        """create a curve

        Args:
            locs (list): List of locators for cv positions
            name (str): name of the function of the curve
            cvs (int): amount of cvs created if curve is rebuilt
            degree (int): degree at which the original curve is built
            rebuild (bool): whether the curve is rebuilt or not

        Return:
            str: Returns the name of the curve
        """
        pos_list = []
        for each in locs:
            pos = cmds.xform(each, t=True, ws=True, q=True)
            pos_list.append(pos)
        end_curve = len(locs)

        crv = cmds.curve(d=degree,
                         name='{}_{}_CRV'.format(self.rig_name, name),
                         p=[(pos_list[0]), (pos_list[1])])
        for x in range(2, end_curve):
            pos = pos_list[x]
            cmds.curve(crv, os=True, a=True, p=(pos[0], pos[1], pos[2]))
        if rebuild is True:
            cmds.rebuildCurve(crv, ch=1, rpo=1, end=1, kr=0, kt=1, s=cvs, d=3)
        return crv

    def create_bones(self, crv, amt_bones):
        par_add = 1.0/amt_bones
        mid_point = amt_bones/2

        srt_list = []
        for x in range(0, amt_bones + 1):
            par = par_add * x
            # get names of the bones
            if x == mid_point:
                side = 'C'
                part = 'main'
            elif x < mid_point:
                side = 'L'
                part = 'mid' + str(x)
            elif x > mid_point:
                side = 'R'
                y = x - mid_point
                part_num = mid_point - y
                part = 'mid' + str(part_num)
            if x == 0 or x == (amt_bones-1):
                part = 'main'

            if side == 'L':
                up_vec_cp = self.up_vec_CP_list[0]
            elif side == 'R':
                up_vec_cp = self.up_vec_CP_list[1]
            else:
                up_vec_cp = self.up_vec_CP_list[2]

            cmds.select(clear=True)
            bone = cmds.joint(name='{}_{}_{}_BONE'.format(side, part, self.rig_name))
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
            cmds.connectAttr(up_vec_cp + '.output', z_cross_product + '.input2')
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

        return srt_list

    def create_sub_ctrls(self, crv, sub_ctrl_locs):
        sub_ctrls = []

        for x in range(0, len(sub_ctrl_locs)):
            cmds.select(clear=True)
            locator = sub_ctrl_locs[x]
            side = locator.split('_')[0]
            ctrl_type = locator.split('_')[1]

            ctrl, srt = self.basic_ctrl(side + '_sub', ctrl_type, scale=.5)
            self.controls.append(srt)
            sub_ctrls.append(ctrl)
            zero = cmds.createNode('transform', name='{}_ZERO'.format(ctrl))
            cmds.parent(ctrl, zero)

            if side == 'L':
                up_vec_cp = self.up_vec_CP_list[0]
            elif side == 'R':
                up_vec_cp = self.up_vec_CP_list[1]
            else:
                up_vec_cp = self.up_vec_CP_list[2]

            pos = cmds.xform(locator, t=True, ws=True, query=True)

            nPCI = cmds.createNode('nearestPointOnCurve', name=ctrl + '_nPCI')
            PCI = cmds.createNode('pointOnCurveInfo', name=ctrl + '_PCI')
            z_cross_product = cmds.createNode('vectorProduct', name=ctrl + '_z_CP')
            y_cross_product = cmds.createNode('vectorProduct', name=ctrl + '_y_CP')
            z_cp_reverse = cmds.createNode('multiplyDivide', name=ctrl + '_z_CP_MULT')
            fbf_matrix = cmds.createNode('fourByFourMatrix', name=ctrl + '_fbfMtx')
            dec_matrix = cmds.createNode('decomposeMatrix', name=ctrl + '_DM')

            cmds.setAttr(nPCI + '.inPositionX', pos[0])
            cmds.setAttr(nPCI + '.inPositionY', pos[1])
            cmds.setAttr(nPCI + '.inPositionZ', pos[2])

            cmds.connectAttr(crv + '.worldSpace[0]', nPCI + '.inputCurve')
            cmds.connectAttr(crv + '.worldSpace[0]', PCI + '.inputCurve')

            cmds.connectAttr(nPCI + '.parameter', PCI + '.parameter')

            par = cmds.getAttr(PCI + '.parameter')
            cmds.delete(nPCI)
            cmds.setAttr(PCI + '.parameter', par)

            cmds.setAttr(z_cross_product + '.operation', 2)
            cmds.setAttr(z_cross_product + '.normalizeOutput', 1)
            cmds.connectAttr(up_vec_cp + '.output', z_cross_product + '.input2')
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

            cmds.parent(zero, srt)
            cmds.setAttr(zero + '.translate', 0, 0, 0)
            cmds.setAttr(zero + '.rotate', 0, 0, 0)
            cmds.setAttr(ctrl + '.translate', 0, 0, 0)

        return sub_ctrls

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

    def basic_ctrl(self, side, ctrl_type, scale=1):
        ctrl = cmds.circle(name='{}_{}_{}_CTRL'.format(side, ctrl_type, self.rig_name))[0]
        cmds.delete(ch=True)
        srt = cmds.createNode('transform', name=ctrl + '_srt')
        cmds.parent(ctrl, srt)

        cmds.setAttr(ctrl + '.scale', scale, scale, scale)
        cmds.makeIdentity(ctrl, apply=True)
        return (ctrl, srt)

    def create_matrix(self, x_vec, y_vec, z_vec, pos):
        matrix = (x_vec[0], x_vec[1], x_vec[2], 0,
                  y_vec[0], y_vec[1], y_vec[2], 0,
                  z_vec[0], z_vec[1], z_vec[2], 0,
                  pos[0], pos[1], pos[2], 0)
        return matrix

    def build(self, amt_of_bones=3):
        self.controls = []
        self.parts = []
        self.bones = []

        # amount of total bones in the rig
        bone_amount = (amt_of_bones * 2) + 2

        # create list of locators for joints on the first driver curve
        beg_loc = self.loc_list[0]
        mid_loc = self.loc_list[(len(self.loc_list)/2)]
        end_loc = self.loc_list[len(self.loc_list) - 1]
        main_loc_list = [beg_loc, mid_loc, end_loc]

        # create curves to drive the joints and controls
        LD1_crv = self.create_curve(self.loc_list, 'LD1', degree=1, rebuild=False)
        LD2_crv = self.create_curve(self.loc_list, 'LD2', rebuild=True, cvs=len(self.loc_list)-1)
        LD3_crv = self.create_curve(self.loc_list, 'LD3', rebuild=True, cvs=len(self.loc_list)-1)
        HD_crv = self.create_curve(self.loc_list, 'HD', cvs=bone_amount)

        cmds.wire(LD2_crv, li=1.000000, w=LD1_crv, dds=(0, 10.0000))
        cmds.wire(HD_crv, li=1.000000, w=LD3_crv, dds=(0, 10.0000))

        wire1 = LD1_crv + 'BaseWire'
        wire2 = LD3_crv + 'BaseWire'

        self.parts.append(LD1_crv)
        self.parts.append(LD2_crv)
        self.parts.append(LD3_crv)
        self.parts.append(HD_crv)
        self.parts.append(wire1)
        self.parts.append(wire2)

        # move edit points of curves to better fit the intended curve
        for x in range(0, len(self.loc_list)):
            pos = cmds.xform(self.loc_list[x], t=1, ws=1, q=1)
            cmds.xform('{}.ep[{}]'.format(LD2_crv, x), t=pos, ws=1)
            cmds.xform('{}.ep[{}]'.format(LD3_crv, x), t=pos, ws=1)

        # create list of locators for joints that aren't on the first curve
        sub_loc_list = copy.copy(self.loc_list)
        for each in main_loc_list:
            sub_loc_list.remove(each)

        # create joints that will drive the curves
        main_driver_jnt_list = []
        for each in main_loc_list:
            name = (each.split('LOC')[0]) + 'crvBone'
            srt = cmds.createNode('transform', name=name + '_srt')
            jnt = cmds.joint(name=name)
            pos = cmds.xform(each, t=1, ws=1, q=1)
            cmds.xform(srt, t=pos, ws=1)
            main_driver_jnt_list.append(jnt)

            self.parts.append(srt)
        cmds.skinCluster(main_driver_jnt_list, LD1_crv)

        sub_driver_jnt_list = []
        for each in self.loc_list:
            name = (each.split('LOC')[0]) + '_sub_crvBone'
            srt = cmds.createNode('transform', name=name + '_srt')
            jnt = cmds.joint(name=name)
            pos = cmds.xform(each, t=1, ws=1, q=1)
            cmds.xform(srt, t=pos, ws=1)
            sub_driver_jnt_list.append(jnt)

            self.parts.append(srt)
        cmds.skinCluster(sub_driver_jnt_list, LD3_crv)

        # create main controls
        main_ctrl_list = []
        L_end_ctrl, L_end_ctrl_srt = self.basic_ctrl('L', 'end')
        R_end_ctrl, R_end_ctrl_srt = self.basic_ctrl('R', 'end')
        C_main_ctrl, C_main_ctrl_srt = self.basic_ctrl('C', 'main')
        self.controls.append(L_end_ctrl_srt)
        self.controls.append(R_end_ctrl_srt)
        self.controls.append(C_main_ctrl_srt)
        main_ctrl_list.append(L_end_ctrl)
        main_ctrl_list.append(C_main_ctrl)
        main_ctrl_list.append(R_end_ctrl)

        L_vec_DM = cmds.createNode('decomposeMatrix',
                                   name='L_{}_vec_DM'.format(self.rig_name))
        C_vec_DM = cmds.createNode('decomposeMatrix',
                                   name='C_{}_vec_DM'.format(self.rig_name))
        R_vec_DM = cmds.createNode('decomposeMatrix',
                                   name='R_{}_vec_DM'.format(self.rig_name))

        cmds.connectAttr(R_end_ctrl + '.worldMatrix[0]', R_vec_DM + '.inputMatrix')
        cmds.connectAttr(C_main_ctrl + '.worldMatrix[0]', C_vec_DM + '.inputMatrix')
        cmds.connectAttr(L_end_ctrl + '.worldMatrix[0]', L_vec_DM + '.inputMatrix')

        # create locator that creates a separate plane
        # for each half of the rig's Y vector
        mid_vec_loc_DM = cmds.createNode('decomposeMatrix',
                                     name='{}_mid_vec_loc_DM'.format(self.rig_name))
        mid_vec_loc = cmds.spaceLocator(name=self.rig_name + '_mid_vec_LOC')[0]
        self.parts.append(mid_vec_loc)
        cmds.connectAttr(mid_vec_loc + '.worldMatrix[0]', mid_vec_loc_DM + '.inputMatrix')

        self.up_vec_CP_list = []
        # create an up vector based on the plane made by the main controls
        for side in ['L', 'R', 'C']:
            if side == 'L':
                root_vec_DM = L_vec_DM
                mid_vec_DM = mid_vec_loc_DM
                end_vec_DM = C_vec_DM
            elif side == 'R':
                root_vec_DM = R_vec_DM
                mid_vec_DM = mid_vec_loc_DM
                end_vec_DM = C_vec_DM
            else:
                root_vec_DM = R_vec_DM
                mid_vec_DM = C_vec_DM
                end_vec_DM = L_vec_DM

            upper_vec_PMA = cmds.createNode('plusMinusAverage',
                                            name='{}_{}_upper_vec_PMA'.format(side, self.rig_name))
            line_vec_PMA = cmds.createNode('plusMinusAverage',
                                           name='{}_{}_line_vec_PMA'.format(side, self.rig_name))
            up_vec_CP = cmds.createNode('vectorProduct',
                                             name='{}_{}_up_vec_PMA'.format(side, self.rig_name))
            self.up_vec_CP_list.append(up_vec_CP)

            cmds.setAttr(upper_vec_PMA + '.operation', 2)
            cmds.connectAttr(mid_vec_DM + '.outputTranslate', upper_vec_PMA + '.input3D[0]')
            cmds.connectAttr(root_vec_DM + '.outputTranslate', upper_vec_PMA + '.input3D[1]')

            cmds.setAttr(line_vec_PMA + '.operation', 2)
            cmds.connectAttr(end_vec_DM + '.outputTranslate', line_vec_PMA + '.input3D[0]')
            cmds.connectAttr(mid_vec_DM + '.outputTranslate', line_vec_PMA + '.input3D[1]')

            cmds.setAttr(up_vec_CP + '.operation', 2)
            cmds.setAttr(up_vec_CP + '.normalizeOutput', 1)
            cmds.connectAttr(upper_vec_PMA + '.output3D', up_vec_CP + '.input1')
            cmds.connectAttr(line_vec_PMA + '.output3D',  up_vec_CP + '.input2')

        L_loc_vector = om.MVector(cmds.xform(main_loc_list[0], t=1, ws=1, q=1))
        C_loc_vector = om.MVector(cmds.xform(main_loc_list[1], t=1, ws=1, q=1))
        R_loc_vector = om.MVector(cmds.xform(main_loc_list[2], t=1, ws=1, q=1))

        last_mid_loc = self.loc_list[len(self.loc_list)-2]
        L_loc2_vector = om.MVector(cmds.xform(self.loc_list[1], t=1, ws=1, q=1))
        R_loc2_vector = om.MVector(cmds.xform(last_mid_loc, t=1, ws=1, q=1))

        # up vector of the plane between the controls
        up_vector = self.get_normal_of_plane(main_loc_list[0], main_loc_list[1], main_loc_list[2]) * -1

        # create aim vectors for controls
        l_aim_vector = (L_loc2_vector - L_loc_vector).normal()
        r_aim_vector = (R_loc2_vector - R_loc_vector).normal()
        c_aim_vector = (L_loc_vector - R_loc_vector).normal()

        # get z vectors for controls
        L_z_vector = l_aim_vector ^ up_vector
        R_z_vector = r_aim_vector ^ up_vector
        C_z_vector = c_aim_vector ^ up_vector

        # create matrices to position and rotate controls
        L_main_ctrl_mtx = self.create_matrix(l_aim_vector, up_vector, L_z_vector, L_loc_vector)
        R_main_ctrl_mtx = self.create_matrix(r_aim_vector, up_vector, R_z_vector, R_loc_vector)
        C_main_ctrl_mtx = self.create_matrix(c_aim_vector, up_vector, C_z_vector, C_loc_vector)

        # position and rotate main controls
        cmds.xform(L_end_ctrl_srt, matrix=L_main_ctrl_mtx)
        cmds.xform(R_end_ctrl_srt, matrix=R_main_ctrl_mtx)
        cmds.xform(C_main_ctrl_srt, matrix=C_main_ctrl_mtx)

        # position mid locator for each side's up vector plane
        L_vec = om.MVector(cmds.xform(L_end_ctrl, t=1, ws=1, q=1))
        R_vec = om.MVector(cmds.xform(R_end_ctrl, t=1, ws=1, q=1))
        loc_pos = (L_vec + R_vec)/2
        cmds.xform(mid_vec_loc, t=loc_pos, ws=1)

        # create sub controls
        sub_ctrl_list = self.create_sub_ctrls(LD2_crv, self.loc_list)

        # attach control joints to controls
        for x in range(0, 3):
            cmds.parentConstraint(main_ctrl_list[x], main_driver_jnt_list[x], mo=True)
        for x in range(0, len(sub_ctrl_list)):
            cmds.parentConstraint(sub_ctrl_list[x], sub_driver_jnt_list[x], mo=True)

        # create bones
        bones = self.create_bones(HD_crv, bone_amount)
        for each in bones:
            self.bones.append(each)

        # create bones for ends that don't rotate with curves
        L_end_bone = bones[0]
        R_end_bone = bones[len(bones)-1]

        L_end_bone_name = L_end_bone.split('BONE')[0] + 'noRot_BONE'
        R_end_bone_name = R_end_bone.split('BONE')[0] + 'noRot_BONE'

        new_L_end_bone = cmds.joint(name=L_end_bone_name)
        new_R_end_bone = cmds.joint(name=R_end_bone_name)
        new_L_end_bone_srt = cmds.createNode('transform', name=L_end_bone_name + 'srt')
        new_R_end_bone_srt = cmds.createNode('transform', name=R_end_bone_name + 'srt')

        self.bones.append(new_L_end_bone_srt)
        self.bones.append(new_R_end_bone_srt)

        cmds.parent(new_L_end_bone, new_L_end_bone_srt)
        cmds.parent(new_R_end_bone, new_R_end_bone_srt)

        L_end_bone_pos = cmds.xform(L_end_bone, t=1, ws=1, q=1)
        R_end_bone_pos = cmds.xform(R_end_bone, t=1, ws=1, q=1)
        L_end_bone_rot = cmds.xform(L_end_bone, ro=1, ws=1, q=1)
        R_end_bone_rot = cmds.xform(R_end_bone, ro=1, ws=1, q=1)

        cmds.xform(new_L_end_bone_srt, t=L_end_bone_pos, ws=1)
        cmds.xform(new_R_end_bone_srt, t=R_end_bone_pos, ws=1)
        cmds.xform(new_L_end_bone_srt, ro=L_end_bone_rot, ws=1)
        cmds.xform(new_R_end_bone_srt, ro=R_end_bone_rot, ws=1)

        cmds.parentConstraint(main_ctrl_list[0], new_L_end_bone_srt)
        cmds.parentConstraint(main_ctrl_list[2], new_R_end_bone_srt)

        # delete leftover locators
        for each in self.loc_list:
            cmds.delete(each)

        # create node for rotation and translation of rig
        root = cmds.createNode('transform', name=self.rig_name + '_root')
        self.parts.append(root)
        cmds.parentConstraint(root, L_end_ctrl_srt, mo=True)
        cmds.parentConstraint(root, R_end_ctrl_srt, mo=True)
        cmds.parentConstraint(root, C_main_ctrl_srt, mo=True)
        cmds.parentConstraint(root, mid_vec_loc, mo=True)

        # add all parts of the rig to their respective groups
        parts_grp = cmds.createNode('transform', name=self.rig_name + '_parts')
        bones_grp = cmds.createNode('transform', name=self.rig_name + '_bones')
        controls_grp = cmds.createNode('transform', name=self.rig_name + '_controls')

        for each in self.parts:
            cmds.parent(each, parts_grp)
        for each in self.bones:
            cmds.parent(each, bones_grp)
        for each in self.controls:
            cmds.parent(each, controls_grp)
