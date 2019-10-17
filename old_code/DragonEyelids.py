import maya.cmds as cmds
import maya.api.OpenMaya as om


class Eyelids:

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
        self.num_joints = num_joints

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

        srt_list = []
        for x in range(0, amt_bones + 1):
            par = par_add * x
            if par == 1:
                par = .99
            # get names of the bones
            part = self.rig_name + '_{}'.format(str(x))

            up_vec_loc_top = self.up_vec_top_list[x]
            up_vec_loc_bot = self.bot_vec_top_list[x]

            cmds.select(clear=True)
            bone = cmds.joint(name='{}_{}_BONE'.format(part, self.rig_name))
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

    def create_controls(self, name='', size=1.0, *args):
        zero_list = []
        ctrl_list = []
        for x, each in enumerate(args):
            new_name = name + '_{}_CTRL'.format(str(x))
            ctrl = cmds.circle(name=new_name)[0]
            new_size = self.size * size
            cmds.setAttr(ctrl + '.scale', new_size, new_size, new_size)
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

    def build(self):
        self.layout_objects = cmds.ls(sl=True)

        # create temporary curve for control positioning
        temp_crv = self.curve_from_objects(self.layout_objects, name='temp_CRV')
        cmds.select(clear=True)
        cmds.rebuildCurve(temp_crv, ch=1, rpo=1, end=1, kr=0, kt=1, kep=1, kcp=0, s=8, d=2)

        # create controls based on curve
        par_add = 1.0/(self.num_ctrls - 1)
        PCI = cmds.createNode('pointOnCurveInfo', name='temp_PCI')
        cmds.connectAttr(temp_crv + '.worldSpace[0]', PCI + '.inputCurve')
        loc_list = []
        for x in range(0, self.num_ctrls):
            parameter = par_add * x

            loc = cmds.spaceLocator()[0]
            loc_list.append(loc)
            cmds.setAttr(PCI + '.parameter', parameter)
            cmds.connectAttr(PCI + '.result.position', loc + '.translate')

            if x > 0:
                cmds.aimConstraint(loc, prev_loc, aimVector=(0, 0, -1), mo=False)
            if x == (self.num_ctrls - 1):
                cmds.aimConstraint(prev_loc, loc, aimVector=(0, 0, 1), mo=False)
            cmds.disconnectAttr(PCI + '.result.position', loc + '.translate')
            prev_loc = loc
        cmds.delete(temp_crv)

        # create curve that will have bind joints
        self.HD_crv = self.curve_from_objects(loc_list, name='{}_HD_CRV'.format(self.rig_name))
        self.parts.append(self.HD_crv)
        cmds.select(clear=True)
        # needed to move rebuild to end of code as it was breaking

        # create low density curve
        self.LD_crv = self.curve_from_objects(loc_list, name='{}_LD_CRV'.format(self.rig_name))
        self.parts.append(self.LD_crv)
        cmds.select(clear=True)
        cmds.rebuildCurve(self.LD_crv, ch=1, rpo=1, end=1, kr=0, kt=1, kep=1, kcp=1, s=8, d=2)
        bot_vec_locs, self.bot_vec_top_list = self.create_dag_on_curve(self.LD_crv, self.num_joints, 'up_vec_bot')
        self.parts.append(bot_vec_locs)

        # create up vector curve
        transform_list = []
        for each in loc_list:
            transform = cmds.spaceLocator(name=each + '_proxy_LOC')[0]
            cmds.parent(transform, each)
            cmds.setAttr(transform + '.t', 0, 1, 0)
            cmds.setAttr(transform + '.r', 0, 0, 0)
            transform_list.append(transform)

        self.up_vec_LD_crv = self.curve_from_objects(transform_list, name='neck_up_vec_CRV')
        self.parts.append(self.up_vec_LD_crv)
        cmds.select(clear=True)
        cmds.rebuildCurve(self.up_vec_LD_crv, ch=1, rpo=1, end=1, kr=0, kt=1, kep=1, kcp=1, s=8, d=2)

        # create high density up vector curve
        self.up_vec_HD_crv = self.curve_from_objects(transform_list, name='neck_up_vec_HD_CRV')
        cmds.rebuildCurve(self.up_vec_HD_crv, ch=1, rpo=1, end=1, kr=0, kt=1, kep=1, kcp=0, s=8, d=2)
        cmds.delete(transform_list)
        top_vec_locs, self.up_vec_top_list = self.create_dag_on_curve(self.up_vec_HD_crv, self.num_joints, 'up_vec_top')
        for each in top_vec_locs:
            self.parts.append(each)
        self.parts.append(self.up_vec_HD_crv)

        # create bones for curve
        self.bones = self.create_bones(self.HD_crv, self.num_joints)

        # create controls
        ctrls, ctrl_zeros = self.create_controls(self.rig_name, .5, *loc_list)
        self.controls.append(ctrl_zeros)
        main_ctrls = []
        sub_ctrls = []
        for x, ctrl in enumerate(ctrls):
            main_ctrl_check = x % 2
            if main_ctrl_check == 0:
                main_ctrls.append(ctrl)
            else:
                sub_ctrls.append(ctrl)

        main_ctrl_index = 0
        for each in sub_ctrls:
            first_ctrl = main_ctrls[main_ctrl_index]
            main_ctrl_index += 1
            second_ctrl = main_ctrls[main_ctrl_index]
            main_ctrl_index += 1
            sub_ctrl_zero = cmds.listRelatives(each, parent=True)[0]
            main_ctrl_index -= 1

            cmds.select(clear=True)
            cmds.select(first_ctrl)
            cmds.select(second_ctrl, add=True)
            cmds.select(sub_ctrl_zero, add=True)

            cmds.pointConstraint(mo=True)
            cmds.select(clear=True)

        # create control joints
        crv_ctrl_joints = []
        for each in ctrls:
            cmds.select(clear=True)
            joint = cmds.joint(name=each + '_JNT')
            zero = cmds.createNode('transform', name=joint + '_ZERO')
            cmds.parent(joint, zero)

            cmds.parentConstraint(each, zero, mo=False)
            crv_ctrl_joints.append(joint)
            self.parts.append(zero)

        cmds.skinCluster(crv_ctrl_joints, self.LD_crv)
        cmds.skinCluster(crv_ctrl_joints, self.up_vec_LD_crv)

        wire1 = cmds.wire(self.HD_crv, li=1.000000, w=self.LD_crv, dds=(0, 10.0000))
        wire2 = cmds.wire(self.up_vec_HD_crv, li=1.000000, w=self.up_vec_LD_crv, dds=(0, 10.0000))

        # rebuild for first curve
        cmds.rebuildCurve(self.HD_crv, ch=1, rpo=1, end=1, kr=0, kt=1, kep=1, kcp=0, s=8, d=2)
        cmds.delete(loc_list)

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


