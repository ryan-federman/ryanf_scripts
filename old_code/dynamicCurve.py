import maya.cmds as cmds
import pymel.core as pm

#name the wire and define the dictionaries
wireName = 'wristWire5'
cableObj = 'ROBM:elbow_cables_blackRubber_02_GEO'
botConstObj = 'wrist_JNT'
topConstObj = 'elbow_JNT'
locDict = {}
jntDict = {}

print locDict
#create locators to position in the cable
x = 0
while x < 9:
    locDict['LOC' + str(x)] = pm.spaceLocator(name = wireName + '_LOC' + str(x))
    LOC = locDict['LOC' + str(x)]
    pm.setAttr(LOC.tz, x)
    x = x + 1

#get locator positions for the cvs
loc0Pos = pm.getAttr(locDict['LOC0'].t)
loc1Pos = pm.getAttr(locDict['LOC1'].t)
loc2Pos = pm.getAttr(locDict['LOC2'].t)
loc3Pos = pm.getAttr(locDict['LOC3'].t)
loc4Pos = pm.getAttr(locDict['LOC4'].t)
loc5Pos = pm.getAttr(locDict['LOC5'].t)
loc6Pos = pm.getAttr(locDict['LOC6'].t)
loc7Pos = pm.getAttr(locDict['LOC7'].t)
loc8Pos = pm.getAttr(locDict['LOC8'].t)

#make curve with a cv at each locator
crv = pm.curve(d = 3, p = [(loc0Pos[0], loc0Pos[1], loc0Pos[2]), (loc1Pos[0], loc1Pos[1], loc1Pos[2]),  (loc2Pos[0], loc2Pos[1], loc2Pos[2]),  (loc3Pos[0], loc3Pos[1], loc3Pos[2]), (loc4Pos[0], loc4Pos[1], loc4Pos[2]), (loc5Pos[0], loc5Pos[1], loc5Pos[2]), (loc6Pos[0], loc6Pos[1], loc6Pos[2]), (loc7Pos[0], loc7Pos[1], loc7Pos[2]), (loc8Pos[0], loc8Pos[1], loc8Pos[2])])
pm.rename(crv, wireName)
pm.rebuildCurve(s = 12)
pm.select(clear = True)



#make a joint at every locator
x = 0

while x < 9:
    if x < 7:
        pos = pm.getAttr(locDict['LOC' + str(x)].t)
        jntDict[wireName + '_' + str(x) + '_JNT'] = pm.joint(name = wireName + '_' + str(x) + '_JNT', p = (pos[0], pos[1], pos[2]))
        jnt = jntDict[wireName + '_' + str(x) + '_JNT']
        x = x + 1
    else:
        if x == 7:
            cmds.select(clear = True)
            pos = pm.getAttr(locDict['LOC' + str(x)].t)
            jntDict[wireName + '_' + str(x) + '_JNT'] = pm.joint(name = wireName + '_' + str(x) + '_JNT', p = (pos[0], pos[1], pos[2]))
            jnt = jntDict[wireName + '_' + str(x) + '_JNT']
            x = x + 1
        else:
            pos = pm.getAttr(locDict['LOC' + str(x)].t)
            jntDict[wireName + '_' + str(x) + '_JNT'] = pm.joint(name = wireName + '_' + str(x) + '_JNT', p = (pos[0], pos[1], pos[2]))
            jnt = jntDict[wireName + '_' + str(x) + '_JNT']
            x = x + 1

#create an IK handle for the joint chain
pm.select(clear = True)
pm.select(jntDict[wireName + '_1_JNT'])
pm.select(jntDict[wireName + '_6_JNT'], add = True)
ikHand = pm.ikHandle(sol = 'ikRPsolver', name = wireName + '_ikHandle')
ikHand = ikHand[0]
#bind the curve to the joints
pm.select(clear = True)

for each in jntDict:
    pm.select(each, add = True)
pm.select(crv, add = True)

pm.bindSkin()
#constrain top joint and ik handle to appropriate joints
pm.parentConstraint(topConstObj, jntDict[wireName + '_0_JNT'], mo = True)

pm.parentConstraint(jntDict[wireName + '_7_JNT'], ikHand, mo = True, skipRotate = ('x', 'y', 'z'))
pm.parentConstraint(botConstObj, jntDict[wireName + '_7_JNT'], mo = True)


for each in locDict:
    pm.delete(locDict[each])
