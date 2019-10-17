import os

from collections import OrderedDict

import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.mel as mel

from rigging_utils import constraint
from rigging_utils import joint
from rigging_utils import skin

import millRig.ui.Window as window
import millRig.ui.graph.GraphView as gw
import millRig.core.parameters as parameters

cmds.loadPlugin("millDeformerUtils", qt=True)


class apply_millrig():

    def __init__(self):
        self.simple_constraints = []
        self.new_controls = []
        self._window = None
        self.top_grp = 'untitled'

        self.bones = OrderedDict()
        self.bones['hip'] = 'Hips'
        self.bones['spine'] = 'Spine'
        self.bones['spine_02'] = 'Spine2'
        self.bones['spine_01'] = 'Spine1'
        self.bones['neck'] = 'Neck'
        self.bones['head'] = 'Head'
        self.bones['r_eye'] = 'RightEye'
        self.bones['l_eye'] = 'LeftEye'
        self.bones['jaw'] = 'Jaw'
        self.bones['r_clav'] = 'RightShoulder'
        self.bones['r_shoulder'] = 'RightArm'
        self.bones['r_elbow'] = 'RightForeArm'
        self.bones['r_hand'] = 'RightHand'
        self.bones['r_thumb_01'] = 'RightHandThumb1'
        self.bones['r_thumb_02'] = 'RightHandThumb2'
        self.bones['r_thumb_03'] = 'RightHandThumb3'
        self.bones['r_thumb_04'] = 'RightHandThumb4'
        self.bones['r_fingerA_01'] = 'RightHandIndex1'
        self.bones['r_fingerA_02'] = 'RightHandIndex2'
        self.bones['r_fingerA_03'] = 'RightHandIndex3'
        self.bones['r_fingerA_04'] = 'RightHandIndex4'
        self.bones['r_fingerB_01'] = 'RightHandMiddle1'
        self.bones['r_fingerB_02'] = 'RightHandMiddle2'
        self.bones['r_fingerB_03'] = 'RightHandMiddle3'
        self.bones['r_fingerB_04'] = 'RightHandMiddle4'
        self.bones['r_fingerC_01'] = 'RightHandRing1'
        self.bones['r_fingerC_02'] = 'RightHandRing2'
        self.bones['r_fingerC_03'] = 'RightHandRing3'
        self.bones['r_fingerC_04'] = 'RightHandRing4'
        self.bones['r_fingerD_01'] = 'RightHandPinky1'
        self.bones['r_fingerD_02'] = 'RightHandPinky2'
        self.bones['r_fingerD_03'] = 'RightHandPinky3'
        self.bones['r_fingerD_04'] = 'RightHandPinky4'
        self.bones['l_clav'] = 'LeftShoulder'
        self.bones['l_shoulder'] = 'LeftArm'
        self.bones['l_elbow'] = 'LeftForeArm'
        self.bones['l_hand'] = 'LeftHand'
        self.bones['l_thumb_01'] = 'LeftHandThumb1'
        self.bones['l_thumb_02'] = 'LeftHandThumb2'
        self.bones['l_thumb_03'] = 'LeftHandThumb3'
        self.bones['l_thumb_04'] = 'LeftHandThumb4'
        self.bones['l_fingerA_01'] = 'LeftHandIndex1'
        self.bones['l_fingerA_02'] = 'LeftHandIndex2'
        self.bones['l_fingerA_03'] = 'LeftHandIndex3'
        self.bones['l_fingerA_04'] = 'LeftHandIndex4'
        self.bones['l_fingerB_01'] = 'LeftHandMiddle1'
        self.bones['l_fingerB_02'] = 'LeftHandMiddle2'
        self.bones['l_fingerB_03'] = 'LeftHandMiddle3'
        self.bones['l_fingerB_04'] = 'LeftHandMiddle4'
        self.bones['l_fingerC_01'] = 'LeftHandRing1'
        self.bones['l_fingerC_02'] = 'LeftHandRing2'
        self.bones['l_fingerC_03'] = 'LeftHandRing3'
        self.bones['l_fingerC_04'] = 'LeftHandRing4'
        self.bones['l_fingerD_01'] = 'LeftHandPinky1'
        self.bones['l_fingerD_02'] = 'LeftHandPinky2'
        self.bones['l_fingerD_03'] = 'LeftHandPinky3'
        self.bones['l_fingerD_04'] = 'LeftHandPinky4'
        self.bones['r_thigh'] = 'RightUpLeg'
        self.bones['r_knee'] = 'RightLeg'
        self.bones['r_foot'] = 'RightFoot'
        self.bones['r_toe'] = 'RightToeBase'
        self.bones['r_toe_end'] = 'RightToeEnd'
        self.bones['l_thigh'] = 'LeftUpLeg'
        self.bones['l_knee'] = 'LeftLeg'
        self.bones['l_foot'] = 'LeftFoot'
        self.bones['l_toe'] = 'LeftToeBase'
        self.bones['l_toe_end'] = 'LeftToeEnd'

        self.face_bones = ['Nostrils',
                           'LipUpperR',
                           'LipUpperL',
                           'LipCornerR',
                           'LipCornerL',
                           'BrowInnerR',
                           'BrowInnerL',
                           'BrowOuterR',
                           'BrowOuterL',
                           'UpperLidR',
                           'UpperLidL',
                           'LowerLidR',
                           'LowerLidL',
                           'CheekR',
                           'CheekL']

        self.millRig_handles = {'hip': ['C_torso_hip_LYT_HANDLE', 'C_torso_body_LYT_HANDLE'],
                                'spine': ['C_torso_spine_01_LYT_HANDLE'],
                                'spine_01': ['C_torso_spine_02_LYT_HANDLE'],
                                'spine_02': ['C_torso_chest_LYT_HANDLE'],
                                'neck': ['C_head_neck_root_LYT_HANDLE'],
                                'head': ['C_head_head_LYT_HANDLE'],
                                'r_eye': ['C_head_eyes_R_LYT_HANDLE'],
                                'l_eye': ['C_head_eyes_L_LYT_HANDLE'],
                                'jaw': ['C_head_jaw_start_LYT_HANDLE'],
                                'r_clav': ['R_shoulder_shoulder_root_LYT_HANDLE'],
                                'r_shoulder': ['R_arm_upper_LYT_HANDLE'],
                                'r_elbow': ['R_arm_lower_LYT_HANDLE'],
                                'r_hand': ['R_arm_hand_LYT_HANDLE'],
                                'r_thumb_01': ['R_thumb_digit_digit_01_LYT_HANDLE'],
                                'r_thumb_02': ['R_thumb_digit_digit_02_LYT_HANDLE'],
                                'r_thumb_03': ['R_thumb_digit_digit_03_LYT_HANDLE'],
                                'r_thumb_04': ['R_thumb_digit_digit_END_LYT_HANDLE'],
                                'r_fingerA_01': ['R_fingerA_digit_digit_01_LYT_HANDLE'],
                                'r_fingerA_02': ['R_fingerA_digit_digit_02_LYT_HANDLE'],
                                'r_fingerA_03': ['R_fingerA_digit_digit_03_LYT_HANDLE'],
                                'r_fingerA_04': ['R_fingerA_digit_digit_END_LYT_HANDLE'],
                                'r_fingerB_01': ['R_fingerB_digit_digit_01_LYT_HANDLE'],
                                'r_fingerB_02': ['R_fingerB_digit_digit_02_LYT_HANDLE'],
                                'r_fingerB_03': ['R_fingerB_digit_digit_03_LYT_HANDLE'],
                                'r_fingerB_04': ['R_fingerB_digit_digit_END_LYT_HANDLE'],
                                'r_fingerC_01': ['R_fingerC_digit_digit_01_LYT_HANDLE'],
                                'r_fingerC_02': ['R_fingerC_digit_digit_02_LYT_HANDLE'],
                                'r_fingerC_03': ['R_fingerC_digit_digit_03_LYT_HANDLE'],
                                'r_fingerC_04': ['R_fingerC_digit_digit_END_LYT_HANDLE'],
                                'r_fingerD_01': ['R_fingerD_digit_digit_01_LYT_HANDLE'],
                                'r_fingerD_02': ['R_fingerD_digit_digit_02_LYT_HANDLE'],
                                'r_fingerD_03': ['R_fingerD_digit_digit_03_LYT_HANDLE'],
                                'r_fingerD_04': ['R_fingerD_digit_digit_END_LYT_HANDLE'],
                                'l_clav': ['L_shoulder_shoulder_root_LYT_HANDLE'],
                                'l_shoulder': ['L_arm_upper_LYT_HANDLE'],
                                'l_elbow': ['L_arm_lower_LYT_HANDLE'],
                                'l_hand': ['L_arm_hand_LYT_HANDLE'],
                                'l_thumb_01': ['L_thumb_digit_digit_01_LYT_HANDLE'],
                                'l_thumb_02': ['L_thumb_digit_digit_02_LYT_HANDLE'],
                                'l_thumb_03': ['L_thumb_digit_digit_03_LYT_HANDLE'],
                                'l_thumb_04': ['L_thumb_digit_digit_END_LYT_HANDLE'],
                                'l_fingerA_01': ['L_fingerA_digit_digit_01_LYT_HANDLE'],
                                'l_fingerA_02': ['L_fingerA_digit_digit_02_LYT_HANDLE'],
                                'l_fingerA_03': ['L_fingerA_digit_digit_03_LYT_HANDLE'],
                                'l_fingerA_04': ['L_fingerA_digit_digit_END_LYT_HANDLE'],
                                'l_fingerB_01': ['L_fingerB_digit_digit_01_LYT_HANDLE'],
                                'l_fingerB_02': ['L_fingerB_digit_digit_02_LYT_HANDLE'],
                                'l_fingerB_03': ['L_fingerB_digit_digit_03_LYT_HANDLE'],
                                'l_fingerB_04': ['L_fingerB_digit_digit_END_LYT_HANDLE'],
                                'l_fingerC_01': ['L_fingerC_digit_digit_01_LYT_HANDLE'],
                                'l_fingerC_02': ['L_fingerC_digit_digit_02_LYT_HANDLE'],
                                'l_fingerC_03': ['L_fingerC_digit_digit_03_LYT_HANDLE'],
                                'l_fingerC_04': ['L_fingerC_digit_digit_END_LYT_HANDLE'],
                                'l_fingerD_01': ['L_fingerD_digit_digit_01_LYT_HANDLE'],
                                'l_fingerD_02': ['L_fingerD_digit_digit_02_LYT_HANDLE'],
                                'l_fingerD_03': ['L_fingerD_digit_digit_03_LYT_HANDLE'],
                                'l_fingerD_04': ['L_fingerD_digit_digit_END_LYT_HANDLE'],
                                'r_thigh': ['R_leg_upper_LYT_HANDLE'],
                                'r_knee': ['R_leg_lower_LYT_HANDLE'],
                                'r_foot': ['R_leg_foot_LYT_HANDLE'],
                                'r_toe': ['R_leg_ball_LYT_HANDLE'],
                                'r_toe_end': ['R_leg_toe_end_LYT_HANDLE'],
                                'l_thigh': ['L_leg_upper_LYT_HANDLE'],
                                'l_knee': ['L_leg_lower_LYT_HANDLE'],
                                'l_foot': ['L_leg_foot_LYT_HANDLE'],
                                'l_toe': ['L_leg_ball_LYT_HANDLE'],
                                'l_toe_end': ['L_leg_toe_end_LYT_HANDLE']}

        self.millRig_build = {'hip': ['C_pelvis_BONE'],
                              'spine': ['C_spine_02_BONE'],
                              'spine_01': ['C_spine_04_BONE'],
                              'spine_02': ['C_chest_BONE'],
                              'neck': ['C_neck_02_CTRL'],
                              'head': ['C_head_CTRL'],
                              'r_eye': ['R_eye_BONE'],
                              'l_eye': ['L_eye_BONE'],
                              'jaw': ['C_jaw_01_BONE'],
                              'r_clav': ['R_shoulder_BONE'],
                              'r_shoulder': ['R_arm_01_upper_BONE'],
                              'r_elbow': ['R_arm_01_lower_BONE'],
                              'r_hand': ['R_hand_BONE'],
                              'r_thumb_01': ['R_thumb_01_CTRL'],
                              'r_thumb_02': ['R_thumb_02_CTRL'],
                              'r_thumb_03': ['R_thumb_03_CTRL'],
                              'r_thumb_04': [''],
                              'r_fingerA_01': ['R_fingerA_01_BONE'],
                              'r_fingerA_02': ['R_fingerA_02_BONE'],
                              'r_fingerA_03': ['R_fingerA_03_BONE'],
                              'r_fingerA_04': [''],
                              'r_fingerB_01': ['R_fingerB_01_BONE'],
                              'r_fingerB_02': ['R_fingerB_02_BONE'],
                              'r_fingerB_03': ['R_fingerB_03_BONE'],
                              'r_fingerB_04': [''],
                              'r_fingerC_01': ['R_fingerC_01_BONE'],
                              'r_fingerC_02': ['R_fingerC_02_BONE'],
                              'r_fingerC_03': ['R_fingerC_03_BONE'],
                              'r_fingerC_04': [''],
                              'r_fingerD_01': ['R_fingerD_01_BONE'],
                              'r_fingerD_02': ['R_fingerD_02_BONE'],
                              'r_fingerD_03': ['R_fingerD_03_BONE'],
                              'r_fingerD_04': [''],
                              'l_clav': ['L_shoulder_BONE'],
                              'l_shoulder': ['L_arm_01_upper_BONE'],
                              'l_elbow': ['L_arm_01_lower_BONE'],
                              'l_hand': ['L_hand_BONE'],
                              'l_thumb_01': ['L_thumb_01_CTRL'],
                              'l_thumb_02': ['L_thumb_02_CTRL'],
                              'l_thumb_03': ['L_thumb_03_CTRL'],
                              'l_thumb_04': [''],
                              'l_fingerA_01': ['L_fingerA_01_BONE'],
                              'l_fingerA_02': ['L_fingerA_02_BONE'],
                              'l_fingerA_03': ['L_fingerA_03_BONE'],
                              'l_fingerA_04': [''],
                              'l_fingerB_01': ['L_fingerB_01_BONE'],
                              'l_fingerB_02': ['L_fingerB_02_BONE'],
                              'l_fingerB_03': ['L_fingerB_03_BONE'],
                              'l_fingerB_04': [''],
                              'l_fingerC_01': ['L_fingerC_01_BONE'],
                              'l_fingerC_02': ['L_fingerC_02_BONE'],
                              'l_fingerC_03': ['L_fingerC_03_BONE'],
                              'l_fingerC_04': [''],
                              'l_fingerD_01': ['L_fingerD_01_BONE'],
                              'l_fingerD_02': ['L_fingerD_02_BONE'],
                              'l_fingerD_03': ['L_fingerD_03_BONE'],
                              'l_fingerD_04': [''],
                              'r_thigh': ['R_leg_01_upper_BONE'],
                              'r_knee': ['R_leg_01_lower_BONE'],
                              'r_foot': ['R_foot_BONE'],
                              'r_toe': ['R_toes_BONE'],
                              'r_toe_end': [''],
                              'l_thigh': ['L_leg_01_upper_BONE'],
                              'l_knee': ['L_leg_01_lower_BONE'],
                              'l_foot': ['L_foot_BONE'],
                              'l_toe': ['L_toes_BONE'],
                              'l_toe_end': ['']}

    def point_to_plane(self, pointA, pointB, pointC, project_point):
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

    def clean_orientation(self):
        # set rotate axis and joint orient of all joints to 0
        old_pos = {}
        for key, value in self.bones.items():
            bone_check = cmds.ls(value)
            if bone_check:
                old_pos[key] = cmds.xform(value, t=True, ws=True, q=True)
        for key, value in self.bones.items():
            bone_check = cmds.ls(value)
            if bone_check:
                cmds.setAttr(value + '.rotateAxisX', 0)
                cmds.setAttr(value + '.rotateAxisY', 0)
                cmds.setAttr(value + '.rotateAxisZ', 0)

                joint.orientation_to_rotation([value])

        for key, value in self.bones.items():
            bone_check = cmds.ls(value)
            if bone_check:
                pos = old_pos[key]
                cmds.xform(self.bones[key], t=pos, ws=True)

    def flatten_ik_planes(self):
        l_shoulder_pos = cmds.xform(self.bones['l_shoulder'], t=True, ws=True, q=True)
        l_elbow_pos = cmds.xform(self.bones['l_elbow'], t=True, ws=True, q=True)
        l_hand_pos = cmds.xform(self.bones['l_hand'], t=True, ws=True, q=True)
        l_thigh_pos = cmds.xform(self.bones['l_thigh'], t=True, ws=True, q=True)
        l_knee_pos = cmds.xform(self.bones['l_knee'], t=True, ws=True, q=True)
        l_foot_pos = cmds.xform(self.bones['l_foot'], t=True, ws=True, q=True)
        r_shoulder_pos = cmds.xform(self.bones['r_shoulder'], t=True, ws=True, q=True)
        r_elbow_pos = cmds.xform(self.bones['r_elbow'], t=True, ws=True, q=True)
        r_hand_pos = cmds.xform(self.bones['r_hand'], t=True, ws=True, q=True)
        r_thigh_pos = cmds.xform(self.bones['r_thigh'], t=True, ws=True, q=True)
        r_knee_pos = cmds.xform(self.bones['r_knee'], t=True, ws=True, q=True)
        r_foot_pos = cmds.xform(self.bones['r_foot'], t=True, ws=True, q=True)

        # get new positions of middle bones
        z_vec = (l_shoulder_pos[0], l_shoulder_pos[1], l_shoulder_pos[2] - 1)
        new_l_elbow = self.point_to_plane(z_vec, l_shoulder_pos, l_hand_pos, l_elbow_pos)

        z_vec = (l_thigh_pos[0], l_thigh_pos[1], l_thigh_pos[2] - 1)
        new_l_knee = self.point_to_plane(z_vec, l_thigh_pos, l_foot_pos, l_knee_pos)

        z_vec = (r_shoulder_pos[0], r_shoulder_pos[1], r_shoulder_pos[2] - 1)
        new_r_elbow = self.point_to_plane(z_vec, r_shoulder_pos, r_hand_pos, r_elbow_pos)

        z_vec = (r_thigh_pos[0], r_thigh_pos[1], r_thigh_pos[2] - 1)
        new_r_knee = self.point_to_plane(z_vec, r_thigh_pos, r_foot_pos, r_knee_pos)

        # move bones into new positions
        cmds.xform(self.bones['l_elbow'], t=new_l_elbow, ws=True)
        cmds.xform(self.bones['l_hand'], t=l_hand_pos, ws=True)

        cmds.xform(self.bones['l_knee'], t=new_l_knee, ws=True)
        cmds.xform(self.bones['l_foot'], t=l_foot_pos, ws=True)

        cmds.xform(self.bones['r_elbow'], t=new_r_elbow, ws=True)
        cmds.xform(self.bones['r_hand'], t=r_hand_pos, ws=True)

        cmds.xform(self.bones['r_knee'], t=new_r_knee, ws=True)
        cmds.xform(self.bones['r_foot'], t=r_foot_pos, ws=True)

    def reset_skincluster(self, geo):
        # get skincluster from geo and reset it
        skc = skin.get_skincluster(geo)
        infs = skin.get_influences(skc)
        projectDirectory = cmds.workspace(q=True, rd=True) + 'data'

        mel.eval('weightsIO -f "{}/test_01.wts" -s {};'.format(projectDirectory, skc))
        cmds.skinCluster(geo, ub=True, e=True)
        cmds.skinCluster(infs, geo, name=skc)
        cmds.select(geo)
        mel.eval('weightsIO -f "{}/test_01.wts" -l;'.format(projectDirectory))
        cmds.sysFile('{}/temp_weights.wts'.format(projectDirectory), delete=True)

    def scale_rig(self, dag):
        # set top group to scale .1 to match scale of mill rig
        current = dag
        parent = 'temp'

        while parent:
            parent = cmds.listRelatives(current, p=True)
            current = parent
            if parent:
                self.top_grp = parent[0]
        cmds.setAttr(self.top_grp + '.s', .1, .1, .1)

    def initialize_millrig(self):
        if self._window is not None:
            self._window.close()
        self._window = window.MillRigWindow()
        self._window.show()

        root = os.getenv('TDSVN_ROOT')
        filename = root + '/maya/modules/millrigger/scripts/millrigger/modules/LDN/biped/Presets/biped.rig'

        parent = self._window.graphView.getGraphRoot()

        if parent is None:
            if filename.endswith(".rig"):
                rigFile = parameters.RigFile(filename)
                if rigFile.moduleType == "Rig":
                    parent = self._window.rigCore
                else:
                    parent = self._window.addRig()
            else:
                parent = self._window.addRig()

        parent.loadModule(filename, self.top_grp)

        # sets spine bones to 8
        gs = gw.GraphScene(self._window)
        gs.graphNodes['C_torso'].module.moduleBuilder.parameters['num_spine_bones'].set_value(8)

    def move_millrig_to_bones(self):
        # move mill rig locators to the position of the bones
        for key, bone in self.bones.items():
            joint.orientation_to_rotation([bone])
            millrig = self.millRig_handles[key]
            pos = cmds.xform(bone, t=True, ws=True, q=True)
            for each in millrig:
                cmds.xform(each, t=pos, ws=True)
                cmds.setAttr(each + '.rotate', 0, 0, 0)

    def create_control(self, dag, parent, size=1, distance=1):
        for each in dag:
            ctrl, node = cmds.circle(name=each + '_CTRL')
            ctrl_zero = cmds.createNode('transform', name=ctrl + '_ZERO')
            cmds.delete(node)

            pos = cmds.xform(each, t=True, ws=True, q=True)
            cmds.parent(ctrl, ctrl_zero)
            cmds.xform(ctrl_zero, t=pos, ws=True)
            cmds.select(ctrl + '.cv[0:]')
            cmds.scale(0.045 * size, 0.045 * size, 0.045 * size, r=True, ocp=True)
            cmds.move(0, 0, 0.08 * distance, r=True, os=True, wd=True)

            con = constraint.simple_constraint(ctrl, each, snap=False)
            zero_con = constraint.simple_constraint(parent, ctrl_zero, snap=False)
            self.simple_constraints.append(con)
            self.simple_constraints.append(zero_con)
            self.new_controls.append(ctrl)

            cmds.setAttr(ctrl + '.overrideEnabled', 1)
            if pos[0] > 0:
                cmds.setAttr(ctrl + '.overrideColor', 18)
            elif pos[0] < 0:
                cmds.setAttr(ctrl + '.overrideColor', 13)
            else:
                cmds.setAttr(ctrl + '.overrideColor', 17)

    def order_hierarchy(self):
        bone_grp = cmds.rename('Reference', 'bones')
        cmds.parent(bone_grp, 'bone_GRP')
        cmds.parent('geo', 'render')
        for each in self.new_controls:
            zero = cmds.listRelatives(each, p=True)[0]
            cmds.parent(zero, 'control_GRP')

    def build(self, fix_planes=True, face=True):
        if not face:
            self.bones.pop('jaw')

        if not self._window:
            # check to see if a piece of geo is selected
            mesh_check = 'temp'
            geo = cmds.ls(sl=True)
            if geo:
                mesh = cmds.listRelatives(geo[0], c=True)
                if mesh:
                    mesh_check = cmds.nodeType(mesh[0])
            if mesh_check != 'mesh':
                raise ValueError('Select a piece of geo')

            # clean up orientation of bones
            self.clean_orientation()
            face_check = cmds.ls(self.face_bones[0])
            if face_check:
                joint.orientation_to_rotation(self.face_bones)

            if fix_planes:
                self.flatten_ik_planes()

            self.reset_skincluster(cmds.ls(sl=True)[0])

            self.scale_rig(cmds.ls(sl=True)[0])

            self.initialize_millrig()

            self.move_millrig_to_bones()

        # switch rig to live
        self._window.moduleEditor.switchRig()

        # constrain bones to mill rig
        for key, bone in self.bones.items():
            millrig = self.millRig_build[key][0]
            if millrig:
                con = constraint.simple_constraint(millrig, bone, snap=False)
                self.simple_constraints.append(con)

        # check to see if face bones exist
        face_check = cmds.ls(self.face_bones[0])
        if face_check:
            self.create_control(self.face_bones, 'C_head_CTRL')

        self.order_hierarchy()

        # disconnect inverse scale from bones if the connection exists
        for key, bone in self.bones.items():
            conns = cmds.listConnections(bone, destination=True, plugs=True)
            if 'Hips.scale' in conns:
                cmds.disconnectAttr('Hips.scale', bone + '.inverseScale')

        cmds.delete(self.top_grp)


human = apply_millrig()
human.build(face=True)
