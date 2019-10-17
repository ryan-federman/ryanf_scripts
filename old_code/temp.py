ribbon = ['C_ribbon', 'L01_ribbon', 'L02_ribbon', 'R01_ribbon', 'R02_ribbon']
ribbon_num = ['C', 'L01', 'L02', 'R01', 'R02']
for x, each in enumerate(ribbon):
    attribute.add_headline('C_global_CTRL', each)
    attribute.add_generic_blend('C_global_CTRL', ribbon_num[x] + '_Amplitude', min_value=-5.0, max_value=5.0, default=0.0)
    attribute.add_generic_blend('C_global_CTRL', ribbon_num[x] + '_Wavelength', min_value=0.1, max_value=10, default=1.0)
    attribute.add_generic_blend('C_global_CTRL', ribbon_num[x] + '_WaveOffset', min_value=-10.0, max_value=10, default=1.0)
    attribute.add_generic_blend('C_global_CTRL', ribbon_num[x] + '_PosOffset', min_value=-100.0, max_value=100, default=1.0)


attribute.add_headline('C_global_CTRL', 'RIBBON')
attribute.add_generic_blend('C_global_CTRL', 'widen', max_value=1000.0)
attribute.add_generic_blend('C_global_CTRL', 'thickness', max_value=1000.0)
attribute.add_generic_blend('C_global_CTRL', 'spacing', max_value=1000.0)

# create rig for ribbon
import maya.cmds as cmds
import maya.api.OpenMaya as om

from rigging_utils.create import matrixramp
from rigging_utils import shape
from rigging_utils.create import curves
from rigging_utils import constraint
from rigging_utils import attribute


