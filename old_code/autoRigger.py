import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel

if pm.window('AutoRig', exists = True):
    pm.deleteUI('AutoRig')

winID = pm.window('AutoRig', title = "Ryan's Auto Rigger", width = 400, height = 400)

topFrame = pm.frameLayout( label = 'Create Locators')

topColumn = pm.columnLayout(adj = True, w = 400)

pm.setParent( topColumn )


instructionText = cmds.textFieldGrp('instructionText', label = 'Instructions', text = 'Create your first locator', ed = False, adj = 2) 

locButton = pm.button( label = 'Create Locator', c = "locCreate(locDict['locNumber'])", w = 70)

fingerText = cmds.textFieldGrp('fingerText', label = 'Finger Name', adj = 2) 

#Create textboxes for the options of what features are on the rig
fkCheck = pm.checkBox('FK')
ikCheck = pm.checkBox('IK')
stretchyCheck = pm.checkBox('Stretchy')

dirCollectionRig = cmds.radioCollection()
lDb = cmds.radioButton( 'left', label='Left' )
rDb = cmds.radioButton( 'right', label='Right' )
cmds.radioCollection( dirCollectionRig, edit = True, select = lDb)
#button for creating the rig

rigButton = pm.button( label = 'RIG', w = 70, c = 'autoRig()')

cmds.showWindow()

#start the count in order for the locators to created in the right succession
locDict = {}
locDict['locNumber'] = 0
locDict['fingerNumber'] = 0

#create a dictionary that stores the names of every finger that is created
fingerDict = {}


print locDict['locNumber']


