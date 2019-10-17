import maya.cmds as cmds
import maya.OpenMaya as om



ikfkDict = {}

def ikfkMatch():
    toolCommand = cmds.radioCollection( exOptionCollection1, query = True, select = True)
    
    if toolCommand == 'FK2IK':
    
        #FK match to IK
        IKtop = cmds.xform(ikfkDict['top'], query = True, ro = True, ws = True)
        IKmid = cmds.xform(ikfkDict['mid'], query = True, ro = True, ws = True)
        IKbot = cmds.xform(ikfkDict['bot'], query = True, ro = True, ws = True)
        
        
        cmds.xform(ikfkDict['topFK'], ro = ( IKtop[0], IKtop[1], IKtop[2] ), ws = True )
        cmds.xform(ikfkDict['midFK'], ro = ( IKmid[0], IKmid[1], IKmid[2] ), ws = True )
        cmds.xform(ikfkDict['botFK'], ro = ( IKbot[0], IKbot[1], IKbot[2] ), ws = True )
    
    if toolCommand == 'IK2FK':
        ##IK match to FK
        FKhandPos = cmds.xform(ikfkDict['botFK'], query = True, t = True, ws = True)
        FKhandRot = cmds.xform(ikfkDict['botFK'], query = True, ro = True, ws = True)
        
        #move IK wrist control to position
        cmds.xform(ikfkDict['ikCTRL'], t = (FKhandPos[0], FKhandPos[1], FKhandPos[2]), ws = True )
        cmds.xform(ikfkDict['ikCTRL'], ro = (FKhandRot[0], FKhandRot[1], FKhandRot[2]), ws = True )
        
        #get vectors of shoulder, elbow, and wrist
        shoulderPos = cmds.xform(ikfkDict['topFK'], query = True, t = True, ws = True)
        shoulderV = om.MVector(shoulderPos[0], shoulderPos[1], shoulderPos[2])
        elbowPos = cmds.xform(ikfkDict['midFK'], query = True, t = True, ws = True)
        elbowV = om.MVector(elbowPos[0], elbowPos[1], elbowPos[2])
        wristV = om.MVector(FKhandPos[0], FKhandPos[1], FKhandPos[2])
        
        #subtract wrist vector from shoulder vector to get the vector between them
        shWrV = shoulderV - wristV
        #divide by 2 to get middle of the vector, where the elbow should be aligned with
        midShWrV = shWrV/2
        #add to wrist vector to get middle of IK
        midArmV = midShWrV + wristV
        #subtract mid arm vector from the elbow vector to get the vector between them
        midArmV2 = elbowV - midArmV
        #multiply by 2 so that it sets the pv position off the elbow
        midArmVBig = midArmV2 * 4
        #add to the mid arm vector to get the position that the pole vector should be in
        pvPosV = midArmVBig + midArmV
        
        cmds.xform(ikfkDict['pvCTRL'], t = (pvPosV.x, pvPosV.y, pvPosV.z), ws = True)
    
    if toolCommand == 'SMRB':
        cmds.error('not set up yet')     

def LarmSelect():
    ikfkDict['limbSelect'] = 'leftArm'
    cmds.textFieldGrp('limbSelectText', e = True, tx = ikfkDict['limbSelect'])
    spaceListCreate()
    ikfkDict['top'] = 'L_arm_upper_ik_JNT'
    ikfkDict['mid'] = 'L_arm_lower_ik_JNT'
    ikfkDict['bot'] = 'L_hand_ik_CTRL' 
    
    ikfkDict['topFK'] = 'L_arm_upper_CTRL'
    ikfkDict['midFK'] = 'L_arm_lower_CTRL'
    ikfkDict['botFK'] = 'L_hand_CTRL'
    
    ikfkDict['ikCTRL'] = 'L_hand_ik_CTRL'
    ikfkDict['pvCTRL'] = 'L_arm_pole_CTRL'

def RarmSelect():
    ikfkDict['limbSelect'] = 'rightArm'
    cmds.textFieldGrp('limbSelectText', e = True, tx = ikfkDict['limbSelect'])
    spaceListCreate()
    ikfkDict['top'] = 'R_arm_upper_ik_JNT'
    ikfkDict['mid'] = 'R_arm_lower_ik_JNT'
    ikfkDict['bot'] = 'R_hand_ik_CTRL' 
    
    ikfkDict['topFK'] = 'R_arm_upper_CTRL'
    ikfkDict['midFK'] = 'R_arm_lower_CTRL'
    ikfkDict['botFK'] = 'R_hand_CTRL'
    
    ikfkDict['ikCTRL'] = 'R_hand_ik_CTRL'
    ikfkDict['pvCTRL'] = 'R_arm_pole_CTRL'

def LlegSelect():
    ikfkDict['limbSelect'] = 'leftLeg'
    cmds.textFieldGrp('limbSelectText', e = True, tx = ikfkDict['limbSelect'])
    spaceListCreate()
    ikfkDict['top'] = 'L_leg_01_upper_twist_BONE'
    ikfkDict['mid'] = 'L_leg_01_lower_twist_BONE'
    ikfkDict['bot'] = 'L_foot_BONE'
    
    ikfkDict['topFK'] = 'L_leg_upper_CTRL'
    ikfkDict['midFK'] = 'L_leg_lower_CTRL'
    ikfkDict['botFK'] = 'L_foot_CTRL'
    
    ikfkDict['ikCTRL'] = 'L_foot_ik_CTRL'
    ikfkDict['pvCTRL'] = 'L_leg_pole_CTRL'
    