class ribbon_rig():

    def __init__(self, dag_pos, name, curve, scale=1.0, dag_num=[5, 9, 17, 30], ctrl_type=['box', 'circle', 'circle']):
        self.dag_pos = dag_pos
        self.name = name
        self.dag_num = dag_num
        self.scale = scale
        self.ctrl_type = ctrl_type
        self.motion_path = curve

    def dag_on_vector(self, dag_pos, dag_num, dag_type, name, control_type='box', scale=1.0):
        pos1 = om.MVector(cmds.xform(dag_pos[0], t=True, ws=True, q=True))
        pos2 = om.MVector(cmds.xform(dag_pos[1], t=True, ws=True, q=True))
        aim_vec = pos2 - pos1
        zero_grps = []
        ofs_grps = []
        dags = []
        for x in range(0, dag_num):
            x1 = float(x)
            num_str = str(x)
            if x < 10:
                num_str = '0' + num_str
            pos = ((1.0/float((dag_num-1))) * (aim_vec)) * x1 + pos1
            zero = cmds.createNode('transform', name='C_{}_{}_{}_ZERO'.format(name, num_str, dag_type))
            ofs = cmds.createNode('transform', name='C_{}_{}_{}_OFS'.format(name, num_str, dag_type))
            cmds.select(clear=True)
            if dag_type == 'CTRL':
                dag = shape.create_nurbscurve(control_type)
                dag = cmds.listRelatives(dag, p=True)
                dag = cmds.rename(dag, 'C_{}_{}_CTRL'.format(name, num_str))
            elif dag_type == 'BONE':
                dag = cmds.joint(name='C_{}_{}_BONE'.format(name, num_str))
            zero_grps.append(zero)
            ofs_grps.append(ofs)
            dags.append(dag)

            cmds.parent(ofs, zero)
            cmds.parent(dag, ofs)
            cmds.xform(zero, t=pos, ws=True)

            cmds.select(clear=True)
            if dag_type != 'BONE':
                cmds.setAttr(dag + '.s', scale, scale, scale)
                cmds.makeIdentity(dag, apply=True)
        return [dags, zero_grps, ofs_grps]

    def create_nurbs_plane(self, dag_pos, name, sections=30):
        crvs = []
        pos1 = om.MVector(cmds.xform(dag_pos[0], t=True, ws=True, q=True))
        pos2 = om.MVector(cmds.xform(dag_pos[1], t=True, ws=True, q=True))

        for x in range(2):
            mtx1 = om.MMatrix()
            mtx1.setElement(3, 2, 2)

            mtx2 = om.MMatrix()
            mtx2.setElement(3, 2, -2)

            crv = curves.curve_from_matrices([mtx1, mtx2], degree=1)
            crvs.append(crv)

        cmds.xform(crvs[0], t=pos1, ws=True)
        cmds.xform(crvs[1], t=pos2, ws=True)

        plane = cmds.loft(crvs[0], crvs[1],
                          name=name,
                          ch=True,
                          uniform=True,
                          sectionSpans=sections,
                          range=False,
                          polygon=0,
                          rsn=True)
        # cmds.delete(crvs)

        return plane

    def follicles_on_plane(self, plane, num):
        par_increment = 1.0/float(num-1)
        parameter = 0.0
        foll_list = []
        for x in range(num):
            if x < 10:
                x_str = '0' + str(x)
            else:
                x_str = str(x)

            # create follicle
            plane_geo = cmds.listRelatives(plane, s=True)[0]
            transform = cmds.createNode('transform', name=plane + '_{}_foll'.format(x_str))
            foll = cmds.createNode('follicle', name=plane + '_{}_follShape'.format(x_str), parent=transform)
            cmds.connectAttr(foll + ".outTranslate", transform + ".t", force=True)
            cmds.connectAttr(foll + ".outRotate", transform + ".r", force=True)
            cmds.setAttr(foll + ".visibility", False)
            cmds.connectAttr(plane_geo + '.local', foll + '.inputSurface')
            cmds.connectAttr(plane_geo + '.worldMatrix[0]', foll + '.inputWorldMatrix')
            cmds.setAttr(foll + '.parameterU', 0.5)
            cmds.setAttr(foll + '.parameterV', parameter)

            parameter += par_increment
            foll_list.append(transform)
        return foll_list

    def attach_to_path(self, curve, dag, level):
        sel = om.MSelectionList()
        sel.add(curve)

        crv = om.MFnNurbsCurve()
        crv.setObject(sel.getDependNode(0))

        point = om.MPoint(om.MVector(cmds.xform(dag, t=True, ws=True, q=True)))

        pos = crv.closestPoint(point)[0]

        cmds.xform(dag, t=(pos[0], pos[1], pos[2]), ws=True)

        param = crv.getParamAtPoint(pos)
        PCI = cmds.createNode('pointOnCurveInfo', name=dag + '_PCI')
        ADD = cmds.createNode('math_Add', name=PCI + 'param_ADD')
        CM = cmds.createNode('composeMatrix', name=dag + '_CM')
        MSC = cmds.createNode('millSimpleConstraint', name=dag + '_MSC')
        PBLEND = cmds.createNode('pairBlend', name=dag + '_PBLEND')

        cmds.connectAttr('C_global_CTRL_slide_MULT.output', ADD + '.input1')
        cmds.setAttr(ADD + '.input2', param)

        cmds.connectAttr(curve + '.worldSpace[0]', PCI + '.inputCurve')
        cmds.connectAttr(ADD + '.output', PCI + '.parameter')

        cmds.connectAttr(PCI + '.position', CM + '.inputTranslate')

        cmds.connectAttr(CM + '.outputMatrix', MSC + '.inMatrix')
        cmds.connectAttr(dag + '.parentInverseMatrix', MSC + '.parentInverseMatrix')

        cmds.connectAttr('C_global_CTRL.level' + str(level), PBLEND + '.weight')
        cmds.connectAttr(MSC + '.outTranslate', PBLEND + '.inTranslate2')

        cmds.connectAttr(PBLEND + '.outTranslate', dag + '.translate')

    def build(self):
        # add attributes to global control
        attribute.add_headline('C_global_CTRL', 'SLIDE')
        attribute.add_generic_blend('C_global_CTRL', 'level1')
        attribute.add_generic_blend('C_global_CTRL', 'level2')
        attribute.add_generic_blend('C_global_CTRL', 'level3')
        attribute.add_generic_blend('C_global_CTRL', 'slide',
                                    min_value=0.0,
                                    max_value=100.0,
                                    default=0.0)

        # create node for slide attribute to be re-ranged to 0-1
        mult = cmds.createNode('math_Multiply', name='C_global_CTRL_slide_MULT')
        cmds.connectAttr('C_global_CTRL.slide', mult + '.input1')
        cmds.setAttr(mult + '.input2', .01)

        # nodes to turn on and off slide attributes for each level of controls
        lvl1_mult = cmds.createNode('math_Multiply', name='C_global_CTRL_level1_MULT')
        lvl2_mult = cmds.createNode('math_Multiply', name='C_global_CTRL_level2_MULT')
        lvl3_mult = cmds.createNode('math_Multiply', name='C_global_CTRL_level3_MULT')

        # create all necessary controls and bones
        controls = []
        for x in range(len(self.dag_num)-1):
            scale = (self.scale / float((len(self.dag_num)-1))) * float(len(self.dag_num)-1 - x)
            num_str = str(x)
            if x < 10:
                num_str = '0' + num_str
            ctrls = self.dag_on_vector(self.dag_pos,
                                       self.dag_num[x],
                                       'CTRL',
                                       '{}_{}'.format(self.name, num_str),
                                       scale=scale,
                                       control_type=self.ctrl_type[x])
            controls.append(ctrls)

        bones = self.dag_on_vector(self.dag_pos,
                                   self.dag_num[-1],
                                   'BONE',
                                   self.name,
                                   scale=1.0)

        parts = []
        # create nurbs planes and follicles for controls and bones
        nrbs_bones = []
        ctrl_bones = []
        prev_bones = []
        for x, ctrls in enumerate(controls):
            cmds.select(clear=True)
            # create bones for nurbs plane to be controlled by
            for each in ctrls[0]:
                cmds.select(clear=True)
                bone = cmds.joint(name=each + '_bone')
                zero = cmds.createNode('transform', name=bone + '_ZERO')
                cmds.parent(bone, zero)
                constraint.simple_constraint(each, zero)
                nrbs_bones.append(zero)
                ctrl_bones.append(bone)
                parts.append(zero)
            if x > 0:
                # create plane and follicles
                cmds.select(clear=True)
                pln_sections = len(prev_ctrls) - 1
                foll_sections = len(ctrls[0])
                plane_name = '{}_0{}_PLN'.format(self.name, x)
                plane = self.create_nurbs_plane(self.dag_pos, name=plane_name, sections=pln_sections)
                folls = self.follicles_on_plane(plane[0], foll_sections)

                parts.append(plane[0])
                for each in folls:
                    parts.append(each)

                # constrain the next level of controls to the follicles
                for x, ctrl in enumerate(ctrls[1]):
                    constraint.simple_constraint(folls[x], ctrl)

                bind_objs = []
                for each in prev_bones:
                    bind_objs.append(each)
                bind_objs.append(plane[0])

                # bind plane to control bones
                skc = cmds.skinCluster(bind_objs, name=plane[0] + '_SKC')

            prev_ctrls = ctrls[1]
            prev_bones = ctrl_bones
            ctrl_bones = []

        # constrain bones to plane for last controls
        num = len(controls) + 1
        pln_sections = len(prev_ctrls) - 1
        foll_sections = len(bones[1])
        plane_name = '{}_{}_PLN'.format(self.name, 'BONE')
        plane = self.create_nurbs_plane(self.dag_pos, name=plane_name, sections=pln_sections)
        folls = self.follicles_on_plane(plane[0], foll_sections)

        parts.append(plane[0])
        for each in folls:
            parts.append(each)

        for x, bone in enumerate(bones[1]):
            constraint.simple_constraint(folls[x], bone)

        bind_objs = []
        for each in prev_bones:
            bind_objs.append(each)
        bind_objs.append(plane[0])
        # bind plane to control bones
        skc = cmds.skinCluster(bind_objs, name=plane[0] + '_SKC')

        for each in controls[0][2]:
            self.attach_to_path(self.motion_path, each, 1)
        for each in controls[1][2]:
            self.attach_to_path(self.motion_path, each, 2)
        for each in controls[2][2]:
            self.attach_to_path(self.motion_path, each, 3)

        # organize outliner
        for each in controls:
            print each
            for ctrl in each[1]:
                cmds.parent(ctrl, 'control_GRP')
        for each in bones[1]:
            cmds.parent(each, 'bone_GRP')
        for each in parts:
            cmds.parent(each, 'parts_GRP')

        # # apply matrix ramp to controls and bones
        # for x, ctrls in enumerate(controls):
        #     if x != 0:
        #         mtx_ramp = matrixramp.create('{}_ctrls{}_mtxramp'.format(self.name, x), controls[x-1][0], ctrls[1])
        #         cmds.setAttr(mtx_ramp + '.blendType', 1)
        #         cmds.setAttr(mtx_ramp + '.outRotateMode', 1)
        #
        # mtx_ramp = matrixramp.create('{}_bones_mtxramp'.format(self.name), controls[-1][0], bones[1])
        # cmds.setAttr(mtx_ramp + '.blendType', 1)
        # cmds.setAttr(mtx_ramp + '.outRotateMode', 1)


