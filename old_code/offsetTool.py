import maya.cmds as cmds

selection = cmds.ls( sl = True )

groupName = cmds.group( em = True, n = selection[0] + '_grp' )

pointConstName = cmds.pointConstraint( selection[0], groupName, mo = False )
cmds.delete( pointConstName[0] )

rotationCoordinates = cmds.xform( selection[0], query = True, ro = True )
translateCoordinates = cmds.xform( selection[0], query = True, t = True )

cmds.parent( selection[0], groupName )

cmds.setAttr( groupName + ".rotate", rotationCoordinates[0], rotationCoordinates[1], rotationCoordinates[2] )

cmds.setAttr( selection[0] + ".rotate", 0,0,0 )