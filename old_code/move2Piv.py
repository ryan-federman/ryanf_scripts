#Move2Pivot Tool
import maya.cmds as cmds

selection = cmds.ls(sl = True)

moveObj = selection[0]
statObj = selection[1]

centerPivot = cmds.xform( selection[1], query = True, rp = True )

cmds.move(centerPivot[0], centerPivot[1], centerPivot[2], moveObj) 