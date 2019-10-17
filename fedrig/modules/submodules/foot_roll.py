import maya.cmds as cmds
import maya.api.OpenMaya as om

from rigging_utils import attribute
from rigging_utils import shape
from rigging_utils.name import Name

import millrigger.modules.NY.misc.ryanf_scripts.util.maths as math


class foot_roll():
    def __init__(self, control):
        self.main_ctrl = control

        self.l_tip_loc = cmds.spaceLocator(name='L_tip_LOC')
        self.l_heel_loc = cmds.spaceLocator(name='L_heel_LOC')
        self.l_ball_loc = cmds.spaceLocator(name='L_ball_LOC')
        self.l_foot_loc = cmds.spaceLocator(name='L_foot_LOC')
        self.l_foot_in_loc = cmds.spaceLocator(name='L_foot_in_LOC')
        self.l_foot_out_loc = cmds.spaceLocator(name='L_foot_out_LOC')

        self.r_tip_loc = cmds.spaceLocator(name='R_tip_LOC')
        self.r_heel_loc = cmds.spaceLocator(name='R_heel_LOC')
        self.r_ball_loc = cmds.spaceLocator(name='R_ball_LOC')
        self.r_foot_loc = cmds.spaceLocator(name='R_foot_LOC')
        self.r_foot_in_loc = cmds.spaceLocator(name='R_foot_in_LOC')
        self.r_foot_out_loc = cmds.spaceLocator(name='R_foot_out_LOC')

        cmds.xform(self.l_tip_loc, t=(0, 0, 1))
        cmds.xform(self.l_heel_loc, t=(0, 0, -1))
        cmds.xform(self.l_ball_loc, t=(0, 0, 0))
        cmds.xform(self.l_foot_in_loc, t=(-1, 0, 0))
        cmds.xform(self.l_foot_out_loc, t=(1, 0, 0))

    def aim_matrix(self, obj, aim_at, up_vector=(0, 1, 0), reverse=False):
        obj_pos = om.MVector(cmds.xform(obj, t=True, ws=True, q=True))
        aim_pos = om.MVector(cmds.xform(aim_at, t=True, ws=True, q=True))
        rev = 1
        if reverse:
            rev = -1
        aim_vec = (obj_pos - aim_pos).normal() * rev
        side_vec = aim_vec ^ om.MVector(up_vector)
        up_vec = (aim_vec ^ side_vec)

        mtx = math.create_matrix(side_vec * -1, up_vec * -1, aim_vec, obj_pos)

        return mtx

    def mirror_locs(self):
        tip_pos = cmds.xform(self.l_tip_loc, t=True, ws=True, q=True)
        heel_pos = cmds.xform(self.l_heel_loc, t=True, ws=True, q=True)
        ball_pos = cmds.xform(self.l_ball_loc, t=True, ws=True, q=True)
        foot_pos = cmds.xform(self.l_foot_loc, t=True, ws=True, q=True)
        foot_in_pos = cmds.xform(self.l_foot_in_loc, t=True, ws=True, q=True)
        foot_out_pos = cmds.xform(self.l_foot_out_loc, t=True, ws=True, q=True)

        cmds.xform(self.r_tip_loc, t=(tip_pos[0] * -1, tip_pos[1], tip_pos[2]))
        cmds.xform(self.r_heel_loc, t=(heel_pos[0] * -1, heel_pos[1], heel_pos[2]))
        cmds.xform(self.r_ball_loc, t=(ball_pos[0] * -1, ball_pos[1], ball_pos[2]))
        cmds.xform(self.r_foot_loc, t=(foot_pos[0] * -1, foot_pos[1], foot_pos[2]))
        cmds.xform(self.r_foot_in_loc, t=(foot_in_pos[0] * -1, foot_in_pos[1], foot_in_pos[2]))
        cmds.xform(self.r_foot_out_loc, t=(foot_out_pos[0] * -1, foot_out_pos[1], foot_out_pos[2]))

    def zero(self, dag, suffix='ZERO'):
        zero = cmds.createNode('transform', name=dag + '_' + suffix)
        ofs = cmds.createNode('transform', name=dag + '_' + 'OFS')
        cmds.parent(ofs, zero)

        pos = cmds.xform(dag, t=True, ws=True, q=True)
        rot = cmds.xform(dag, ro=True, ws=True, q=True)

        cmds.xform(zero, t=pos, ws=True)
        cmds.xform(zero, ro=rot, ws=True)

        cmds.parent(dag, ofs)

        return zero

    def build(self):
        self.mirror_locs()

        for side in ['L', 'R']:
            main_ctrl = self.main_ctrl.split('_', 1)[1]
            main_ctrl = side + '_' + main_ctrl

            if side == 'L':
                tip_loc = self.l_tip_loc
                heel_loc = self.l_heel_loc
                ball_loc = self.l_ball_loc
                foot_loc = self.l_foot_loc
                foot_in_loc = self.l_foot_in_loc
                foot_out_loc = self.l_foot_out_loc
            else:
                tip_loc = self.r_tip_loc
                heel_loc = self.r_heel_loc
                ball_loc = self.r_ball_loc
                foot_loc = self.r_foot_loc
                foot_in_loc = self.r_foot_in_loc
                foot_out_loc = self.r_foot_out_loc

            attribute.add_headline(main_ctrl, 'FOOT')
            attribute.add_generic_blend(main_ctrl, 'ballRoll', min_value=-180, max_value=180, default=0.0)
            attribute.add_generic_blend(main_ctrl, 'footRollForward', min_value=-180, max_value=180, default=0.0)
            attribute.add_generic_blend(main_ctrl, 'footRollSide', min_value=-180, max_value=180, default=0.0)
            attribute.add_generic_blend(main_ctrl, 'toeRotate', min_value=-180, max_value=180, default=0.0)

            namer = Name(name='foot', side=side)

            # create pivots and position them
            tip_pivot = cmds.createNode('transform', name=namer.replace(add_to_tags='tip_pivot',
                                                                        suffix='transform'))
            tip_pivot_ctrl = shape.create_nurbscurve('locator', name=namer.replace(add_to_tags='tip_pivot',
                                                                                   suffix='control'))
            tip_pivot_ctrl = cmds.listRelatives(tip_pivot_ctrl, p=True)[0]

            heel_pivot = cmds.createNode('transform', name=namer.replace(add_to_tags='heel_pivot',
                                                                         suffix='transform'))
            heel_pivot_ctrl = shape.create_nurbscurve('locator', name=namer.replace(add_to_tags='heel_pivot',
                                                                                    suffix='control'))
            heel_pivot_ctrl = cmds.listRelatives(heel_pivot_ctrl, p=True)[0]

            ball_pivot = cmds.createNode('transform', name=namer.replace(add_to_tags='ball_pivot',
                                                                         suffix='transform'))
            ball_pivot_ctrl = shape.create_nurbscurve('locator', name=namer.replace(add_to_tags='ball_pivot',
                                                                                    suffix='control'))
            ball_pivot_ctrl = cmds.listRelatives(ball_pivot_ctrl, p=True)[0]

            foot_pivot = cmds.spaceLocator(name=namer.replace(add_to_tags='ik',
                                                              suffix='MTX'))[0]
            foot_pivot_ctrl = shape.create_nurbscurve('locator', name=namer.replace(add_to_tags='foot_pivot',
                                                                                    suffix='control'))
            foot_pivot_ctrl = cmds.listRelatives(foot_pivot_ctrl, p=True)[0]

            foot_in_pivot = cmds.createNode('transform', name=namer.replace(add_to_tags='foot_in_pivot',
                                                                            suffix='transform'))
            foot_in_pivot_ctrl = shape.create_nurbscurve('locator', name=namer.replace(add_to_tags='foot_in_pivot',
                                                                                       suffix='control'))
            foot_in_pivot_ctrl = cmds.listRelatives(foot_in_pivot_ctrl, p=True)[0]

            foot_out_pivot = cmds.createNode('transform', name=namer.replace(add_to_tags='foot_out_pivot',
                                                                             suffix='transform'))
            foot_out_pivot_ctrl = shape.create_nurbscurve('locator', name=namer.replace(add_to_tags='foot_out_pivot',
                                                                                        suffix='control'))
            foot_out_pivot_ctrl = cmds.listRelatives(foot_out_pivot_ctrl, p=True)[0]

            toe_pivot = cmds.createNode('transform', name=namer.replace(add_to_tags='toe_pivot',
                                                                        suffix='transform'))
            toe_pivot_ctrl = shape.create_nurbscurve('locator', name=namer.replace(add_to_tags='toe_pivot',
                                                                                   suffix='control'))
            toe_pivot_ctrl = cmds.listRelatives(toe_pivot_ctrl, p=True)[0]

            ctrls = [tip_pivot_ctrl, heel_pivot_ctrl, ball_pivot_ctrl, foot_pivot_ctrl, foot_in_pivot_ctrl, foot_out_pivot_ctrl, toe_pivot_ctrl]
            pivots = [tip_pivot, heel_pivot, ball_pivot, foot_pivot, foot_in_pivot, foot_out_pivot, toe_pivot]

            tip_mtx = self.aim_matrix(tip_loc, heel_loc)
            cmds.xform(tip_pivot_ctrl, matrix=tip_mtx)

            heel_mtx = self.aim_matrix(heel_loc, tip_loc, reverse=True)
            cmds.xform(heel_pivot_ctrl, matrix=heel_mtx)

            pos = cmds.xform(ball_loc, t=True, ws=True, q=True)
            cmds.xform(ball_pivot_ctrl, matrix=heel_mtx)
            cmds.xform(ball_pivot_ctrl, t=pos)
            cmds.xform(toe_pivot_ctrl, matrix=heel_mtx)
            cmds.xform(toe_pivot_ctrl, t=pos)

            pos = cmds.xform(foot_loc, t=True, ws=True, q=True)
            cmds.xform(foot_pivot_ctrl, matrix=heel_mtx)
            cmds.xform(foot_pivot_ctrl, t=pos)

            pos = cmds.xform(foot_in_loc, t=True, ws=True, q=True)
            cmds.xform(foot_in_pivot_ctrl, matrix=heel_mtx)
            cmds.xform(foot_in_pivot_ctrl, t=pos)

            pos = cmds.xform(foot_out_loc, t=True, ws=True, q=True)
            cmds.xform(foot_out_pivot_ctrl, matrix=heel_mtx)
            cmds.xform(foot_out_pivot_ctrl, t=pos)

            tip_ctrl_zero = self.zero(tip_pivot_ctrl)
            heel_ctrl_zero = self.zero(heel_pivot_ctrl)
            ball_ctrl_zero = self.zero(ball_pivot_ctrl)
            foot_ctrl_zero = self.zero(foot_pivot_ctrl)
            foot_in_ctrl_zero = self.zero(foot_in_pivot_ctrl)
            foot_out_ctrl_zero = self.zero(foot_out_pivot_ctrl)
            toe_ctrl_zero = self.zero(toe_pivot_ctrl)

            tip_zero = self.zero(tip_pivot)
            heel_zero = self.zero(heel_pivot)
            ball_zero = self.zero(ball_pivot)
            foot_zero = self.zero(foot_pivot)
            foot_in_zero = self.zero(foot_in_pivot)
            foot_out_zero = self.zero(foot_out_pivot)
            toe_zero = self.zero(toe_pivot)
            pivot_zeros = [tip_zero, heel_zero, ball_zero, foot_zero, foot_in_zero, foot_out_zero, toe_zero]

            cmds.parent(tip_zero, tip_pivot_ctrl)
            cmds.parent(heel_zero, heel_pivot_ctrl)
            cmds.parent(ball_zero, ball_pivot_ctrl)
            cmds.parent(foot_zero, foot_pivot_ctrl)
            cmds.parent(foot_in_zero, foot_in_pivot_ctrl)
            cmds.parent(foot_out_zero, foot_out_pivot_ctrl)
            cmds.parent(toe_zero, toe_pivot_ctrl)
            for zero in pivot_zeros:
                cmds.setAttr(zero + '.translate', 0, 0, 0)
                cmds.setAttr(zero + '.rotate', 0, 0, 0)

            cmds.parent(foot_ctrl_zero, ball_pivot)
            cmds.parent(ball_ctrl_zero, foot_in_pivot)
            cmds.parent(toe_ctrl_zero, foot_in_pivot)
            cmds.parent(foot_in_ctrl_zero, foot_out_pivot)
            cmds.parent(foot_out_ctrl_zero, heel_pivot)
            cmds.parent(heel_ctrl_zero, tip_pivot)

            for i, ctrl in enumerate(ctrls):
                pivot = pivots[i] + '_OFS'
                self.reverse(ctrl + '.translate', pivot + '.translate')

            # attach attributes on control to pivots
            tip_cond = cmds.createNode('condition', name=namer.replace(add_to_tags='tip',
                                                                       suffix='condition'))
            heel_cond = cmds.createNode('condition', name=namer.replace(add_to_tags='heel',
                                                                        suffix='condition'))
            foot_in_cond = cmds.createNode('condition', name=namer.replace(add_to_tags='foot_in',
                                                                           suffix='condition'))
            foot_out_cond = cmds.createNode('condition', name=namer.replace(add_to_tags='foot_out',
                                                                            suffix='condition'))

            # reverse for rotation for if it is the right side
            if side == 'R':
                foot_side_mult = cmds.createNode('math_Multiply', name=namer.replace(add_to_tags='foot_in_pivot',
                                                                                     suffix='math_Multiply'))
                cmds.connectAttr(main_ctrl + '.footRollSide', foot_side_mult + '.input1')
                cmds.setAttr(foot_side_mult + '.input2', -1)

                foot_side_attr = foot_side_mult + '.output'
                foot_in_operation = 4
                foot_out_operation = 2
            else:
                foot_side_attr = main_ctrl + '.footRollSide'
                foot_in_operation = 2
                foot_out_operation = 4

            cmds.connectAttr(main_ctrl + '.footRollForward', tip_cond + '.colorIfTrueR')
            cmds.connectAttr(main_ctrl + '.footRollForward', tip_cond + '.firstTerm')
            cmds.setAttr(tip_cond + '.operation', 2)
            cmds.setAttr(tip_cond + '.colorIfFalseR', 0)
            cmds.connectAttr(tip_cond + '.outColorR', tip_zero + '.rx')

            cmds.connectAttr(main_ctrl + '.footRollForward', heel_cond + '.colorIfTrueR')
            cmds.connectAttr(main_ctrl + '.footRollForward', heel_cond + '.firstTerm')
            cmds.setAttr(heel_cond + '.operation', 4)
            cmds.setAttr(heel_cond + '.colorIfFalseR', 0)
            cmds.connectAttr(heel_cond + '.outColorR', heel_zero + '.rx')

            cmds.connectAttr(foot_side_attr, foot_in_cond + '.colorIfTrueR')
            cmds.connectAttr(foot_side_attr, foot_in_cond + '.firstTerm')
            cmds.setAttr(foot_in_cond + '.operation', foot_in_operation)
            cmds.setAttr(foot_in_cond + '.colorIfFalseR', 0)
            cmds.connectAttr(foot_in_cond + '.outColorR', foot_in_zero + '.rz')

            cmds.connectAttr(foot_side_attr, foot_out_cond + '.colorIfTrueR')
            cmds.connectAttr(foot_side_attr, foot_out_cond + '.firstTerm')
            cmds.setAttr(foot_out_cond + '.operation', foot_out_operation)
            cmds.setAttr(foot_out_cond + '.colorIfFalseR', 0)
            cmds.connectAttr(foot_out_cond + '.outColorR', foot_out_zero + '.rz')

            cmds.connectAttr(main_ctrl + '.ballRoll', ball_zero + '.rx')
            cmds.connectAttr(main_ctrl + '.toeRotate', toe_zero + '.rx')

            for ctrl in ctrls:
                for attr in ['.rx', '.ry', '.rz', '.sx', '.sy', '.sz']:
                    cmds.setAttr(ctrl + attr,
                                 lock=True,
                                 channelBox=False,
                                 keyable=False)
                cmds.setAttr(ctrl + '.v', 0, channelBox=False, keyable=False)

            piv_vis = [tip_pivot_ctrl, heel_pivot_ctrl, foot_in_pivot_ctrl, foot_out_pivot_ctrl]
            attribute.add_visibility_attr(main_ctrl, 'pivots', items=piv_vis, default=0)

    @staticmethod
    def reverse(source, destination):
        """Multiplies the given source attribute by -1

        Args:
            source (str): source attribute
            destination (str): destination attribute
        Returns:
            str: multiply node
        """

        node_name = source.split('.')[0] + '_MLT'
        mult = cmds.createNode('math_MultiplyVector', name=node_name)

        cmds.connectAttr(source, mult + '.input1')
        cmds.setAttr(mult + '.input2', -1)

        cmds.connectAttr(mult + '.output', destination)

        return mult