#function for creating the locators in order to position the joints
def locCreate(locNumber):
    if locNumber == 0:
        locDict['shoulderLocator'] = pm.spaceLocator( n = 'shoulderPlace_LOC' )
        cmds.textFieldGrp('instructionText', edit=True, tx="Place your shoulder locator and then click 'Create Locator'")
        pm.headsUpMessage("Place your shoulder locator and then click 'Create Locator'", time = 5)
    
    if locNumber == 1:
        locDict['elbowLocator'] = pm.spaceLocator( n = 'elbowPlace_LOC' )
        
        #get the position of the previously made locator
        prevPos = cmds.getAttr(locDict['shoulderLocator'] + '.t')
        prevPos = prevPos[0]
        xPos = prevPos[0]
        yPos = prevPos[1]
        zPos = prevPos[2]
        
        #move the loc so it is separated in space from the shoulder loc
        cmds.setAttr(locDict['elbowLocator'] + '.tx' , xPos + 1 )
        cmds.setAttr(locDict['elbowLocator'] + '.ty' , yPos )
        cmds.setAttr(locDict['elbowLocator'] + '.tz' , zPos )
        
        cmds.textFieldGrp('instructionText', edit=True, tx="Place your elbow locator and then click 'Create Locator'")
        pm.headsUpMessage("Place your elbow locator and then click 'Create Locator'", time = 5)
        
    if locNumber == 2:
        locDict['wristLocator'] = pm.spaceLocator( n = 'wristPlace_LOC' )

        
        #get the position of the previously made locator
        prevPos = cmds.getAttr(locDict['elbowLocator'] + '.t')
        prevPos = prevPos[0]
        xPos = prevPos[0]
        yPos = prevPos[1]
        zPos = prevPos[2]
        
        #move the loc so it is separated in space from the elbow loc
        cmds.setAttr(locDict['wristLocator'] + '.tx' , xPos + 1 )
        cmds.setAttr(locDict['wristLocator'] + '.ty' , yPos )
        cmds.setAttr(locDict['wristLocator'] + '.tz' , zPos )
        
        cmds.textFieldGrp('instructionText', edit=True, tx="Place your wrist locator and then click 'Create Locator'")
        pm.headsUpMessage("Place your elbow locator and then click 'Create Locator'", time = 5)
    
    if locNumber == 3:
        locDict['handLocator'] = pm.spaceLocator( n = 'handPlace_LOC' )
        
        #get the position of the previously made locator
        prevPos = cmds.getAttr(locDict['wristLocator'] + '.t')
        prevPos = prevPos[0]
        xPos = prevPos[0]
        yPos = prevPos[1]
        zPos = prevPos[2]
        
        #move the loc so it is separated in space from the elbow loc
        cmds.setAttr(locDict['handLocator'] + '.tx' , xPos + 1 )
        cmds.setAttr(locDict['handLocator'] + '.ty' , yPos )
        cmds.setAttr(locDict['handLocator'] + '.tz' , zPos )
        
        cmds.textFieldGrp('instructionText', edit=True, tx="Place your hand locator in the middle of the hand and then click 'Create Locator'")
        pm.headsUpMessage("Place your hand locator in the middle of the hand and then click 'Create Locator'", time = 5)
        
    if locNumber == 4:
        
        #get the position of the previously made locator
        prevPos = cmds.getAttr(locDict['handLocator'] + '.t')
        prevPos = prevPos[0]
        xPos = prevPos[0]
        yPos = prevPos[1]
        zPos = prevPos[2]
        
        #create locator for firstThumb
        locDict['thumb1Locator'] = pm.spaceLocator( n = 'thumb1Place_LOC' )
        
        #move the loc so it is separated in space from the elbow loc
        cmds.setAttr(locDict['thumb1Locator'] + '.tx' , xPos )
        cmds.setAttr(locDict['thumb1Locator'] + '.ty' , yPos )
        cmds.setAttr(locDict['thumb1Locator'] + '.tz' , zPos + 1 )
        
        #create locators for all the subsequent thumb joints
        locDict['thumb2Locator'] = pm.spaceLocator(n = 'thumb2Place_LOC')
        cmds.setAttr(locDict['thumb2Locator'] + '.tx' , xPos )
        cmds.setAttr(locDict['thumb2Locator'] + '.ty' , yPos )
        cmds.setAttr(locDict['thumb2Locator'] + '.tz' , zPos + 3 )
        
        locDict['thumb3Locator'] = pm.spaceLocator(n = 'thumb3Place_LOC')
        cmds.setAttr(locDict['thumb3Locator'] + '.tx' , xPos )
        cmds.setAttr(locDict['thumb3Locator'] + '.ty' , yPos )
        cmds.setAttr(locDict['thumb3Locator'] + '.tz' , zPos + 5 )
        
        locDict['thumbTipLocator'] = pm.spaceLocator(n = 'thumbTipPlace_LOC')
        cmds.setAttr(locDict['thumbTipLocator'] + '.tx' , xPos )
        cmds.setAttr(locDict['thumbTipLocator'] + '.ty' , yPos )
        cmds.setAttr(locDict['thumbTipLocator'] + '.tz' , zPos + 7 )
        
        
        #create two nurbs curves that indicate direction
        mel.eval('circle; rotate -r -os -fo -60 0 0 ; rotate -r -os -fo -30 0 0 ; makeIdentity -apply true -t 1 -r 1 -s 1 -n 0 -pn 1; select -addFirst makeNurbCircle1 ; setAttr "makeNurbCircle1.degree" 1; setAttr "makeNurbCircle1.sections" 20; setAttr "makeNurbCircle1.sections" 15; select -r nurbsCircle1.cv[0] nurbsCircle1.cv[15] ; move -r -os -wd 0 0 -0.805299 ; select -r nurbsCircle1.cv[0:1] nurbsCircle1.cv[14:15] ; move -r -os -wd 0 0 -0.493941 ; select -r nurbsCircle1.cv[1] nurbsCircle1.cv[14] ; scale -r -p 0cm 0cm -1.407486cm 1.300099 1 1 ; select -r nurbsCircle1.cv[2] nurbsCircle1.cv[13] ; scale -r -p 0cm 0cm -0.669131cm 0.289046 1 1 ; move -r -os -wd 0 0 -0.749436 ; move -r -os -wd 0 0 0.0114854 ; select -cl  ; select -r nurbsCircle1.cv[9:12] ; scale -r -p 0.791154cm 0cm 0.25cm 1e-005 1 1 ; select -r nurbsCircle1.cv[3:6] ; scale -r -p -0.791154cm 0cm 0.25cm 1e-005 1 1 ; select -r nurbsCircle1.cv[3:6] nurbsCircle1.cv[9:12] ; scale -r -p 0cm 0cm 0.25cm 0.522222 1 1 ; select -r nurbsCircle1.cv[8:12] ; scale -r -p 0.310535cm 0cm 0.334565cm 1e-005 1 1 ; select -r nurbsCircle1.cv[3:7] ; scale -r -p -0.310535cm 0cm 0.334565cm 1e-005 1 1 ; select -r nurbsCircle1.cv[3:12] ; move -r -os -wd 0 0 -0.790447 ; scale -r -p 0cm 0cm -0.455882cm 0.711111 1 1 ; scale -r -p 0cm 0cm -0.455882cm 1 1 0.644444 ; move -r -os -wd 0 0 -0.323243 ; move -r -os -wd 0 0 0.36496 ; select -cl  ;')
        cmds.rename('nurbsCircle1', 'thumb1tyPlace')
        cmds.setAttr('thumb1tyPlace' + '.overrideEnabled', 1)
        cmds.setAttr('thumb1tyPlace' + '.overrideColor', 14)
        #duplicate it for the other thumb locs
        cmds.duplicate('thumb1tyPlace', name = 'thumb2tyPlace')
        cmds.duplicate('thumb1tyPlace', name = 'thumb3tyPlace')
        cmds.duplicate('thumb1tyPlace', name = 'thumbTiptyPlace')

        cmds.duplicate('thumb1tyPlace', name = 'thumb1tzPlace')
        cmds.setAttr('thumb1tzPlace' + '.overrideEnabled', 1)
        cmds.setAttr('thumb1tzPlace' + '.overrideColor', 6)
        
        cmds.duplicate('thumb1tzPlace', name = 'thumb2tzPlace')
        cmds.duplicate('thumb1tzPlace', name = 'thumb3tzPlace')
        cmds.duplicate('thumb1tzPlace', name = 'thumbTiptzPlace')
        
        #move each position indicator to it's locator and orient it accordingly
        point1 = pm.pointConstraint(locDict['thumb1Locator'], 'thumb1tyPlace', mo = False)
        pm.delete(point1)
        cmds.makeIdentity('thumb1tyPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        cmds.setAttr('thumb1tyPlace.rx', 90)
        cmds.setAttr('thumb1tyPlace.sx', .7)
        cmds.setAttr('thumb1tyPlace.sy', .7)
        cmds.setAttr('thumb1tyPlace.sz', .7)
        cmds.setAttr('thumb1tyPlace.ty', .5)
        pm.parent('thumb1tyPlace', locDict['thumb1Locator'])
        cmds.makeIdentity('thumb1tyPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        
        point1 = pm.pointConstraint(locDict['thumb1Locator'], 'thumb1tzPlace', mo = False)
        pm.delete(point1)
        cmds.makeIdentity('thumb1tzPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        cmds.setAttr('thumb1tzPlace.rx', 180)
        cmds.setAttr('thumb1tzPlace.sx', .7)
        cmds.setAttr('thumb1tzPlace.sy', .7)
        cmds.setAttr('thumb1tzPlace.sz', .7)
        cmds.setAttr('thumb1tzPlace.tz', .5)
        pm.parent('thumb1tzPlace', locDict['thumb1Locator'])
        cmds.makeIdentity('thumb1tzPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        
        
        
        point1 = pm.pointConstraint(locDict['thumb2Locator'], 'thumb2tyPlace', mo = False)
        pm.delete(point1)
        cmds.makeIdentity('thumb2tyPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        cmds.setAttr('thumb2tyPlace.rx', 90)
        cmds.setAttr('thumb2tyPlace.sx', .7)
        cmds.setAttr('thumb2tyPlace.sy', .7)
        cmds.setAttr('thumb2tyPlace.sz', .7)
        cmds.setAttr('thumb2tyPlace.ty', .5)
        pm.parent('thumb2tyPlace', locDict['thumb2Locator'])
        cmds.makeIdentity('thumb2tyPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        
        point1 = pm.pointConstraint(locDict['thumb2Locator'], 'thumb2tzPlace', mo = False)
        pm.delete(point1)
        cmds.makeIdentity('thumb2tzPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        cmds.setAttr('thumb2tzPlace.rx', 180)
        cmds.setAttr('thumb2tzPlace.sx', .7)
        cmds.setAttr('thumb2tzPlace.sy', .7)
        cmds.setAttr('thumb2tzPlace.sz', .7)
        cmds.setAttr('thumb2tzPlace.tz', .5)
        pm.parent('thumb2tzPlace', locDict['thumb2Locator'])
        cmds.makeIdentity('thumb2tzPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        
        point1 = pm.pointConstraint(locDict['thumb3Locator'], 'thumb3tyPlace', mo = False)
        pm.delete(point1)
        cmds.makeIdentity('thumb3tyPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        cmds.setAttr('thumb3tyPlace.rx', 90)
        cmds.setAttr('thumb3tyPlace.sx', .7)
        cmds.setAttr('thumb3tyPlace.sy', .7)
        cmds.setAttr('thumb3tyPlace.sz', .7)
        cmds.setAttr('thumb3tyPlace.ty', .5)
        pm.parent('thumb3tyPlace', locDict['thumb3Locator'])
        cmds.makeIdentity('thumb3tyPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        
        point1 = pm.pointConstraint(locDict['thumb3Locator'], 'thumb3tzPlace', mo = False)
        pm.delete(point1)
        cmds.makeIdentity('thumb3tzPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        cmds.setAttr('thumb3tzPlace.rx', 180)
        cmds.setAttr('thumb3tzPlace.sx', .7)
        cmds.setAttr('thumb3tzPlace.sy', .7)
        cmds.setAttr('thumb3tzPlace.sz', .7)
        cmds.setAttr('thumb3tzPlace.tz', .5)
        pm.parent('thumb3tzPlace', locDict['thumb3Locator'])
        cmds.makeIdentity('thumb3tzPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        
        point1 = pm.pointConstraint(locDict['thumbTipLocator'], 'thumbTiptyPlace', mo = False)
        pm.delete(point1)
        cmds.makeIdentity('thumbTiptyPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        cmds.setAttr('thumbTiptyPlace.rx', 90)
        cmds.setAttr('thumbTiptyPlace.sx', .7)
        cmds.setAttr('thumbTiptyPlace.sy', .7)
        cmds.setAttr('thumbTiptyPlace.sz', .7)
        cmds.setAttr('thumbTiptyPlace.ty', .5)
        pm.parent('thumbTiptyPlace', locDict['thumbTipLocator'])
        cmds.makeIdentity('thumb2tyPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        
        point1 = pm.pointConstraint(locDict['thumbTipLocator'], 'thumbTiptzPlace', mo = False)
        pm.delete(point1)
        cmds.makeIdentity('thumbTiptzPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        cmds.setAttr('thumbTiptzPlace.rx', 180)
        cmds.setAttr('thumbTiptzPlace.sx', .7)
        cmds.setAttr('thumbTiptzPlace.sy', .7)
        cmds.setAttr('thumbTiptzPlace.sz', .7)
        cmds.setAttr('thumbTiptzPlace.tz', .5)
        pm.parent('thumbTiptzPlace', locDict['thumbTipLocator'])
        cmds.makeIdentity('thumbTiptzPlace', apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        
        
        
        
        
    if locNumber > 4:
        
        fingerName = cmds.textFieldGrp(fingerText, query = True, text = True)
        #check to see if there is a name in the text box
        if fingerName == '':
            cmds.error('Put a name in the finger name text box')
        
        #check to see if the name already exists
        if cmds.objExists(fingerName + '1_LOC'):
            cmds.error('Finger name already exists')
            
        locDict['fingerNumber'] = locDict['fingerNumber'] + 1
        fingerNumber = str(locDict['fingerNumber'])
        
        
        fingerDict['finger' + fingerNumber] = fingerName
        
        print 'yes'
        
        
        
        #make 4 locators for each joint in a finger    
        prevPos = cmds.getAttr(locDict['handLocator'] + '.tx')
        locDict[fingerName + '1Locator'] = pm.spaceLocator(n = fingerName + '1' + '_LOC')
        cmds.setAttr(locDict[fingerName + '1Locator'] + '.tx', prevPos + 1)
        
        locDict[fingerName + '2Locator'] = pm.spaceLocator(n = fingerName + '2' + '_LOC')
        cmds.setAttr(locDict[fingerName + '2Locator'] + '.tx', prevPos + 2)
        
        locDict[fingerName + '3Locator'] = pm.spaceLocator(n = fingerName + '3' + '_LOC')
        cmds.setAttr(locDict[fingerName + '3Locator'] + '.tx', prevPos + 3)
        
        locDict[fingerName + 'TipLocator'] = pm.spaceLocator(n = fingerName + 'Tip' + '_LOC')
        cmds.setAttr(locDict[fingerName + 'TipLocator'] + '.tx', prevPos + 4)
        
        cmds.textFieldGrp('instructionText', edit=True, tx = "Position the locators on the finger and then click 'Create Locator'")

        
        
        
    
    locDict['locNumber'] = locNumber + 1
  
    
def autoRig():
    if locDict['locNumber'] < 6:
        cmds.error('create your locators')
    #check the side of the rig this arm will be created for    
    direction = cmds.radioCollection( dirCollectionRig, query=True, sl=True)
    
    #create shoulder joint, group it, orient it to point at next locator
    shoulderJoint = cmds.joint( name = direction + '_shoulder_jnt')
    shoulderJointGrp = cmds.group( shoulderJoint, name = shoulderJoint + '_grp')
    
    pC1 = pm.pointConstraint(locDict['shoulderLocator'], shoulderJointGrp)
    aC1 = pm.aimConstraint(locDict['elbowLocator'], shoulderJointGrp, offset = [0,0,0], weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpType = 'scene')
    pm.delete(pC1)
    pm.delete(aC1)
    
    
    
    
    #create elbow joint, group it, orient it to point at next locator
    elbowJoint = cmds.joint( name = direction + 'elbow_jnt')
    elbowJointGrp = cmds.group( elbowJoint, name = elbowJoint + '_grp')
    
    pC1 = pm.pointConstraint(locDict['elbowLocator'], elbowJointGrp)
    aC1 = pm.aimConstraint(locDict['wristLocator'], elbowJoint, offset = [0,0,0], weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpType = 'scene')
    pm.delete(pC1)
    pm.delete(aC1)
    cmds.makeIdentity(elbowJoint, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
    
    cmds.parent(elbowJointGrp, shoulderJoint)
    
    #create wrist joint, group it, orient it to point at next locator
    wristJoint = cmds.joint( name = direction + 'wrist_jnt')
    wristJointGrp = cmds.group( wristJoint, name = wristJoint + '_grp')
    
    pC1 = pm.pointConstraint(locDict['wristLocator'], wristJointGrp)
    pm.delete(pC1)
    pm.parent(wristJointGrp, elbowJoint)
    cmds.setAttr(wristJointGrp + '.r', 0,0,0)
    
    aC1 = pm.aimConstraint(locDict['handLocator'], wristJoint, offset = [0,0,0], weight = 1, aimVector = [1,0,0], upVector = [0,1,0], worldUpType = 'scene')
    pm.delete(aC1)
    cmds.makeIdentity(wristJoint, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
    
    #create FK joints and move them to their respective joints
    cmds.select(cl = True)
    
    shoulderFKjnt = cmds.joint(name = direction + 'shoulderFK_jnt')
    cmds.setAttr( shoulderFKjnt + '.radius', 1.5 )
    shoulderFKjntGrp = cmds.group( shoulderFKjnt, name = shoulderFKjnt + '_grp')
    
    pC1 = pm.pointConstraint( shoulderJoint, shoulderFKjntGrp )
    oC1 = pm.orientConstraint( shoulderJoint, shoulderFKjntGrp )
    pm.delete(pC1)
    pm.delete(oC1)
    
    shoulderFKOrient = cmds.getAttr(shoulderJoint + '.jointOrient')[0]
    cmds.setAttr( shoulderFKjnt + '.jointOrient', shoulderFKOrient[0], shoulderFKOrient[1], shoulderFKOrient[2] )
    
    cmds.orientConstraint(shoulderFKjnt, shoulderJoint)
    
    #create shoulder control
    shoulderControl = cmds.circle(name = direction + '_' + 'shoulder_ctl')[0]
    cmds.setAttr(shoulderControl + '.ry', 90)
    cmds.makeIdentity(shoulderControl, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
    shoulderControlGroup = cmds.group(shoulderControl, name = shoulderControl + '_grp')
    pC1 = cmds.pointConstraint(shoulderJoint, shoulderControlGroup, mo = False)
    oC1 = cmds.orientConstraint(shoulderJoint, shoulderControlGroup, mo = False)
    cmds.delete(pC1)
    cmds.delete(oC1)
    
    cmds.orientConstraint(shoulderControl, shoulderFKjnt, mo = True)
    
    #create FK elbow joint
    cmds.select(cl = True)
    elbowFKjnt = cmds.joint(name = direction + 'elbowFK_jnt')
    cmds.setAttr( elbowFKjnt + '.radius', 1.5 )
    elbowFKjntGrp = cmds.group( elbowFKjnt, name = elbowFKjnt + '_grp')
    
    pC1 = pm.pointConstraint( elbowJoint, elbowFKjntGrp )
    
    pm.delete(pC1)
    
    
    elbowFKOrient = cmds.getAttr(elbowJoint + '.jointOrient')[0]
    cmds.setAttr( elbowFKjnt + '.jointOrient', elbowFKOrient[0], elbowFKOrient[1], elbowFKOrient[2] )

    cmds.parent( elbowFKjntGrp, shoulderFKjnt )
    
    cmds.setAttr( elbowFKjntGrp + '.r', 0,0,0 )
    
    cmds.orientConstraint(elbowFKjnt, elbowJoint, mo = True)
    
    #create elbow control
    elbowControl = cmds.circle(name = direction + '_' + 'elbow_ctl')[0]
    cmds.setAttr(elbowControl + '.ry', 90)
    cmds.makeIdentity(elbowControl, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
    elbowControlGroup = cmds.group(elbowControl, name = elbowControl + '_grp')
    pC1 = cmds.pointConstraint(elbowJoint, elbowControlGroup, mo = False)
    oC1 = cmds.orientConstraint(elbowJoint, elbowControlGroup, mo = False)
    cmds.delete(pC1)
    cmds.delete(oC1)
    cmds.parent(elbowControlGroup, shoulderControl)
    
    cmds.orientConstraint(elbowControl, elbowFKjnt, mo = True)
    
    #create FK wrist joint
    cmds.select(cl = True)
    wristFKjnt = cmds.joint(name = direction + 'wristFK_jnt')
    cmds.setAttr( wristFKjnt + '.radius', 1.5 )
    wristFKjntGrp = cmds.group( wristFKjnt, name = wristFKjnt + '_grp')
    
    pC1 = pm.pointConstraint( wristJoint, wristFKjntGrp )
    
    pm.delete(pC1)
    
    
    wristFKOrient = cmds.getAttr(wristJoint + '.jointOrient')[0]
    cmds.setAttr( wristFKjnt + '.jointOrient', wristFKOrient[0], wristFKOrient[1], wristFKOrient[2] )

    cmds.parent( wristFKjntGrp, elbowFKjnt )

    cmds.setAttr( wristFKjntGrp + '.r', 0,0,0 )
    
    cmds.orientConstraint(wristFKjnt, wristJoint, mo = True)
    
    #create wrist control
    wristControl = cmds.circle(name = direction + '_' + 'wrist_ctl')[0]
    cmds.setAttr(wristControl + '.ry', 90)
    cmds.makeIdentity(wristControl, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
    wristControlGroup = cmds.group(wristControl, name = wristControl + '_grp')
    pC1 = cmds.pointConstraint(wristJoint, wristControlGroup, mo = False)
    oC1 = cmds.orientConstraint(wristJoint, wristControlGroup, mo = False)
    cmds.delete(pC1)
    cmds.delete(oC1)
    cmds.parent(wristControlGroup, elbowControl)
    
    cmds.orientConstraint(wristControl, wristFKjnt, mo = True)
    
    #create hand joint
    handJnt = cmds.joint(name = direction + 'hand_jnt' )
    
    pC1 = pm.pointConstraint(locDict['handLocator'], handJnt, mo = False)
    pm.delete(pC1)
    pm.parent(handJnt, wristJoint)
    
    #create thumb joints
    thumb1Jnt = cmds.joint(name = direction + '_' + 'thumb1_jnt')
    thumb1JntGrp = cmds.group(thumb1Jnt, name = thumb1Jnt + '_grp')
    
    pC1 = pm.pointConstraint(locDict['thumb1Locator'], thumb1JntGrp)
    oC1 = pm.orientConstraint(locDict['thumb1Locator'], thumb1JntGrp)
    pm.delete(pC1)
    pm.delete(oC1)
    pm.parent(thumb1JntGrp, handJnt)
    
    #create thumb1 control
    thumb1Control = cmds.circle(name = direction + '_' + 'thumb1_ctl')[0]
    
    cmds.makeIdentity(thumb1Control, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
    thumb1ControlGroup = cmds.group(thumb1Control, name = thumb1Control + '_grp')
    pC1 = cmds.pointConstraint(thumb1Jnt, thumb1ControlGroup, mo = False)
    oC1 = cmds.orientConstraint(thumb1Jnt, thumb1ControlGroup, mo = False)
    cmds.delete(pC1)
    cmds.delete(oC1)
    cmds.parent(thumb1ControlGroup, wristControl)
    
    cmds.orientConstraint(thumb1Control, thumb1Jnt, mo = True)
    
    #create thumb2 joint
    thumb2Jnt = cmds.joint(name = direction + '_' + 'thumb2_jnt')
    thumb2JntGrp = cmds.group(thumb2Jnt, name = thumb2Jnt + '_grp')
    
    pC1 = pm.pointConstraint(locDict['thumb2Locator'], thumb2JntGrp)
    oC1 = pm.orientConstraint(locDict['thumb2Locator'], thumb2JntGrp)
    pm.delete(pC1)
    pm.delete(oC1)
    pm.parent(thumb2JntGrp, thumb1Jnt)
    
    #create thumb2 control
    thumb2Control = cmds.circle(name = direction + '_' + 'thumb2_ctl')[0]
    
    cmds.makeIdentity(thumb2Control, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
    thumb2ControlGroup = cmds.group(thumb2Control, name = thumb2Control + '_grp')
    pC1 = cmds.pointConstraint(thumb2Jnt, thumb2ControlGroup, mo = False)
    oC1 = cmds.orientConstraint(thumb2Jnt, thumb2ControlGroup, mo = False)
    cmds.delete(pC1)
    cmds.delete(oC1)
    cmds.parent(thumb2ControlGroup, thumb1Control)
    
    cmds.orientConstraint(thumb2Control, thumb2Jnt, mo = True)
    
    
    #create thumb3 joint
    thumb3Jnt = cmds.joint(name = direction + '_' + 'thumb3_jnt')
    thumb3JntGrp = cmds.group(thumb3Jnt, name = thumb3Jnt + '_grp')
    
    pC1 = pm.pointConstraint(locDict['thumb3Locator'], thumb3JntGrp)
    oC1 = pm.orientConstraint(locDict['thumb3Locator'], thumb3JntGrp)
    pm.delete(pC1)
    pm.delete(oC1)
    pm.parent(thumb3JntGrp, thumb2Jnt)
    
    #create thumb3 control
    thumb3Control = cmds.circle(name = direction + '_' + 'thumb3_ctl')[0]
    
    cmds.makeIdentity(thumb3Control, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
    thumb3ControlGroup = cmds.group(thumb3Control, name = thumb3Control + '_grp')
    pC1 = cmds.pointConstraint(thumb3Jnt, thumb3ControlGroup, mo = False)
    oC1 = cmds.orientConstraint(thumb3Jnt, thumb3ControlGroup, mo = False)
    cmds.delete(pC1)
    cmds.delete(oC1)
    cmds.parent(thumb3ControlGroup, thumb2Control)
    
    cmds.orientConstraint(thumb3Control, thumb3Jnt, mo = True)
    
    #create thumbTip joint
    thumbTipJnt = cmds.joint(name = direction + '_' + 'thumbTip_jnt')
    thumbTipJntGrp = cmds.group(thumbTipJnt, name = thumbTipJnt + '_grp')
    
    pC1 = pm.pointConstraint(locDict['thumbTipLocator'], thumbTipJntGrp)
    oC1 = pm.orientConstraint(locDict['thumbTipLocator'], thumbTipJntGrp)
    pm.delete(pC1)
    pm.delete(oC1)
    pm.parent(thumbTipJntGrp, thumb3Jnt)
    
    #create finger joints
    for i in fingerDict:
        cmds.select(cl = True)
        fingerName = fingerDict[i]
        
        #create first joint and position it to the first loc
        joint1Name = direction + '_' + fingerName + '1_jnt'
        joint1 = cmds.joint(name = joint1Name)
        joint1Grp = cmds.group(joint1, name = joint1Name + '_grp')
        pC1 = pm.pointConstraint(fingerName + '1_LOC', joint1Grp, mo = False)
        aC1 = pm.aimConstraint(fingerName + '2_LOC', joint1Grp, mo = False)
        pm.delete(pC1)
        pm.delete(aC1)
        
        pm.parent(joint1Grp, handJnt)
        
        #create control, position it, and have it control the joint group
        control1Name = direction + '_' + fingerName + '1_ctl'
        control1 = cmds.circle(name = control1Name)[0]
        cmds.setAttr(control1 + '.ry', 90)
        cmds.makeIdentity(control1, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        
        control1Grp = cmds.group(control1, name = control1Name + '_grp')
        pC1 = cmds.pointConstraint(joint1, control1Grp)
        oC1 = cmds.orientConstraint(joint1, control1Grp)
        cmds.delete(pC1)
        cmds.delete(oC1)
        cmds.parent(control1Grp, wristControl)
        
        cmds.orientConstraint(control1, joint1, mo = True)
        
        
        #create second joint and position it to the first loc
        joint2Name = direction + '_' + fingerName + '2_jnt'
        joint2 = cmds.joint(name = joint2Name)
        joint2Grp = cmds.group(joint2, name = joint2Name + '_grp')
        pC1 = pm.pointConstraint(fingerName + '2_LOC', joint2Grp, mo = False)
        aC1 = pm.aimConstraint(fingerName + '3_LOC', joint2Grp, mo = False)
        pm.delete(pC1)
        pm.delete(aC1)
        cmds.parent(joint2Grp, joint1)
        
        #create control, position it, and have it control the joint group
        control2Name = direction + '_' + fingerName + '2_ctl'
        control2 = cmds.circle(name = control2Name)[0]
        cmds.setAttr(control2 + '.ry', 90)
        cmds.makeIdentity(control2, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        
        control2Grp = cmds.group(control2, name = control2Name + '_grp')
        pC1 = cmds.pointConstraint(joint2, control2Grp)
        oC1 = cmds.orientConstraint(joint2, control2Grp)
        cmds.delete(pC1)
        cmds.delete(oC1)
        
        cmds.orientConstraint(control2, joint2, mo = True)
        
        cmds.parent(control2Grp, control1)
        
        
        #create third joint and position it to the first loc
        joint3Name = direction + '_' + fingerName + '3_jnt'
        joint3 = cmds.joint(name = joint3Name)
        joint3Grp = cmds.group(joint3, name = joint3Name + '_grp')
        pC1 = pm.pointConstraint(fingerName + '3_LOC', joint3Grp, mo = False)
        aC1 = pm.aimConstraint(fingerName + 'Tip_LOC', joint3Grp, mo = False)
        pm.delete(pC1)
        pm.delete(aC1)
        cmds.parent(joint3Grp, joint2)
        
        #create control, position it, and have it control the joint group
        control3Name = direction + '_' + fingerName + '3_ctl'
        control3 = cmds.circle(name = control3Name)[0]
        cmds.setAttr(control3 + '.ry', 90)
        cmds.makeIdentity(control3, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
        
        control3Grp = cmds.group(control3, name = control3Name + '_grp')
        pC1 = cmds.pointConstraint(joint3, control3Grp)
        oC1 = cmds.orientConstraint(joint3, control3Grp)
        cmds.delete(pC1)
        cmds.delete(oC1)
        
        cmds.orientConstraint(control3, joint3, mo = True)
        
        cmds.parent(control3Grp, control2)
        
        
        #create fourth joint and position it to the first loc
        jointTipName = direction + '_' + fingerName + 'Tip_jnt'
        jointTip = cmds.joint(name = jointTipName)
        jointTipGrp = cmds.group(jointTip, name = jointTipName + '_grp')
        pC1 = pm.pointConstraint(fingerName + 'Tip_LOC', jointTipGrp, mo = False)
        pm.delete(pC1)
        cmds.parent(jointTipGrp, joint3)
        
    for i in locDict:
        if i == 'locNumber':
            #locDict['locNumber'] = 0
            #print 'locNumber'
            print 'locNumber reset'
        
        
        elif i == 'fingerNumber':
            #locDict['fingerNumber'] = 0
            #print 'fingerNumber'
            print 'fingerNumber reset'
        
        else:
            print i + ' deleted'
    
            pm.delete(locDict[i])
    

    locDict.clear
    locDict['locNumber'] = 0
    locDict['fingerNumber'] = 0 
    fingerDict.clear