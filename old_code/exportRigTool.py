import maya.cmds as cmds
import pymel.core as pm

uiDict = {}
exRigDict = {}

winID = 'exportRig'

if pm.window(winID, exists = True):
    pm.deleteUI(winID)

winID = pm.window('exportRig', width = 200)
topColumn = pm.columnLayout(adj = True)
pm.separator()
pm.separator()
pm.separator()
pm.separator()
pm.separator()
#Create button that loads the rig into the tool
loadColumn = pm.columnLayout(w = 100)
loadRigText = pm.textFieldGrp( 'loadRigText', tx = 'Select Root Group and Load Rig', width = 300, editable = False)
pm.button(label = 'Load Rig', w = 200, h = 35, c = 'loadRig()')
pm.setParent('..')
pm.separator()
pm.separator()
pm.separator()
pm.separator()
pm.separator()
#button for creating joints
riggingLayout = pm.frameLayout(label = 'Rigging', cll = True, cl = True)
pm.separator(style = 'none')
jointCreateButton = pm.button( label = 'Create Export Joints', w = 70, h = 50, c = 'createJoints()' )
pm.separator(style = 'in')
pm.separator(style = 'none')


pm.setParent( topColumn )


#part of tool that creates sets for the joints
animPrepLayout = pm.frameLayout(label = 'Animation Prep', cll = True, cl = True)
pm.separator(style = 'none')
pm.rowLayout( numberOfColumns=2, columnWidth2=( 100, 100 ), columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)] )

addJointButton = pm.button( label = 'Add Joint', w = 45, h = 30, c = 'addJoints()')
removeJointButton = pm.button( label = 'Remove Joint', w = 45, h = 30, c = 'removeJoints()')

pm.setParent( '..' )

setJointsTSL = pm.textScrollList( numberOfRows=8, allowMultiSelection=True )
pm.columnLayout(adj = True, w = 50)
setNameText = pm.textFieldGrp( 'setNameText', width = 300, editable = True)
pm.setParent( '..' )

reparentLayout1 = pm.columnLayout(adj = True, w = 50)
uiDict['selectionSetsCL1'] = pm.columnLayout(adj = True, w = 50)
uiDict['setsOM1'] = pm.optionMenu('')
pm.rowLayout( numberOfColumns=3, columnWidth2=( 100, 100 ), columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)] )
width = 65
height = 30
pm.button( label = 'Create Set', w = width, h = height, c = 'createSet()' )
pm.button( label = 'Load Set', w = width, h = height, c = 'loadSet()' )
pm.button( label = 'Delete Set', w = width, h = height, c = 'deleteSet()' )
pm.setParent(animPrepLayout)
pm.separator(style = 'in')
pm.separator(style = 'none')
pm.setParent(topColumn)

animExportLayout = pm.frameLayout(label = 'Animation Export', cll = True, cl = True)
pm.separator(style = 'none')
reparentLayout2 = pm.columnLayout(adj = True, w = 50)
uiDict['selectionSetsCL2'] = pm.columnLayout(adj = True, w = 50)

uiDict['setsOM2'] = pm.optionMenu()
pm.setParent('..')
pm.setParent('..')

pm.separator(height = 1)
prepAnimButtCL2 = pm.columnLayout(adj = True, w = 50)
pm.button( label = 'Prepare Animation', h = 50, c = 'prepareAnim()')

pm.setParent('..')
pm.separator(style = 'in')
pm.separator(style = 'none')


pm.showWindow()

#remakes the first option menu with the necessary sets
def remakeMenu1(setList):
    pm.deleteUI(uiDict['selectionSetsCL1'])
    uiDict['selectionSetsCL1'] = pm.columnLayout(adj = True, w = 50, parent = reparentLayout1)
    uiDict['setsOM1'] = pm.optionMenu()
    for each in setList:
        pm.menuItem(label = each)
    pm.rowLayout( numberOfColumns=3, columnWidth2=( 100, 100 ), columnAlign=(1, 'right'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)] )
    width = 65
    height = 30
    pm.button( label = 'Create Set', w = width, h = height, c = 'createSet()' )
    pm.button( label = 'Load Set', w = width, h = height, c = 'loadSet()' )
    pm.button( label = 'Delete Set', w = width, h = height, c = 'deleteSet()' )


#remakes the second option menu with the necessary sets
def remakeMenu2(setList):
    pm.deleteUI(uiDict['selectionSetsCL2'])
    uiDict['selectionSetsCL2'] = pm.columnLayout(adj = True, w = 50, parent = reparentLayout2)

    uiDict['setsOM2'] = pm.optionMenu()
    for each in setList:
        pm.menuItem(label = each)
