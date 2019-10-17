import pymel.core as pm
import maya.cmds as cmds


class eyeLidSetup:

    def __init__(self, rig_name):
        self.locList = []
        self.locNum = 0

        self.jntList = []

        self.mainCtrlJnt = ''
        self.mainCtrlJntSrt = ''

        self.midACtrlJnt = ''
        self.midACtrlJntSrt = ''

        self.midBCtrlJntSrt = ''
        self.midBCtrlJnt = ''

        self.begCtrlJntSrt = ''
        self.begCtrlJnt = ''

        self.endCtrlJntSrt = ''
        self.endCtrlJnt = ''

        self.rig_name = rig_name

    def create_starter_locs(self):
        self.starter_loc_list = []
        list = cmds.ls(sl = True, fl=True)
        for each in list:
            pos = cmds.xform(each, t=True, ws=True, query=True)
            loc = cmds.spaceLocator()
            cmds.xform(loc, t=(pos[0], pos[1], pos[2]))
            self.starter_loc_list.append(loc)

    def create_curve(self):
        vtx_list = cmds.ls(sl=True)
        print vtx_list

        # create curve with a cv at each vertex
        pos_list = []
        crv_list = []
        for each in vtx_list:
            v = cmds.xform(each, t=1, ws=1, query=1)
            pos_list.append(v)
        end_curve = len(pos_list) - 1

        crv1 = cmds.curve(d=1,
                          name=self.rig_name + '_EL_CRV',
                          p=[(pos_list[0]), (pos_list[1])])
        for x in range(2, end_curve + 1):
            pos = pos_list[x]
            print pos
            cmds.curve(crv1, os=True, a=True, p=(pos[0], pos[1], pos[2]))
        crv_list.append(crv1)
        cmds.select(clear = True)

        for each in self.starter_loc_list:
            cmds.delete(each)
        return crv1


    #create locators for each cv
    def createLoc(self, side, topBot, crv):
        degs = pm.getAttr( crv + '.degree' )
        spans = pm.getAttr( crv + '.spans' )
        cvs = degs+spans

        for x in range(0, cvs):
            each = crv + '.cv[' + str(x) + ']'

            pos = pm.xform(each, t = True, ws = True, query = True)
            loc = pm.spaceLocator(name = side + '_' + topBot + 'El_' + str(self.locNum) + '_LOC')
            self.locNum += 1
            self.locList.append(loc)

            nPCI = pm.createNode('nearestPointOnCurve', name = str(loc) + '_nPCI')
            PCI = pm.createNode('pointOnCurveInfo', name = str(loc) + '_PCI')

            pm.setAttr(nPCI.inPositionX, pos[0])
            pm.setAttr(nPCI.inPositionY, pos[1])
            pm.setAttr(nPCI.inPositionZ, pos[2])

            pm.connectAttr(crv + '.worldSpace[0]', nPCI.inputCurve)
            pm.connectAttr(crv + '.worldSpace[0]', PCI.inputCurve)

            pm.connectAttr(nPCI.parameter, PCI.parameter)
            pm.connectAttr(PCI.position, loc.translate)

            par = pm.getAttr(PCI.parameter)
            pm.delete(nPCI)
            pm.setAttr(PCI.parameter, par)

    #create joint and create node network to make it slide along eye
    def createJnts(self, midLoc):
        for each in self.locList:
            name = each.split('_LOC')[0]
            name = name + '_BONE'
            srt = pm.group(em = True, name = name + '_srt')
            jnt = pm.joint(name = name)

            pos = pm.xform(midLoc, t = True, ws = True, query = True)
            pm.setAttr(srt.translate, pos[0], pos[1], pos[2] )

            PMA = pm.createNode('plusMinusAverage', name = name + '_PMA')
            magnitude = pm.createNode('distanceBetween', name = name + '_magnitude')
            unitVector = pm.createNode('multiplyDivide', name = name + '_unitVector')
            unitVectorMult = pm.createNode('multiplyDivide', name = name + '_unitVector')

            #get vector between the eye and the locator
            pm.connectAttr(each.translate, PMA.input3D[0])
            pm.connectAttr(midLoc + '.translate', PMA.input3D[1])
            pm.setAttr(PMA.operation, 2)

            #get magnitude of vector between eye and the locator
            pm.connectAttr(each.worldMatrix[0], magnitude.inMatrix1)
            pm.connectAttr(midLoc + '.worldMatrix[0]', magnitude.inMatrix2)

            #get the unit vector
            pm.connectAttr(PMA.output3D, unitVector.input1)
            pm.connectAttr(magnitude.distance, unitVector.input2X)
            pm.connectAttr(magnitude.distance, unitVector.input2Y)
            pm.connectAttr(magnitude.distance, unitVector.input2Z)
            pm.setAttr(unitVector.operation, 2)

            #multiply the unit vector so that it is forward enough in space
            pm.connectAttr(unitVector.output, unitVectorMult.input1)
            mag = pm.getAttr(magnitude.distance)
            pm.setAttr(unitVectorMult.input2X, mag)
            pm.setAttr(unitVectorMult.input2Y, mag)
            pm.setAttr(unitVectorMult.input2Z, mag)
            pm.connectAttr(unitVectorMult.output, jnt.translate)




    def reorderLoc(self):
        self.locList = pm.ls(sl = True)
        self.locNum = len(self.locList)


    #put controls in the correct places among the curve
    def crvCTRLjnt(self, side, topBot):
        #if amount of locators is even find the middle position of the two middle most locators
        if self.locNum % 2 == 0:
            num = self.locNum / 2
            num2 = num + 1

            pos1 = pm.xform(self.locList[num], t = True, ws = True, query = True)
            pos2 = pm.xform(self.locList[num], t = True, ws = True, query = True)

            posX = (pos1[0] + pos2[0]) / 2.0000
            posY = (pos1[1] + pos2[1]) / 2.0000
            posZ = (pos1[2] + pos2[2]) / 2.0000

        #if the amount of locators is odd find the position of the middle locator
        else:
            num = (self.locNum / 2)
            pos = pm.xform(self.locList[num], t = True, ws = True, query = True)

            posX = pos[0]
            posY = pos[1]
            posZ = pos[2]

        pm.select(clear = True)
        self.mainCtrlJnt = pm.joint(name = side + '_' + topBot + 'MainEl_ctrlBone')
        pm.select(clear = True)
        self.mainCtrlJntSrt = pm.group(em = True, name = side + '_' + topBot + 'MainEl_ctrlBone_srt')
        pm.parent(self.mainCtrlJnt, self.mainCtrlJntSrt)

        pm.xform(self.mainCtrlJntSrt, t = (posX, posY, posZ), ws = True)
        pm.select(clear = True)

        #create first mid controller
        numB = int(self.locNum / 4)
        posB = pm.xform(self.locList[numB], t = True, ws = True, query = True)

        self.midACtrlJntSrt = pm.group(name = side + '_' + topBot + 'midAel_ctrlBone_srt', em = True)
        self.midACtrlJnt = pm.joint(name = side + '_' + topBot + 'midAel_ctrlBone')
        pm.xform(self.midACtrlJntSrt, t = (posB[0], posB[1], posB[2]), ws = True)
        pm.select(clear = True)


        #create first mid controller
        numB = int(self.locNum * .75)
        posB = pm.xform(self.locList[numB], t = True, ws = True, query = True)

        self.midBCtrlJntSrt = pm.group(name = side + '_' + topBot + 'midBel_ctrlBone_srt', em = True)
        self.midBCtrlJnt = pm.joint(name = side + '_' + topBot + 'midBel_ctrlBone')
        pm.xform(self.midBCtrlJntSrt, t = (posB[0], posB[1], posB[2]), ws = True)

        #create beginning controller
        pos = pm.xform(self.locList[0], t = True, ws = True, query = True)

        self.begCtrlJntSrt = pm.group(name = side + '_' + topBot + 'begEl_ctrlBone_srt', em = True)
        self.begCtrlJnt = pm.joint(name = side + '_' + topBot + 'begEl_ctrlBone')
        pm.xform(self.begCtrlJntSrt, t = (pos[0], pos[1], pos[2]), ws = True)

        #create end controller
        length = len(self.locList) - 1
        pos = pm.xform(self.locList[length], t = True, ws = True, query = True)

        self.endCtrlJntSrt = pm.group(name = side + '_' + topBot + 'endEl_ctrlBone_srt', em = True)
        self.endCtrlJnt = pm.joint(name = side + '_' + topBot + 'endEl_ctrlBone')
        pm.xform(self.endCtrlJntSrt, t = (pos[0], pos[1], pos[2]), ws = True)