# creating zipper rig
import maya.cmds as cmds
L_blends = []
R_blends = []
for x in range(0, 33):
    blendNode = cmds.createNode('blendColors', name='R_vest_zipper_cp{}_BLND'.format(x))
    R_blends.append(blendNode)
    pos1 = cmds.xform('R_vest_zipper_base_CRVShape.controlPoints[{}]'.format(x), t=True, ws=True, q=True)
    pos2 = cmds.xform('vest_zipper_BS_CRVShape.controlPoints[{}]'.format(x), t=True, ws=True, q=True)

    cmds.setAttr(blendNode + '.color1', pos1[0], pos1[1], pos1[2])
    cmds.setAttr(blendNode + '.color2', pos2[0], pos2[1], pos2[2])
    cmds.connectAttr(blendNode + '.output', 'R_vest_zipper_CRVShape.controlPoints[{}]'.format(x))

for x in range(0, 33):
    blendNode = cmds.createNode('blendColors', name='L_vest_zipper_cp{}_BLND'.format(x))
    L_blends.append(blendNode)
    pos1 = cmds.xform('L_vest_zipper_base_CRVShape.controlPoints[{}]'.format(x), t=True, ws=True, q=True)
    pos2 = cmds.xform('vest_zipper_BS_CRVShape.controlPoints[{}]'.format(x), t=True, ws=True, q=True)

    cmds.setAttr(blendNode + '.color1', pos1[0], pos1[1], pos1[2])
    cmds.setAttr(blendNode + '.color2', pos2[0], pos2[1], pos2[2])
    cmds.connectAttr(blendNode + '.output', 'L_vest_zipper_CRVShape.controlPoints[{}]'.format(x))

npcs = {}
for x in range(0, 33):
    npc = cmds.createNode('nearestPointOnCurve', name='zipper_crv_cp{}_NPC'.format(x))
    npcs[x] = npc
    cond1 = cmds.createNode('condition', name='zipper_crv_cp{}_0_COND'.format(x))
    cond2 = cmds.createNode('condition', name='zipper_crv_cp{}_1_COND'.format(x))
    sub1 = cmds.createNode('math_Subtract', name='zipper_crv_cp{}_0_SUB'.format(x))
    add = cmds.createNode('math_Add', name='zipper_crv_cp{}_ADD'.format(x))
    sub2 = cmds.createNode('math_Subtract', name='zipper_crv_cp{}_1_SUB'.format(x))
    div = cmds.createNode('math_Divide', name='zipper_crv_cp{}_DIV'.format(x))
    sqrt = cmds.createNode('math_Power', name='zipper_crv_cp{}_SQRT'.format(x))
    reverse = cmds.createNode('reverse', name='zipper_crv_cp{}_RVS'.format(x))
    blend = cmds.createNode('blendColors', name='zipper_crv_cp{}_BLEND'.format(x))

    # connect attributes of this cv's nearestPointOnCurve
    pos = cmds.xform('vest_zipper_BS_CRVShape.controlPoints[{}]'.format(x), t=True, ws=True, q=True)
    cmds.setAttr(npc + '.inPosition', pos[0], pos[1], pos[2])
    cmds.connectAttr('vest_zipper_BS_CRVShape.worldSpace[0]'.format(x), npc + '.inputCurve')

    # connect/set attributes of this cv's first condition
    cmds.connectAttr('vest_zipper_NPC.parameter', cond1 + '.firstTerm')
    cmds.connectAttr(npc + '.parameter', cond1 + '.secondTerm')
    cmds.connectAttr(cond2 + '.outColor', cond1 + '.colorIfTrue')
    cmds.setAttr(cond1 + '.operation', 4)

    # connect/set attributes of this cv's second condition
    cmds.connectAttr('vest_zipper_NPC.parameter', cond2 + '.firstTerm')
    cmds.connectAttr(sub1 + '.output', cond2 + '.secondTerm')
    cmds.connectAttr(sqrt + '.output', cond2 + '.colorIfTrueR')
    cmds.setAttr(cond2 + '.operation', 2)
    cmds.setAttr(cond2 + '.colorIfFalseR', 0)

    # set attribute of add/limit node
    cmds.connectAttr('vest_zipper_pos_LOC.zipFalloff', add + '.input1')

    # connect attributes of this cv's first subtract node
    cmds.connectAttr(npc + '.parameter', sub1 + '.input1')
    cmds.connectAttr(add + '.output', sub1 + '.input2')

    # connect attributes of this cv's second subtract node
    cmds.connectAttr('vest_zipper_NPC.parameter', sub2 + '.input1')
    cmds.connectAttr(sub1 + '.output', sub2 + '.input2')

    # connect attributes of this cv's divide node
    cmds.connectAttr(sub2 + '.output', div + '.input1')
    cmds.connectAttr(add + '.output', div + '.input2')

    # connect/set attributes of this cv's square root node
    cmds.connectAttr(div + '.output', sqrt + '.input')
    cmds.setAttr(sqrt + '.exponent', 2)

    # connect to condition to reverse
    cmds.connectAttr(cond1 + '.outColorR', reverse + '.inputX')

    # connect blender attribute
    cmds.connectAttr(reverse + '.outputX', blend + '.color1R')
    cmds.setAttr(blend + '.color2R', 1)
    cmds.connectAttr('vest_zipper_pos_LOC.zip', blend + '.blender')

    # connect to blenders of the corresponding cvs
    cmds.connectAttr(blend + '.outputR', 'L_vest_zipper_cp{}_BLND.blender'.format(x))
    cmds.connectAttr(blend + '.outputR', 'R_vest_zipper_cp{}_BLND.blender'.format(x))

# make connections to get vector between zipper and zip close
pma = cmds.createNode('plusMinusAverage', name='zipper_zipVec_PMA')
cmds.setAttr(pma + '.operation', 2)
cmds.connectAttr('vest_zipper_pos_LOCShape.worldPosition[0]', pma + '.input3D[0]')
cmds.connectAttr('vest_zipper_NPC_LOCShape.worldPosition[0]', pma + '.input3D[1]')

