import numpy as np

import maya.cmds as cmds
import maya.api.OpenMaya as om

import millrigger.modules.NY.misc.ryanf_scripts.create.nurbs as nrb

from rigging_utils import maths
from rigging_utils import attribute
from rigging_utils import name
from rigging_utils.create import curves


def coaster_skin():
    r = 50
    for i in range(0, r):
        bone = 'C_coaster_r_rail_{}_BONE'.format(str(i))
        geo = 'R_rail_{}_GEO'.format(str(i))
        cmds.skinCluster(bone, geo)
    for i in range(0, r):
        bone = 'C_coaster_l_rail_{}_BONE'.format(str(i))
        geo = 'L_rail_{}_GEO'.format(str(i))
        cmds.skinCluster(bone, geo)
    for i in range(0, r):
        bone = 'C_coaster_c_rail_{}_BONE'.format(str(i))
        geo = 'B_tube_{}_GEO'.format(str(i))
        cmds.skinCluster(bone, geo)
    for i in range(0, 16):
        geo_grp = 'ppTrackRingModel_{}_GRP'.format(str(i))
        geos = cmds.listRelatives(geo_grp, c=True)
        bone_num = i * 3
        bone = 'C_coaster_c_rail_{}_BONE'.format(str(bone_num))
        for geo in geos:
            cmds.skinCluster(bone, geo)
    # for i in range(0, r):
    #     for x in range(3):
    #         bone = 'C_coaster_main{}_{}_BONE'.format(str(x), str(i))
    #         if x == 0:
    #             geos = cmds.ls('strut_C_*_{}_GEO'.format(str(i)))
    #         elif x == 1:
    #             geos = cmds.ls('strut_B_*_{}_GEO'.format(str(i)))
    #         elif x == 2:
    #             geos = cmds.ls('strut_A_*_{}_GEO'.format(str(i)))
    #         for geo in geos:
    #             cmds.skinCluster(bone, geo)


def coaster_proxy_skin(create=False):
    if create:
        for i, each in enumerate(cmds.ls(sl=True)):
            nodes = cmds.listRelatives(each, ad=True)
            nodes.append(each)
            for node in nodes:
                name_list = node.split('_')
                name_list.insert(-1, str(i))
                new_name = ''
                for x, string in enumerate(name_list):
                    if string == name_list[-1]:
                        new_name += string
                    else:
                        new_name += string + '_'
                cmds.rename(node, new_name)

        sel = cmds.ls(sl=True)[0]
        for i in range(1, 50):
            geo = cmds.duplicate(sel, rc=True)[0]
            cmds.xform(geo, t=(0, 0, i * 10))
            nodes = cmds.listRelatives(geo, ad=True)
            nodes.append(geo)
            for node in nodes:
                name_list = node.split('_')

                name_list.insert(-1, str(i))
                new_name = ''
                for x, string in enumerate(name_list):
                    if string == name_list[-1]:
                        new_name += string
                    else:
                        new_name += string + '_'
                cmds.rename(node, new_name)

    r = 51
    for i in range(1, r):
        bone_num = i - 1
        if i < 10:
            num = '0' + str(i)
        else:
            num = str(i)

        bone = 'C_coaster_r_rail_{}_BONE'.format(bone_num)
        geo = 'R_rail_{}_proxy_GEO'.format(num)
        cmds.skinCluster(bone, geo)

        bone = 'C_coaster_l_rail_{}_BONE'.format(bone_num)
        geo = 'L_rail_{}_proxy_GEO'.format(num)
        cmds.skinCluster(bone, geo)

        bone = 'C_coaster_c_rail_{}_BONE'.format(bone_num)
        geo = 'C_rail_{}_proxy_GEO'.format(num)
        cmds.skinCluster(bone, geo)

        # bone = 'C_coaster_main0_{}_BONE'.format(bone_num)
        # geo = 'C_strut_{}_proxy_GEO'.format(num)
        # cmds.skinCluster(bone, geo)


