import maya.cmds as cmds

smDict = {}


if cmds.window('SpaceMatch', exists = True):
	cmds.deleteUI('SpaceMatch')


winID = cmds.window('SpaceMatch', title = 'SpaceMatch Tool', width = 300, height = 400)

topFrame = cmds.frameLayout( label = 'Create Spaces')

topColumn = cmds.columnLayout(adj = True)

#Create textbox in which the space that is about to be created is shown
firstTextRow = cmds.rowLayout( nc = 2)

spaceText = cmds.textFieldGrp( 'spaceText', label = 'Space', width = 300 )

spaceTextButton = cmds.button( label = 'GET OBJ', w = 70, c = "addToTxtBox('spaceText')")

cmds.setParent( topColumn )

#Create button to create the space
topColumn2 = cmds.columnLayout( rs = 20 )
spaceButton = cmds.button( label = 'Create Space', width = 400, c = 'createSpace()')

#Create textbox in which the object in which the spaces are being applied to are shown
secondTextRow = cmds.rowLayout( nc = 2 )

applySpaceText = cmds.textFieldGrp( 'applySpaceText', label = 'Object', width = 300)

applySpaceTextButton = cmds.button( label = 'GET OBJ', w = 70, c = "addToTxtBox('applySpaceText')" )

cmds.setParent( topColumn )

#Create checkboxes in order to know exactly what kind of space you are creating
Translation = cmds.checkBox('Translation')
Rotation = cmds.checkBox('Rotation')

#Create button to apply space
topColumn3 = cmds.columnLayout( rs = 20 )
applySpaceButton = cmds.button( label = 'Apply Space', width = 400, c = 'applySpace()')

#Change Spaces part of tool
cmds.setParent( top = True)
csFrame = cmds.frameLayout(label = 'Change Spaces', cll = True, cl = True)
smDict['lsButton'] = cmds.button( label = 'Load Spaces', h = 40, c = 'spaceButtonCreate()')

smDict['spaceFrame'] = cmds.frameLayout(label = 'Selected Object Spaces')
smDict['spaceColumn'] = cmds.columnLayout(adj = True, rs = 5)

cmds.showWindow()


def spaceButtonCreate():
	cmds.deleteUI(smDict['spaceColumn'])
	smDict['spaceColumn'] = cmds.columnLayout(adj = True, rs = 5)

	asObject = cmds.textFieldGrp('applySpaceText', query = True, text = True)
	attrList = cmds.attributeQuery('follow', node = asObject, listEnum = True)
	attrList = attrList[0].split(':')

	x = 0
	for each in attrList:
		command = ("spaceMatch(" + str(x) + ")")
		smDict[each] = cmds.button(l = each, c = command, p = smDict['spaceColumn'])
		x = x + 1


def spaceMatch(spVal):
	asObject = cmds.textFieldGrp('applySpaceText', query = True, text = True)
	
	#make a locator and move it to the object
	spaceLoc = cmds.spaceLocator()
	
	locConstraint = cmds.pointConstraint(  asObject, spaceLoc, mo = False )
	
	cmds.delete(locConstraint)
	
	#translation = cmds.xform(asObject, q = True, ws = True, rp = True)

	rotation = cmds.xform(asObject, q = True, ws = True, ro = True)

	cmds.setAttr(asObject + '.follow', spVal)

	cmds.xform(asObject, ws = True, ro = rotation)
	
	#check to see if the constraint involves translate values and if it does then move it to the position of the locator
	constraintCheck = cmds.getAttr( asObject + '.ty', lock = True )
	
	if constraintCheck == False:
		cmds.pointConstraint( spaceLoc, asObject, mo = False )

	cmds.setKeyframe( asObject )

	cmds.delete(spaceLoc)


def addToTxtBox(box):
	selection = cmds.ls(sl=True)
	if len(selection) == 0:
		cmds.error( "Nothing is selected")
	if len(selection) > 1:
		cmds.error( "More than one thing selected")

	cmds.textFieldGrp(box, e = True, tx = selection[0])


def createSpace():
	text = cmds.textFieldGrp('spaceText', query = True, text = True)
	if text == '':
		cmds.error("Put an object in the text bar")

	#make group for the spaces
	try:
		cmds.select('space_grp')
		cmds.select(clear = True)
	except:
		cmds.group( em = True, name = 'space_grp')


	#check to see if the space exists
	cmds.select(clear = True)
	try:
		cmds.select(text + '_space')
	except:
		print ''
	if len(cmds.ls(sl=True)) == 1:
		cmds.error('Space already exists')
	cmds.select(clear = True)


	#create the space and move it the pivot of the object
	spaceGroup = cmds.group( em = True, name = (text + '_space'))
	spaceGrpMove = cmds.pointConstraint( text, spaceGroup,  mo = False )
	cmds.delete(spaceGrpMove)
	cmds.makeIdentity(spaceGroup, apply = True)
	cmds.parentConstraint( text, spaceGroup )
	cmds.parent( spaceGroup, 'space_grp')