# connect wire for overall zipper deformation
for x in range(0, 33):
    dist = cmds.createNode('distanceBetween', name='zipper_cp{}_DIST'.format(x))
    cond = cmds.createNode('condition', name='zipper_bigDeform_cp{}_COND'.format(x))
    div = cmds.createNode('math_Divide', name='zipper_bigDeform_cp{}_DIV'.format(x))
    sub = cmds.createNode('math_Subtract', name='zipper_bigDeform_cp{}_SUB'.format(x))
    mult = cmds.createNode('math_MultiplyVector', name='zipper_bigDeform_cp{}_0_MULT'.format(x))
    mult2 = cmds.createNode('math_MultiplyVector', name='zipper_bigDeform_cp{}_1_MULT'.format(x))
    add = cmds.createNode('math_AddVector', name='zipper_bigDeform_cp{}_ADD'.format(x))

    # connect to distance node
    cmds.connectAttr('vest_zipper_NPC.parameter', dist + '.point1X')
    cmds.connectAttr(npcs[x] + '.parameter', dist + '.point2X')

    # connect to condition
    pos = cmds.getAttr('vest_zipper_deform_BS_CRVShape.controlPoints[{}]'.format(x))[0]
    cmds.setAttr(cond + '.operation', 2)
    cmds.setAttr(cond + '.colorIfTrue', pos[0], pos[1], pos[2])
    cmds.connectAttr(dist + '.distance', cond + '.firstTerm')
    cmds.connectAttr('vest_zipper_pos_LOC.zipPieceFalloff', cond + '.secondTerm')
    cmds.connectAttr(add + '.output', cond + '.colorIfFalse')

    # connect to divide node
    cmds.connectAttr(dist + '.distance', div + '.input1')
    cmds.connectAttr('vest_zipper_pos_LOC.zipPieceFalloff', div + '.input2')

    # connect to subtract node that will be the scalar value of the vector
    cmds.setAttr(sub + '.input1', 1)
    cmds.connectAttr(div + '.output', sub + '.input2')

    # connect to mult node to get scaled vector
    cmds.connectAttr(pma + '.output3D', mult + '.input1')
    cmds.connectAttr(sub + '.output', mult + '.input2')

    # connect scaled vector to attribute, turns on and off the deformation
    cmds.connectAttr(mult + '.output', mult2 + '.input1')
    cmds.connectAttr('vest_zipper_pos_LOC.zipPiece', mult2 + '.input2')

    # connect to add node to get final cv position
    pos = cmds.getAttr('vest_zipper_deform_BS_CRVShape.controlPoints[{}]'.format(x))[0]
    cmds.connectAttr(mult2 + '.output', add + '.input1')
    cmds.setAttr(add + '.input2', pos[0], pos[1], pos[2])

    # connect up to cv
    cmds.connectAttr(cond + '.outColor', 'vest_zipper_deform_BS_CRVShape.controlPoints[{}]'.format(x))


# store controls and their attribute values
class anim_pose():
    def __init__(self):
        self.saved_pose = {}
        self.ctrls = cmds.ls(sl=True)

    def store_pose(self):
        for each in self.ctrls:
            key_attrs = cmds.listAttr(each, keyable=True)
            if key_attrs:
                for attr in key_attrs:
                    value = cmds.getAttr(each + '.' + attr)
                    self.saved_pose[each + '.' + attr] = value

    def apply_pose(self, apply, selected):
        if apply == 'all':
            for attr, value in self.saved_pose.items():
                cmds.setAttr(attr, value)
        if apply == 'selected':
            print selected
            for each in selected:
                key_attrs = cmds.listAttr(each, keyable=True)
                print key_attrs
                for attr in key_attrs:
                    full_attr = each + '.' + attr
                    value = self.saved_pose[full_attr]
                    print value
                    cmds.setAttr(full_attr, value)

    def update_pose(self, pose):
        self.saved_pose = pose


# reconnecting spaces
from rigging_utils import constraint


def constrain(source, objs):
    for each in objs:
        constraint.create_constraint('simple', source, each)


# ball roll
spaces = ['R_boot_rim_CTRL_IK_SPACE']
constrain('R_ball_roll_CTRL', spaces)

# leg end
spaces = ['R_toes_CTRL_FK_SPACE', 'R_boot_rim_CTRL_FK_SPACE']
constrain('R_leg_end_CTRL', spaces)
constraint.point_constraint('R_leg_end_CTRL', 'R_boot_rim_forward_vec_LOC', snap=False)

# toe roll
constrain('R_toe_roll_CTRL', ['R_toes_CTRL_IK_SPACE'])

# foot ik
constrain('R1_foot_ik_CTRL', 'R_boot_rim_forward_vec_LOC_ZERO')


# mirror an object over the x axis
def mirror_object(object, mirrored_object):
    mtx = cmds.xform(object, matrix=True, ws=True, q=True)
    x = [mtx[0], mtx[1] * -1, mtx[2] * -1]
    y = [mtx[4], mtx[5] * -1, mtx[6] * -1]
    z = [mtx[8], mtx[9] * -1, mtx[10] * -1]
    p = [mtx[12] * -1, mtx[13], mtx[14]]
    new_mtx = [x[0], x[1], x[2], 0,
               y[0], y[1], y[2], 0,
               z[0], z[1], z[2], 0,
               p[0], p[1], p[2], 1]
    cmds.xform(mirrored_object, matrix=new_mtx, ws=True)

# function for transferring animation
def animation_transfer():
    # start and end of the timeline
    cmds.select('AGBR:*CTRL')
    ctrls = cmds.ls(sl=True)
    cmds.select(clear=True)
    start = int(cmds.playbackOptions(query=True, min=True))
    end = int(cmds.playbackOptions(query=True, max=True))

    unshared_ctrls = ['AGBR:R_foot_ik_CTRL|AGBR:R_leg_SHARED_CTRL', 'AGBR:R_foot_ik_toes_CTRL', 'AGBR:R_foot_ik_ball_CTRL', 'AGBR:L_foot_ik_ball_CTRL', 'AGBR:C_pelvis_CTRL|AGBR:C_spine_SHARED_CTRL', 'AGBR:L_foot_ik_toes_CTRL', 'AGBR:L_foot_ik_CTRL|AGBR:L_leg_SHARED_CTRL']

    for frame in range(start, end):
        cmds.currentTime(frame, edit=True)

        for each in ctrls:
            if each not in unshared_ctrls:
                attrs = cmds.listAttr(each, keyable=True)
                copy_ctrl = 'AGTR:' + each.split(':')[1]
                print each
                for att in attrs:
                    if att != 'bank':
                        value = cmds.getAttr(copy_ctrl + '.' + att)
                        cmds.setAttr(each + '.' + att, value)
                cmds.setKeyframe(each)

    # for old, new in rig_match.items():
    #     loc = cmds.spaceLocator()
    #     pos = cmds.xform(new, t=True, ws=True, q=True)
    #     rot = cmds.xform(new, ro=True, ws=True, q=True)
    #     cmds.xform(loc, t=pos, ws=True)
    #     cmds.xform(loc, ro=rot, ws=True)
    #     proxy_locs[old] = loc
    #     pc = cmds.parentConstraint(old, loc, mo=True)

    # for frame in range(start, end + 1):
    #     if frame != 0:
    #         cmds.currentTime(frame, edit=True)
    #     for old, new in rig_match.items():
    #         pos = cmds.xform(proxy_locs[old], t=True, ws=True, q=True)
    #         rot = cmds.xform(proxy_locs[old], ro=True, ws=True, q=True)
    #         if new == 'AGTR:C_spine_01_BONE':
    #             cmds.xform(new, t=pos, ws=True)
    #         cmds.xform(new, ro=rot, ws=True)
    #         cmds.setKeyframe(new)

