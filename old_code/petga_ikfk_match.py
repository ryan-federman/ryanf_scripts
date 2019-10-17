import maya.cmds as cmds
import maya.OpenMaya as om


class create_ik_chain():

    def __init__(self, first, second, third):
        self.first_loc = first
        self.second_loc = second
        self.third_loc = third

    def define_vectors(self):
        self.root_pos = cmds.xform(self.first_loc, q=True, ws=True, t=True)
        self.mid_pos = cmds.xform(self.second_loc, q=True, ws=True, t=True)
        self.end_pos = cmds.xform(self.third_loc, q=True, ws=True, t=True)

        self.root_vec = om.MVector(self.root_pos[0], self.root_pos[1], self.root_pos[2])
        self.mid_vec = om.MVector(self.mid_pos[0], self.mid_pos[1], self.mid_pos[2])
        self.end_vec = om.MVector(self.end_pos[0], self.end_pos[1], self.end_pos[2])

    def pole_vector_ctrl(self, name):
        transform = cmds.createNode('transform', name + '_PV_CTRL')
        shapeList = []
        for x in range(0, 3):
            nurbsCircle = cmds.circle()
            crv = nurbsCircle[0]
            node = nurbsCircle[1]

            cmds.setAttr(node + '.degree', 1)
            cmds.setAttr(node + '.sections', 4)

            if x == 0:
                pass
            if x == 1:
                cmds.setAttr(crv + '.rotateY', 90)
                cmds.makeIdentity(crv, apply=True)
            if x == 2:
                cmds.setAttr(crv + '.rotateX', 90)
                cmds.makeIdentity(crv, apply=True)

            cmds.delete(crv, ch=True)
            shape = cmds.listRelatives(crv, s=True)[0]
            shapeList.append(shape)

        for each in shapeList:
            cmds.parent(each, transform, r=True, s=True)

        return transform

    def createLoc(self, pos):
        loc = cmds.spaceLocator()
        cmds.xform(loc, t=(pos[0], pos[1], pos[2]), ws = True)

        return loc

    def planeNormal(self):
        ''' get normal vector of plane by getting the cross product of two vectors
         that lie along the plane'''

        upper_vec = (self.mid_vec - self.root_vec).normal()
        line_vec =  (self.end_vec - self.mid_vec).normal()

        self.normalVector = (upper_vec ^ line_vec).normal()

        return self.normalVector

    def composeMatrix(self, obj, aim_target, apply_rot):
        obj_pos = cmds.xform(obj, q=True, ws=True, t=True)
        aim_target_pos = cmds.xform(aim_target, q=True, ws=True, t=True)

        obj_vec = om.MVector(obj_pos[0], obj_pos[1], obj_pos[2])
        aim_target_vec = om.MVector(aim_target_pos[0], aim_target_pos[1], aim_target_pos[2])

        # get vector that is being aimed
        x_vec = (aim_target_vec - obj_vec).normal()

        # get up vector/the plane's normal
        y_vec = self.planeNormal()

        # get the cross product of the aim vector and up vector to
        # complete the matrix
        z_vec = (x_vec ^ y_vec).normal()

        # create the matrix
        matrix = []

        # if you want rotation applied add the vectors to the matrix,
        # if not use a standard matrix
        if apply_rot:
            for x in range(0, 4):
                if x != 3:
                    matrix.append(x_vec[x])
                else:
                    matrix.append(0)

            for x in range(0, 4):
                if x != 3:
                    matrix.append(y_vec[x])
                else:
                    matrix.append(0)

            for x in range(0, 4):
                if x != 3:
                    matrix.append(z_vec[x])
                else:
                    matrix.append(0)
        else:
            matrix = [1, 0, 0, 0,
                      0, 1, 0, 0,
                      0, 0, 1, 0,]
        # translation values
        for x in range(0, 4):
            if x != 3:
                matrix.append(obj_pos[x])
            else:
                matrix.append(0)

        return matrix

    def createJoint(self, obj, aim, name, apply_rot):
        cmds.select(clear = True)
        # create joint and position it
        jnt = cmds.joint(name = name + '_BONE')
        srt = cmds.createNode('transform', name = jnt + '_srt')
        cmds.parent(jnt, srt)
        matrix = self.composeMatrix(obj, aim, apply_rot)
        cmds.xform(srt, matrix = matrix)

        return jnt, srt

    def create_chain(self, root_loc, mid_loc, end_loc):
        # create joints
        root = self.createJoint(root_loc, mid_loc, 'shoulder', True)
        root_bone = root[0]

        mid = self.createJoint(mid_loc, end_loc, 'elbow', True)
        mid_bone = mid[0]
        mid_srt = mid[1]

        end = self.createJoint(end_loc, mid_loc, 'wrist', False)
        end_srt = end[1]

        # create chain
        cmds.parent(mid_srt, root_bone)
        cmds.parent(end_srt, mid_bone)
        cmds.xform(end_srt, ro=(0, 0, 0))

    def poleVectorPos(self):

        root_joint_vec = self.root_vec
        mid_joint_vec = self.mid_vec
        end_joint_vec = self.end_vec

        line = (end_joint_vec - root_joint_vec).normal()
        point = (mid_joint_vec - root_joint_vec)

        scale_value = (line * point)
        proj_vec = line * scale_value

        mid_point = root_joint_vec + proj_vec

        short_pole_vec_pos = point - proj_vec

        # find length of arm
        root_to_mid_len = (mid_joint_vec - root_joint_vec).length()
        mid_to_end_len = (end_joint_vec - mid_joint_vec).length()
        total_length = root_to_mid_len + mid_to_end_len

        # normalize the vector between the mid joint and the projected
        # vector or dot product, and multiply it by the length of the chain
        pole_vec_pos = mid_point + (short_pole_vec_pos.normal() * total_length)

        self.pole_loc = self.createLoc(pole_vec_pos)