def fern_displacement_setup(ref_geos, geos, controls):
    if len(ref_geos) != len(geos):
        print len(ref_geos)
        print len(geos)
        cmds.error("Number of dags doesn't match up")

    elif len(geos) != len(controls):
        print len(geos)
        print len(controls)
        cmds.error("Number of dags doesn't match up")

    for i, ref in enumerate(ref_geos):
        init_scale = cmds.getAttr(ref + '.sx')
        geo = geos[i]
        geo_shape = cmds.listRelatives(geo, s=True)[1]
        ctrl = controls[i]

        attribute.add_generic_blend(geo_shape, 'mtoa_constant_leafScale', max_value=100)
        attribute.add_generic_blend(geo_shape, 'mtoa_constant_initialScale', default=init_scale, max_value=100)

        pma = cmds.createNode('plusMinusAverage', name=geo_shape + '_PMA')
        div = cmds.createNode('math_Divide', name=geo_shape + '_DIV')
        mult = cmds.createNode('math_Multiply', name=geo_shape + '_MULT')

        cmds.connectAttr(ctrl + '.localScaleX', pma + '.input1D[0]')
        cmds.connectAttr(ctrl + '.localScaleY', pma + '.input1D[1]')
        cmds.connectAttr(ctrl + '.localScaleZ', pma + '.input1D[2]')

        cmds.connectAttr(pma + '.output1D', div + '.input1')
        cmds.setAttr(div + '.input2', 3)

        cmds.connectAttr(div + '.output', mult + '.input1')
        cmds.connectAttr(geo_shape + '.mtoa_constant_initialScale', mult + '.input2')

        cmds.connectAttr(mult + '.output', geo_shape + '.mtoa_constant_leafScale')


def new_fern_displacement_setup(geos, controls):

    for i, ref in enumerate(geos):
        # init_scale = cmds.getAttr(ref + '.mtoa_constant_initialScale')
        geo = geos[i]
        geo_shape = cmds.listRelatives(geo, s=True)[1]
        ctrl = controls[i]

        # attribute.add_generic_blend(geo_shape, 'mtoa_constant_leafScale', max_value=100)
        # attribute.add_generic_blend(geo_shape, 'mtoa_constant_initialScale', default=init_scale, max_value=100)

        pma = cmds.createNode('plusMinusAverage', name=geo_shape + '_PMA')
        div = cmds.createNode('math_Divide', name=geo_shape + '_DIV')
        mult = cmds.createNode('math_Multiply', name=geo_shape + '_MULT')
        dm = cmds.createNode('decomposeMatrix', name=ctrl + '_DM')

        cmds.connectAttr(ctrl + '.worldMatrix[0]', dm + '.inputMatrix')

        cmds.connectAttr(dm + '.outputScaleX', pma + '.input1D[0]')
        cmds.connectAttr(dm + '.outputScaleY', pma + '.input1D[1]')
        cmds.connectAttr(dm + '.outputScaleZ', pma + '.input1D[2]')

        cmds.connectAttr(pma + '.output1D', div + '.input1')
        cmds.setAttr(div + '.input2', 3)

        cmds.connectAttr(div + '.output', mult + '.input1')
        cmds.connectAttr(geo_shape + '.mtoa_constant_initialScale', mult + '.input2')

        cmds.connectAttr(mult + '.output', geo_shape + '.mtoa_constant_leafScale')