# function to take two spaces and connect it to a world attribute

def apply_spaces(spaces, ctrl):
    ctrl_dm = cmds.createNode('decomposeMatrix', name=ctrl + '_DM')
    ctrl_mm = cmds.createNode('multMatrix', name=ctrl + '_MM')
    mmb = cmds.createNode('millMatrixBlend', name=ctrl + '_MMB')

    for x, each in enumerate(spaces):
        cmds.connectAttr(each + '.worldMatrix[0]', mmb + 'inMatrix{}'.format(str(x)))


def store_density(obj, num_jnts):
    params = []
    step = 100.0/num_jnts
    frame = 0
    while frame < 100:
        cmds.currentTime(frame, edit=True)
        value = cmds.getAttr(obj + '.tz')
        params.append(value)
        frame += step
    return params


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


rig_match = {}

L_arm = {'AGTR:L_shoulder_BONE': 'L_shoulder_JNT',
         'AGTR:L_arm_01_upper_BONE': 'L_arm_upper_JNT',
         'AGTR:L_arm_03_upper_BONE': 'L_arm_upper_roll_JNT',
         'AGTR:L_arm_01_lower_BONE': 'L_arm_lower_JNT',
         'AGTR:L_arm_03_lower_BONE': 'L_arm_lower_roll_JNT',
         'AGTR:L_hand_BONE': 'L_hand_JNT',
         'AGTR:L_thumb_01_BONE': 'L_thumb_01_JNT',
         'AGTR:L_thumb_02_BONE': 'L_thumb_02_JNT',
         'AGTR:L_thumb_03_BONE': 'L_thumb_03_JNT',
         'AGTR:L_fingerA_01_BONE': 'L_fingerA_01_JNT',
         'AGTR:L_fingerA_02_BONE': 'L_fingerA_02_JNT',
         'AGTR:L_fingerA_03_BONE': 'L_fingerA_03_JNT',
         'AGTR:L_fingerB_01_BONE': 'L_fingerB_01_JNT',
         'AGTR:L_fingerB_02_BONE': 'L_fingerB_02_JNT',
         'AGTR:L_fingerB_03_BONE': 'L_fingerB_03_JNT',
         'AGTR:L_fingerC_01_BONE': 'L_fingerC_01_JNT',
         'AGTR:L_fingerC_02_BONE': 'L_fingerC_02_JNT',
         'AGTR:L_fingerC_03_BONE': 'L_fingerC_03_JNT',
         'AGTR:L_fingerD_01_BONE': 'L_fingerD_01_JNT',
         'AGTR:L_fingerD_02_BONE': 'L_fingerD_02_JNT',
         'AGTR:L_fingerD_03_BONE': 'L_fingerD_03_JNT'}
R_arm = {}
for key, value in L_arm.items():
    new_key = key.replace('L_', 'R_')
    new_value = value.replace('L_', 'R_')
    R_arm[new_key] = new_value

L_leg = {'AGTR:L_leg_01_upper_BONE': 'L_leg_upper_JNT',
         'AGTR:L_leg_03_upper_BONE': 'L_leg_upper_roll_JNT',
         'AGTR:L_leg_01_lower_BONE': 'L_leg_lower_JNT',
         'AGTR:L_leg_03_lower_BONE': 'L_leg_lower_roll_JNT',
         'AGTR:L_foot_BONE': 'L_foot_JNT',
         'AGTR:L_toes_BONE': 'L_foot_ball_JNT'}
R_leg = {}
for key, value in L_leg.items():
    new_key = key.replace('L_', 'R_')
    new_value = value.replace('L_', 'R_')
    R_leg[new_key] = new_value

body = {'AGTR:C_spine_01_BONE': 'C_pelvis_JNT',
        'AGTR:C_spine_02_BONE': 'C_spine_01_JNT',
        'AGTR:C_spine_03_BONE': 'C_spine_02_JNT',
        'AGTR:C_chest_BONE': 'C_spine_03_JNT',
        'AGTR:C_neck_01_BONE': 'C_neck_01_JNT',
        'AGTR:C_neck_02_BONE': 'C_neck_02_JNT',
        'AGTR:C_head_BONE': 'C_head_JNT',
        'AGTR:C_jaw_01_BONE': 'C_jaw_01_JNT',
        'AGTR:C_jaw_02_BONE': 'C_jaw_02_JNT'}


def dict_to_dict(old_dict, new_dict):
    for key, value in old_dict.items():
        new_dict[key] = value


dict_to_dict(R_arm, rig_match)
dict_to_dict(L_arm, rig_match)
dict_to_dict(R_leg, rig_match)
dict_to_dict(L_leg, rig_match)
dict_to_dict(body, rig_match)

animation_transfer(rig_match)


# store vertex positions to apply later
class vertex():
    def __init__(self):
        self.vtx_list = cmds.ls(sl=True, fl=True)
        self.pos_dict = {}

    def store_position(self):
        for each in self.vtx_list:
            pos = cmds.xform(each, t=True, ws=True, q=True)
            self.pos_dict[each] = pos

    def move_vertex(self, selection=True):
        if selection:
            vertices = cmds.ls(sl=True, fl=True)
            for each in vertices:
                pos = self.pos_dict[each]
                cmds.select(each)
                cmds.move(pos[0], pos[1], pos[2])
        else:
            for each in self.vtx_list:
                pos = self.pos_dict[each]
                cmds.select(each)
                cmds.move(pos[0], pos[1], pos[2])




# create bone at dag
def bone_on_dag(dag, constrain=True):
    cmds.select(clear=True)
    split_name = dag.split('_')
    name = ''
    for x, part in enumerate(split_name):
        if x < (len(split_name) - 1):
            name += part + '_'
        else:
            name += 'BONE'

    bone = cmds.joint(name=name)
    constraint = cmds.parentConstraint(dag, bone, mo=False)
    if not constrain:
        cmds.delete(constraint)

# mirror tool for joints
import maya.cmds as cmds

selection1 = cmds.ls(sl=True)
for selection in selection1:
    orig_dir = selection.split('_')[0]
    if orig_dir == 'L':
        mirror_dir = 'R'
    else:
        mirror_dir = 'L'
    mirrored_jnt_list = selection.split('_')
    mirrored_jnt = mirror_dir
    for x in range(1, len(mirrored_jnt_list)):
        mirrored_jnt = mirrored_jnt + '_' + mirrored_jnt_list[x]

    top = cmds.createNode('transform', name='top_GRP')
    mirror = cmds.createNode('transform', name='mirror_GRP')
    cmds.parent(mirror, top)

    pc1 = cmds.parentConstraint(selection, mirror)
    cmds.delete(pc1)

    cmds.setAttr(top + '.scaleX', -1)
    pc2 = cmds.parentConstraint(mirror, mirrored_jnt)
    cmds.delete(pc2)

    cmds.delete(top)

