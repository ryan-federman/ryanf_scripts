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

    def nurbs_plane(self, dags, name):
        mtxs = []
        for each in dags:
            mtx = cmds.xform(each, matrix=True, ws=True, q=True)
            mtxs.append(mtx)
        mtx1 = om.MMatrix()
        mtx1.setElement(3, 2, 2)
        mtx2 = om.MMatrix()
        mtx2.setElement(3, 2, -2)

        prof_crv1 = curves.curve_from_matrices(mtxs, name=name + '_prof1_CRV', degree=2)
        prof_crv2 = curves.curve_from_matrices(mtxs, name=name + '_prof2_CRV', degree=2)

        rail_crv1 = curves.curve_from_matrices([mtx1, mtx2], name=name + '_rail1_CRV', degree=1)
        rail_crv2 = curves.curve_from_matrices([mtx1, mtx2], name=name + '_rail2_CRV', degree=1)

        # cmds.xform(prof_crv1, t=(0, 0, 2), ws=True)
        # cmds.xform(prof_crv2, t=(0, 0, -2), ws=True)
        # cmds.xform(rail_crv1, matrix=mtxs[0], ws=True)
        # cmds.xform(rail_crv2, matrix=mtxs[-1], ws=True)

        plane = cmds.doubleProfileBirailSurface(prof_crv1,
                                                prof_crv2,
                                                rail_crv1,
                                                rail_crv2,
                                                po=0,
                                                name=name)

        constraint.simple_constraint(dags[0], rail_crv1)
        constraint.simple_constraint(dags[-1], rail_crv2)

        for x, each in enumerate(dags):
            scon1 = cmds.createNode("millSimpleConstraint", name=prof_crv1 + '_MSC')
            scon2 = cmds.createNode("millSimpleConstraint", name=prof_crv1 + '_MSC')

            cmds.connectAttr(each + '.worldMatrix[0]', scon1 + '.inMatrix')
            cmds.connectAttr(each + '.parentInverseMatrix[0]', scon1 + '.parentInverseMatrix')

            cmds.connectAttr(each + '.worldMatrix[0]', scon2 + '.inMatrix')
            cmds.connectAttr(each + '.parentInverseMatrix[0]', scon2 + '.parentInverseMatrix')

            cmds.setAttr(scon1 + '.translateOffset', 0, 0, 2)
            cmds.setAttr(scon2 + '.translateOffset', 0, 0, -2)

            cmds.connectAttr(scon1 + '.outTranslate', prof_crv1 + '.cv[{}]'.format(x))
            cmds.connectAttr(scon2 + '.outTranslate', prof_crv2 + '.cv[{}]'.format(x))

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
                plane = self.nurbs_plane(prev_ctrls, name=plane_name)
                # plane = self.create_nurbs_plane(self.dag_pos, name=plane_name, sections=pln_sections)
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

                # # bind plane to control bones
                # cmds.skinCluster(bind_objs, name=plane[0] + '_SKC')

            prev_ctrls = ctrls[1]
            prev_bones = ctrl_bones
            ctrl_bones = []

        # constrain bones to plane for last controls
        pln_sections = len(prev_ctrls) - 1
        foll_sections = len(bones[1])
        plane_name = '{}_{}_PLN'.format(self.name, 'BONE')
        plane = self.nurbs_plane(prev_ctrls, name=plane_name)
        # plane = self.create_nurbs_plane(self.dag_pos, name=plane_name, sections=pln_sections)
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

        # # bind plane to control bones
        # cmds.skinCluster(bind_objs, name=plane[0] + '_SKC')

        # for each in controls[0][2]:
        #     self.attach_to_path(self.motion_path, each, 1)
        # for each in controls[1][2]:
        #     self.attach_to_path(self.motion_path, each, 2)
        # for each in controls[2][2]:
        #     self.attach_to_path(self.motion_path, each, 3)

        # organize outliner
        for each in controls:
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
