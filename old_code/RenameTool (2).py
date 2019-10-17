import maya.cmds as cmds
import pymel.core as pm

def hierarchy():
    cmds.select( hi = True )    
    selection = pm.ls( sl = True )

def prefix(pre, Left, Right):
    selection = pm.ls( sl = True, tr = True )
    preLeft = Left + '_'
    preRight = Right + '_'

    for each in selection:
        object1 = str(each)
        x = 0
        for prefix in preList:
            if prefix in str(each):
                x = x + 1
                removePrefix = prefix
        if x > 0:
            query1 = True
        else:
            query1 = False
        query2 = preLeft in str(each)
        query3 = preRight in str(each)
        if '|' in each:
            repeatList = object1.split('|')
            object1 = repeatList[1]
        if query1 == True:
            newName = object1.split(removePrefix)
            newName = '{a}_'.format(a = pre) + newName[1]
        elif query2 == True:
            newName = object1.split(preLeft)
            newName = '{a}_'.format(a = pre) + newName[1]
        elif query3 == True:
            newName = object1.split(preRight)
            newName = '{a}_'.format(a = pre) + newName[1]
        else:
            newName = '{a}_'.format(a = pre) + object1
        pm.rename(each, newName)

def prefixAdd(pre):
    selection = pm.ls( sl = True, tr = True)
    for each in selection:
        object1 = str(each)
        if '|' in object1:
            repeatList = object1.split('|')
            object1 = repeatList[1]
        newName = pre + '_' + object1
        pm.rename(each, newName) 

def suffix( suf, left, right ):
    selection = pm.ls( sl=True )
    suffix = '_' + suf

    for each in selection:
        nameList = each.split('_')
        x = len(nameList)
        x = x - 1
        y = 1
        newName = nameList[0]
        
        #Checking to see if a prefix is in the name
        leftC = left in each
        rightC = right in each
        if leftC or rightC == True:
            prefixC = True
        else:
            prefixC = False
        #If an object only has a prefix and a name then it will just add the suffix
        if prefixC == True and len(nameList) == 2:
            newName = each + '_' + suf
        #Replaces the last text after the last '_' with the suffix
        else:
            while y < x:
                newName = newName + '_' + nameList[y]
                y = y + 1
            newName = newName + '_{a}'.format(a = suf)
        pm.rename(each, newName)

def suffixAdd( suf ):
    selection = pm.ls( sl=True )
    for each in selection:
        newName = each + '_' + suf
        pm.rename(each, newName)


 

def name( newName, Left, Right, suf ):
    selection = pm.ls(sl = True )
    z = 1

    for each in selection:
        reNamed = newName
        nameList = each.split('_')
        x = len(nameList)
        y = x-1
        condition = True
        condition1 = True
        prefix = nameList[0]
        suffix = nameList[y]
        if len(selection) == 1:
            reNamed = newName
        else:
            reNamed = newName + str(z)

        if x == 1:
            reNamed = reNamed
        elif x == 3:
            reNamed = prefix + '_' + reNamed + '_' + suffix
        else:
            for pre in preList:
                if pre in each:
                    reNamed = pre + reNamed
                    condition = False
            if condition == True:
                if Left in each:
                    reNamed = Left + '_' + reNamed
                if Right in each:
                    reNamed = Right + '_' + reNamed
            for suffix in sufList:
                if suffix in each:
                    reNamed = reNamed + suffix
                    condition1 = False
            if condition1 == True:
                if suf in each:
                    reNamed = reNamed + '_' + suf
        z = z + 1

        pm.rename(each, reNamed)

def nameSpace():
    selection = pm.ls( sl = True, tr = True )

    for each in selection:
        name = str(each)
        nameList = name.split(':')
        if len(nameList) == 2:
            newName = nameList[1]
            pm.rename(each, newName)

def fullRename(preVar, nameVar, sufVar):
    #Checking to see if the respective checkboxes are checked
    prefixC = False
    nameC = False
    suffixC = False
    if cmds.checkBox( preCheck, query=True, value = True) == True:
        prefixC = True
    if cmds.checkBox( nameCheck, query=True, value = True) == True:
        nameC = True
    if cmds.checkBox( sufCheck, query=True, value = True) == True:
        suffixC = True

    #Adds whatever checkboxes are checked to the name
    newName = 'placeHolder'
    if prefixC == True:
        newName = newName + '_' + preVar
    if nameC == True:
        newName = newName + '_' + nameVar
    if suffixC == True:
        newName = newName + '_' + sufVar
        newNameList = newName.split('_')
    length = len(newNameList)

    if length == 2:
        newName = newNameList[1]
    if length == 3:
        newName = newNameList[1] + '_' + newNameList[2]
    if length == 4:
        newName = newNameList[1] + '_' + newNameList[2] + '_' + newNameList[3]
       
    selection = cmds.ls( sl = True, tr = True )
    x = 1
    for each in selection:
        if len(selection) == 1:
            newName = newName
        else:
            newName = newName + str(x)
        cmds.rename(each, newName)
        x = x + 1