# scale of an ik chain
import maya.cmds as cmds
import maya.api.OpenMaya as om


def distance(first_vec, second_vec):
    ''' Gets the magnitude of the vector between two vectors on an 'xz' plane

    Args:
        first_vec (om.MVector): Vector of first vector
        second_vec (om.MVector): Vector of second vector

    Returns:
        float: magnitude of distance between the two vectors
    '''
    distance = (first_vec - second_vec).length()
    return distance


ikh = ''
jnts = cmds.ls(sl=True)
parent_transform = cmds.listRelatives(jnts[0], p=True)[0]
pos1 = om.MVector(cmds.xform(parent_transform, t=1, ws=1, q=1))
pos2 = om.MVector(cmds.xform(ikh, t=1, ws=1, q=1))
dist = distance(pos1, pos2)
dm1 = cmds.createNode('decomposeMatrix', name=jnts[0] + '_DM')
dm2 = cmds.createNode('decomposeMatrix', name=ikh + '_DM')
distance = cmds.createNode('distanceBetween', name=jnts[0].split('JNT')[0] + 'DIST')
div = cmds.createNode('multiplyDivide', name=ikh + '_dist_DIV')
cond = cmds.createNode('condition', name=ikh + '_COND')


cmds.connectAttr(parent_transform + '.worldMatrix[0]', distance + '.inMatrix1')
cmds.connectAttr(ikh + '.worldMatrix[0]', distance + '.inMatrix2')

cmds.setAttr(div + '.operation', 2)
cmds.setAttr(div + '.input2X', dist)
cmds.connectAttr(distance + '.distance', div + '.input1X')

cmds.setAttr(cond + '.secondTerm', dist)
cmds.setAttr(cond + '.operation', 4)
cmds.setAttr(cond + '.colorIfTrueR', 1)
cmds.connectAttr(distance + '.distance', cond + '.firstTerm')
cmds.connectAttr(div + '.outputX', cond + '.colorIfFalseR')

for each in [jnts[0]]:
    cmds.connectAttr(cond + '.outColorR', each + '.scaleY')



class BonesOnCrv():

    def __init__(self, rig_name, ctrl_size=1):
        selection = cmds.ls(sl=True)
        self.up_vec_crv = selection[1]
        self.crv = selection[0]
        self.rig_name = rig_name
        self.size = ctrl_size

    def create_dag_on_curve(self, crv, amt_dag, name):
        par_add = 1.0/amt_dag
        mid_point = amt_dag/2

        srt_list = []
        dag_list = []
        for x in range(0, amt_dag + 1):
            par = par_add * x

            part = self.rig_name + '_{}'.format(str(x))

            cmds.select(clear=True)
            dag = cmds.spaceLocator(name='{}_{}_LOC'.format(part, name))[0]
            srt = cmds.createNode('transform', name='{}_srt'.format(dag))
            srt_list.append(srt)
            dag_list.append(dag)
            cmds.parent(dag, srt)

            PCI = cmds.createNode('pointOnCurveInfo', name=str(dag) + '_PCI')

            cmds.connectAttr(crv + '.worldSpace[0]', PCI + '.inputCurve')

            cmds.setAttr(PCI + '.parameter', par)

            cmds.connectAttr(PCI + '.position', dag + '.translate')

        return srt_list, dag_list

    def circle_shape(self, name):
        ctrl = cmds.circle(name=name)[0]

        return ctrl

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

    def create_controls(self, dag_list, shape='circle', name='', split1='', size=1):
        zero_list = []
        ctrl_list = []
        for x, each in enumerate(dag_list):
            if split1 != '':
                name = each
                new_name = 'C_' + name.split(split1)[0] + 'CTRL'
            else:
                new_name = 'C_' + name + '_{}_CTRL'.format(x)
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

    def create_bones(self, crv, amt_bones):
            par_add = 1.0/amt_bones
            cmds.addAttr(crv, ln='jointRot', at='double', min=0, max=1, dv=0, k=True)

            srt_list = []
            for x in range(0, amt_bones + 1):
                # create space for

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

    def build(self):
        self.bot_vec_top_list = self.create_dag_on_curve(self.crv, 10, name='bot')[1]
        self.up_vec_top_list = self.create_dag_on_curve(self.up_vec_crv, 10, name='top')[1]

        amt_cvs = cmds.getAttr(self.crv + '.spans')
        loc_list = []
        for x in range(0, amt_cvs):
            pos1 = cmds.xform(self.crv + '.cv[{}]'.format(str(x)), t=1, ws=1, q=1)
            loc = cmds.spaceLocator()[0]
            cmds.xform(loc, t=pos1, ws=True)
            loc_list.append(loc)

        ctrls, ctrls_zero = self.create_controls(loc_list,
                                                 name=self.rig_name,
                                                 size=1)

        ctrl_jnts = []
        for each in ctrls:
            jnt = cmds.joint(name=each + '_JNT')
            cmds.parentConstraint(each, jnt, mo=False)
            ctrl_jnts.append(jnt)

        cmds.skinCluster(ctrl_jnts, self.crv)
        cmds.skinCluster(ctrl_jnts, self.up_vec_crv)

        self.create_bones(self.crv, 10)


# rotation for wheels
import maya.cmds as cmds

selection = cmds.ls(sl=True)
for each in selection:
    mult = cmds.createNode('math_Multiply', name=each + '_wheel_MULT')
    OFS = cmds.listRelatives(each, parent=True)[0]

    cmds.connectAttr('C_truck_01_CTRL.wheelRot', mult + '.input1')
    cmds.setAttr(mult + '.input2', 10)

    cmds.connectAttr(mult + '.output', OFS + '.rotateX')

# create zero group
import maya.cmds as cmds

selection = cmds.ls(sl=True)
for each in selection:
    zero = cmds.createNode('transform', name=each + '_ZERO')

    pos = cmds.xform(each, t=True, ws=True, q=True)
    rot = cmds.xform(each, ro=True, ws=True, q=True)

    cmds.xform(zero, t=pos, ws=True)
    cmds.xform(zero, ro=rot, ws=True)

    cmds.parent(each, zero)

selection = cmds.ls(sl=True)
new_name = selection[0] + '_foll'
foll = cmds.rename(selection[1], new_name)