def createJoints():
    #put all selected joints into a list
    jointSelection = pm.ls(sl = True)

    #check to see that everything in selection is a joint
    for each in jointSelection:
        type = pm.nodeType(each)
        if type != 'joint':
            pm.error('Non-Joints are selected')

    #if root group doesn't exist tell rigger to create a ROOT group
    try:
        pm.select('*ROOT')
        rootGRP = pm.ls(sl = True)[0]
        rigName = rootGRP.split('_')[0]
    except:
        pm.error("Create Top Group that is named CHARACTER_ROOT")
    #if rig node exists select it and put it in variable, if not create the node
    try:
        pm.select(rigName + '_exportRigNode')
        exportRigNode = pm.ls(sl = True)[0]
        pm.select(clear = True)

    except:
        exportRigNode = pm.group(em = True, name = rigName + '_exportRigNode')
        pm.select(exportRigNode)
        pm.setAttr(exportRigNode.tx, keyable = False)
        pm.setAttr(exportRigNode.ty, keyable = False)
        pm.setAttr(exportRigNode.tz, keyable = False)
        pm.setAttr(exportRigNode.rx, keyable = False)
        pm.setAttr(exportRigNode.ry, keyable = False)
        pm.setAttr(exportRigNode.rz, keyable = False)
        pm.setAttr(exportRigNode.sx, keyable = False)
        pm.setAttr(exportRigNode.sy, keyable = False)
        pm.setAttr(exportRigNode.sz, keyable = False)
        pm.setAttr(exportRigNode.v, keyable = False)
        pm.select(clear = True)

    #parent node under ROOT group
    pm.parent(exportRigNode, rootGRP)


    #create joints and put them under export joint group
    try:
        pm.select(rigName + '_exportJNT_GRP')
        exportJntGRP = pm.ls(sl = True)[0]
    except:
        exportJntGRP = pm.group(em = True, name = rigName + '_exportJNT_GRP')
        pm.parent(exportJntGRP, rootGRP)
        pm.scaleConstraint('master_CTRL', exportJntGRP)

    #check to see if joint list exists and if not then create it and put every joint under it
    try:
        attrList = pm.attributeQuery('joints', node = exportRigNode, listEnum = True)[0]
        attrList = attrList.split(':')
        print attrList
        #delete attribute so you can rebuild it, check to see if the joint already exists and if it doesn't add it to the enum
        pm.deleteAttr(exportRigNode.joints)
        jointAttr = ''
        #find the joints in the selection that are new and add them into the list of the attribute
        selection = set()
        for each in jointSelection:
            selection.add(each.name() + '_export')

        oldJnts = set(attrList)

        newJnts = selection.difference(oldJnts)


        print oldJnts
        print newJnts

        for each in oldJnts:
            jointAttr = jointAttr + each + ':'
        pm.select(clear = True)

        for each in newJnts:
            jointAttr = jointAttr + each + ':'
        pm.select(clear = True)
        for each in newJnts:
            each = each.replace('_export', '')
            jnt = pm.joint(name = each + '_export')
            pm.parent(jnt, exportJntGRP)
            pm.parentConstraint(each, jnt)
            selection = pm.ls(sl = True)

        pm.addAttr(exportRigNode, at = 'enum', en = jointAttr, sn = 'joints', keyable = True)
    except:
        #create new joints that are specified and then add them into the list of joints
        x = 0
        jointAttr = ''
        for each in jointSelection:
            jnt = pm.joint(name = each + '_export')
            pm.parent(jnt, exportJntGRP)
            pm.parentConstraint(each, jnt)
            if x == 0:
                jointAttr = each + '_export:'
                x = x + 1
            else:
                jointAttr = jointAttr + each + '_export:'
        pm.addAttr(exportRigNode, at = 'enum', en = jointAttr, sn = 'joints', keyable = True)



def addJoints():
    #select joints and check to see that they are actually joints/are export joints
    selection = pm.ls(sl = True)
    for each in selection:
        type = pm.nodeType(each)
        if type != 'joint':
            pm.error('Non-Joints are selected')
        jointName = each.split('_')
        num = len(jointName)
        num = num - 1
        if jointName[num] != 'BONE':
            pm.error('Non export joints selected')

    #query all joints in the textScrollList and check to make sure there are no more than 20 joints/have not
    #been added to the list yet
    TSLitems = pm.textScrollList(setJointsTSL, query = True, ai = True)
    lenSelection = len(selection)
    lenTSL = len(TSLitems)
    numJoints = lenSelection + lenTSL
    if numJoints >= 21:
        pm.error('Set list will have more than 20 joints')
    for jnt in selection:
        for each in TSLitems:
            if each == jnt:
                pm.error(each + ' already added to set')

    #add joints to the text scroll list
    for jnt in selection:
        pm.textScrollList(setJointsTSL, a = jnt, e = True)

