import maya.cmds as cmds
import pymel.core as pm

#select the objects where the animation transfer will occur
selection = pm.ls(sl = True)

animObj = selection[0]
transObj = selection[1]

#get list of keyable attributes
attrs = pm.listAttr(animObj, keyable = True)

#loop that goes to each keyframe, sets the controls to each other, sets a keyframe

#find the first key and end key of the timeline then set the timeline to the first key
y = 0
firstKey = pm.playbackOptions(minTime = True, query = True)
endKey = pm.playbackOptions(maxTime = True, query = True)
pm.currentTime(firstKey, edit = True)

#loop to go to each keyframe on the old object and apply the values to the new object
while y < 2:

    #loop that sets every keyable attribute of the former object to the attrs of the new object

    for each in attrs:
        #check to see if the attribute has a key at the current time
        attrName = animObj + '.' + each
        keyTimes = pm.keyframe(attrName, query = True)
        frameCheck = False
        for frame in keyTimes:
            time = pm.currentTime(query = True)
            if frame == time:
                frameCheck = True
        #if the attribute has a key at this time set a key on the attribute
        if frameCheck == True:
            attrValue = pm.getAttr(animObj+ '.' + each)
            pm.setAttr(transObj + '.' + each, attrValue)
            pm.setKeyframe(transObj + '.' + each)

    #check to see if the next key frame is the first in the time slider and if so end the loop
    num = pm.findKeyframe( timeSlider = True, which = "next")
    if num == firstKey:
        y = y + 1
    pm.currentTime( num, edit=True )