ZERO = cmds.createNode('transform', name=selection[0] + '_null_ZERO')
pos = cmds.xform(selection[0], t=True, ws=True, q=True)
rot = cmds.xform(selection[0], ro=True, ws=True, q=True)
cmds.xform(ZERO, t=pos, ws=True)
cmds.xform(ZERO, ro=rot, ws=True)
null = cmds.duplicate(ZERO, name=selection[0] + '_null')[0]
cmds.parent(null, ZERO)

cmds.parentConstraint(foll, null, mo=True)

OFS = selection[0] + '_OFS'
cmds.connectAttr(null + '.t', OFS + '.t')
cmds.connectAttr(null + '.r', OFS + '.r')



# squash stretch for chain
import maya.cmds as cmds


class ChainSquash():

    def __init__(self, side):
        self.bones = cmds.ls(sl=True)
        self.side = side

    def create_ctrl(self, name):
        self.ctrl = cmds.circle(name=self.side + '_%s_CTRL' % name)[0]
        self.ctrl_transform = cmds.createNode('transform', name=self.ctrl + 'ZERO')
        self.ctrl_DM = cmds.createNode('decomposeMatrix', name=self.ctrl + '_DM')

        cmds.parent(self.ctrl, self.ctrl_transform)
        cmds.addAttr(self.ctrl, ln='squash', min=0, dv=0)
        cmds.addAttr(self.ctrl, ln='squashDistance', min=0, dv=0)
        cmds.setAttr(self.ctrl + '.squash', k=True, e=True)
        cmds.setAttr(self.ctrl + '.squashDistance', k=True, e=True)

    def build(self):
        self.create_ctrl('squash')
        ctrl_pos = cmds.xform(self.bones[2], t=1, ws=1, q=1)
        ctrl_rot = cmds.xform(self.bones[2], ro=1, ws=1, q=1)
        cmds.xform(self.ctrl_transform, t=ctrl_pos, ws=1)
        cmds.xform(self.ctrl_transform, ro=ctrl_rot, ws=1)

        for bone in self.bones:
            # DM = cmds.createNode('decomposeMatrix', name=bone + '_DM')
            # PMA = cmds.createNode('plusMinusAverage', name=DM + '_PMA')
            dist_between = cmds.createNode('distanceBetween', name=bone + '_DIST')
            cond = cmds.createNode('condition', name=dist_between + '_COND')
            mult = cmds.createNode('math_Multiply', name=bone + '_squash_MULT')
            set_range = cmds.createNode('setRange', name=cond + '_SR')
            PMA = cmds.createNode('plusMinusAverage', name=bone + '_squash_PMA')
            # dist_div = cmds.createNode('math_Divide', name=bone + 'dist_scale')

            cmds.connectAttr(bone + '.worldMatrix[0]', dist_between + '.inMatrix1')
            cmds.connectAttr(self.ctrl + '.worldMatrix[0]', dist_between + '.inMatrix2')

            cmds.connectAttr(dist_between + '.distance', cond + '.firstTerm')
            cmds.connectAttr(dist_between + '.distance', cond + '.colorIfTrueR')
            # cmds.connectAttr(dist_between + '.distance', dist_div + '.input1')
            cmds.connectAttr(self.ctrl + '.squashDistance', cond + '.secondTerm')
            cmds.connectAttr(self.ctrl + '.squashDistance', cond + '.colorIfFalseR')
            cmds.setAttr(cond + '.operation', 4)

            cmds.connectAttr(self.ctrl + '.squashDistance', set_range + '.oldMaxX')
            cmds.connectAttr(cond + '.outColorR', set_range + '.valueX')
            cmds.setAttr(set_range + '.minX', 1)
            cmds.setAttr(set_range + '.maxX', 0)

            cmds.connectAttr(set_range + '.outValueX', mult + '.input1')
            cmds.connectAttr(self.ctrl + '.squash', mult + '.input2')

            cmds.setAttr(PMA + '.input1D[0]', 1)
            cmds.connectAttr(mult + '.output', PMA + '.input1D[1]')

            cmds.connectAttr(PMA + '.output1D', bone + '.scaleX')
            cmds.connectAttr(PMA + '.output1D', bone + '.scaleZ')






# making sticky deformers made by mill rig look like ren's sticky deformers
import maya.cmds as cmds

shape_transform, softMod_ctrl = cmds.ls(sl=True)
new_shape = cmds.listRelatives(shape_transform, s=True)[0]
parent_transform = cmds.listRelatives(softMod_ctrl, p=True)[0]
old_loc_shape_list = cmds.listRelatives(parent_transform, s=True)
old_sticky_loc_shape_list = cmds.listRelatives(softMod_ctrl, s=True)
for each in old_loc_shape_list:
    type = cmds.nodeType(each)
    if type == 'locator':
        old_loc_shape = each
for each in old_sticky_loc_shape_list:
    type = cmds.nodeType(each)
    if type == 'locator':
        old_sticky_loc_shape = each

cmds.setAttr(old_sticky_loc_shape + '.visibility', 0)
cmds.setAttr(softMod_ctrl + '.displayFalloff', 0)

cmds.select(softMod_ctrl)

cmds.parent(shape_transform, parent_transform)
cmds.setAttr(shape_transform + '.translate', 0, 0, 0)
cmds.setAttr(shape_transform + '.rotate', 0, 0, 0)

cmds.parent(new_shape, softMod_ctrl, r=True, s=True)

cmds.addAttr(softMod_ctrl, ln='pivotVis', at='long', min=0, max=1, dv=0, k=0)
cmds.setAttr(softMod_ctrl + '.pivotVis', channelBox=True)

cmds.connectAttr(softMod_ctrl + '.pivotVis', old_loc_shape + '.visibility')

cmds.delete(shape_transform)

# transfer weights by vertex
import maya.cmds as cmds
import maya.mel as mel

v_list = cmds.ls(sl=True, fl=True)
inf_dict = {}
wts_dict = {}

for v in v_list:
    mdl = v.split('.')[0]
    skin = mel.eval('findRelatedSkinCluster "{0}"'.format(mdl))
    inf_dict[v] = cmds.skinCluster(skin, q=True, inf=True)
    print v
    wts_dict[v]= cmds.skinPercent(skin, v, q=True, v=True)

import maya.cmds as cmds
import maya.mel as mel

for v in v_list:
    mdl = 'bearmom_onfours_GEO'
    skin = mel.eval('findRelatedSkinCluster "{0}"'.format(mdl))
    cmds.skinPercent(skin, v, tv=zip(inf, wts))


# class for moving joints for mill north rigs
import maya.cmds as cmds


