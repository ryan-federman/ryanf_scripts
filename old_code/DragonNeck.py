import maya.cmds as cmds
import maya.api.OpenMaya as om


class DragonNeck():

    def __init__(self, num_ctrls, name, spacing=10, num_joints=10, size=10):
        self.num_ctrls = num_ctrls
        self.rig_name = name
        self.spacing = spacing
        self.size = size
        self.controls = []
        self.parts = []
        self.parts_neck_space = []
        self.bones = []
        self.bones_neck_space = []
        self.layout_objects = []
        self.ctrl_layout_objects = []
        self.main_spaces = []
        self.pos_spaces = []
        self.create_layout_objects()
        self.num_joints = num_joints

    def create_layout_objects(self):
        pos = 0
        for x in range(0, self.num_ctrls):
            if x == 0:
                loc = cmds.spaceLocator(name=self.rig_name + '_beg_LD_crv_loc')[0]
                sub_loc = cmds.spaceLocator(name=self.rig_name + '_sub_{}_LD_crv_loc'.format(x))[0]
            elif x > 0 and x < (self.num_ctrls - 1):
                loc = cmds.spaceLocator(name=self.rig_name + '_mid_{}_LD_crv_loc'.format(x))[0]
                sub_loc = cmds.spaceLocator(name=self.rig_name + '_sub_{}_LD_crv_loc'.format(x))[0]
            else:
                loc = cmds.spaceLocator(name=self.rig_name + '_end_LD_crv_loc')[0]
                sub_loc = False
            cmds.xform(loc, t=(0, 0, pos * self.spacing))
            pos = pos + 1
            self.layout_objects.append(loc)
            if sub_loc:
                cmds.xform(sub_loc, t=(0, 0, pos * self.spacing))
                pos = pos + 1
                cmds.setAttr(sub_loc + '.localScaleX', .5)
                self.layout_objects.append(sub_loc)

    def curve_from_objects(self, dag_nodes, name='C_generic_CRV', degree=2):
        """Create a Nurbs curve and link it with the locators

        Args:
            dag_nodes(list of strings): List of objects for each CV of the resulting curve
            name (str): Name of node
            degree (int): egree of the curve

        Returns:
            string: resulting curve
        """

        pos = [(0, 0, 0)]
        if len(dag_nodes) == 2:
            degree = 1
        curve = cmds.curve(name=name, d=degree, p=pos * len(dag_nodes))

        for i, dag_node in enumerate(dag_nodes):
            loc = cmds.listRelatives(dag_node, s=True)[0]
            cmds.connectAttr(loc + ".worldPosition", "{0}.cv[{1}]".format(curve, i), force=True)

        return curve

    def diamond_shape(self, name):
        ctrl1 = cmds.circle()
        cmds.setAttr(ctrl1[1] + '.degree', 1)
        cmds.setAttr(ctrl1[1] + '.sections', 4)
        ctrl2 = cmds.duplicate(ctrl1[0])[0]
        cmds.setAttr(ctrl2 + '.rx', 90)
        ctrl3 = cmds.duplicate(ctrl2)[0]
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

        return transform

    def circle_shape(self, name):
        ctrl = cmds.circle(name=name)[0]

        return ctrl

    def create_controls(self, shape='circle', name='', split1='', size=1, *args):
        zero_list = []
        ctrl_list = []
        for each in args:
            if split1 != '':
                name = each
                new_name = 'C_' + name.split(split1)[0] + 'CTRL'
            else:
                new_name = 'C_' + name + '_CTRL'
            if shape == 'circle':
                ctrl = self.circle_shape(new_name)
            else:
                ctrl = self.diamond_shape(new_name)
            cmds.setAttr(ctrl + '.scale', self.size * size, self.size * size, self.size * size)
            cmds.makeIdentity(ctrl, apply=True)
            ctrl_OFS = cmds.createNode('transform', name=new_name + '_OFS')
            ctrl_ZERO = cmds.createNode('transform', name=new_name + '_ZERO')
            cmds.parent(ctrl, ctrl_OFS)
            cmds.parent(ctrl_OFS, ctrl_ZERO)
            pos = cmds.xform(each, t=True, ws=True, q=True)
            cmds.xform(ctrl_ZERO, t=pos, ws=True)

            zero_list.append(ctrl_ZERO)
            ctrl_list.append(ctrl)
        return ctrl_list, zero_list

    def create_dag_on_curve(self, crv, amt_dag, name):
        par_add = 1.0/amt_dag
        mid_point = amt_dag/2

        srt_list = []
        dag_list = []
        for x in range(0, amt_dag + 1):
            par = par_add * x

            part = self.rig_name + '_{}'.format(str(x))

            cmds.select(clear=True)
            dag = cmds.spaceLocator(name='{}_{}_{}_LOC'.format(name, part, self.rig_name))[0]
            srt = cmds.createNode('transform', name='{}_srt'.format(dag))
            srt_list.append(srt)
            dag_list.append(dag)
            cmds.parent(dag, srt)

            PCI = cmds.createNode('pointOnCurveInfo', name=str(dag) + '_PCI')

            cmds.connectAttr(crv + '.worldSpace[0]', PCI + '.inputCurve')

            cmds.setAttr(PCI + '.parameter', par)

            cmds.connectAttr(PCI + '.position', dag + '.translate')

        return srt_list, dag_list

    def create_bones(self, crv, amt_bones):
        par_add = 1.0/amt_bones
        mid_point = amt_bones/2

        srt_list = []
        for x in range(0, amt_bones + 1):
            par = par_add * x
            if par == 1:
                par = .99
            # get names of the bones
            side = 'C'
            part = self.rig_name + '_{}'.format(str(x))

            # up_vec_cp = up_vec_list[x]
            up_vec_loc_top = self.up_vec_top_list[x]
            up_vec_loc_bot = self.bot_vec_top_list[x]

            cmds.select(clear=True)
            bone = cmds.joint(name='{}_{}_{}_BONE'.format(side, part, self.rig_name))
            srt = cmds.createNode('transform', name='{}_srt'.format(bone))
            srt_list.append(srt)
            cmds.parent(bone, srt)

            up_vec_cp_pma = cmds.createNode('plusMinusAverage', name=bone + '_up_vec_PMA')
            up_vec_cp = cmds.createNode('vectorProduct', name=bone + '_up_vec_VP')

            PCI = cmds.createNode('pointOnCurveInfo', name=str(bone) + '_PCI')
            z_cross_product = cmds.createNode('vectorProduct', name=bone + '_z_CP')
            y_cross_product = cmds.createNode('vectorProduct', name=bone + '_y_CP')
            z_cp_reverse = cmds.createNode('multiplyDivide', name=bone + '_z_CP_MULT')
            fbf_matrix = cmds.createNode('fourByFourMatrix', name=bone + '_fbfMtx')
            dec_matrix = cmds.createNode('decomposeMatrix', name=bone + '_DM')

            cmds.connectAttr(up_vec_loc_top + '.worldPosition', up_vec_cp_pma + '.input3D[0]')
            cmds.connectAttr(up_vec_loc_bot + '.worldPosition', up_vec_cp_pma + '.input3D[1]')
            cmds.setAttr(up_vec_cp_pma + '.operation', 2)

            cmds.connectAttr(up_vec_cp_pma + '.output3D', up_vec_cp + '.input1')
            cmds.setAttr(up_vec_cp + '.operation', 0)
            cmds.setAttr(up_vec_cp + '.normalizeOutput', 1)

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

    def list_connected_attrs(self, object, destination=True, source=True):
        '''
        Lists all connected attributes to an objects transform attributes
        :param object: Object being queried
        :param destination: Whether the destination attributes will be listed
        :param source: Whether the source attributes will be listed
        :return: dictionary of object's attribute as the key and the connections as values
        '''
        conn_attrs = {}
        conn_attrs['t'] = cmds.listConnections(object + '.t', plugs=True, d=destination, s=source)
        conn_attrs['tx'] = cmds.listConnections(object + '.tx', plugs=True, d=destination, s=source)
        conn_attrs['ty'] = cmds.listConnections(object + '.ty', plugs=True, d=destination, s=source)
        conn_attrs['tz'] = cmds.listConnections(object + '.tz', plugs=True, d=destination, s=source)

        conn_attrs['r'] = cmds.listConnections(object + '.r', plugs=True, d=destination, s=source)
        conn_attrs['rx'] = cmds.listConnections(object + '.rx', plugs=True, d=destination, s=source)
        conn_attrs['ry'] = cmds.listConnections(object + '.ry', plugs=True, d=destination, s=source)
        conn_attrs['rz'] = cmds.listConnections(object + '.rz', plugs=True, d=destination, s=source)

        return conn_attrs

    def create_auto_pv(self, root, mid, end, ikh):
        root_vec = cmds.createNode('decomposeMatrix', name=ikh + '_root_vec')
        mid_vec = cmds.createNode('decomposeMatrix', name=ikh + '_mid_vec')
        end_vec = cmds.createNode('decomposeMatrix', name=ikh + '_end_vec')

        line_vec_SV = cmds.createNode('math_SubtractVector', name=ikh + '_line_vec_SV')
        point_vec_SV = cmds.createNode('math_SubtractVector', name=ikh + '_point_vec_SV')
        line_vec_normalize = cmds.createNode('vectorProduct', name=ikh + '_line_vec')
        scale_value = cmds.createNode('vectorProduct', name=ikh + '_scale_value')
        proj_vec_mult = cmds.createNode('multiplyDivide', name=ikh + '_proj_vec_MULT')
        mid_point_add = cmds.createNode('math_AddVector', name=ikh + '_mid_point_ADD')

        short_pole_vec_pos_SV = cmds.createNode('math_SubtractVector', name=ikh + 'short_pole_vec_pos_SV')
        short_pole_vec_pos_SV_normalize = cmds.createNode('vectorProduct', name=ikh + 'short_pole_vec_pos_SV_normalize')

        root_to_mid_len_DB = cmds.createNode('distanceBetween', name=ikh + '_root_to_mid_len_DB')
        mid_to_end_len_DB = cmds.createNode('distanceBetween', name=ikh + '_mid_to_end_len_DB')
        len_of_chain_add = cmds.createNode('math_Add', name=ikh + '_len_of_chain_ADD')
        len_pole_vec = cmds.createNode('math_MultiplyVector', name=ikh + '_len_pole_vec_MV')
        pole_vec_pos = cmds.createNode('math_AddVector', name=ikh + '_pole_vec_pos')

        loc = cmds.spaceLocator(name=ikh + '_PV_LOC')[0]
        loc_cm = cmds.createNode('composeMatrix', name=loc + '_CM')
        loc_mm = cmds.createNode('multMatrix', name=loc + '_MM')
        loc_dm = cmds.createNode('decomposeMatrix', name=loc + '_DM')

        cmds.connectAttr(root + '.worldMatrix[0]', root_vec + '.inputMatrix')
        cmds.connectAttr(mid + '.worldMatrix[0]', mid_vec + '.inputMatrix')
        cmds.connectAttr(end + '.worldMatrix[0]', end_vec + '.inputMatrix')

        cmds.connectAttr(end_vec + '.outputTranslate', line_vec_SV + '.input1')
        cmds.connectAttr(root_vec + '.outputTranslate', line_vec_SV + '.input2')

        cmds.setAttr(line_vec_normalize + '.operation', 0)
        cmds.setAttr(line_vec_normalize + '.normalizeOutput', 1)
        cmds.connectAttr(line_vec_SV + '.output', line_vec_normalize + '.input1')

        cmds.connectAttr(mid_vec + '.outputTranslate', point_vec_SV + '.input1')
        cmds.connectAttr(root_vec + '.outputTranslate', point_vec_SV + '.input2')

        cmds.connectAttr(line_vec_normalize + '.output', scale_value + '.input1')
        cmds.connectAttr(point_vec_SV + '.output', scale_value + '.input2')

        cmds.connectAttr(line_vec_normalize + '.output', proj_vec_mult + '.input1')
        cmds.connectAttr(scale_value + '.output', proj_vec_mult + '.input2')

        cmds.connectAttr(point_vec_SV + '.output', short_pole_vec_pos_SV + '.input1')
        cmds.connectAttr(proj_vec_mult + '.output', short_pole_vec_pos_SV + '.input2')

        cmds.connectAttr(short_pole_vec_pos_SV + '.output', short_pole_vec_pos_SV_normalize + '.input1')
        cmds.setAttr(short_pole_vec_pos_SV_normalize + '.operation', 0)
        cmds.setAttr(short_pole_vec_pos_SV_normalize + '.normalizeOutput', 1)

        cmds.connectAttr(root + '.worldMatrix[0]', root_to_mid_len_DB + '.inMatrix1')
        cmds.connectAttr(mid + '.worldMatrix[0]', root_to_mid_len_DB + '.inMatrix2')

        cmds.connectAttr(mid + '.worldMatrix[0]', mid_to_end_len_DB + '.inMatrix1')
        cmds.connectAttr(end + '.worldMatrix[0]', mid_to_end_len_DB + '.inMatrix2')

        cmds.connectAttr(root_to_mid_len_DB + '.distance', len_of_chain_add + '.input1')
        cmds.connectAttr(mid_to_end_len_DB + '.distance', len_of_chain_add + '.input2')

        cmds.connectAttr(short_pole_vec_pos_SV_normalize + '.output', len_pole_vec + '.input1')
        cmds.connectAttr(len_of_chain_add + '.output', len_pole_vec + '.input2')

        cmds.connectAttr(root_vec + '.outputTranslate', mid_point_add + '.input1')
        cmds.connectAttr(proj_vec_mult + '.output', mid_point_add + '.input2')

        cmds.connectAttr(mid_point_add + '.output', pole_vec_pos + '.input1')
        cmds.connectAttr(len_pole_vec + '.output', pole_vec_pos + '.input2')

        cmds.connectAttr(pole_vec_pos + '.output', loc_cm + '.inputTranslate')

        cmds.connectAttr(loc_cm + '.outputMatrix', loc_mm + '.matrixIn[0]')
        cmds.connectAttr(loc + '.parentInverseMatrix[0]', loc_mm + '.matrixIn[1]')

        cmds.connectAttr(loc_mm + '.matrixSum', loc_dm + '.inputMatrix')

        cmds.connectAttr(loc_dm + '.outputTranslate', loc + '.translate')

        cmds.poleVectorConstraint(loc, ikh)

        return loc

    def create_dag_dm(self, object):
        try:
            cmds.select(object + '_DM')
            cmds.select(clear=True)
            dm = object + '_DM'

        except:
            dm = cmds.createNode('decomposeMatrix', name=object + '_DM')
            cmds.connectAttr(object + '.worldMatrix[0]', dm + '.inputMatrix')

        return dm

    def build_1(self):
        big_ik_chain_joints = []
        for each in self.layout_objects:
            new_name = each.split('LD_crv')
            new_name = new_name[0] + 'big_ik_JNT'
            joint = cmds.joint(name=new_name)
            pos = cmds.xform(each, t=True, ws=True, query=True)
            cmds.xform(joint, t=pos, ws=True)
            big_ik_chain_joints.append(joint)
        self.bones_neck_space.append(big_ik_chain_joints[0])

        # create controls
        self.ctrls = []
        self.ctrls_zero = []
        self.ctrls_zero_neck_space = []

        big_ik_ctrls = self.create_controls('circle', '', 'big_ik_JNT', 1, *big_ik_chain_joints)
        for each in big_ik_ctrls[0]:
            self.ctrls.append(each)
        for each in big_ik_ctrls[1]:
            self.ctrls_zero.append(each)
            self.ctrls_zero_neck_space.append(each)

        ik_main_ctrl = self.create_controls('circle', 'neck_IK', '', 2, big_ik_chain_joints[-1])
        for each in ik_main_ctrl[0]:
            self.ctrls.append(each)
        for each in ik_main_ctrl[1]:
            self.ctrls_zero.append(each)
            self.ctrls_zero_neck_space.append(each)

        base_ctrl = self.create_controls('circle', 'neck_base', '', 2, big_ik_chain_joints[0])
        self.ctrls.append(base_ctrl[0][0])
        self.controls.append(base_ctrl[1])

        # aim controls at the next control down the chain
        for x in range(0, len(big_ik_ctrls[1])-1):
            const = cmds.aimConstraint(big_ik_ctrls[1][x+1], big_ik_ctrls[1][x],
                                       aimVector=(0, 0, 1),
                                       mo=False)
            cmds.delete(const)

        # constrain main controls to main ik chain
        for joint, zero, in zip(big_ik_chain_joints, self.ctrls_zero):
            if 'sub' not in zero:
                if zero == self.ctrls_zero[-2]:
                    cmds.orientConstraint(ik_main_ctrl[0], zero, mo=True)
                else:
                    cmds.orientConstraint(joint, zero, mo=True)

        # create second set of control joints, will control the sub controls
        cmds.select(clear=True)

        small_ik_chain_joints = []
        for each in self.layout_objects:
            new_name = each.split('LD_crv')
            new_name = new_name[0] + 'small_ik_JNT'
            joint = cmds.joint(name=new_name)
            pos = cmds.xform(each, t=True, ws=True, query=True)
            cmds.xform(joint, t=pos, ws=True)
            small_ik_chain_joints.append(joint)
        self.bones_neck_space.append(small_ik_chain_joints[0])

        # create ik handles for second chain
        x = 0
        small_ikh_list = []
        for each in small_ik_chain_joints:
            if x == 0:
                start_joint = each
                x += 1
            elif x == 1:
                x += 1
                ctrl = each.split('small_ik_JNT')
                ctrl = 'C_' + ctrl[0] + 'CTRL_ZERO'
                cmds.parentConstraint(each, ctrl, mo=True)
                cmds.select(clear=True)

            elif x == 2:
                end_joint = each
                new_name = each.split('small_ik_JNT')
                ctrl = 'C_' + new_name[0] + 'CTRL'
                new_name = new_name[0] + 'ikh'
                small_ikh = cmds.ikHandle(sj=start_joint,
                                          ee=end_joint,
                                          sol='ikRPsolver',
                                          name=new_name)[0]
                cmds.parentConstraint(ctrl, small_ikh, mo=True)
                cmds.select(clear=True)
                start_joint = each
                small_ikh_list.append(small_ikh)
                self.parts_neck_space.append(small_ikh)
                x = 1

        x = 0
        for each in small_ikh_list:
            root = big_ik_chain_joints[x]
            x += 1
            mid = big_ik_chain_joints[x]
            x += 1
            end = big_ik_chain_joints[x]

            pv = self.create_auto_pv(root, mid, end, each)

            self.parts.append(pv)

        # create ik chain to drive control positions
        big_ikh = cmds.ikHandle(sj=big_ik_chain_joints[0],
                                ee=big_ik_chain_joints[-1],
                                sol='ikSpringSolver')[0]
        self.big_ikh = big_ikh

        # create up vector for aim constraint
        up_vec_loc = cmds.spaceLocator(name=self.rig_name + '_big_ikh_PV_up_vec')[0]
        cmds.parent(up_vec_loc, base_ctrl[0][0])
        cmds.setAttr(up_vec_loc + '.t', 0, 10, 0)

        # create pv control
        loc = cmds.spaceLocator(name='big_ikh_loc_PV')[0]
        big_pv, big_pv_zero = self.create_controls('diamond',
                                                   self.rig_name + '_big_ikh_PV',
                                                   '',
                                                   .6,
                                                   loc)

        big_pv = big_pv[0]
        big_pv_zero = big_pv_zero[0]
        cmds.poleVectorConstraint(big_pv, big_ikh)

        # pv position
        big_ikh_pos = cmds.xform(big_ikh, t=True, ws=True, q=True)
        beg_ctrl_pos = cmds.xform(self.ctrls[0], t=True, ws=True, q=True)

        big_ikh_vec = om.MVector(big_ikh_pos)
        beg_ctrl_vec = om.MVector(beg_ctrl_pos)

        pv_pos = (beg_ctrl_vec - big_ikh_vec)/2

        cmds.xform(big_pv_zero, t=pv_pos, ws=True)

        self.parts_neck_space.append(big_ikh)

        # create group that makes pv follow chain
        new_name = big_pv + '_follow_ZERO'
        pv_follow_grp = cmds.createNode('transform', name=new_name)
        pos = cmds.xform(base_ctrl[0][0], t=True, ws=True, q=True)
        cmds.xform(pv_follow_grp, t=pos, ws=True)
        cmds.aimConstraint(ik_main_ctrl[0], pv_follow_grp,
                           aimVector=(0, 0, 1),
                           worldUpType='object',
                           worldUpObject=up_vec_loc,
                           mo=False)
        cmds.parent(big_pv_zero, pv_follow_grp)
        self.ctrls_zero_neck_space.append(pv_follow_grp)

        # create spaces to control position of each mid control
        space_grp = cmds.createNode('transform', name='SPACE_GRP')
        main_space_grp = cmds.createNode('transform', name='main_SPACE_GRP')
        pos_space_grp = cmds.createNode('transform', name='pos_SPACE_GRP')
        self.parts.append(space_grp)

        cmds.parent(main_space_grp, space_grp)
        cmds.parent(pos_space_grp, space_grp)

        pos_spaces = []
        main_ctrls = []
        main_jnts = []

        # creates spaces that follow positions of every other given dag node and
        # puts the original dag node into a list for later use
        def create_pos_spaces(list, new_dag_list):
            x = 0
            for each in list:
                if x == 0:
                    pos_space = cmds.createNode('transform', name=each + '_pos_SPACE')
                    cmds.pointConstraint(each, pos_space, mo=True)
                    pos_spaces.append(pos_space)
                    cmds.parent(pos_space, pos_space_grp)
                    new_dag_list.append(each)
                    x += 1
                elif x == 1:
                    x = 0

        create_pos_spaces(big_ik_chain_joints, main_jnts)
        create_pos_spaces(self.ctrls, main_ctrls)

        x = 0

        # create main spaces for all mid controls and make them follow both the
        # big ik chain and the 'parent' control
        for ctrl, joint in zip(main_ctrls, main_jnts):
            if x == 0:
                x += 1
            else:
                ctrl_space = main_ctrls[x-1] + '_pos_SPACE'
                joint_space = joint + '_pos_SPACE'
                prev_joint_space = main_jnts[x-1] + '_pos_SPACE'
                main_space = cmds.createNode('transform', name=ctrl + '_main_SPACE')
                add_vec = cmds.createNode('math_AddVector', name=main_space + '_1_AV')
                sub_vec = cmds.createNode('math_SubtractVector', name=main_space + '_SV')
                add_vec_2 = cmds.createNode('math_AddVector', name=main_space + '_2_AV')
                MM = cmds.createNode('multMatrix', name=ctrl + '_ZER0_pos_MM')
                DM = cmds.createNode('decomposeMatrix', name=MM + '_DM')

                cmds.connectAttr(ctrl_space + '.t', add_vec + '.input1')
                cmds.connectAttr(joint_space + '.t', add_vec + '.input2')

                cmds.connectAttr(add_vec + '.output', sub_vec + '.input1')
                cmds.connectAttr(prev_joint_space + '.t', sub_vec + '.input2')

                pos = cmds.xform(ctrl + '_ZERO', t=True, ws=True, q=True)
                cmds.connectAttr(sub_vec + '.output', add_vec_2 + '.input1')
                cmds.setAttr(add_vec_2 + '.input2', pos[0], pos[1], pos[2])

                cmds.connectAttr(add_vec_2 + '.output', main_space + '.t')

                cmds.connectAttr(main_space + '.worldMatrix[0]', MM + '.matrixIn[0]')
                cmds.connectAttr(ctrl + '_ZERO.parentInverseMatrix[0]', MM + '.matrixIn[1]')

                cmds.connectAttr(MM + '.matrixSum', DM + '.inputMatrix')
                cmds.connectAttr(DM + '.outputTranslate', ctrl + '_ZERO.t')

                cmds.parent(main_space, space_grp)

                x += 1


        # create low density curve
        self.LD_crv = self.curve_from_objects(self.layout_objects, name='ctrl_neck_LD_CRV')
        self.parts.append(self.LD_crv)
        cmds.select(clear=True)
        cmds.rebuildCurve(self.LD_crv, ch=1, rpo=1, end=1, kr=0, kt=1, kep=1, kcp=1, s=8, d=2)
        bot_vec_locs, self.bot_vec_top_list = self.create_dag_on_curve(self.LD_crv, self.num_joints, 'up_vec_bot')
        for each in bot_vec_locs:
            self.parts.append(each)

        # create up vector curve
        transform_list = []
        for each in big_ik_ctrls[0]:
            transform = cmds.spaceLocator(name=each + '_proxy_LOC')[0]
            cmds.parent(transform, each)
            cmds.setAttr(transform + '.t', 0, 1, 0)
            cmds.setAttr(transform + '.r', 0, 0, 0)
            transform_list.append(transform)

        self.up_vec_crv = self.curve_from_objects(transform_list, name='neck_up_vec_CRV')
        self.parts.append(self.up_vec_crv)
        cmds.select(clear=True)
        cmds.rebuildCurve(self.up_vec_crv, ch=1, rpo=1, end=1, kr=0, kt=1, kep=1, kcp=1, s=8, d=2)
        cmds.delete(transform_list)
        top_vec_locs, self.up_vec_top_list = self.create_dag_on_curve(self.up_vec_crv, self.num_joints, 'up_vec_top')
        for each in top_vec_locs:
            self.parts.append(each)

        # create bones for curve
        self.bones = self.create_bones(self.LD_crv, self.num_joints)

        # create base bone
        base_bone = cmds.joint(name=self.rig_name + '_base_BONE')
        cmds.parentConstraint(base_ctrl[0][0], base_bone, mo=False)
        self.bones.append(base_bone)

        # create control joints
        crv_ctrl_joints = []
        for each in big_ik_ctrls[0]:
            cmds.select(clear=True)
            joint = cmds.joint(name=each + '_JNT')
            zero = cmds.createNode('transform', name=joint + '_ZERO')
            cmds.parent(joint, zero)

            cmds.parentConstraint(each, zero, mo=False)
            crv_ctrl_joints.append(joint)
            self.parts.append(zero)

        cmds.skinCluster(crv_ctrl_joints, self.LD_crv)
        cmds.skinCluster(crv_ctrl_joints, self.up_vec_crv)


        # space for each control switching between setup and simple ik
        ik_spaces = []
        for x, each in enumerate(big_ik_ctrls[1]):
            # create space attribute on control
            ctrl = big_ik_ctrls[0][x]
            cmds.addAttr(ctrl, ln='SPACE', at='double', min=0, max=1, dv=0, k=True)

            world_space = cmds.createNode('transform', name=each + '_world_SPACE')
            ik_space = cmds.createNode('transform', name=each + '_ik_SPACE')
            pos = cmds.xform(each, t=True, ws=True, q=True)
            rot = cmds.xform(each, ro=True, ws=True, q=True)
            cmds.xform(world_space, t=pos, ws=True)
            cmds.xform(world_space, ro=rot, ws=True)
            cmds.xform(ik_space, t=pos, ws=True)
            cmds.xform(ik_space, ro=rot, ws=True)

            ik_spaces.append(ik_space)

            if ctrl == big_ik_ctrls[0][-1]:
                cmds.parent(world_space, ik_main_ctrl[0])
            else:
                cmds.parent(world_space, big_ik_chain_joints[x])

            if 'sub' in each:
                # make it so that space follows both the big ik chain and moves
                # with it's previous and next controls

                cmds.select(clear=True)

                prev_ctrl = big_ik_ctrls[0][x-1]
                next_ctrl = big_ik_ctrls[0][x+1]
                prev_jnt = big_ik_chain_joints[x-1]
                next_jnt = big_ik_chain_joints[x+1]
                jnt = big_ik_chain_joints[x]

                prev_ctrl_dm = self.create_dag_dm(prev_ctrl)
                next_ctrl_dm = self.create_dag_dm(next_ctrl)
                prev_jnt_dm = self.create_dag_dm(prev_jnt)
                next_jnt_dm = self.create_dag_dm(next_jnt)
                jnt_dm = self.create_dag_dm(jnt)

                ctrl_av = cmds.createNode('plusMinusAverage', name=each + '_CTRL_AV')
                jnt_av = cmds.createNode('plusMinusAverage', name=each + '_JNT_AV')

                ctrl_div = cmds.createNode('multiplyDivide', name=each + '_CTRL_vector')
                jnt_div = cmds.createNode('multiplyDivide', name=each + '_JNT_vector')

                fake_point_constraint = cmds.createNode('plusMinusAverage', name=each + '_middling_PMA')

                final_position_pma = cmds.createNode('plusMinusAverage', name=each + '_final_position_PMA')
                final_position_cm = cmds.createNode('composeMatrix', name=each + '_final_position_CM')
                final_position_mm = cmds.createNode('multMatrix', name=each + '_final_position_MM')
                final_position_dm = cmds.createNode('decomposeMatrix', name=each + '_final_position_DM')

                cmds.connectAttr(next_ctrl_dm + '.outputTranslate', ctrl_av + '.input3D[0]')
                cmds.connectAttr(prev_ctrl_dm + '.outputTranslate', ctrl_av + '.input3D[1]')

                cmds.connectAttr(next_jnt_dm + '.outputTranslate', jnt_av + '.input3D[0]')
                cmds.connectAttr(prev_jnt_dm + '.outputTranslate', jnt_av + '.input3D[1]')

                cmds.setAttr(ctrl_div + '.operation', 2)
                cmds.setAttr(ctrl_div + '.input2X', 2)
                cmds.setAttr(ctrl_div + '.input2Y', 2)
                cmds.setAttr(ctrl_div + '.input2Z', 2)
                cmds.connectAttr(ctrl_av + '.output3D', ctrl_div + '.input1')

                cmds.setAttr(jnt_div + '.operation', 2)
                cmds.setAttr(jnt_div + '.input2X', 2)
                cmds.setAttr(jnt_div + '.input2Y', 2)
                cmds.setAttr(jnt_div + '.input2Z', 2)
                cmds.connectAttr(jnt_av + '.output3D', jnt_div + '.input1')

                cmds.setAttr(fake_point_constraint + '.operation', 2)
                cmds.connectAttr(ctrl_div + '.output', fake_point_constraint + '.input3D[0]')
                cmds.connectAttr(jnt_div + '.output', fake_point_constraint + '.input3D[1]')

                cmds.setAttr(final_position_pma + '.operation', 1)
                cmds.connectAttr(jnt_dm + '.outputTranslate', final_position_pma + '.input3D[0]')
                cmds.connectAttr(fake_point_constraint + '.output3D', final_position_pma + '.input3D[1]')

                cmds.connectAttr(final_position_pma + '.output3D', final_position_cm + '.inputTranslate')

                cmds.connectAttr(final_position_cm + '.outputMatrix', final_position_mm + '.matrixIn[0]')
                cmds.connectAttr(world_space + '.parentInverseMatrix[0]', final_position_mm + '.matrixIn[1]')

                cmds.connectAttr(final_position_mm + '.matrixSum', final_position_dm + '.inputMatrix')

                cmds.connectAttr(final_position_dm + '.outputTranslate', world_space + '.translate')

            attrs = self.list_connected_attrs(each, destination=False)
            for dest, source in attrs.items():
                if source is not None:
                    cmds.connectAttr(source[0], ik_space + '.' + dest)
                    cmds.disconnectAttr(source[0], each + '.' + dest)

            # connect both spaces to the control
            blend = cmds.createNode('millMatrixBlend', name=ctrl + '_SPC_BLEND')
            mm = cmds.createNode('multMatrix', name=ctrl + '_SPC_MM')
            dm = cmds.createNode('decomposeMatrix', name=ctrl + '_SPC_DM')

            cmds.connectAttr(world_space + '.worldMatrix[0]', blend + '.inMatrix1')
            cmds.connectAttr(ik_space + '.worldMatrix[0]', blend + '.inMatrix2')

            cmds.connectAttr(blend + '.outMatrix', mm + '.matrixIn[0]')
            cmds.connectAttr(each + '.parentInverseMatrix[0]', mm + '.matrixIn[1]')

            cmds.connectAttr(mm + '.matrixSum', dm + '.inputMatrix')
            cmds.connectAttr(dm + '.outputTranslate', each + '.translate')
            cmds.connectAttr(dm + '.outputRotate', each + '.rotate')

            cmds.connectAttr(ctrl + '.SPACE', blend + '.blend')

        ik_spc_grp = cmds.createNode('transform', name='ik_space_GRP')
        for each in ik_spaces:
            cmds.parent(each, ik_spc_grp)
        cmds.parentConstraint(base_ctrl[0][0], ik_spc_grp, mo=True)

        # create offset control for end control
        ofs_name = (big_ik_ctrls[0][-1].split('CTRL')[0]) + '_OFS_CTRL'

        ctrl = cmds.duplicate(big_ik_ctrls[0][-1])
        cmds.scale(.7, .7, .7, ctrl)
        cmds.makeIdentity(ctrl, apply=True)
        cmds.parent(big_ik_ctrls[0][-1], ctrl)
        cmds.rename(big_ik_ctrls[0][-1], ofs_name)
        cmds.rename(ctrl, big_ik_ctrls[0][-1])

        cmds.addAttr(big_ik_ctrls[0][-1], ln='secondaryControl', at='long', min=0, max=1, dv=0, k=True)
        cmds.connectAttr(big_ik_ctrls[0][-1] + '.secondaryControl', ofs_name + '.v')
        cmds.connectAttr(big_ik_ctrls[0][-1] + '.SPACE', ofs_name + '.SPACE')

        # add all parts to the appropriate groups
        world_ofs_parts = cmds.createNode('transform', name=self.rig_name + '_parts_WORLD_OFS')
        world_ofs_ctrls = cmds.createNode('transform', name=self.rig_name + '_ctrls_WORLD_OFS')
        jnt_zero = cmds.createNode('transform', name=self.rig_name + '_JNTS_ZERO')

        self.parts.append(world_ofs_parts)
        self.parts.append(jnt_zero)
        self.controls.append(world_ofs_ctrls)

        cmds.parentConstraint(base_ctrl[0], world_ofs_ctrls, mo=True)
        cmds.parentConstraint(base_ctrl[0], world_ofs_parts, mo=True)
        cmds.pointConstraint(base_ctrl[0], jnt_zero, mo=True)
        cmds.pointConstraint(ik_main_ctrl[0], big_ikh, mo=True)

        for each in self.ctrls_zero_neck_space:
            cmds.parent(each, world_ofs_ctrls)
        for each in self.parts_neck_space:
            cmds.parent(each, world_ofs_parts)
        for each in self.bones_neck_space:
            cmds.parent(each, jnt_zero)

        bone_grp = cmds.createNode('transform', name=self.rig_name + '_bone_GRP')
        parts_grp = cmds.createNode('transform', name=self.rig_name + '_parts_GRP')
        control_grp = cmds.createNode('transform', name=self.rig_name + '_control_GRP')

        cmds.parent(bone_grp, 'bone_GRP')
        cmds.parent(parts_grp, 'parts_GRP')
        cmds.parent(control_grp, 'control_GRP')

        for each in self.bones:
            cmds.parent(each, bone_grp)
        for each in self.parts:
            cmds.parent(each, parts_grp)
        for each in self.controls:
            cmds.parent(each, control_grp)

        cmds.select(clear=True)
        for each in self.layout_objects:
            if each != big_ikh:
                cmds.delete(each)


