import maya.cmds as cmds
import pymel.core as pm
import maya.OpenMaya as om

selection = cmds.ls(sl = True)

multMatrix = pm.createNode('multMatrix', name = selection[0] + selection[1] + '_constMM')
decMatrix = pm.createNode('decomposeMatrix', name = selection[0] + selection[1]+ '_DM')


#Find the vector between the two objects for the maintain offset option

posA = cmds.xform(selection[0], q = True, ws = True, t = True)
posB = cmds.xform(selection[1], q = True, ws = True, t = True)

a = om.MVector(posA[0], posA[1], posA[2])
b = om.MVector(posB[0], posB[1], posB[2])

c = a - b

#create translate offset and then subtract the vector between the two objects from the world position of your first object
tOffset = pm.createNode('plusMinusAverage', name = selection[0] + selection[1] + 'transOffPMA')

pm.connectAttr(decMatrix.outputTranslate, tOffset.input3D[0])
pm.setAttr(tOffset + '.operation', 2)
pm.setAttr(tOffset + '.input3D[1].input3Dx', c.x )
pm.setAttr(tOffset + '.input3D[1].input3Dy', c.y )
pm.setAttr(tOffset + '.input3D[1].input3Dz', c.z )