def applySpace():
	
	#store both the space object and the object you want to apply the space too
	space = cmds.textFieldGrp('spaceText', query = True, text = True)

	
	#find the name of the space object without it's namespace
	spaceName = space.split(':')
	spaceNumber = len(spaceName) - 1
	spaceName = spaceName[spaceNumber]

	
	smDict['asObject'] = cmds.textFieldGrp('applySpaceText', query = True, text = True)

	#check to see if there is text in the text boxes
	if space == '':
		cmds.error( ' There is nothing in the space text box ')

	if smDict['asObject'] == '':
		cmds.error( ' There is nothing in the object text box ')

	#check to see if the space you are applying is already applied
	if cmds.attributeQuery('follow', node = smDict['asObject'], exists = True ) == True:
		attrList = cmds.attributeQuery('follow', node = smDict['asObject'], listEnum = True)
		attrList = attrList[0].split(':')
		for each in attrList:
			if each == space:
				cmds.error('This space has already been applied')

	#check to see if the spaceGroup exists
	try:
		spaceGroup = smDict['asObject'] + '_spaceGrp'
		cmds.select(spaceGroup)

	except:
		#get the parent of the object so that when you group it you can put it back in it's original place
		parent = cmds.listRelatives(smDict['asObject'], p = True)
		spaceGroup = cmds.group( em = True, name = (smDict['asObject'] + '_spaceGrp'))
		spaceGroupMove = cmds.pointConstraint(  smDict['asObject'], spaceGroup, mo = False)
		cmds.delete(spaceGroupMove)
		cmds.makeIdentity(spaceGroup, apply = True)

		#put your object under the space group
		print spaceGroup
		print parent
		print smDict['asObject']

		if parent != None:
			cmds.parent(spaceGroup, parent)
		cmds.parent(smDict['asObject'], spaceGroup)


	#depending on what checkboxes are checked make your space
	translationCheck = 0
	rotationCheck = 0

	if cmds.checkBox( 'Translation', query=True, value = True) == True:
		translationCheck = 1
	if cmds.checkBox( 'Rotation', query=True, value = True) == True:
		rotationCheck = 3

	constraintCheck = translationCheck + rotationCheck

	if constraintCheck == 1:
		constraint = cmds.pointConstraint( space, spaceGroup, mo = True)
		constraintType = '_spaceGrp_pointConstraint1.'
	if constraintCheck == 3:
		constraint = cmds.orientConstraint( space, spaceGroup, mo = True)
		constraintType = '_spaceGrp_orientConstraint1.'
	if constraintCheck == 4:
		constraint = cmds.parentConstraint( space, spaceGroup, mo = True)
		constraintType = '_spaceGrp_parentConstraint1.'

	if constraintCheck == 0:
		cmds.error('Check a space type')

	#check to see if follow attribute exists and if not make one
	if cmds.attributeQuery('follow', node = smDict['asObject'], exists = True ) == True:
		#return all the enum names in the attribute and then add the new attr at the end
		print 'yes'
		attrList = cmds.attributeQuery('follow', node = smDict['asObject'], listEnum = True)
		attrListName = (attrList[0] + ':' + spaceName)
		print attrListName
		#delete the attribute and then reAdd it with the new enum list
		cmds.deleteAttr( smDict['asObject'], at = 'follow')
		cmds.select(smDict['asObject'])
		cmds.addAttr( ln = 'follow', at = 'enum', en = attrListName, keyable = True )

	else:
		cmds.select(smDict['asObject'])
		cmds.addAttr( ln = 'follow', at = 'enum', en = (spaceName + ':'), keyable = True )
		attrList = spaceName

	#split the attrList by : to make an actual list
	attrList = cmds.attributeQuery('follow', node = smDict['asObject'], listEnum = True)

	attrList = attrList[0].split(':')

	attrListEnd = len(attrList) - 1

	x = 0

	#Set driven keys on the attributes on the constraint 

	for each in attrList:
		conAttr = each + 'W' + str(x)
		if x == 0:
			cmds.setAttr( smDict['asObject'] + '.follow', x )
			cmds.setAttr( smDict['asObject'] + constraintType + conAttr, 1)
			cmds.setDrivenKeyframe( smDict['asObject'] + constraintType, at = conAttr, cd = smDict['asObject'] + '.follow')
			cmds.setAttr(smDict['asObject'] + '.follow', x + 1)
			cmds.setAttr(smDict['asObject'] + constraintType + conAttr, 0)
			cmds.setDrivenKeyframe( smDict['asObject'] + constraintType, at =conAttr, cd = smDict['asObject'] + '.follow')

			

		if x > 0 and x < attrListEnd:
			cmds.setAttr( smDict['asObject'] + '.follow', x - 1 )
			cmds.setAttr( smDict['asObject'] + constraintType + conAttr, 0)
			cmds.setDrivenKeyframe( smDict['asObject'] + constraintType, at = conAttr, cd = smDict['asObject'] + '.follow')
			cmds.setAttr(smDict['asObject'] + '.follow', x )
			cmds.setAttr(smDict['asObject'] + constraintType + conAttr, 1)
			cmds.setDrivenKeyframe( smDict['asObject'] + constraintType, at =conAttr, cd = smDict['asObject'] + '.follow')
			cmds.setAttr( smDict['asObject'] + '.follow', x + 1 )
			cmds.setAttr( smDict['asObject'] + constraintType + conAttr, 0)
			cmds.setDrivenKeyframe( smDict['asObject'] + constraintType, at = conAttr, cd = smDict['asObject'] + '.follow')

			
		if x == attrListEnd:
			cmds.setAttr( smDict['asObject'] + '.follow', x )
			cmds.setAttr( smDict['asObject'] + constraintType + conAttr, 1)
			cmds.setDrivenKeyframe( smDict['asObject'] + constraintType, at = conAttr, cd = smDict['asObject'] + '.follow')
			cmds.setAttr(smDict['asObject'] + '.follow', x - 1 )
			cmds.setAttr(smDict['asObject'] + constraintType + conAttr, 0)
			cmds.setDrivenKeyframe( smDict['asObject'] + constraintType, at =conAttr, cd = smDict['asObject'] + '.follow')


		x = x + 1