RbotEyeLid = eyeLidSetup()
RbotEyeLid.createLoc('R', 'bot', 'R_botEL_HD_CRV')
RbotEyeLid.createJnts('R_eye_LOC')

RbotEyeLid.crvCTRLjnt('R', 'bot')


RtopEyeLid = eyeLidSetup()
RtopEyeLid.createLoc('R', 'top', 'R_topEL_HD_CRV')
RtopEyeLid.createJnts('R_eye_LOC')

RtopEyeLid.crvCTRLjnt('R', 'top')

RtopEyeLid.locList



LbotEyeLid = eyeLidSetup()
LbotEyeLid.createLoc('L', 'bot', 'L_botEL_HD_CRV')
LbotEyeLid.createJnts('L_eye_LOC')

LbotEyeLid.crvCTRLjnt('L', 'bot')






LtopEyeLid = eyeLidSetup()
LtopEyeLid.createLoc('L', 'top', 'L_topEL_HD_CRV')
LtopEyeLid.createJnts('L_eye_LOC')

LtopEyeLid.crvCTRLjnt('L', 'top')







topELVTX = pm.ls(sl = True, fl = True)
botELVTX = pm.ls(sl = True, fl = True)

for each in topELVTX:
    pm.select(each, add = True)

for each in botELVTX:
    pm.select(each, add = True)