# tb.new_fern_displacement_setup(l_geos, l_controls)
# tb.new_fern_displacement_setup(r_geos, r_controls)
#
# l_controls = [u'L37_spiral_root_CTRL', u'L36_spiral_root_CTRL', u'L35_spiral_root_CTRL', u'L34_spiral_root_CTRL', u'L_spiral_root_CTRL', u'L_spiral_0_CTRL', u'L1_spiral_root_CTRL', u'L1_spiral_0_CTRL', u'L2_spiral_root_CTRL', u'L2_spiral_0_CTRL', u'L3_spiral_root_CTRL', u'L4_spiral_root_CTRL', u'L4_spiral_0_CTRL', u'L5_spiral_root_CTRL', u'L5_spiral_0_CTRL', u'L6_spiral_root_CTRL', u'L6_spiral_0_CTRL', u'L7_spiral_root_CTRL', u'L7_spiral_0_CTRL', u'L8_spiral_root_CTRL', u'L8_spiral_0_CTRL', u'L9_spiral_root_CTRL', u'L10_spiral_root_CTRL', u'L11_spiral_root_CTRL', u'L12_spiral_root_CTRL', u'L13_spiral_root_CTRL', u'L14_spiral_root_CTRL', u'L15_spiral_root_CTRL', u'L16_spiral_root_CTRL', u'L17_spiral_root_CTRL', u'L18_spiral_root_CTRL', u'L19_spiral_root_CTRL', u'L20_spiral_root_CTRL', u'L20_spiral_1_CTRL', u'L21_spiral_root_CTRL', u'L22_spiral_root_CTRL', u'L23_spiral_root_CTRL', u'L23_spiral_1_CTRL', u'L24_spiral_root_CTRL', u'L24_spiral_2_CTRL', u'L24_spiral_1_CTRL', u'L25_spiral_root_CTRL', u'L25_spiral_2_CTRL', u'L25_spiral_1_CTRL', u'L26_spiral_root_CTRL', u'L27_spiral_root_CTRL', u'L27_spiral_2_CTRL', u'L27_spiral_1_CTRL', u'L28_spiral_root_CTRL', u'L29_spiral_root_CTRL', u'L30_spiral_root_CTRL', u'L31_spiral_root_CTRL', u'L32_spiral_root_CTRL', u'L33_spiral_root_CTRL']
# l_geos = [u'R_leaf20_GEO', u'L37_spiral_2_CTRL', u'R_leaf19_GEO', u'L36_spiral_3_CTRL', u'R_leaf18_GEO', u'R_leaf17_GEO', u'FERM:R_leaf16_GEO', u'FERM:R_leaf15_GEO', u'FERM:R_leaf14_GEO', u'FERM:R_leaf13_GEO', u'FERM:R_leaf12_GEO', u'FERM:R_leaf11_GEO', u'FERM:R_leaf10_GEO', u'FERM:R_leaf09_GEO', u'FERM:R_leaf08_GEO', u'FERM:R_leaf07_GEO', u'FERM:R_leaf06_GEO', u'FERM:R_leaf05_GEO', u'FERM:R_leaf04_GEO', u'FERM:R_leaf03_GEO', u'FERM:R_leaf02_GEO', u'FERM:R_leaf01_GEO']
# r_controls = [u'R36_spiral_root_CTRL', u'R35_spiral_root_CTRL', u'R34_spiral_root_CTRL', u'R33_spiral_root_CTRL', u'R_spiral_root_CTRL', u'R_spiral_0_CTRL', u'R1_spiral_root_CTRL', u'R1_spiral_0_CTRL', u'R2_spiral_root_CTRL', u'R2_spiral_0_CTRL', u'R3_spiral_root_CTRL', u'R3_spiral_0_CTRL', u'R4_spiral_root_CTRL', u'R4_spiral_0_CTRL', u'R5_spiral_root_CTRL', u'R6_spiral_root_CTRL', u'R6_spiral_0_CTRL', u'R7_spiral_root_CTRL', u'R7_spiral_0_CTRL', u'R8_spiral_root_CTRL', u'R9_spiral_root_CTRL', u'R9_spiral_0_CTRL', u'R10_spiral_root_CTRL', u'R11_spiral_root_CTRL', u'R12_spiral_root_CTRL', u'R13_spiral_root_CTRL', u'R14_spiral_root_CTRL', u'R15_spiral_root_CTRL', u'R16_spiral_root_CTRL', u'R17_spiral_root_CTRL', u'R18_spiral_root_CTRL', u'R19_spiral_root_CTRL', u'R20_spiral_root_CTRL', u'R21_spiral_root_CTRL', u'R22_spiral_root_CTRL', u'R23_spiral_root_CTRL', u'R24_spiral_root_CTRL', u'R25_spiral_root_CTRL', u'R26_spiral_root_CTRL', u'R27_spiral_root_CTRL', u'R28_spiral_root_CTRL', u'R29_spiral_root_CTRL', u'R29_spiral_0_CTRL', u'R30_spiral_root_CTRL', u'R30_spiral_0_CTRL', u'R31_spiral_root_CTRL', u'R32_spiral_root_CTRL', u'R32_spiral_0_CTRL']
# r_geos = [u'L_leaf19_GEO', u'L_leaf18_GEO', u'L_leaf17_GEO', u'L_leaf16_GEO', u'FERM:L_leaf15_GEO', u'FERM:L_leaf14_GEO', u'FERM:L_leaf13_GEO', u'FERM:L_leaf12_GEO', u'FERM:L_leaf11_GEO', u'FERM:L_leaf10_GEO', u'FERM:L_leaf09_GEO', u'FERM:L_leaf08_GEO', u'FERM:L_leaf07_GEO', u'FERM:L_leaf06_GEO', u'FERM:L_leaf05_GEO', u'FERM:L_leaf04_GEO', u'FERM:L_leaf03_GEO', u'FERM:L_leaf02_GEO', u'FERM:L_leaf01_GEO']

