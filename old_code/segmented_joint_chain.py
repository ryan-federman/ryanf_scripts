import maya.cmds as cmds
import maya.api.OpenMaya as om


class joint_chain():
    def __init__(self, rig_name, amt_joints=50):
        self.rig_name = rig_name
        self.step = 0
        self.amt_joints = amt_joints
        self.locs = []
        self.jnts = []
        self.jnt_params = []

    def composeMatrix(self, aim_vec, apply_rot=True):
        obj_vec = om.MVector(0, 0, 0)
        aim_target_vec = om.MVector(aim_vec)

        # get vector that is being aimed
        x_vec = (aim_target_vec).normal()

        # temp up vec to find z vec
        temp_up_vec = om.MVector(0, -1, 0)

        # get the cross product of the aim vector and up vector to
        # complete the matrix
        z_vec = (x_vec ^ temp_up_vec).normal()

        # get up vector/the plane's normal
        y_vec = (x_vec ^ z_vec).normal()

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
                      0, 0, 1, 0, ]
        # translation values
        for x in range(0, 4):
            if x != 3:
                matrix.append(obj_vec[x])
            else:
                matrix.append(0)

        return matrix

    def create_locators(self):
        for x in range(0, 5):
            loc = cmds.spaceLocator(name="proxy_{}_LOC".format(str(x)))
            cmds.xform(loc, t=(0, 0, x * 5), ws=True)
            self.locs.append(loc)

    def create_joints(self):
        cmds.select(clear=True)
        jnts_per_section = self.amt_joints/(len(self.locs) - 1)
        chain_length = 0

        # iterate through each section between the locators
        for x, loc in enumerate(self.locs):
            if loc != self.locs[-1]:
                # define distance between the two locators of the section
                vec1 = om.MVector(cmds.xform(loc, t=True, ws=True, q=True))
                vec2 = om.MVector(cmds.xform(self.locs[x+1], t=True, ws=True, q=True))
                aim_vec = (vec2 - vec1)
                chain_length += aim_vec.length()
                tx = aim_vec.length()/jnts_per_section

                # add the appropriate amount of joints for each section
                for y in range(0, jnts_per_section):
                    jnt = cmds.joint()
                    self.jnts.append(jnt)
                    if y == 0:
                        if x > 0:
                            cmds.parent(jnt, world=True)
                        mtx = self.composeMatrix(aim_vec)
                        cmds.xform(jnt, matrix=mtx)
                        loc_pos = cmds.xform(self.locs[x], t=True, ws=True, q=True)
                        cmds.xform(jnt, t=loc_pos, ws=True)
                        if x > 0:
                            cmds.parent(jnt, self.jnts[-2])
                    else:
                        cmds.xform(jnt, t=(tx, 0, 0))
            else:
                jnt = cmds.joint()
                self.jnts.append(jnt)
                cmds.setAttr(jnt + '.tx', tx)

        # rename all joints accordingly
        new_jnts = []
        for x, each in enumerate(self.jnts):
            if x < 10:
                jnt_name = "{}_0{}_BONE".format(self.rig_name, str(x))
            else:
                jnt_name = "{}_{}_BONE".format(self.rig_name, str(x))
            cmds.rename(each, jnt_name)
            new_jnts.append(jnt_name)

        # remake joint list with the proper names
        self.jnts = []
        for each in new_jnts:
            self.jnts.append(each)

        # find the parameter value for each joint on a potential curve
        param = 0
        for x, each in enumerate(self.jnts):
            if x == 0:
                param = 0.0
            elif each == self.jnts[-1]:
                param = 1.0
            else:
                tx = cmds.getAttr(each + '.tx')
                param += tx/chain_length
            self.jnt_params.append(param)

    def store_locs(self):
        self.locs = cmds.ls(sl=True)

    def store_joints(self):
        self.jnts = cmds.ls(sl=True)

    def reduce_step(self):
        self.step = 0

    def reposition(self):
        cmds.select(clear=True)
        jnts_per_section = self.amt_joints/(len(self.locs) - 1)
        jnt_num = 0
        chain_length = 0
        for x, loc in enumerate(self.locs):
            if loc != self.locs[-1]:
                vec1 = om.MVector(cmds.xform(loc, t=True, ws=True, q=True))
                vec2 = om.MVector(cmds.xform(self.locs[x+1], t=True, ws=True, q=True))
                aim_vec = (vec2 - vec1)
                chain_length += aim_vec.length()
                tx = aim_vec.length()/jnts_per_section
                for y in range(0, jnts_per_section):
                    jnt = self.jnts[jnt_num]
                    if y == 0:
                        if x > 0:
                            cmds.parent(jnt, world=True)
                        mtx = self.composeMatrix(aim_vec)
                        cmds.xform(jnt, matrix=mtx)
                        loc_pos = cmds.xform(self.locs[x], t=True, ws=True, q=True)
                        cmds.xform(jnt, t=loc_pos, ws=True)
                        if x > 0:
                            cmds.parent(jnt, self.jnts[jnt_num - 1])
                        jnt_num += 1
                    else:
                        cmds.xform(jnt, t=(tx, 0, 0))
                        jnt_num += 1
            else:
                jnt = self.jnts[-1]
                cmds.setAttr(jnt + '.tx', tx)

        # find the parameter value for each joint on a potential curve
        param = 0
        self.jnt_params = []
        for x, each in enumerate(self.jnts):
            if x == 0:
                param = 0.0
            elif each == self.jnts[-1]:
                param = 1.0
            else:
                tx = cmds.getAttr(each + '.tx')
                param += tx/chain_length
            self.jnt_params.append(param)

    def build(self):
        if self.step == 0:
            if cmds.ls(sl=True):
                self.locs = cmds.ls(sl=True)
            else:
                self.create_locators()
            self.step += 1
        elif self.step == 1:
            self.create_joints()
