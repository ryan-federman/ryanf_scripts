import maya.cmds as cmds
import pymel.core as pm

#Select every joint down the chain and then query
fkJoints = cmds.ls(sl = True)

#Select every fk control then query
fkCTRLS = cmds.ls(sl = True)

#Select IK control then query
ikCTRL = cmds.ls(sl = True)

#Select magic hand control then query
mHandCTRL = cmds.ls(sl = True)

#get name of finger
finName = fkCTRLS[0].split('S')
finName = finName[0]
print finName

#orient constrain the joints to the FK controls
x = 0
for jnt in fkJoints:
    cmds.orientConstraint(fkCTRLS[x], jnt, mo = True)
    x = x + 1

#duplicate base joint to make IK joint chain
cmds.select(clear = True)
cmds.select(fkJoints[0])
ikJoints = cmds.duplicate()

#rename all IK joints
cmds.select(hi = True)
selection = pm.ls(sl = True)
x = 0
ikJNTS = []
for each in selection:
    if x == 0:
        ikJNT1 = each
        ikJNTS.append(ikJNT1)
    if x == 1:
        ikJNT2 = each
        ikJNTS.append(ikJNT2)
    if x == 2:
        ikJNT3 = each
        ikJNTS.append(ikJNT3)
    if x == 3:
        ikJNT4 = each
        ikJNTS.append(ikJNT4)
    x = x + 1

pm.rename(ikJNT1, finName + 'IK1_JNT' )
pm.rename(ikJNT2, finName + 'IK2_JNT' )
pm.rename(ikJNT3, finName + 'IK3_JNT' )
pm.rename(ikJNT4, finName + 'IK4_JNT' )

#make each joint larger and color it red

for each in ikJNTS:
    pm.setAttr(each.radi, .43 )

pm.setAttr(ikJNT1.overrideColor, 13)

#set preferred angle of middle finger joint
pm.setAttr(ikJNT3.rx, 90)
pm.joint(ikJNT3, e = True, spa = True, ch = True )
pm.setAttr(ikJNT3.rx, 0)

#create IK handle
cmds.select(clear = True)
pm.select(ikJNT2)
pm.select(ikJNT4, add = True)
ikHand = pm.ikHandle(sol = 'ikRPsolver', name = finName + 'IKHandle')
ikHand = ikHand[0]
ikHandGRP = pm.group(ikHand, name = ikHand + '_GRP')

#create up vector for IK
upVector = pm.spaceLocator(name = finName + 'upVector')
locPosition = pm.xform(ikJNT3, ws = True, t = True, query = True)
pm.xform(upVector, ws = True, t = (locPosition[0], locPosition[1] + 5, locPosition[2]))

#parent contrain upVector to the first IK joint so that it always remains aligned with the chain
pm.parentConstraint(ikJNT1, upVector, mo = True)

#constrain the IK to pole vector and the ik finger control
pm.poleVectorConstraint(upVector, ikHand)
pm.pointConstraint(ikCTRL[0], ikHand)

#aim the knuckle joint at the ik control
pm.aimConstraint(ikCTRL[0], ikJNT1, mo = True, weight = 1, aimVector = (0,0,1), upVector = (0,1,0), worldUpType = 'vector', worldUpVector = (0,1,0), skip = ['x','z'])

#parent constrain the y rotation of your IK CTRL so it stays oriented to the chain
pm.parentConstraint(ikJNT1, ikCTRL[0], mo = True, skipTranslate = ['x','y','z'], skipRotate = ['x','z'])

#tie the rotation of the IK end joint to your IK control
pm.orientConstraint(ikCTRL[0], ikJNT4, mo = True)

#connect rotation of ik joints plus the values on your magic hand to the offset group of each fk control
x = 1
for each in fkCTRLS:
    if x == 1:
        PMA = pm.createNode('plusMinusAverage', name = finName + '1PMA')
        pm.connectAttr(mHandCTRL[0] + '.' + finName + 'Spread', PMA.input1D[0])
        pm.connectAttr(ikJNT1.ry, PMA.input1D[1])
        pm.connectAttr(PMA.output1D, each + '_off.ry')
        x = x + 1
    else:
        y = x - 1
        PMA = pm.createNode('plusMinusAverage', name = finName + str(x) + 'PMA')
        pm.connectAttr(mHandCTRL[0] + '.' + finName + str(y), PMA.input1D[0])
        pm.connectAttr(finName + 'IK' + str(x) + '_JNT.rx', PMA.input1D[1])
        pm.connectAttr(PMA.output1D, each + '_off.rx')
        x = x + 1
