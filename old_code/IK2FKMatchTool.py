import maya.cmds as cmds
import maya.OpenMaya as om

ikfkDict = {}

def spaceListCreate():
	cmds.deleteUI(ikfkDict['spaceColumn'])
	ikfkDict['spaceColumn'] = cmds.columnLayout(adj = True, rs = 5)

	asObject = cmds.textFieldGrp('applySpaceText', query = True, text = True)
	attrList = cmds.attributeQuery('follow', node = asObject, listEnum = True)
	attrList = attrList[0].split(':')

	x = 0
	for each in attrList:
		command = ("spaceMatch(" + str(x) + ")")
		smDict[each] = cmds.button(l = each, c = command, p = smDict['spaceColumn'])
		x = x + 1





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
cmds.canvas(hsvValue = (60, .81, 1), width = 25, height = 25) 
cmds.setParent('..')

cmds.rowLayout(numberOfColumns = 3, columnAttach3 = ('left', 'left', 'left'), columnOffset3 = (192, 10, 10))
cmds.canvas(hsvValue = (360, .49, 1), width = 10, height = 45)
cmds.canvas(hsvValue = (60, .81, 1), width = 30, height = 50)
cmds.canvas(hsvValue = (187, .49, 1), width = 10, height = 45)
cmds.setParent('..')

cmds.rowLayout(numberOfColumns = 2, columnAttach2 = ('left', 'left'), columnOffset2 = (213, 8))
cmds.canvas(hsvValue = (360, .49, 1), width = 10, height = 55)
cmds.canvas(hsvValue = (187, .49, 1), width = 10, height = 55)
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

cmds.rowLayout(numberOfColumns = 1, columnAttach1 = 'left')
smOptionList = cmds.textScrollList('smOptions', append = ('No Spaces Available'), nr = 3)
cmds.setParent('..')

cmds.rowLayout(numberOfColumns = 1, columnAttach1 = 'left', columnOffset1 = 180)
cmds.button('matchButton', label = 'Match', width = 100, height = 30)

cmds.showWindow()





#FK match to IK
IKshoulder = cmds.xform('L_arm_upper_ik_JNT', query = True, ro = True, ws = True)
IKelbow = cmds.xform('L_arm_lower_ik_JNT', query = True, ro = True, ws = True)
IKwrist = cmds.xform('L_hand_ik_CTRL', query = True, ro = True, ws = True)


cmds.xform('L_arm_upper_CTRL', ro = ( IKshoulder[0], IKshoulder[1], IKshoulder[2] ), ws = True )
cmds.xform('L_arm_lower_CTRL', ro = ( IKelbow[0], IKelbow[1], IKelbow[2] ), ws = True )
cmds.xform('L_hand_CTRL', ro = ( IKwrist[0], IKwrist[1], IKwrist[2] ), ws = True )

##IK match to FK
FKhandPos = cmds.xform('L_hand_CTRL', query = True, t = True, ws = True)
FKhandRot = cmds.xform('L_hand_CTRL', query = True, ro = True, ws = True)

#move IK wrist control to position
cmds.xform('L_hand_ik_CTRL', t = (FKhandPos[0], FKhandPos[1], FKhandPos[2]), ws = True )
cmds.xform('L_hand_ik_CTRL', ro = (FKhandRot[0], FKhandRot[1], FKhandRot[2]), ws = True )

#get vectors of shoulder, elbow, and wrist
shoulderPos = cmds.xform('L_arm_upper_CTRL', query = True, t = True, ws = True)
shoulderV = om.MVector(shoulderPos[0], shoulderPos[1], shoulderPos[2])
elbowPos = cmds.xform('L_arm_lower_CTRL', query = True, t = True, ws = True)
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

cmds.xform('L_arm_pole_CTRL', t = (pvPosV.x, pvPosV.y, pvPosV.z), ws = True)

'''cmds.spaceLocator()
cmds.xform(t = (pvPosV.x, pvPosV.y, pvPosV.z), ws = True )


shoulderLoc = cmds.spaceLocator(name = 'shoulderLoc')
cmds.xform(shoulderLoc, t = (shoulderV.x, shoulderV.y, shoulderV.z), ws = True )

elbowLoc = cmds.spaceLocator(name = 'elbowLoc')
cmds.xform(elbowLoc, t = (elbowV.x, elbowV.y, elbowV.z), ws = True )

wristLoc = cmds.spaceLocator(name = 'wristLoc')
cmds.xform(wristLoc, t = (wristV.x, wristV.y, wristV.z), ws = True )

shWrLoc = cmds.spaceLocator(name = 'shWrLoc')
cmds.xform(shWrLoc, t = (shWrV.x, shWrV.y, shWrV.z), ws = True )




cmds.delete(shoulderLoc)
cmds.delete(elbowLoc)
cmds.delete(wristLoc)
cmds.delete(shWrLoc)'''