def integer_conditions(attribute, num, name='vis'):
    dag = attribute.split('.')[0]
    conditions = []
    for i in range(num):
        condition = cmds.createNode('condition', name='{}_{}_{}_COND'.format(dag, name, i))
        conditions.append(condition)

        cmds.connectAttr(attribute, condition + '.firstTerm')
        cmds.setAttr(condition + '.secondTerm', i)
        cmds.setAttr(condition + '.colorIfTrueR', 1)
        cmds.setAttr(condition + '.colorIfFalseR', 0)
        cmds.setAttr(condition + '.operation', 3)

    return conditions


def coaster_visibility_unfold(attribute, dags):
    conds = integer_conditions(attribute, len(dags))
    for i, dag in enumerate(dags):
        cmds.connectAttr(conds[i] + '.outColorR', dag + '.v')


def remove_from_list(num_splits, list1):
    for each in list1:
        num = len(each.split('_'))
        if num > num_splits:
            list1.remove(each)
    return list1

# # strut_grps = []
# # for i in range(0, 50):
# #     c = 'strut_C_{}_GRP'.format(i)
# #     b = 'strut_B_{}_GRP'.format(i)
# #     a = 'strut_A_{}_GRP'.format(i)
# #
# #     strut_grps.append(c)
# #     strut_grps.append(b)
# #     strut_grps.append(a)
#
#
# strut_grps = cmds.ls('*:strutRig')
#
# c_tubes = cmds.ls('B_tube_*_GEO')
# l_tubes = cmds.ls('L_rail_*_GEO')
# r_tubes = cmds.ls('R_rail_*_GEO')
#
# c_tubes = tb.remove_from_list(4, c_tubes)
# l_tubes = tb.remove_from_list(4, l_tubes)
# r_tubes = tb.remove_from_list(4, r_tubes)
#
# tb.coaster_visibility_unfold('C_coaster_track_main_0_CTRL.buildVUnfold', strut_grps)
# tb.coaster_visibility_unfold('C_coaster_Lrail_main_0_CTRL.buildVUnfold', l_tubes)
# tb.coaster_visibility_unfold('C_coaster_Rrail_main_0_CTRL.buildVUnfold', r_tubes)
# tb.coaster_visibility_unfold('C_coaster_Crail_main_0_CTRL.buildVUnfold', c_tubes)
#
# struts = cmds.ls('C_strut_*_proxy_GEO')
# r_rails = cmds.ls('R_rail_*_proxy_GEO')
# l_rails = cmds.ls('L_rail_*_proxy_GEO')
# c_rails = cmds.ls('C_rail_*_proxy_GEO')
#
# tb.coaster_visibility_unfold('C_coaster_track_main_0_CTRL.buildVUnfold', struts)
# tb.coaster_visibility_unfold('C_coaster_Lrail_main_0_CTRL.buildVUnfold', l_rails)
# tb.coaster_visibility_unfold('C_coaster_Rrail_main_0_CTRL.buildVUnfold', r_rails)
# tb.coaster_visibility_unfold('C_coaster_Crail_main_0_CTRL.buildVUnfold', c_rails)


def add_enum(node, name, *args):
    '''Wrapper for making an enum attribute

    Args:
        node (str): node to add attribute to
        name (str): name of attribute
        *args: arguments that will be the enum names of the attribute
    Return:
         (str): attribute name
    '''

    enum_names = ''
    for i, arg in enumerate(args):
        if arg != args[-1]:
            enum_names += arg + ':'
        else:
            enum_names += arg

    cmds.addAttr(node,
                 shortName=name,
                 attributeType='enum',
                 enumName=enum_names,
                 keyable=True)

    return '{}.{}'.format(node, name)


def linspace_curve(curve, num):
    ''' Provide matrices that are an equal distribution along a curve

    Args:
        curve (str): name of curve to get information from
        num (int): number of matrices to be returned
    Return:
         list[om.MMatrix()]: list of matrices
    '''
    sel = om.MSelectionList()
    sel.add(curve)

    crv = om.MFnNurbsCurve()
    crv.setObject(sel.getDagPath(0))

    curve_length = crv.length()
    lengths = np.linspace(0, curve_length, num)

    matrices = []
    mscs = []

    for length in lengths:
        poci = cmds.createNode('pointOnCurveInfo')
        cm = cmds.createNode('composeMatrix')
        msc = cmds.createNode('millSimpleConstraint')
        mscs.append(msc)

        param = crv.findParamFromLength(length)
        if param == 0:
            param = .001
        if length == lengths[-1]:
            param -= .001

        cmds.connectAttr(curve + '.worldSpace[0]', poci + '.inputCurve')
        cmds.setAttr(poci + '.parameter', param)
        cmds.connectAttr(poci + '.position', cm + '.inputTranslate')
        cmds.connectAttr(cm + '.outputMatrix', msc + '.inMatrix')

        aim_vec = crv.tangent(param)
        side_vec = crv.normal(param)
        up_vec = aim_vec ^ side_vec
        pos = crv.getPointAtParam(param)

        mtx = maths.vectors_to_matrix(row1=aim_vec.normal(),
                                      row2=up_vec.normal(),
                                      row3=side_vec.normal(),
                                      row4=pos)
        matrices.append(mtx)

    return matrices, mscs