cmds.select([u'L_eb_LOC1', u'L_eb_LOC2', u'L_eb_LOC3', u'L_eb_LOC4', u'L_eb_LOC5', u'L_eb_LOC6', u'L_eb_LOC7', u'L_eb_LOC8', u'L_eb_LOC9'])
L_eb = Eyelids(name='L_eb', num_ctrls=5, size=6)
L_eb.build()

cmds.select([u'R_eb_LOC1', u'R_eb_LOC2', u'R_eb_LOC3', u'R_eb_LOC4', u'R_eb_LOC5', u'R_eb_LOC6', u'R_eb_LOC7', u'R_eb_LOC8', u'R_eb_LOC9'])
R_eb = Eyelids(name='R_eb', num_ctrls=5, size=6)
R_eb.build()

cmds.select([u'L_top_el_ref_LOC1', u'L_top_el_ref_LOC2', u'L_top_el_ref_LOC3', u'L_top_el_ref_LOC4', u'L_top_el_ref_LOC5', u'L_top_el_ref_LOC6', u'L_top_el_ref_LOC7', u'L_top_el_ref_LOC8'])
L_top_el = Eyelids(name='L_top_el', num_ctrls=5, size=2)
L_top_el.build()

cmds.select([u'L_bot_el_ref_LOC1', u'L_bot_el_ref_LOC2', u'L_bot_el_ref_LOC3', u'L_bot_el_ref_LOC4', u'L_bot_el_ref_LOC5', u'L_bot_el_ref_LOC6', u'L_bot_el_ref_LOC7', u'L_bot_el_ref_LOC8'])
L_bot_el = Eyelids(name='L_bot_el', num_ctrls=5, size=2)
L_bot_el.build()

cmds.select([u'R_top_el_ref_LOC1', u'R_top_el_ref_LOC2', u'R_top_el_ref_LOC3', u'R_top_el_ref_LOC4', u'R_top_el_ref_LOC5', u'R_top_el_ref_LOC6', u'R_top_el_ref_LOC7', u'R_top_el_ref_LOC8'])
R_top_el = Eyelids(name='R_top_el', num_ctrls=5, size=2)
R_top_el.build()

cmds.select([u'R_bot_el_ref_LOC1', u'R_bot_el_ref_LOC2', u'R_bot_el_ref_LOC3', u'R_bot_el_ref_LOC4', u'R_bot_el_ref_LOC5', u'R_bot_el_ref_LOC6', u'R_bot_el_ref_LOC7', u'R_bot_el_ref_LOC8'])
R_bot_el = Eyelids(name='R_bot_el', num_ctrls=5, size=2)
R_bot_el.build()
