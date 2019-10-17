import pymel.core as pm

topJnt = pm.ls(sl = True)[0]
botJnt = pm.ls(sl = True)[0]
selection = pm.ls(sl = True)

x = 1.0
for each in selection:
    blendAmt = x/10
    print blendAmt

    multMatrix1 = pm.createNode('multMatrix', name = 'spineTwist' + str(int(x)) + '_MM1')
    decMatrix1 = pm.createNode('decomposeMatrix', name = 'spineTwist' + str(int(x)) + '_decMatrix1')
    quatToEuler1 = pm.createNode('quatToEuler', name = 'spineTwist' + str(int(x)) + '_QTE1')


    multMatrix2 = pm.createNode('multMatrix', name = 'spineTwist' + str(int(x)) + '_MM2')
    decMatrix2 = pm.createNode('decomposeMatrix', name = 'spineTwist' + str(int(x)) + '_decMatrix2')
    quatToEuler2 = pm.createNode('quatToEuler', name = 'spineTwist' + str(int(x)) + '_QTE2')

    blendColors = pm.createNode('blendColors', name = 'spineTwist' + str(int(x)) + 'blend')

    pm.connectAttr(topJnt.worldMatrix, multMatrix1.matrixIn[0])
    pm.connectAttr(botJnt.worldMatrix, multMatrix2.matrixIn[0])

    pm.connectAttr(each.parentInverseMatrix, multMatrix1.matrixIn[1])
    pm.connectAttr(each.parentInverseMatrix, multMatrix2.matrixIn[1])

    pm.connectAttr(multMatrix1.matrixSum, decMatrix1.inputMatrix)
    pm.connectAttr(multMatrix2.matrixSum, decMatrix2.inputMatrix)

    pm.connectAttr(decMatrix1.outputQuatY, quatToEuler1.inputQuatY)
    pm.connectAttr(decMatrix1.outputQuatW, quatToEuler1.inputQuatW)

    pm.connectAttr(decMatrix2.outputQuatY, quatToEuler2.inputQuatY)
    pm.connectAttr(decMatrix2.outputQuatW, quatToEuler2.inputQuatW)

    pm.connectAttr(quatToEuler1.outputRotateY, blendColors.color1.color1R)
    pm.connectAttr(quatToEuler2.outputRotateY, blendColors.color2.color2R)

    pm.connectAttr(blendColors.outputR, each.rotateY)

    pm.setAttr(blendColors.blender, blendAmt)

    x = x + 1.0