def gather_controls():
    namespace_ctrls = cmds.ls('*:*CTRL')
    regular_ctrls = cmds.ls('*CTRL')
    all_controls = namespace_ctrls + regular_ctrls
    num_ctrls = None
    ribbon_ctrls = []
    ctrl_order = {}
    for ctrl in all_controls:
        if cmds.ls(ctrl + '.ribbonCtrl'):
            i = cmds.getAttr(ctrl + '.ribbonCtrl')
            ctrl_order[i] = ctrl
        elif cmds.ls(ctrl + '.ribbonRoot'):
            num_ctrls = cmds.getAttr(ctrl + '.numControls')
    for i in range(len(ctrl_order)):
        ribbon_ctrls.append(ctrl_order[i])
    return ribbon_ctrls, num_ctrls


def reset_controls():
    ctrls, num_dags = gather_controls()

    for i, dag in enumerate(ctrls):
        ofs = dag + '_OFS'
        if cmds.ls(ofs + '.curveMSC'):
            msc = cmds.getAttr(ofs + '.curveMSC', asString=True)
            cmds.deleteAttr(ofs + '.curveMSC')
            cmds.delete(msc)
        cmds.setAttr(ofs + '.t', 0, 0, 0)
        cmds.setAttr(ofs + '.r', 0, 0, 0)
        cmds.setAttr(dag + '.r', 0, 0, 0)


def move_to_curve(curve):
    ctrls, num_dags = gather_controls()
    dags = []
    for i in range(num_dags):
        dags.append(ctrls[i])
    matrices, mscs = linspace_curve(curve, num_dags)

    if cmds.ls(ctrls[0] + '_OFS.curveMSC'):
        reset_controls()

    for i, dag in enumerate(dags):
        ofs = dag + '_OFS'
        cmds.connectAttr(ofs + '.parentInverseMatrix[0]', mscs[i] + '.parentInverseMatrix')
        cmds.connectAttr(mscs[i] + '.outTranslate', ofs + '.translate')

        cmds.xform(dag, matrix=matrices[i], ws=True)

        add_enum(ofs, 'curveMSC', mscs[i])


def attach_to_rig(bones, dag):
    ''' Attaches a dag to the nearest point of skinned geometry

    Args:
        name (str): base name of dags created in method
        geo (str): geometry to attach to
        dag (str): dag node to attach to the geometry
    Returns:
        str: name of follicle plane geo
    '''
    if cmds.ls(dag + '_parentConstraint1'):
        cmds.delete(dag + '_parentConstraint1')

    # find closest bones to the given dag node
    constrain_bones = []
    dag_pos = cmds.xform(dag, matrix=True, ws=True, q=True)
    distances = {}
    for bone in bones:
        bone_pos = cmds.xform(bone, matrix=True, ws=True, q=True)
        distance = maths.matrix_distance(dag_pos, bone_pos)
        distances[bone] = distance

    closest_bone = None
    for x in range(2):
        for bone, distance in distances.items():
            if not closest_bone:
                closest_bone = bone
            else:
                if distance < distances[closest_bone]:
                    closest_bone = bone
        constrain_bones.append(closest_bone)

    # constrain dag node to closest bones
    con = cmds.parentConstraint(constrain_bones[0], constrain_bones[1], dag, mo=True)
    print con