def removeJoints():
    #query what is selected in the text scroll list and delete whatever is selected from the list
    TSLitems = pm.textScrollList(setJointsTSL, query = True, si = True)
    for each in TSLitems:
        TSLitems = pm.textScrollList(setJointsTSL, ri = each, e = True)

def createSet():

    #query what your new set name is, if there is no name or if the set exists already return an error
    setName = pm.textFieldGrp(setNameText, query = True, tx = True)

    if setName == '':
        pm.error('No set name in text box')
    try:
        pm.select('*exportRigNode')
        exportRigNode = pm.ls(sl = True)[0]
        attrList = pm.attributeQuery('sets', node = exportRigNode, listEnum = True)[0]
        attrList = attrList.split(':')
        x = 0


    except:
        #add the attribute that contains all sets along with the attribute which contains your first set
        pm.select('*exportRigNode')
        exportRigNode = pm.ls(sl = True)[0]
        pm.addAttr(exportRigNode, at = 'enum', en = setName + ':', sn = 'sets', keyable = True)
        TSLitems = pm.textScrollList(setJointsTSL, query = True, ai = True)
        TSLattr = ''
        for each in TSLitems:
            TSLattr = TSLattr + each + ':'
        pm.addAttr(exportRigNode, at = 'enum', en = TSLattr, sn = setName + '_set', keyable = True)


        x = 1

    if x == 0:
        #check to see if the set already exists, if not add the set to the sets attribute and then create
        #a new attribute which holds all of the joints in the set
        for each in attrList:
            if each == setName:
                pm.error('Set already exists')
        setsAttr = ''
        for each in attrList:
            setsAttr = setsAttr + each + ':'
        setsAttr = setsAttr + setName + ':'
        pm.deleteAttr(exportRigNode.sets)
        pm.addAttr(exportRigNode, at = 'enum', en = setsAttr, sn = 'sets', keyable = True)

        TSLitems = pm.textScrollList(setJointsTSL, query = True, ai = True)
        TSLattr = ''
        for each in TSLitems:
            TSLattr = TSLattr + each + ':'
        pm.addAttr(exportRigNode, at = 'enum', en = TSLattr, sn = setName + '_set', keyable = True)

    #get all attributes of the export rig node and check to see which sets have been created
    nodeAttrList = pm.listAttr(exportRigNode, keyable = True)
    setList = []
    for attr in nodeAttrList:
        if '_set' in attr:
            uiDict['setName'] = attr.replace('_set', '')
            setList.append(uiDict['setName'])

    remakeMenu1(setList)
    remakeMenu2(setList)



def loadRig():

    selection = pm.ls(sl = True)
    if len(selection) > 1:
        pm.error('More than one object selected')
    rootGRP = str(selection[0])

    if 'ROOT' not in rootGRP:
        pm.error('This is not a ROOT group')

    root = rootGRP.replace('_ROOT', '')
    exportRigNode = root + '_exportRigNode'

    #get all attributes of the export rig node and check to see which sets have been created
    nodeAttrList = pm.listAttr(exportRigNode, keyable = True)
    setList = []
    for attr in nodeAttrList:
        if '_set' in attr:
            setName = attr.replace('_set', '')
            setList.append(setName)
    print setList

    remakeMenu1(setList)
    remakeMenu2(setList)

    pm.textFieldGrp( loadRigText, tx = root + ' rig is loaded', e = True)

#take the attribute on the exportRigNode associated with the selected set and load the joints into the text scroll list

def loadSet():
    TSLitems = pm.textScrollList(setJointsTSL, query = True, removeAll = True, e = True)
    selectedSet = pm.optionMenu(uiDict['setsOM1'], query = True, value = True)
    exportRigNode = pm.ls('*_exportRigNode')[0]

    attrList = pm.attributeQuery(selectedSet + '_set', node = exportRigNode, listEnum = True)[0]
    jnts = attrList.split(':')
    for each in jnts:
        pm.textScrollList(setJointsTSL, a = each, e = True)

    pm.textFieldGrp( setNameText, tx = selectedSet, e = True)

def deleteSet():
    selectedSet = pm.optionMenu(uiDict['setsOM1'], query = True, value = True)
    exportRigNode = pm.ls('*_exportRigNode')[0]
    pm.deleteAttr(exportRigNode + '.' + selectedSet + '_set')

    attrList = pm.attributeQuery('sets', node = exportRigNode, listEnum = True)[0]
    attrList = attrList.split(':')

    attrList.remove(selectedSet)

    setsAttr = ''
    for each in attrList:
        setsAttr = setsAttr + each + ':'
    pm.deleteAttr(exportRigNode.sets)
    pm.addAttr(exportRigNode, at = 'enum', en = setsAttr, sn = 'sets', keyable = True)

    #get all attributes of the export rig node and check to see which sets have been created
    nodeAttrList = pm.listAttr(exportRigNode, keyable = True)
    setList = []
    for attr in nodeAttrList:
        if '_set' in attr:
            setName = attr.replace('_set', '')
            setList.append(setName)

    remakeMenu1(setList)
    remakeMenu2(setList)


