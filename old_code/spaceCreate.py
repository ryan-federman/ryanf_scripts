import maya.cmds as cmds
import pymel.core as pm

spaceDict = {}
spaceDict['spaceObj'] = 'none'

winID = 'spaceCreate'

if pm.window(winID, exists = True):
    pm.deleteUI(winID)

winID = pm.window('spaceCreate', width = 200)

pm.frameLayout(label = 'Create Spaces')
topColumn = pm.columnLayout(adj = True)

#Create textbox in which the space that is about to be created is shown
firstTextRow = pm.rowLayout( nc = 2)

spaceText = pm.textFieldGrp( 'spaceText', label = 'Space', width = 300, editable = False  )

spaceTextButton = pm.button( label = 'GET OBJ', w = 70, c = 'spaceTextbox()' )

cmds.setParent( topColumn )

#Create button to create the space
topColumn2 = pm.columnLayout( rs = 20 )
spaceButton = pm.button( label = 'Create Space', width = 400, c = 'spaceCreate()')

pm.setParent( topColumn )

#Create textbox in which the object in which the spaces are being applied to are shown
secondTextRow = pm.rowLayout( nc = 2 )

applySpaceText = pm.textFieldGrp( 'applySpaceText', label = 'Object', width = 300, editable = False)

applySpaceTextButton = pm.button( label = 'GET OBJ', w = 70, c = 'objTextbox()' )

cmds.setParent( topColumn )

#Create checkboxes in order to know exactly what kind of space you are creating
transCheck = pm.checkBox('Translation')
rotCheck = pm.checkBox('Rotation')

#Create button to apply space
topColumn3 = pm.columnLayout( rs = 20 )
applySpaceButton = pm.button( label = 'Apply Space', width = 400, c = 'applySpace()')

#Create button to apply space
topColumn4 = pm.columnLayout( rs = 20 )
deleteSpaceButton = pm.button( label = 'Delete Space', width = 400, c = 'deleteSpace()')




pm.showWindow()


#Fill in the text box for the space object and fill the variable in your dictionary with that object
def spaceTextbox():
    space = pm.ls(sl = True)

    if len(space) == 0:
        cmds.error("Select an object")
    if len(space) > 1:
        cmds.error("More than one object selected")
    else:
        space = space[0]
        pm.textFieldGrp( spaceText, e = True, tx = space )
        spaceDict['spaceObj'] = space


def spaceCreate():
    #query the control and create what the name of it's space will be
    if spaceDict['spaceObj'] == 'none':
        cmds.error('No space is loaded')
    else:
        spaceName = spaceDict['spaceObj'] + '_SPACE'

    #check to see if your main spaces group is created
    cmds.select(clear = True)
    try:
        cmds.select('SPACES_GRP')
        cmds.select(clear = True)
        print 'exists'
    except:
        spaceGRP = pm.group(em = True, name = 'SPACES_GRP')
        print 'doesntexist'

    #check to see if the space for your object already exists
    try:
        cmds.select(spaceName)
    except:
        pm.select(clear = True)
    selection = pm.ls(sl = True)
    if len(selection) == 1:
        cmds.error('This space already exists')

    #create space for the object
    space = pm.group(em = True, name = spaceName)
    pm.parent(space, 'SPACES_GRP')
    spaceConstraint = pm.parentConstraint(spaceDict['spaceObj'], space, mo = False)


#Fill in the text box for the object where the space is being applied and fill the variable in your dictionary with that object
def objTextbox():
    obj = pm.ls(sl = True)
    spaceDict['applyObj'] = obj[0]
    applySpaceText = pm.textFieldGrp( 'applySpaceText', e = True, tx = obj[0])

