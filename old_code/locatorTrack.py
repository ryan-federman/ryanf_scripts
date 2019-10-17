import pymel.core as pm

#get prefix of GEO
prefix = pm.ls(sl = True)
prefix = prefix[0].split(':')
prefix = prefix[0]

try:
    pm.select(prefix + ':L_cornea_GEO')
    addOn = ''
except:
    addOn = 'HenModel_base_v004_'

#the 3 vertices that each locator is snapped to
L_eye = prefix + addOn + ':L_cornea_GEO.vtx[1394]'
R_eye = prefix + addOn + ':R_cornea_GEO.vtx[1394]'
beak = prefix + addOn + ':Hen_head_GEO.vtx[3132]'

#start and end of the timeline
start = int(pm.playbackOptions(query = True, min = True))
end = int(pm.playbackOptions(query = True, max = True))


for x in range(start, end):
    pm.currentTime( x, edit=True )
    #get position of each vtx
    L_eye_pos = pm.xform(L_eye, t = True, ws = True, query = True)
    R_eye_pos = pm.xform(R_eye, t = True, ws = True, query = True)
    beak_pos = pm.xform(beak, t = True, ws = True, query = True)

    #bring locator to position
    pm.xform('CHBR:beak_LOC', t = (beak_pos[0], beak_pos[1], beak_pos[2]), ws = True)
    pm.xform('CHBR:L_eye_LOC', t = (L_eye_pos[0], L_eye_pos[1], L_eye_pos[2]), ws = True)
    pm.xform('CHBR:R_eye_LOC', t = (R_eye_pos[0], R_eye_pos[1], R_eye_pos[2]), ws = True)

    #set key on each locator
    pm.setKeyframe('CHBR:beak_LOC')
    pm.setKeyframe('CHBR:L_eye_LOC')
    pm.setKeyframe('CHBR:R_eye_LOC')


