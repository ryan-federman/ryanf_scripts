import maya.cmds as cmds
import pymel.core as pm

#check to see if you want the rotation,translation, or both matched
translation = True
rotation = True

#account for different gimbals
rotXChange = 0
rotYChange = 0
rotZChange = 0

#parameters for the time that keys are set in
timeSlider = [0,180]






#function to match the positions of the two objects
def posRotMatch(oldCTRL, newCTRL, rotXChange, rotYChange, rotZChange, translation, rotation):
    #create groups, put top group under the old control and rotate it to match the 0 rotation of the new control
    topGRP = pm.group(em = True)
    posGRP = pm.group(em = True)
    pm.parent(posGRP, topGRP)

    pm.parent(topGRP, oldCTRL)
    pm.setAttr(topGRP.t, 0,0,0)
    pm.setAttr(topGRP.r, 0,0,0)

    pm.setAttr(posGRP.r, rotXChange, rotYChange, rotZChange)

    if translation == True:
        mainTrans = pm.xform(oldCTRL, t = True, query = True, ws = True)
        pm.xform(newCTRL, t = (mainTrans[0], mainTrans[1], mainTrans[2]), ws = True)
    else:
        translation = False

    if rotation == True:

        mainRot = pm.xform(posGRP, ro = True, query = True, ws = True)
        x = mainRot[0]
        y = mainRot[1]
        z = mainRot[2]

        pm.xform(newCTRL, ro = (x,y,z), ws = True)

    pm.delete(topGRP)



#put both controls into variables
sel = pm.ls(sl = True)
oldCTRL = sel[0]
newCTRL = sel[1]

#set time start and time end
timeStart = timeSlider[0]
timeEnd = timeSlider[1]

import time
#loop that goes to each keyframe, sets the controls to each other, sets a keyframe
cmds.currentTime( timeStart, edit=True )
y = 0
first = cmds.findKeyframe( time = (timeStart, timeEnd))
while y < 2:
    pm.select(oldCTRL)
    num = cmds.findKeyframe( timeSlider = True, which = "next")
    if num == first:
        y = y + 1
    cmds.currentTime( num, edit=True )
    posRotMatch(oldCTRL, newCTRL, rotXChange, rotYChange, rotZChange, translation, rotation)
    time.sleep(1)
    pm.setKeyframe(newCTRL)
