import pymel.core as pm

import pymel.core as pm
import maya.cmds as cmds

obj = cmds.ls(sl=True)[0]
baked = cmds.listRelatives(obj, ad=True, shapes=False, typ='transform')
connections = []
for each in baked:
    type = cmds.nodeType(each)
    if type == 'transform' or type == 'joint':
        cmds.select(each)
        conns = cmds.listConnections(each, source=True)
        if conns != None:
            for conn in conns:
                connections.append(conn)
    else:
        baked.remove(each)
cmds.select(clear=True)
for each in baked:
    cmds.select(each, add=True)

for each in connections:
    cmds.delete(each)