class mill_north_rig():

    def __init__(self):
        self.loc_list = []

    def create_locs(self):
        selection = cmds.ls(sl=True)
        for each in selection:
            pos = cmds.xform(each, t=True, ws=True, query=True)
            rot = cmds.xform(each, ro=True, ws=True, query=True)
            try:
                jnt_parent = cmds.listRelatives(each, parent=True)[0]
                loc_parent = jnt_parent + '_pos_LOC'
                parent_exists = True
                srt_check = jnt_parent.split('_')
                srt_check = srt_check[len(srt_check)-1]
                if srt_check == 'srt':
                    cmds.error()
            except:
                parent_exists = False
            name = each + '_pos_LOC'

            loc = cmds.spaceLocator(n=name)[0]
            self.loc_list.append(loc)

            cmds.xform(loc, t=pos, ws=True)
            cmds.xform(loc, ro=rot, ws=True)

            if parent_exists:
                cmds.parent(loc, loc_parent)

    def mirror_loc(self, static_side):
        list = cmds.ls(sl=True)
        static_side = ('_{}_'.format(static_side))
        if static_side == '_l_':
            other_side = '_r_'
        else:
            other_side = '_l_'

        for each in list:
            if other_side in each:
                pass
            else:
                if static_side in each:
                    mirrored_obj = each.replace(static_side, other_side)

                    world_zero_scale = cmds.createNode('transform')
                    scale_transform = cmds.createNode('transform')
                    cmds.parent(scale_transform, world_zero_scale)
                    first_pos = cmds.xform(each, t=True, ws=True, q=True)
                    first_rot = cmds.xform(each, ro=True, ws=True, q=True)
                    cmds.xform(scale_transform, t=first_pos, ws=True)
                    cmds.xform(scale_transform, ro=first_rot, ws=True)
                    cmds.setAttr(world_zero_scale + '.scaleX', -1)
                    cmds.parent(scale_transform, world=True)
                    sec_pos = cmds.xform(scale_transform, t=True, ws=True, q=1)
                    sec_rot = cmds.xform(scale_transform, ro=True, ws=True, q=1)

                    cmds.xform(mirrored_obj, t=sec_pos, ws=True)
                    cmds.xform(mirrored_obj, ro=sec_rot, ws=True)

                    cmds.delete(world_zero_scale)
                    cmds.delete(scale_transform)
                else:
                    pass

    def move_joint_to_loc(self, pose=True):
        if pose:
            world_space = False
        else:
            world_space = True
        list = cmds.ls(sl=True)
        if len(list) == 0:
            list = self.loc_list
            world_space = True

        for each in list:
            obj_type = cmds.objectType(each, i='joint')
            if obj_type:
                loc = each + '_pos_LOC'

                pos = cmds.xform(loc, t=True, ws=world_space, query=True)
                rot = cmds.xform(loc, ro=True, ws=world_space, query=True)
                cmds.xform(each, t=pos, ws=world_space)
                cmds.xform(each, ro=rot, ws=world_space)

            else:
                jnt = each.split('_pos_LOC')[0]

                pos = cmds.xform(each, t=True, ws=world_space, query=True)
                rot = cmds.xform(each, ro=True, ws=world_space, query=True)
                cmds.xform(jnt, t=pos, ws=world_space)
                cmds.xform(jnt, ro=rot, ws=world_space)

    def make_obj_world(self):
        list = cmds.ls(sl=True)
        for each in list:
            parent_key = each + '_parent'
            cmds.parent(each, world=True)

    def make_obj_local(self):
        list = cmds.ls(sl=True)
        for each in list:
            parent_key = each + '_parent'
            child_key = each + '_child'

            if self.relatives[parent_key]:
                try:
                    cmds.parent(each, self.relatives[parent_key])
                except:
                    pass

    def store_locs(self):
        self.loc_list = cmds.ls(sl=True)
        self.relatives = {}
        for each in self.loc_list:
            parent_key = each + '_parent'
            child_key = each + '_child'

            try:
                self.relatives[parent_key] = cmds.listRelatives(each, parent=1)[0]
            except:
                self.relatives[parent_key] = None
            self.relatives[child_key] = cmds.listRelatives(each, c=True, typ='transform')

    def orient_to_plane(self):
        '''
        takes respective locator and orients it to the plane that is created
        by the parent and child of the locator
        :return:
        '''


# create follicles on a surface
def create_follicle(self, num_objs, fun, foll_list, foll_transform_list, nrbs_plane):
    local_foll_list = []
    # using the amount of objects create follicles with equal space
    # along the given nurbs plane
    for x in range(0, num_objs):
        foll = cmds.createNode('follicle', name=self.rig_name + '_' + fun + '_' + str(x) + '_follicle')
        foll_list.append(foll)

        nurbs_pln_shape = cmds.listRelatives(nrbs_plane, children=True, shapes=True)[0]
        foll_transform = cmds.listRelatives(foll, parent=True)[0]
        foll_transform = cmds.rename(foll_transform, foll + '_srt')
        foll_transform_list.append(foll_transform)
        local_foll_list.append(foll_transform)

        cmds.connectAttr(nurbs_pln_shape + '.local', foll + '.inputSurface')
        cmds.connectAttr(nurbs_pln_shape + '.worldMatrix[0]', foll + '.inputWorldMatrix')
        cmds.connectAttr(foll + '.outRotate', foll_transform + '.rotate')
        cmds.connectAttr(foll + '.outTranslate', foll_transform + '.translate')

        if num_objs == 1:
            parU = 0
        else:
            parU = float(x) / (num_objs - 1)
        cmds.setAttr(foll + '.parameterU', parU)
        cmds.setAttr(foll + '.parameterV', .5)
    return local_foll_list


# copy skin weights to multiple new geos
new_geos = cmds.ls(sl=True)
for geo in new_geos:
    hist = cmds.listHistory(geo)
    sc = ''
    for each in hist:
        type = cmds.nodeType(each)
        if type == 'skinCluster':
            sc = each
    cmds.copySkinWeights(ss='skinCluster1258', ds=sc, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')

# create movable soft deformer
import maya.cmds as cmds


def soft_deformer(ctrl_name):
    # get position for the follicle on the mesh
    selection = cmds.ls(sl=True)
    geo = selection[0].split('.')[0]
    component = selection[0].split('.')[1]
    if 'f' in component:
        uvs = cmds.polyListComponentConversion(ff=True, tuv=True)
        uv_list = []

        for each in uvs:
            if ':' in each:
                each = each.split('[')[1].split(']')[0]
                nums = each.split(':')
                difference = nums[1] - nums[0]
                # add already existing uvs into the list
                for each in nums:
                    uv = geo + '.map[{}]'.format(each)
                    uv_list.append(uv)
                if difference > 1:
                    for x in range(1, difference):
                        mid_uv = geo + '.map[{}]'.format(str(int(nums[1]) - x))
                        uv_list.append(mid_uv)
        print uv_list
