import pymel.core as pm

selection = pm.ls(sl = True)

selection = selection[0].split(':')
selection = selection[0]

#start and end of the timeline
start = int(pm.playbackOptions(query = True, min = True))
end = int(pm.playbackOptions(query = True, max = True))


wattleCTRL = selection + ':main_wattle_CTRL'
trackCTRL = selection + ':wattle_DYN_tracking_CTRL'

for x in range(start, end):
    pm.currentTime( x, edit=True )
    #get position and rotation of wattle
    pos = pm.xform(wattleCTRL, t = True, ws = True, query = True)
    rot = pm.xform(wattleCTRL, ro = True, ws = True, query = True)

    #account for offset
    newPosX = pos[0] - 3.0512130280106695e-15
    newPosY = pos[1] - 19.90173490308113
    newPosZ = pos[2] - 14.172344786334

    newRotX = rot[0] - 73.21978134383842
    newRotY = rot[1]
    newRotZ = rot[2]

    #position and rotate tracking control
    pm.setAttr(trackCTRL + '.translateX', newPosX)
    pm.setAttr(trackCTRL + '.translateY', newPosY)
    pm.setAttr(trackCTRL + '.translateZ', newPosZ)

    pm.setAttr(trackCTRL + '.rotateX', newRotX)
    pm.setAttr(trackCTRL + '.rotateY', newRotY)
    pm.setAttr(trackCTRL + '.rotateZ', newRotZ)

    #set key on CTRL
    pm.setKeyframe(trackCTRL)
