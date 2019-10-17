import pymel.core as pm

crv = 'tail_HD_CRV'
selection = pm.ls(sl = True)

for each in selection:
    pos = pm.xform(each, t = True, ws = True, query = True)

    nPCI = pm.createNode('nearestPointOnCurve', name = str(each) + '_nPCI')
    PCI = pm.createNode('pointOnCurveInfo', name = str(each) + '_PCI')
    CM = pm.createNode('composeMatrix', name = str(each) + '_PCI')
    MM = pm.createNode('multMatrix', name = str(each) + '_MM')
    FBFMat = pm.createNode('fourByFourMatrix', name = str(each) + '_crvMatrix')
    tanReverse = pm.createNode('multiplyDivide', name = str(each) + '_tanReverse_MULT')
    rotDM = pm.createNode('decomposeMatrix', name = str(each) + '_rotDM')
    posDM = pm.createNode('decomposeMatrix', name = str(each) + '_posDM')

    pm.setAttr(nPCI.inPositionX, pos[0])
    pm.setAttr(nPCI.inPositionY, pos[1])
    pm.setAttr(nPCI.inPositionZ, pos[2])

    pm.connectAttr(crv + '.worldSpace[0]', nPCI.inputCurve)
    pm.connectAttr(crv + '.worldSpace[0]', PCI.inputCurve)

    pm.connectAttr(nPCI.parameter, PCI.parameter)
    pm.connectAttr(PCI.position, CM.inputTranslate)

    pm.connectAttr(CM.outputMatrix, MM.matrixIn[0])
    pm.connectAttr(each.parentInverseMatrix[0], MM.matrixIn[1])

    pm.connectAttr(MM.matrixSum, posDM.inputMatrix)

    pm.connectAttr(posDM.outputTranslate, each.translate)

    par = pm.getAttr(PCI.parameter)
    pm.delete(nPCI)
    pm.setAttr(PCI.parameter, par)

    pm.connectAttr(PCI.normalizedTangent, tanReverse.input1)
    pm.setAttr(tanReverse.input2Z, -1)

    pm.connectAttr(tanReverse.outputX, FBFMat.in02)
    pm.connectAttr(tanReverse.outputY, FBFMat.in01)
    pm.connectAttr(tanReverse.outputZ, FBFMat.in00)

    pm.connectAttr(FBFMat.output, rotDM.inputMatrix)

    pm.connectAttr(rotDM.outputRotate, each.rotate)





    