def RlegSelect():
    ikfkDict['limbSelect'] = 'rightLeg'
    cmds.textFieldGrp('limbSelectText', e = True, tx = ikfkDict['limbSelect'])
    spaceListCreate()
    ikfkDict['top'] = 'R_leg_01_upper_twist_BONE'
    ikfkDict['mid'] = 'R_leg_01_lower_twist_BONE'
    ikfkDict['bot'] = 'R_foot_BONE'
    
    ikfkDict['topFK'] = 'R_leg_upper_CTRL'
    ikfkDict['midFK'] = 'R_leg_lower_CTRL'
    ikfkDict['botFK'] = 'R_foot_CTRL'
    
    ikfkDict['ikCTRL'] = 'R_foot_ik_CTRL'
    ikfkDict['pvCTRL'] = 'R_leg_pole_CTRL'
    

def headSelect():
    ikfkDict['limbSelect'] = 'head'
    cmds.textFieldGrp('limbSelectText', e = True, tx = ikfkDict['limbSelect'])
    spaceListCreate()



def spaceListCreate():

	asObject = cmds.textFieldGrp('limbSelectText', query = True, text = True)
	
	if asObject == 'head':
	    cmds.textScrollList(smOptionList, e = True, ra = True, append = ('worldRotate', 'customRotate', 'worldTranslate', 'customTranslate') )
	if asObject == 'leftArm':
	    cmds.textScrollList(smOptionList, e = True, ra = True, append = ('world', 'custom') )
	if asObject == 'rightArm':
	    cmds.textScrollList(smOptionList, e = True, ra = True, append = ('world', 'custom') )
	if asObject == 'leftLeg':
	    cmds.textScrollList(smOptionList, e = True, ra = True, append = ('footWorld', 'footCustom', 'pvWorld', 'pvFollow') )
	if asObject == 'rightLeg':
	    cmds.textScrollList(smOptionList, e = True, ra = True, append = ('footWorld', 'footCustom', 'pvWorld', 'pvFollow') )
	    





ikFkToolID = 'ikFkTool Tool'



if cmds.window(ikFkToolID, exists = True):
    cmds.deleteUI(ikFkToolID)
    
cmds.window(ikFkToolID, width = 200)

topColumn = cmds.columnLayout( 'column01', adjustableColumn = True)

topFrame = cmds.frameLayout('Select Rig')

rigSelRow = cmds.rowLayout('rigSelRow', numberOfColumns = 2, parent = topFrame, adj = 1)
instructionText = cmds.textFieldGrp('instructionText', label = 'Rig Name', text = 'Select a control', ed = False, adj = 2)
rigSelectButton = cmds.button(label = 'Select', w = 70)

cmds.setParent( topColumn )

cmds.separator( height=40, style='in' )

cmds.columnLayout(rowSpacing = 10)
cmds.rowLayout(numberOfColumns = 1, columnAttach1 = 'left', columnOffset1 = 202)
cmds.text( label='Limb Select' )
cmds.setParent('..')

cmds.rowLayout(numberOfColumns = 1, columnAttach1 = ('left'), columnOffset1 = (217) )
cmds.canvas(hsvValue = (60, .81, 1), width = 25, height = 25, pc = 'headSelect()') 
cmds.setParent('..')

cmds.rowLayout(numberOfColumns = 3, columnAttach3 = ('left', 'left', 'left'), columnOffset3 = (192, 10, 10))
cmds.canvas(hsvValue = (360, .49, 1), width = 10, height = 45, pc = 'RarmSelect()')
cmds.canvas(hsvValue = (60, .81, 1), width = 30, height = 50, en = False)
cmds.canvas(hsvValue = (187, .49, 1), width = 10, height = 45, pc = 'LarmSelect()')
cmds.setParent('..')

cmds.rowLayout(numberOfColumns = 2, columnAttach2 = ('left', 'left'), columnOffset2 = (213, 8))
cmds.canvas(hsvValue = (360, .49, 1), width = 10, height = 55, pc = 'RlegSelect()')
cmds.canvas(hsvValue = (187, .49, 1), width = 10, height = 55, pc = 'LlegSelect()')
cmds.setParent('..')

cmds.rowLayout(numberOfColumns = 1, columnAttach1 = ('left'), columnOffset1 = (0))
cmds.textFieldGrp('limbSelectText', label = 'Selected Limb', text = 'Select a limb', ed = False, adj = 2)
cmds.setParent(topColumn)

cmds.separator( height=40, style='in' )

exOptionCollection1 = cmds.radioCollection('exOptionCollection1')
IK2FKrb = cmds.radioButton('IK2FK', label = 'IK match to FK')
FK2IKrb = cmds.radioButton('FK2IK', label = 'FK match to IK')
sMrb = cmds.radioButton('SMRB', label = 'Space Match')
cmds.radioCollection( exOptionCollection1, edit = True, select = IK2FKrb)

ikfkDict['spaceRow'] = cmds.rowLayout(numberOfColumns = 1, columnAttach1 = 'left')
smOptionList = cmds.textScrollList('smOptions', append = ('No Spaces Available'), nr = 3)
cmds.setParent('..')

ikfkDict['buttonRow'] = cmds.rowLayout(numberOfColumns = 1, columnAttach1 = 'left', columnOffset1 = 180)
cmds.button('matchButton', label = 'Match', width = 100, height = 30, c = 'ikfkMatch()' )

cmds.showWindow()

