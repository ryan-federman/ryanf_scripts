import pymel.core as pm
import maya.api.OpenMaya as om
import maya.cmds as cmds

numJntCreate = 15
numCtrlCreate = 3

rig = 'tail'


class dagCreate():
    def __init__(self, rig):
        self.begCtrl = None
        self.endCtrl = None
        self.begLoc = None
        self.endLoc = None

        self.jointList = []
        self.rotBSjointList = []
        self.transBSjointList = []

        self.boneFollList = []
        self.bonefollTransformList = []
        self.ctrlFollList = []
        self.ctrlfollTransformList = []

        self.rigName = rig

    # control for translation
    def transCTRL(self, numCTRL):
        shapeList = []
        emptyTransformList = []
        CTRL = cmds.createNode('transform', name = self.rigName + '_' +
                               str(numCTRL) + '_translate_CTRL')
        cmds.addAttr(CTRL, at='float', min=0, max=10, sn='ctrlPosition',
                     keyable=True)
        cmds.addAttr(CTRL, at='float', min=0, max=10, sn='falloff',
                     keyable=True)
        cmds.addAttr(CTRL, at='float', min=0, max=5, sn='multiplier',
                     keyable=True)
        cmds.addAttr(CTRL, at='float', sn='numberJoints', keyable=True)
        for x in range(0, 4):
            ctrl = cmds.circle()[0]
            emptyTransformList.append(ctrl)
            shape = cmds.listRelatives(ctrl, shapes = True)[0]
            shapeList.append(shape)
            conn = cmds.listConnections(shape, source = True)[0]

            cmds.setAttr(conn + '.degree', 1)
            cmds.setAttr(conn + '.sections', 3)
            cmds.setAttr(ctrl + '.rotateY', 90)
            cmds.setAttr(ctrl + '.scale', 0.386833, 0.386833, 0.386833)
            cmds.makeIdentity(ctrl, apply = True)
            if x == 0:
                cmds.setAttr(ctrl + '.translateY', 1.322)
                cmds.makeIdentity(ctrl, apply = True)
            elif x == 1:
                cmds.setAttr(ctrl + '.rotateX', 90)
                cmds.setAttr(ctrl + '.translateZ', 1.322)
                cmds.makeIdentity(ctrl, apply = True)
            elif x == 2:
                cmds.setAttr(ctrl + '.rotateX', 180)
                cmds.setAttr(ctrl + '.translateY', -1.322)
                cmds.makeIdentity(ctrl, apply = True)
            elif x == 3:
                cmds.setAttr(ctrl + '.rotateX', -90)
                cmds.setAttr(ctrl + '.translateZ', -1.322)
                cmds.makeIdentity(ctrl, apply = True)

        for each in shapeList:
            cmds.parent(each, CTRL, shape = True, r = True)
        for each in emptyTransformList:
            cmds.delete(each)
        cmds.delete(CTRL, ch = True)
        return(CTRL)

    # controls for setting up the rig
    def rigPosition(self):

        # create the controls and locators
        self.begCtrl = cmds.polyCube(name=rig + '_begOfChain_CTRL')[0]
        cmds.select(self.begCtrl + '.vtx[0:7]')
        cmds.scale(1.939412, 1.939412, 1.939412)
        cmds.delete(self.begCtrl, ch=True)

        self.endCtrl = cmds.polyCube(name=rig + '_endOfChain_CTRL')[0]
        cmds.select(self.endCtrl + '.vtx[0:7]')
        cmds.scale(1.939412, 1.939412, 1.939412)
        cmds.delete(self.endCtrl, ch=True)

        self.begLoc = cmds.spaceLocator(name=rig + '_begOfChain_LOC')[0]
        cmds.setAttr(self.begLoc + '.rotateOrder', 5)
        self.endLoc = cmds.spaceLocator(name=rig + '_endOfChain_LOC')[0]

        # make the 'controls' invisible
        ctrlShader = cmds.shadingNode('lambert', asShader=True,
            name='invisCtrl_shader')
        shaderSet = cmds.sets(renderable=True, noSurfaceShader=True, empty=True,
            name='invisCtrl_shader_SG')
        cmds.connectAttr(ctrlShader + '.outColor', shaderSet + '.surfaceShader',
            f=True)
        cmds.setAttr(ctrlShader + '.transparency', 1, 1, 1)

        cmds.select(self.begCtrl)
        cmds.select(self.endCtrl, add=True)
        cmds.select(ctrlShader, add=True)
        cmds.sets(e=True, forceElement=shaderSet)
        cmds.select(clear=True)

        ctrls = [self.begCtrl, self.endCtrl]
        for each in ctrls:
            cmds.setAttr(each + 'Shape' + '.castsShadows', 0)
            cmds.setAttr(each + 'Shape' + '.receiveShadows', 0)
            cmds.setAttr(each + 'Shape' + '.motionBlur', 0)
            cmds.setAttr(each + 'Shape' + '.primaryVisibility', 0)
            cmds.setAttr(each + 'Shape' + '.smoothShading', 0)
            cmds.setAttr(each + 'Shape' + '.visibleInReflections', 0)
            cmds.setAttr(each + 'Shape' + '.visibleInRefractions', 0)
            cmds.setAttr(each + 'Shape' + '.doubleSided', 0)

        # parent the locators under the controls and then aim the locators at
        #  each other
        cmds.parent(self.begLoc, self.begCtrl)
        cmds.parent(self.endLoc, self.endCtrl)

        cmds.setAttr(self.begCtrl + '.translateX', -5)
        cmds.setAttr(self.endCtrl + '.translateX', 5)

        cmds.aimConstraint(self.begCtrl, self.endLoc, aimVector=(-1, 0, 0),
            upVector=(0, 1, 0), worldUpType='scene')
        cmds.aimConstraint(self.endCtrl, self.begLoc, aimVector=(1, 0, 0),
            upVector=(0, 1, 0), worldUpType='scene')

        cmds.setAttr(self.begLoc + '.overrideEnabled', 1)
        cmds.setAttr(self.begLoc + '.overrideDisplayType', 2)
        cmds.setAttr(self.endLoc + '.overrideEnabled', 1)
        cmds.setAttr(self.endLoc + '.overrideDisplayType', 2)

        # create curve to visualize the chain
        crv = cmds.curve(p=[(-1, 0, 0), (1, 0, 0)], d=1, ws=True,
            name=self.rigName + '_CRV')
        cmds.connectAttr(self.begLoc + '.worldPosition',
            crv + '.controlPoints[0]')
        cmds.connectAttr(self.endLoc + '.worldPosition',
            crv + '.controlPoints[1]')
        cmds.setAttr(crv + '.overrideEnabled', 1)
        cmds.setAttr(crv + '.overrideDisplayType', 2)

    def jointConnections(self, CTRL, numCTRL, jointTx, function, jointList):
        joints = jointList
        numJoints = len(joints)

        # get number of joints affected by factoring in the falloff
        numJointsMult = cmds.createNode('multiplyDivide',
            name=CTRL + '_numJoint_MULT')
        numJointsSetRange = cmds.createNode('setRange',
            name=CTRL + '_numJoint_setRange')
        falloffRemap = cmds.createNode('math_Multiply',
            name=CTRL + '_falloffRemap_MULT')

        cmds.connectAttr(CTRL + '.falloff', falloffRemap + '.input1')

        cmds.connectAttr(falloffRemap + '.output', numJointsMult + '.input1X')
        cmds.setAttr(numJointsMult + '.input2X', 2)

        cmds.connectAttr(numJointsMult + '.outputX',
            numJointsSetRange + '.valueX')
        cmds.setAttr(numJointsSetRange + '.oldMinX', 0)
        cmds.setAttr(numJointsSetRange + '.oldMaxX', 1)
        cmds.setAttr(numJointsSetRange + '.minX', 1)
        cmds.setAttr(numJointsSetRange + '.maxX', (numJoints + 1))

        cmds.connectAttr(numJointsSetRange + '.outValueX',
            CTRL + '.numberJoints')

        # create node for controls position in uv space
        ctrlPosDiv = cmds.createNode('multiplyDivide',
            name=CTRL + '_ctrlPos_DIV')
        cmds.connectAttr(CTRL + '.ctrlPosition', ctrlPosDiv + '.input1X')
        cmds.setAttr(ctrlPosDiv + '.input2X', 10)
        cmds.setAttr(ctrlPosDiv + '.operation', 2)

        for x in range(0, numJoints):
            jnt = jointList[x]
            cmds.select(jnt + '_' + str(numCTRL) + '_srt')
            jntSRT = cmds.ls(sl=True)[0]
            cmds.select(clear=True)

            # get position of joint along the nurbs surface
            jointPos = x / float(numJoints - 1)
            cmds.setAttr(jnt + '.jointPos', jointPos)

            # get distance between control and joint
            distance = cmds.createNode('plusMinusAverage',
                name=jnt + '_' + str(numCTRL) + '_distance_PMA')
            distanceABS = cmds.createNode('math_Absolute',
                name=jnt + '_' + str(numCTRL) + '_distance_ABSvalue')

            cmds.connectAttr(ctrlPosDiv + '.outputX', distance + '.input1D[0]')
            cmds.connectAttr(jnt + '.jointPos', distance + '.input1D[1]')
            cmds.setAttr(distance + '.operation', 2)

            cmds.connectAttr(distance + '.output1D', distanceABS + '.input')

            # get the percentage of the way that the distance is to the end
            # of the falloff and reverse it
            distDivFalloff = cmds.createNode('multiplyDivide',
                name=jnt + '_' + str(numCTRL) + '_distDivFalloff_DIV')
            distDivFalloffReverse = cmds.createNode('reverse',
                name=jnt + '_' + str(numCTRL) + '_distDivFalloff_reverse')

            cmds.connectAttr(distanceABS + '.output',
                distDivFalloff + '.input1X')
            cmds.setAttr(falloffRemap + '.input2', .05)

            cmds.connectAttr(falloffRemap + '.output',
                distDivFalloff + '.input2X')
            cmds.setAttr(distDivFalloff + '.operation', 2)

            cmds.connectAttr(distDivFalloff + '.outputX',
                distDivFalloffReverse + '.inputX')

            networkFunction = [function]
            for fun in networkFunction:
                # apply multiplier to the control's rotation or translation
                # and then feed it into the joint's srt

                multiplier = cmds.createNode('math_MultiplyVector',
                    name=jnt + '_' + str(numCTRL) + '_' + fun + '_multiplier_MULT')
                divByAmtOfJnts = cmds.createNode('multiplyDivide',
                    name=jnt + '_' + str(numCTRL) + '_' + fun + '_numJoints_DIV')
                rotTimesTwo = cmds.createNode('math_MultiplyVector',
                    name=jnt + '_' + str(numCTRL) + '_' + fun + '_rotTimesTwo_MULT')
                lessThanFalloffCond = cmds.createNode('condition',
                    name=jnt + '_' + str(numCTRL) + '_' + fun + '_lessThanFalloff_COND')
                moreThanFalloffCond = cmds.createNode('condition',
                    name=jnt + '_' + str(numCTRL) + '_' + fun + '_moreThanFalloff_COND')
                lowerFalloffPos = cmds.createNode('plusMinusAverage',
                    name=jnt + '_' + str(numCTRL) + '_' + fun + '_lowerFalloffPos_PMA')
                higherFalloffPos = cmds.createNode('plusMinusAverage',
                    name=jnt + '_' + str(numCTRL) + '_' + fun + '_higherFalloffPos_PMA')

                cmds.connectAttr(distDivFalloffReverse + '.outputX', multiplier + '.input2')

                cmds.connectAttr(CTRL + '.' + fun, multiplier + '.input1')

                cmds.connectAttr(multiplier + '.output', divByAmtOfJnts + '.input1')
                cmds.connectAttr(CTRL + '.numberJoints', divByAmtOfJnts + '.input2X')
                cmds.connectAttr(CTRL + '.numberJoints', divByAmtOfJnts + '.input2Y')
                cmds.connectAttr(CTRL + '.numberJoints', divByAmtOfJnts + '.input2Z')
                cmds.setAttr(divByAmtOfJnts + '.operation', 2)

                cmds.connectAttr(divByAmtOfJnts + '.output', rotTimesTwo + '.input1')
                cmds.setAttr(rotTimesTwo + '.input2', 2)

                cmds.connectAttr(ctrlPosDiv + '.outputX', lowerFalloffPos + '.input1D[0]')
                cmds.connectAttr(falloffRemap + '.output', lowerFalloffPos + '.input1D[1]')
                cmds.setAttr(lowerFalloffPos + '.operation', 2)

                cmds.connectAttr(ctrlPosDiv + '.outputX', higherFalloffPos + '.input1D[0]')
                cmds.connectAttr(falloffRemap + '.output', higherFalloffPos + '.input1D[1]')
                cmds.setAttr(higherFalloffPos + '.operation', 1)

                cmds.connectAttr(CTRL + '.multiplier', rotTimesTwo + '.input2')


                cmds.connectAttr(rotTimesTwo + '.output', lessThanFalloffCond + '.colorIfFalse')

                cmds.connectAttr(lowerFalloffPos + '.output1D', lessThanFalloffCond + '.firstTerm')
                cmds.connectAttr(jnt + '.jointPos', lessThanFalloffCond + '.secondTerm')
                cmds.setAttr(lessThanFalloffCond + '.operation', 2)

                cmds.connectAttr(lessThanFalloffCond + '.outColor', moreThanFalloffCond + '.colorIfFalse')
                cmds.connectAttr(higherFalloffPos + '.output1D', moreThanFalloffCond + '.firstTerm')
                cmds.connectAttr(jnt + '.jointPos', moreThanFalloffCond + '.secondTerm')
                cmds.setAttr(moreThanFalloffCond + '.operation', 4)

                if fun == 'translate':
                    transOFS = cmds.createNode('plusMinusAverage', name = jnt
                                               + '_' + str(numCTRL) + '_transOFS')
                    OFS = cmds.getAttr(jntSRT + '.t')[0]
                    cmds.setAttr(transOFS + '.input3D[1].input3Dx', OFS[0])
                    cmds.setAttr(transOFS + '.input3D[1].input3Dy', OFS[1])
                    cmds.setAttr(transOFS + '.input3D[1].input3Dz', OFS[2])

                    cmds.connectAttr(moreThanFalloffCond + '.outColor', transOFS + '.input3D[0]')
                    cmds.connectAttr(transOFS + '.output3D', jntSRT + '.translate')

                if fun == 'rotate':
                    rotOFS = cmds.createNode('plusMinusAverage', name = jnt
                                               + '_' + str(numCTRL) + '_rotOFS')
                    OFS = cmds.getAttr(jntSRT + '.rotate')[0]
                    cmds.setAttr(rotOFS + '.input3D[1].input3Dx', OFS[0])
                    cmds.setAttr(rotOFS + '.input3D[1].input3Dy', OFS[1])
                    cmds.setAttr(rotOFS + '.input3D[1].input3Dz', OFS[2])

                    cmds.connectAttr(moreThanFalloffCond + '.outColor', rotOFS + '.input3D[0]')
                    cmds.connectAttr(rotOFS + '.output3D', jntSRT + '.rotate')

            cmds.setAttr(CTRL + '.multiplier', 2)
            cmds.setAttr(CTRL + '.falloff', 5)

    def createJointHierarchy(self, jointList, numJnt, numCtrls, type, jointTx, offset):
        # create joints
        for x in range(0, numJnt):
            cmds.select(clear=True)
            jnt = cmds.joint(name=self.rigName + '_' + str(x) + type + '_BONE')
            cmds.addAttr(at='float', sn='jointPos')
            jointList.append(jnt)
            for y in range(0, numCtrls):
                if y == 0:
                    grp = cmds.createNode('transform', name=str(jnt) + '_' + str(y) + '_srt')
                    cmds.setAttr(grp + '.rotateOrder', 5)
                    parGrp = grp
                    if x > 0:
                        cmds.parent(grp, parJnt)
                else:
                    grp = cmds.createNode('transform', name=str(jnt) + '_' + str(y) + '_srt')
                    cmds.setAttr(grp + '.rotateOrder', 5)
                    cmds.parent(grp, parGrp)
                    parGrp = grp
            cmds.parent(jnt, parGrp)
            parJnt = jnt

        # offset joints to fill space between locators
        x = 0
        for each in jointList:
            if x == 0:
                grp = each + '_0_srt'
                pos = cmds.xform(self.begLoc, t=True, ws=True, query=True)
                rot = cmds.xform(self.begLoc, ro=True, r=True, query=True)

                pos = [pos[0], pos[1], (pos[2] + offset)]
                cmds.xform(grp, t=pos, ws=True)
                cmds.xform(grp, ro=rot, ws=True)
                x += 1
            else:
                grp = str(jointList[x]) + '_0_srt'
                cmds.setAttr(grp + '.tx', jointTx)
                x += 1

    def createFollicle(self, numObjs, fun, follList, follTransformList, nrbsPlane):
        for x in range(0, numObjs):
            foll = cmds.createNode('follicle', name=self.rigName + '_'  + fun + '_' + str(x) + '_follicle')
            follList.append(foll)

            nurbsPlnShape = cmds.listRelatives(nrbsPlane, children=True, shapes=True)[0]
            follTransform = cmds.listRelatives(foll, parent=True)[0]
            follTransform = cmds.rename(follTransform, foll + '_srt')
            follTransformList.append(follTransform)

            cmds.connectAttr(nurbsPlnShape + '.local', foll + '.inputSurface')
            cmds.connectAttr(nurbsPlnShape + '.worldMatrix[0]', foll + '.inputWorldMatrix')
            cmds.connectAttr(foll + '.outRotate', follTransform + '.rotate')
            cmds.connectAttr(foll + '.outTranslate', follTransform + '.translate')

            if numObjs == 1:
                parU = 0
            else:
                parU = float(x) / (numObjs - 1)
            cmds.setAttr(foll + '.parameterU', parU)
            cmds.setAttr(foll + '.parameterV', .5)

    def jointSetup(self, numJnt, numCtrls):
        self.jointList = []
        self.rotBSjointList = []
        self.transBSjointList = []

        # get length of vector between the two locators
        pos1, pos2 = cmds.xform(self.begLoc, t=1, ws=1, q=1), cmds.xform(self.endLoc, t=1, ws=1, q=1)
        v1, v2 = om.MVector(pos1), om.MVector(pos2)
        v = v1 - v2
        magnitude = float(om.MVector(v).length())
        jointTx = float(magnitude / float(numJnt - 1))

        self.createJointHierarchy(self.jointList, numJnt, numCtrls, '', jointTx, 0)
        self.createJointHierarchy(self.rotBSjointList, numJnt, numCtrls, '_rotBS', jointTx, 4)
        self.createJointHierarchy(self.transBSjointList, numJnt, numCtrls, '_transBS', jointTx, 8)

        # create curves to loft a surface between them
        posList = []
        for each in self.jointList:
            v = cmds.xform(each, t=1, ws=1, query=1)
            posList.append(v)
        endCurve = len(posList) - 1
        crv1 = cmds.curve(d=1, name=self.rigName + '_01_CRV',
            p=[(posList[0]), (posList[1])])
        for x in range(2, endCurve + 1):
            tempCrv = cmds.curve(crv1, os=True, a=True, p=(posList[x]))
        crv2 = cmds.duplicate(crv1, name=self.rigName + '_02_CRV')[0]

        # move the curves and loft a surface between them
        cmds.parent(crv1, self.jointList[0])
        cmds.parent(crv2, self.jointList[0])
        pos1 = cmds.getAttr(crv1 + '.translate')[0]
        pos2 = cmds.getAttr(crv2 + '.translate')[0]
        cmds.xform(crv1, t=(pos1[0], pos1[1], (pos1[2] + 1)))
        cmds.xform(crv2, t=(pos2[0], pos2[1], (pos2[2] - 1)))

        cmds.parent(crv1, w=True)
        cmds.parent(crv2, w=True)

        nrbsPlane = cmds.loft(crv1, crv2, d=3, rsn=True, name=self.rigName + '_nrbsPlane')[0]
        cmds.rebuildSurface(nrbsPlane, ch=1, rpo=1, kr=0, kc=0, su=0, sv=0)
        cmds.select(clear=True)

        # create nurbs planes for blendshapes of main nurbs plane
        rotNrbsPlane = cmds.duplicate(nrbsPlane, name = self.rigName + '_rotBS_nrbsPlane')[0]
        transNrbsPlane = cmds.duplicate(nrbsPlane, name = self.rigName + '_transBS_nrbsPlane')[0]
        cmds.setAttr(rotNrbsPlane + '.translateZ', 4)
        cmds.setAttr(transNrbsPlane + '.translateZ', 8)
        cmds.delete(crv1)
        cmds.delete(crv2)

        # bind blendshape joints to nurbs blendshape geo
        cmds.skinCluster(self.rotBSjointList, rotNrbsPlane, mi = 1)
        cmds.skinCluster(self.transBSjointList, transNrbsPlane, mi = 1)

        # make blendshapes for nurbs planes
        blendshape = cmds.blendShape(rotNrbsPlane, nrbsPlane, n = self.rigName + '_blendshape')
        cmds.blendShape( blendshape, e= True, t = (nrbsPlane, 1, transNrbsPlane, 1))
        cmds.blendShape(blendshape, e = True, w = (0, 1.0))
        cmds.blendShape(blendshape, e = True, w = (1, 1.0))

        # create follicle for bones and then put the bones under the follicles
        self.createFollicle(numJnt, 'BONE', self.boneFollList, self.bonefollTransformList, nrbsPlane)
        for x in range(0, len(self.jointList)):
            jointSrt = self.jointList[x] + '_0_srt'
            cmds.parent(jointSrt, self.bonefollTransformList[x])

        # create follicles for controls
        self.createFollicle(numCtrls, 'CTRL', self.ctrlFollList, self.ctrlfollTransformList, nrbsPlane)

        transCtrlList = []
        # create controls and connect them to their follicles
        for x in range(0, numCtrls):
            ctrl = cmds.circle(name=self.rigName + '_' + str(x) + '_CTRL')[0]
            translateCTRL = self.transCTRL(x)
            translateSrt = cmds.createNode('transform', name=translateCTRL + '_srt')
            transCtrlList.append(translateSrt)
            srt = cmds.createNode('transform', name=ctrl + '_srt')

            # attach translate control's position to rotation control
            cmds.parent(translateCTRL, translateSrt)
            MSC = cmds.createNode('millSimpleConstraint', name = translateSrt + '_MSC')
            cmds.connectAttr(ctrl + '.worldMatrix[0]', MSC + '.inMatrix')
            cmds.connectAttr(translateSrt + '.parentInverseMatrix', MSC + '.parentInverseMatrix')
            cmds.connectAttr(MSC + '.outTranslate', translateSrt + '.translate')

            # setup basic control, add attributes
            shape = cmds.listRelatives(ctrl, children=True, shapes=True)[0]
            try:
                conn = cmds.listConnections(shape, source=True)[0]
                cmds.delete(conn)
            except:
                pass
            cmds.setAttr(ctrl + '.rotateY', 90)
            cmds.makeIdentity(ctrl, apply=True)
            cmds.parent(ctrl, srt)

            cmds.addAttr(ctrl, at='float', min=0, max=10, sn='ctrlPosition',
                keyable=True)
            cmds.addAttr(ctrl, at='float', min=0, max=10, sn='falloff',
                keyable=True)
            cmds.addAttr(ctrl, at='float', min=0, max=5, sn='multiplier',
                keyable=True)
            cmds.addAttr(ctrl, at='float', sn='numberJoints', keyable=True)

            # move ctrl into position and connect to follicle
            pos = cmds.xform(self.ctrlfollTransformList[x], t=True, ws=True,
                query=True)
            cmds.xform(srt, t=pos, ws=True)
            cmds.parent(srt, self.ctrlfollTransformList[x])
            cmds.setAttr(srt + '.rotate', 90, 0, 0)

            follPosition = cmds.getAttr(self.ctrlFollList[x] + '.parameterU')
            follPosition = follPosition * 10
            cmds.setAttr(ctrl + '.ctrlPosition', follPosition)

            posMultNode = cmds.createNode('multiplyDivide', name=self.rigName +
                                          '_ctrlPosition_' + str(x) + '_MULT')

            cmds.connectAttr(ctrl + '.ctrlPosition', posMultNode + '.input1X')
            cmds.connectAttr(ctrl + '.ctrlPosition', translateCTRL + '.ctrlPosition')
            cmds.setAttr(posMultNode + '.input2X', 10)
            cmds.setAttr(posMultNode + '.operation', 2)

            cmds.connectAttr(posMultNode + '.outputX', self.ctrlFollList[x] + '.parameterU')

            # lock unused attributes on controls
            cmds.setAttr(ctrl + '.translateX', l=True, k=False, cb=False)
            cmds.setAttr(ctrl + '.translateY', l=True, k=False, cb=False)
            cmds.setAttr(ctrl + '.translateZ', l=True, k=False, cb=False)
            cmds.setAttr(ctrl + '.scaleX', l=True, k=False, cb=False)
            cmds.setAttr(ctrl + '.scaleY', l=True, k=False, cb=False)
            cmds.setAttr(ctrl + '.scaleZ', l=True, k=False, cb=False)
            cmds.setAttr(ctrl + '.visibility', l=True, k=False, cb=False)
            cmds.setAttr(ctrl + '.numberJoints', k=False, cb=False)

            cmds.setAttr(translateCTRL + '.rotateX', l=True, k=False, cb=False)
            cmds.setAttr(translateCTRL + '.rotateY', l=True, k=False, cb=False)
            cmds.setAttr(translateCTRL + '.rotateZ', l=True, k=False, cb=False)
            cmds.setAttr(translateCTRL + '.scaleX', l=True, k=False, cb=False)
            cmds.setAttr(translateCTRL + '.scaleY', l=True, k=False, cb=False)
            cmds.setAttr(translateCTRL + '.scaleZ', l=True, k=False, cb=False)
            cmds.setAttr(translateCTRL + '.visibility', l=True, k=False, cb=False)
            cmds.setAttr(translateCTRL + '.numberJoints', k=False, cb=False)
            cmds.setAttr(translateCTRL + '.ctrlPosition', k=False, cb=False)

            # connect control transformations to joints
            self.jointConnections(ctrl, x, jointTx, 'rotate', self.rotBSjointList)
            self.jointConnections(translateCTRL, x, jointTx, 'translate', self.transBSjointList)

        # create main control for rig
        masterCtrl = cmds.circle(name=self.rigName + '_main_CTRL')[0]
        cmds.delete(masterCtrl, ch = True)
        masterCtrlSrt = cmds.createNode('transform', name=masterCtrl + '_srt')
        cmds.parent(masterCtrl, masterCtrlSrt)
        pos = cmds.xform(self.begLoc, t=True, ws=True, query=True)
        rot = cmds.xform(self.begLoc, ro=True, ws=True, query=True)
        cmds.xform(masterCtrlSrt, ws=True, t=(pos[0], pos[1], pos[2]))
        cmds.xform(masterCtrlSrt, ws=True, ro=(rot[0], rot[1], rot[2]))

        cmds.parent(nrbsPlane, masterCtrl)
        for each in transCtrlList:
            cmds.parent(each, masterCtrl)
        for each in self.jointList:
            cmds.scaleConstraint(masterCtrl, each, mo=True)




poop = dagCreate(rig)

poop.rigPosition()

poop.jointSetup(numJntCreate, numCtrlCreate)