def printTxtField(fieldID):
    print cmds.textField( fieldID, query=True, text=True)

def printCheckBox():
    leftVar = cmds.textField(leftText, query = True, text = True)
    rightVar = cmds.textField(rightText, query = True, text = True)
    preVar = directionButton(dirCollection)
    sufVar = cmds.textField( sufField, query = True, text = True ) 
    sufButton = cmds.radioCollection( sufCollection, query = True, sl = True)
    preButton = cmds.radioCollection( preAddCollection, query = True, sl = True)
    nameVar = cmds.textField( nameField, query = True, text = True)

    if cmds.checkBox( hiCheck, query = True, value = True) == True:
        hierarchy()
    if cmds.checkBox( fullCheck, query = True, value = True) == False:
        if cmds.checkBox( nSpaceCheck, query = True, value = True) == True:
            nameSpace()
        if cmds.checkBox( preCheck, query=True, value = True) == True:
            if preButton == 'replace':
                prefix( preVar, leftVar, rightVar )
            else:
                prefixAdd( preVar )
            prefixC = True
        else:
            prefixC = False
        if cmds.checkBox( sufCheck, query=True, value = True) == True:
            if sufButton == 'replace':
                suffix( sufVar, leftVar, rightVar )
            else:
                suffixAdd( sufVar )
            suffixC = True
        else:
            suffixC = False
        if cmds.checkBox( nameCheck, query=True, value = True) == True:
            name(nameVar, leftVar, rightVar, sufVar)
            nameC = True
        else:
            nameC = False
    else:
        #Checking to see if the respective checkboxes are checked
        prefixC = False
        nameC = False
        suffixC = False
        if cmds.checkBox( preCheck, query=True, value = True) == True:
            prefixC = True
        if cmds.checkBox( nameCheck, query=True, value = True) == True:
            nameC = True
        if cmds.checkBox( sufCheck, query=True, value = True) == True:
            suffixC = True

        selection = pm.ls(sl=True, tr = True)
        #Adds whatever checkboxes are checked to the name
        
        #Number for name variable when renaming multiple objects
        x = 1
        for each in selection:
            #Number for telling how many checkboxes are checked
            y = 0
            newName = 'placeholder'
            if prefixC == True:
                newName = preVar
                y = y + 1
            if nameC == True:
                newNameVar = nameVar
                if len(selection) > 1:
                    newNameVar = nameVar + str(x)
                    x = x + 1
                if prefixC == True:
                    newName = newName + '_' + newNameVar
                else:
                    newName = newNameVar
                y = y + 1
            if suffixC == True:
                if prefixC or nameC == True:
                    newName = newName + '_' + sufVar
                else:
                    newName = sufVar
            pm.rename(each, newName)


def directionButton(dirID):
     if cmds.radioCollection( dirID, query=True, sl=True) == 'left':
        return cmds.textField(leftText, query = True, text = True)
     else:
        return cmds.textField(rightText, query = True, text = True)

#Set Possible Suffixes
sufList = ['_jnt', '_grp', '_GRP', '_JNT', '_geo', '_GEO', '_loc', '_LOC']

#Set Possible Prefixes
preList= ['left_', 'right_', 'r_', 'l_', 'Right_', 'Left_', 'rt_', 'lt_', 'RIGHT_', 'LEFT_']

winID = 'Rename Tool'

if cmds.window(winID, exists = True):
    cmds.deleteUI(winID)

winID = cmds.window('Rename Tool', width = 200)

cmds.frameLayout( label = 'Prefix')
leftText = cmds.textField('leftText', text = 'left')
rightText = cmds.textField('rightText', text = 'right')
dirCollection = cmds.radioCollection()
db1 = cmds.radioButton( 'left', label='Left' )
db2 = cmds.radioButton( 'right', label='Right' )
preAddCollection = cmds.radioCollection()
pAb1 = cmds.radioButton( 'replace', label='Replace')
pAb2 = cmds.radioButton( 'add', label = 'Add')
cmds.radioCollection( dirCollection, edit = True, select = db1)
cmds.radioCollection( preAddCollection, edit = True, select = pAb1)


cmds.frameLayout( label = 'Name')
nameField = cmds.textField('nameField')


cmds.frameLayout( label = 'Suffix')
sufField = cmds.textField('sufField')
sufCollection = cmds.radioCollection()
sb1 = cmds.radioButton( 'replace', label = 'Replace')
sb2 = cmds.radioButton( 'add', label = 'Add')
cmds.radioCollection( sufCollection, edit = True, select = sb1)

cmds.frameLayout( label = 'Checks')
hiCheck = cmds.checkBox('Hierarchy')
preCheck = cmds.checkBox('Prefix')
nameCheck = cmds.checkBox('Name')
sufCheck = cmds.checkBox('Suffix')
nSpaceCheck = cmds.checkBox('NameSpace Erase')
fullCheck = cmds.checkBox('Full Rename')

cmds.button( label = 'Rename', command = 'printCheckBox()')


cmds.showWindow()