neck1 = DragonNeck(num_ctrls=5, name='neck', spacing=50, num_joints=20, size=30)
move_locators()
neck1.build_1()


def move_locators():
    for key in loc_positions:
        value = loc_positions[key]
        cmds.xform(key, t=value, ws=True)


loc_positions = {}
for each in neck1.layout_objects:
    pos = cmds.xform(each, t=True, ws=True, q=True)
    loc_positions[each] = pos


loc_positions = {u'neck_beg_LD_crv_loc': [0.0, -54.157588958740234, -392.6517639160156],
 u'neck_end_LD_crv_loc': [0.0, 47.14804386420681, -24.650727719493872],
 u'neck_mid_1_LD_crv_loc': [-1.1368683772161603e-13,
                            -31.165081024169922,
                            -243.97296142578125],
 u'neck_mid_2_LD_crv_loc': [0.0, 58.12437438964844, -158.38580322265625],
 u'neck_mid_3_LD_crv_loc': [0.0, 75.64048767089844, -84.22313690185547],
 u'neck_sub_0_LD_crv_loc': [0.0, -49.9415168762207, -319.42413330078125],
 u'neck_sub_1_LD_crv_loc': [-1.1368683772161603e-13,
                            14.827093124389648,
                            -192.3018798828125],
 u'neck_sub_2_LD_crv_loc': [0.0, 77.52207946777344, -122.9169692993164],
 u'neck_sub_3_LD_crv_loc': [-2.842170943040401e-14,
                            64.78275299072266,
                            -51.134307861328125]}

