import maya.cmds as cmds
import pymel.core as pm

#get list of faces for the control
controlFaces = cmds.ls(sl = True)

#get the name of the original object
object = (controlFaces[0]).split('.')
originalObject = object[0]

#create new object and query the number of faces
newCTRL = cmds.duplicate(originalObject, name = originalObject + '_newCTRL')
nFaces = cmds.polyEvaluate(f=True)

cmds.select(clear = True)

#create transform geo node and connect the necessary attributes to its input geo and transform
transGeoNode = pm.createNode('transformGeometry', name = newCTRL[0] + '_transGEO')

print str(transGeoNode)

cmds.connectAttr(newCTRL[0] + '.worldInverseMatrix', str(transGeoNode) + '.transform' )
cmds.connectAttr(originalObject + '.outMesh', str(transGeoNode) + '.inputGeometry')

#get shape node of the new CTRL and then check to see if there is anything connected to it's inMesh attr
ctrlShapeNode = cmds.listRelatives(newCTRL[0], shapes = True)
ctrlShapeNode = ctrlShapeNode[0]

cmds.select(clear = True)
cmds.select(ctrlShapeNode)

conn = cmds.listConnections(c = True, d = False)
print conn
#disconnect anything that is connected to the new CTRL's in mesh attribute
if conn == None:
    print 'none'
else:
    inMeshCheck = 'no'
    for each in conn:
        
        if inMeshCheck == 'yes':
            print each
            disconnShapeNode = cmds.listRelatives(each, shapes = True)
            disconnShapeNode = disconnShapeNode[0] + '.outMesh'
            cmds.disconnectAttr(disconnShapeNode, inConn)
        if '.inMesh' in each:
            inConn = each
            inMeshCheck = 'yes'
        


cmds.connectAttr(str(transGeoNode) + '.outputGeometry', ctrlShapeNode + '.inMesh')

cmds.select(clear = True)
#select all of the new objects faces
x = 0

while x < nFaces:
    face = newCTRL[0] + '.f[' + str(x) + ']'
    cmds.select(face, add = True)

    x = x + 1




print controlFaces

#deselect all of the original faces you selected    
x = 0

while x < len(controlFaces):
    face = controlFaces[x]
    print controlFaces
    face = face.split('.')
    face = newCTRL[0] + '.' + face[1]
    print face
    cmds.select(face, deselect = True)
    
    x = x + 1
    
cmds.delete()

#select the faces of the control and slightly scale them so that it is slightly off the geometry
cmds.select(clear = True)
x = 0

while x < len(controlFaces):
    face = controlFaces[x]
    print controlFaces
    face = face.split('.')
    face = newCTRL[0] + '.' + face[1]
    print face
    cmds.select(face, add = True)
    
    x = x + 1
    
cmds.scale(1.01,1.01,1.01, r = True)
cmds.select(clear = True)    


cmds.setAttr(ctrlShapeNode + '.castsShadows', 0)
cmds.setAttr(ctrlShapeNode + '.receiveShadows', 0)
cmds.setAttr(ctrlShapeNode + '.holdOut', 0)
cmds.setAttr(ctrlShapeNode + '.motionBlur', 0)
cmds.setAttr(ctrlShapeNode + '.primaryVisibility', 0)
cmds.setAttr(ctrlShapeNode + '.visibleInReflections', 0)
cmds.setAttr(ctrlShapeNode + '.visibleInRefractions', 0)
cmds.setAttr(ctrlShapeNode + '.doubleSided', 0)
cmds.setAttr(ctrlShapeNode + '.smoothShading', 0)

    
    