# # script for attaching fern dags to proxy geo
# import millrigger.modules.NY.misc.ryanf_scripts.util.control_shapes as cs
# import millrigger.modules.NY.misc.ryanf_scripts.create.dag as dag
# import millrigger.modules.NY.misc.ryanf_scripts.create.deform as deform
# import millrigger.modules.NY.misc.ryanf_scripts.create.nurbs as nrb
# import millrigger.modules.NY.misc.ryanf_scripts.util.attribute as attribute
# import millrigger.modules.NY.misc.ryanf_scripts.util.maths as maths
# import millrigger.modules.NY.misc.ryanf_scripts.testbed as tb
# import millrigger.modules.NY.misc.ryanf_scripts.tools.ribbonToCurve as rtc
#
# from rigging_utils import attribute as attr
# reload(cs)
# reload(dag)
# reload(attribute)
# reload(deform)
# reload(nrb)
# reload(maths)
# reload(tb)
# reload(rtc)
#
# for each in cmds.ls(sl=True):
#     zero = each + '_ZERO'
#     if cmds.ls(zero + '_parentConstraint1'):
#         cmds.delete(zero + '_parentConstraint1')
#     dag.dag_to_geo(zero, 'C_spiral_proxy_GEO')
#     attr.add_generic_blend(each, 'meshPosition')
#     mp = cmds.getAttr(zero + '.meshPosition')
#     cmds.connectAttr(each + '.meshPosition', zero + '.meshPosition')
#     cmds.setAttr(each + '.meshPosition', mp)

# # create 100 locators down a value in Z
# lengths = np.linspace(0, 68.853, 150)
# jnts = []
# matrices = []
# for i, each in enumerate(lengths):
#     mtx = maths.vectors_to_matrix(row4=(0, 0, each))
#     matrices.append(mtx)
# curves.curve_from_matrices(matrices, name='C_ribbon_CRV', degree=1)
# for i, each in enumerate(lengths):
#     cmds.select(clear=True)
#     jnt = cmds.joint(name='C_ribbon_{}_CRV_BONE'.format(i))
#     cmds.xform(jnt, t=(0, 0, each))
#     jnts.append(jnt)
#
#
# locs = cmds.ls(sl=True)
# matrices = nrb.linspace_curve('C_ribbon_CRV', 150)
# for i, mtx in enumerate(matrices):
#     pos = maths.get_matrix_position(mtx)
#     cmds.xform(locs[i], t=(pos[0], pos[1], pos[2]))

# stored_values = {}
# controls = cmds.ls('PRBR:C_ribbon_main_*_CTRL')
# for ctrl in controls:
#     ctrl_values = {}
#     pos = cmds.

def closest_vtx_on_mesh(geo, point):
    obj = om.MSelectionList()
    obj.add(geo)
    mesh = om.MFnMesh(obj.getComponent(0)[0])

    pos = om.MPoint(point[0], point[1], point[2])
    point, normal, face = mesh.getClosestPointAndNormal(pos, space=4)
    face = '{}.f[{}]'.format(geo, face)
    vertices = cmds.polyListComponentConversion(face, tv=True)
    vertices = cmds.ls(vertices, fl=True)
    start_pos = om.MVector(point[0], point[1], point[2])
    # find which vertex has the same position as the given point
    shortest_distance = None
    closest_vtx = None
    for i, vtx in enumerate(vertices):
        pos = cmds.xform(vtx, t=True, ws=True, q=True)
        end_pos = om.MVector(pos[0], pos[1], pos[2])
        distance = (start_pos - end_pos).length()
        if not closest_vtx:
            shortest_distance = distance
            closest_vtx = vtx
        elif distance < shortest_distance:
            shortest_distance = distance
            closest_vtx = vtx
        if distance == 0:
            break
    return closest_vtx


def populate_among_plane(surface, dag, num):
    sel = om.MSelectionList()
    sel.add(surface)

    plane = om.MFnNurbsSurface()
    plane.setObject(sel.getDagPath(0))

    params = np.linspace(0, 1, num)

    new_dags = []
    for par in params:
        new_dag = cmds.duplicate(dag)[0]
        pos = plane.getPointAtParam(0.5, par)
        cmds.xform(new_dag, t=(pos[0], pos[1], pos[2]), ws=True)
        new_dags.append(new_dag)

    for dag in new_dags:
        nrb.attach_to_surface(surface, dag, snap=True)


def create_locs():
    for each in cmds.ls(sl=True):
        name = each + '_LOC'
        loc = cmds.spaceLocator(name=name)[0]
        pos = cmds.xform(each, t=True, ws=True, q=True)
        rot = cmds.xform(each, ro=True, ws=True, q=True)

        cmds.xform(loc, t=pos, ws=True)
        cmds.xform(loc, ro=rot, ws=True)


def move_to_locs():
    for each in cmds.ls(sl=True):
        handle = each.split('_LOC')[0]
        pos = cmds.xform(each, t=True, ws=True, q=True)
        rot = cmds.xform(each, ro=True, ws=True, q=True)

        cmds.xform(handle, t=pos, ws=True)
        cmds.xform(handle, ro=rot, ws=True)