#start and end of the timeline
start = int(cmds.playbackOptions(query=True, min=True))
end = int(cmds.playbackOptions(query=True, max=True))

for frame in range(start, end + 1):
    for side in ['L', 'R']:
        cmds.currentTime(frame, edit=True)
        arm = create_ik_chain('%s_shoulder_CTRL' % side, '%s_elbow_CTRL' % side, '%s_wrist_CTRL' % side)
        arm.define_vectors()
        arm.poleVectorPos()
        rot = cmds.xform('%s_wrist_CTRL' % side, ro=True, ws=True, query=True)
        pos = arm.end_pos
        cmds.xform('%s_wrist_IK_CTRL' % side, ro=rot, ws=True)
        cmds.xform('%s_wrist_IK_CTRL' % side, t=(pos[0], pos[1], pos[2]), ws=True)
        loc_pos = cmds.xform(arm.pole_loc[0], t=True, ws=True, q=True)
        cmds.xform('%s_arm_PV_CTRL' % side, t=(loc_pos[0], loc_pos[1], loc_pos[2]), ws=True)
        cmds.delete(arm.pole_loc[0])
        cmds.setKeyframe('%s_wrist_IK_CTRL' % side)
        cmds.setKeyframe('%s_arm_PV_CTRL' % side)

        leg = create_ik_chain('%s_hip_JNT' % side, '%s_knee_JNT' % side, '%s_ankle_JNT' % side)
        leg.define_vectors()
        leg.poleVectorPos()
        rot = cmds.xform('%s_ankle_JNT' % side, ro=True, ws=True, query=True)
        pos = leg.end_pos
        cmds.xform('%s_foot_CTRL' % side, ro=rot, ws=True)
        cmds.xform('%s_foot_CTRL' % side, t=(pos[0], pos[1], pos[2]), ws=True)
        loc_pos = cmds.xform(leg.pole_loc[0], t=True, ws=True, q=True)
        cmds.xform('%s_leg_PV_CTRL' % side, t=(loc_pos[0], loc_pos[1], loc_pos[2]), ws=True)
        cmds.delete(leg.pole_loc[0])
        cmds.setKeyframe('%s_foot_CTRL' % side)
        cmds.setKeyframe('%s_leg_PV_CTRL' % side)