def prepareAnim():
    #check to make sure a rig is loaded into the tool
    loadRigCheck = pm.textFieldGrp( loadRigText, query = True, tx = True)
    if 'rig is loaded' not in loadRigCheck:
        pm.error('Load a rig')

    #check to see what the selected set is
    selectedSet = pm.optionMenu(uiDict['setsOM2'], query = True, value = True)

    loadedRig = loadRigCheck.replace(' rig is loaded', '')
    exportRigNode = loadedRig + '_exportRigNode'

    allJnts = pm.attributeQuery('joints', node = exportRigNode, listEnum = True)[0]
    allJnts = allJnts.split(':')

    jntList = pm.attributeQuery(selectedSet + '_set', node = exportRigNode, listEnum = True)[0]
    jntList = jntList.split(':')


    #parent all joints under one joint so that the import works into AR studio
    x = 0

    for each in jntList:
        if x == 0:
            parentJnt = each
        else:
            pm.parent(each, parentJnt)

        x = x + 1

    #find what joints are not being used in the set
    deleteList = []
    for each in allJnts:
        for jnt in jntList:
            if jnt == each:
                deleteList.append(each)

    jntListSet = set(jntList)
    allJntsSet = set(allJnts)
    deleteJntsSet = allJntsSet.difference(jntListSet)

    #find the skinclusters that are connected to the selected joints
    scList = []
    pm.select('skinCluster*')
    selection = pm.ls(sl = True)
    for each in selection:
        type = pm.nodeType(each)
        if type == 'skinCluster':
            scList.append(each)

    usedScSet = set()
    #find which skin clusters are being used by the specified joints
    for sc in scList:
        influences = pm.skinCluster(sc, query = True, wi = True)

        #convert the influences to strings so it can be compared
        influenceSet = set()
        for each in influences:
            influenceSet.add(str(each))

        sharedInfSet = influenceSet.intersection(jntListSet)

        if len(sharedInfSet) > 0:
            usedScSet.add(sc)

    #get a list of all geo in the scene
    geo = []
    shapes = cmds.ls(s = True)
    for each in shapes:
        type = cmds.nodeType(each)
        if type == 'mesh':
            geo.append(each)
    allGeoSet = set(geo)


    #find the geo that is not being used in the rig
    keepGeoSet = set()
    influencedGeo = []
    for sc in usedScSet:

        influencedGeoPM = pm.skinCluster(sc, query = True, g = True)
        for each in influencedGeoPM:
            parent = pm.listRelatives(each, p = True)
            children = pm.listRelatives(parent, c = True)
            for child in children:
                geo = str(child)
                influencedGeo.append(geo)

        for each in influencedGeo:
            keepGeoSet.add(each)

    deleteGeoSet = allGeoSet.difference(keepGeoSet)

    #bake joints
    start = pm.playbackOptions(query = True, min = True)
    end = pm.playbackOptions(query = True, max = True)

    pm.bakeResults(jntListSet, simulation = True, t = str(start) + ':' + str(end), shape = True, sampleBy = 1, disableImplicitControl = True, preserveOutsideKeys = True,
    sparseAnimCurveBake = False, removeBakedAttributeFromLayer = False, removeBakedAnimFromLayer = False, bakeOnOverrideLayer = False, minimizeRotation = True, controlPoints = False)


    #delete everything in the scene that doesn't need to be in the export
    pm.select('*Constraint*')
    pm.delete()

    print deleteGeoSet
    pm.delete(deleteGeoSet)
    pm.delete(deleteJntsSet)

    rootChildren = cmds.listRelatives(loadedRig + '_ROOT',c = True)
    geoGRP = ''
    jntGRP = ''

    for each in rootChildren:
        if 'geo' in each:
            geoGRP = each
        if 'bone' in each:
            jntGRP = each

    if geoGRP == '':
        pm.error('No GEO_GRP under ROOT group')

    rootChildren.remove(geoGRP)
    rootChildren.remove(jntGRP)

    for each in rootChildren:
        pm.delete(each)

    pm.select(clear = True)
    #delete all empty nulls
    trList = cmds.ls(tr = True)

    for each in trList:
        type = cmds.nodeType(each)
        if type == 'transform':
            children = cmds.listRelatives(each, c = True)
            if children == None:
                cmds.delete(each)

    #run it again to delete any leftover empty nodes
    trList = cmds.ls(tr = True)

    for each in trList:
        type = cmds.nodeType(each)
        if type == 'transform':
            children = cmds.listRelatives(each, c = True)
            if children == None:
                cmds.delete(each)