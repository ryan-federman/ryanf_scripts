import pymel.core as pm

jnts = pm.ls(sl = True)

parent = 'jaw'

for each in jnts:

    pm.select(parent)
    newName = each.split('_BONE')[0]

    jnt = pm.joint(name = newName)
    pm.parentConstraint(each, jnt, mo = False)


selection = pm.ls(sl = True)

for each in selection:
    pm.select(each)
    parent1 = pm.listRelatives(each, p = True)
    zero = pm.group(name = each + '_ZERO')
    pm.rename(parent1, zero)


for each in selection:
    pos = pm.xform(each, t = True, query = True, ws = True)
    rot = pm.xform(each, ro = True, query = True, ws = True)

    zero = pm.group(em = True, name = each + '_ZERO')

    parent1 = pm.listRelatives(each, p = True)

    pm.parent(zero, parent1)

    pm.xform(zero, t = (pos[0], pos[1], pos[2]), ws = True)
    pm.xform(zero, ro = (rot[0], rot[1], rot[2]), ws = True)

    pm.parent(each, zero)


selection = pm.ls(sl = True)


for x in range (0, len(selection)):
    ctrl = selection[x]
    jnt = ctrl.split('DYN')[0] + 'BONE'

    pm.select(ctrl)
    pm.addAttr(at = 'enum', en = 'FK:FKDYN:', shortName = 'dyns', keyable = True)
    pm.addAttr(at = 'float', shortName = 'dynInfluence', min = 0, max = 1, keyable = True)
    pm.select(clear = True)

    dynInfMultT = pm.createNode('multiplyDivide', name = jnt + '_dynInfMultT')
    dynCondT = pm.createNode('condition', name = jnt + '_dyn_CONDT')
    dynInfPMA1T = pm.createNode('plusMinusAverage', name = jnt + '_dynInfPMA1T')
    dynInfPMA2T = pm.createNode('plusMinusAverage', name = jnt + '_dynInfPMA2T')

    dynInfMultRot = pm.createNode('multiplyDivide', name = jnt + '_dynInfMultRot')
    dynCondR = pm.createNode('condition', name = jnt + '_dyn_CONDR')
    dynInfPMA1R = pm.createNode('plusMinusAverage', name = jnt + '_dynInfPMA1R')
    dynInfPMA2R = pm.createNode('plusMinusAverage', name = jnt + '_dynInfPMA2R')

    oldChainSRT = ((jnt.split('BONE')[0]) + 'bone_SRT_ZERO')
    newChainSRT = jnt + '_SRT'
    oldRot = jnt + '_rotMM_PMA'

    pos = pm.xform(oldChainSRT, t = True, relative = True, query = True)
    rot = pm.xform(oldChainSRT, ro = True, relative = True, query = True)

    pm.setAttr(dynInfPMA1R.input3D[0], rot[0], rot[1], rot[2])
    pm.connectAttr(oldRot + '.output3D', dynInfPMA1R.input3D[1])
    pm.setAttr(dynInfPMA1R.operation, 2)

    pm.connectAttr(dynInfPMA1R.output3D, dynInfMultRot.input1)
    pm.connectAttr(ctrl.dynInfluence, dynInfMultRot.input2X)
    pm.connectAttr(ctrl.dynInfluence, dynInfMultRot.input2Y)
    pm.connectAttr(ctrl.dynInfluence, dynInfMultRot.input2Z)

    pm.connectAttr(dynInfMultRot.output, dynInfPMA2R.input3D[0])
    pm.setAttr(dynInfPMA2R.input3D[1], rot[0], rot[1], rot[2])

    pm.connectAttr(dynInfPMA2R.output3D, dynCondR.colorIfFalse)
    pm.connectAttr(ctrl.dyns, dynCondR.firstTerm)
    pm.setAttr(dynCondR.colorIfTrue, rot[0], rot[1], rot[2])

    oldRotAttr = pm.listConnections( newChainSRT + '.rotate', d=False, s=True, p = True )[0]
    pm.disconnectAttr(oldRotAttr, newChainSRT + '.rotate')

    pm.connectAttr(dynCondR.outColor, newChainSRT + '.rotate')



    pm.setAttr(dynInfPMA1T.input3D[0], pos[0], pos[1], pos[2])
    pm.connectAttr(oldChainSRT + '.translate', dynInfPMA1T.input3D[1])
    pm.setAttr(dynInfPMA1T.operation, 2)

    pm.connectAttr(dynInfPMA1T.output3D, dynInfMultT.input1)
    pm.connectAttr(ctrl.dynInfluence, dynInfMultT.input2X)
    pm.connectAttr(ctrl.dynInfluence, dynInfMultT.input2Y)
    pm.connectAttr(ctrl.dynInfluence, dynInfMultT.input2Z)

    pm.connectAttr(dynInfMultT.output, dynInfPMA2T.input3D[0])
    pm.setAttr(dynInfPMA2T.input3D[1], pos[0], pos[1], pos[2])

    pm.connectAttr(dynInfPMA2T.output3D, dynCondT.colorIfFalse)
    pm.connectAttr(ctrl.dyns, dynCondT.firstTerm)
    pm.setAttr(dynCondT.colorIfTrue, pos[0], pos[1], pos[2])

    oldPosAttr = pm.listConnections( newChainSRT + '.translate', d=False, s=True, p = True )[0]
    pm.disconnectAttr(oldPosAttr, newChainSRT + '.translate')

    pm.connectAttr(dynCondT.outColor, newChainSRT + '.translate')