def applySpace():
    #check to make sure there are checkboxes applied and what constraint you should use
    numCheck = 0
    tCheck = pm.checkBox(transCheck, query = True, value = True)
    rCheck = pm.checkBox(rotCheck, query = True, value = True)
    if tCheck == True:
        numCheck = numCheck + 1
    if rCheck == True:
        numCheck = numCheck + 2
    if numCheck == 0:
        pm.error('Pick a space type')

    #check to see if the space to be applied actually exists
    applySpace = str(spaceDict['spaceObj']) + '_SPACE'
    try:
        pm.select(applySpace)
        pm.select(clear = True)
    except:
        pm.error('no space created for object')
    if pm.attributeQuery('SPACE', node = spaceDict['applyObj'], exists = True ) == True:

        #return all the enum names in the attribute and then add the new attr at the end
        attrList = pm.attributeQuery('SPACE', node = spaceDict['applyObj'], listEnum = True)
        attrList = attrList[0].split(':')

        #create a variable to use when recreating the space attribute
        #create a list of the spaces that are already created including the one you are making right now at the end
        for each in attrList:
            if spaceDict['spaceObj'] == each:
                pm.error('space is already applied')
        x = 0
        for each in attrList:
            if x == 0:
                newAttrList = each
                x = x + 1
            else:
                newAttrList = newAttrList + ':' + each
        attrListVar = newAttrList + ':' + spaceDict['spaceObj']
        attrList.append(str(spaceDict['spaceObj']))

        #create the newest condition node for the spaces and set it's base attributes before connections
        secondTermAttr = len(attrList) - 1
        newSpaceCondition = pm.createNode('condition', name = (spaceDict['applyObj'] + '_' + spaceDict['spaceObj'] + 'SPACE' + '_COND'))

        pm.setAttr(newSpaceCondition.colorIfTrueR, 1)
        pm.setAttr(newSpaceCondition.colorIfFalseR, 0)
        pm.setAttr(newSpaceCondition.secondTerm, secondTermAttr)

        #delete the attribute and then reAdd it with the new enum list
        pm.deleteAttr( spaceDict['applyObj'], at = 'SPACE')
        pm.select(spaceDict['applyObj'])
        pm.addAttr( ln = 'SPACE', at = 'enum', en = attrListVar, keyable = True )
    else:
        #create space attr on object and then apply the space to its parent srt group
        pm.select(clear = True)
        pm.select(spaceDict['applyObj'])
        pm.addAttr( sn = 'SPACE', at = 'enum', enumName = (spaceDict['spaceObj'] + ':'), keyable = True)

        #create condition node and set it's base attributes
        newSpaceCondition = pm.createNode('condition', name = (spaceDict['applyObj'] + '_' + spaceDict['spaceObj'] + 'SPACE' + '_COND'))
        pm.setAttr(newSpaceCondition.colorIfTrueR, 1)
        pm.setAttr(newSpaceCondition.colorIfFalseR, 0)

    #check to see if the object is in a "space" group and if not put it in one then set up the space (and it's connections) on that group
    parentGroupName = spaceDict['applyObj'] + '_SPACE_srt'
    objParent = pm.listRelatives(spaceDict['applyObj'], parent = True)

    try:
        pm.select(parentGroupName + '_parentConstraint1')
        consCheck = 1
    except:
        consCheck = 0

    if len(objParent) == 0 or objParent[0] != parentGroupName:

        spaceSrt = pm.group(em = True, name = parentGroupName)
        moveConstraint = pm.parentConstraint(spaceDict['applyObj'], spaceSrt, mo = False)
        pm.delete(moveConstraint)
        pm.parent(spaceDict['applyObj'], spaceSrt)
        pm.parent(spaceSrt, objParent)

        if numCheck == 1:
            pc = pm.parentConstraint(spaceDict['spaceObj'] + '_SPACE', spaceSrt, mo = True, skipRotate = ['x','y','z'])
        if numCheck == 2:
            pc = pm.parentConstraint(spaceDict['spaceObj'] + '_SPACE', spaceSrt, mo = True, skipTranslate = ['x','y','z'])
        if numCheck == 3:
            pc = pm.parentConstraint(spaceDict['spaceObj'] + '_SPACE', spaceSrt, mo = True)

        #apply connections to this space's condition
        pm.connectAttr(spaceDict['applyObj'].SPACE, newSpaceCondition.firstTerm)
        pm.connectAttr(newSpaceCondition.outColorR, pc + '.' + str(spaceDict['spaceObj']) + '_SPACEW0')

    elif (len(objParent) == 1 or objParent[0] == parentGroupName) and consCheck == 0:
        pm.select(spaceDict['spaceObj'] + '_SPACE')
        pm.select(parentGroupName, add = True)

        if numCheck == 1:
            pc = pm.parentConstraint(spaceDict['spaceObj'] + '_SPACE', parentGroupName, mo = True, skipRotate = ['x','y','z'])
        if numCheck == 2:
            pc = pm.parentConstraint(spaceDict['spaceObj'] + '_SPACE', parentGroupName, mo = True, skipTranslate = ['x','y','z'])
        if numCheck == 3:
            pc = pm.parentConstraint(spaceDict['spaceObj'] + '_SPACE', parentGroupName, mo = True)

        #apply connections to this space's condition
        pm.connectAttr(spaceDict['applyObj'].SPACE, newSpaceCondition.firstTerm)
        pm.connectAttr(newSpaceCondition.outColorR, pc + '.' + str(spaceDict['spaceObj']) + '_SPACEW0')

    #since there are spaces that exist you use the information stored to recreate the connections and create ones for the new space
    else:
        #delete the old constraint and rebuild it with all spaces
        x = 0
        for each in attrList:
            conditionName = str(spaceDict['applyObj']) + '_' + each + 'SPACE_COND'
            try:
                pm.disconnectAttr(conditionName + '.outColorR', parentGroupName + '_parentConstraint1' + '.' + each + '_SPACEW' + str(x) )
            except:
                print ' '
            x = x + 1
        pm.delete(parentGroupName + '_parentConstraint1')

        #select all the spaces in the same order as the attribute and rebuild the parent constraint
        pm.select(clear = True)
        for each in attrList:
           pm.select(each + '_SPACE', add = True)
        pm.select(parentGroupName, add = True)

        #check to see what kind of constraint you are going to apply
        if numCheck == 1:
            pc = pm.parentConstraint(mo = True, skipRotate = ['x','y','z'])
        if numCheck == 2:
            pc = pm.parentConstraint(mo = True, skipTranslate = ['x','y','z'])
        if numCheck == 3:
            pc = pm.parentConstraint(mo = True)

        #connect the SPACE attribute to the conditions
        x = 0
        for each in attrList:
            conditionName = str(spaceDict['applyObj']) + '_' + each + 'SPACE_COND'
            pm.connectAttr(spaceDict['applyObj'].SPACE, conditionName + '.firstTerm')
            pm.connectAttr(conditionName + '.outColorR', (str(pc) + '.' + each + '_SPACEW' + str(x)))
            x = x + 1

def deleteSpace():
    try:
        pm.delete(spaceDict['applyObj'] + '_SPACE_srt_parentConstraint1')
        pm.deleteAttr(spaceDict['applyObj'].SPACE)
    except:
        pm.error('No Spaces Applied')