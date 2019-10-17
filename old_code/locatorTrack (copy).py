import pymel.core as pm

L_eye = pm.ls(sl = True)[0]
R_eye = pm.ls(sl = True)[0]
beak = pm.ls(sl = True)[0]


start = int(pm.playbackOptions(query = True, min = True))
end = int(pm.playbackOptions(query = True, max = True))


for x in range(start, end):
    pm.currentTime( x, edit=True )
    #get position of each vtx
    L_eye_pos = pm.xform(L_eye, t = True, ws = True, query = True)
    R_eye_pos = pm.xform(R_eye, t = True, ws = True, query = True)
    beak_pos = pm.xform(beak, t = True, ws = True, query = True)

    #bring locator to position
    pm.xform('beak_LOC', t = (beak_pos[0], beak_pos[1], beak_pos[2]), ws = True)
    pm.xform('L_eye_LOC', t = (L_eye_pos[0], L_eye_pos[1], L_eye_pos[2]), ws = True)
    pm.xform('R_eye_LOC', t = (R_eye_pos[0], R_eye_pos[1], R_eye_pos[2]), ws = True)

    #set key on each locator
    pm.setKeyframe('beak_LOC')
    pm.setKeyframe('L_eye_LOC')
    pm.setKeyframe('R_eye_LOC')

pln = pm.ls(sl = True)[0]
pos0 = pm.getAttr(pln.controlPoints[0])
pos1 = pm.getAttr(pln.controlPoints[1])
pos2 = pm.getAttr(pln.controlPoints[2])

node0 = pm.createNode('plusMinusAverage', name = 'cp0_PMA')
node1 = pm.createNode('plusMinusAverage', name = 'cp1_PMA')
node2 = pm.createNode('plusMinusAverage', name = 'cp2_PMA')

pm.setAttr(node0.input3D[1].input3D, pos0[0],pos0[1],pos0[2])
pm.setAttr(node1.input3D[1].input3D, pos1[0],pos1[1],pos1[2])
pm.setAttr(node2.input3D[1].input3D, pos2[0],pos2[1],pos2[2])