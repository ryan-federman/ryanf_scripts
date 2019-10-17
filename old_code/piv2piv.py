import maya.cmds as cmds

selection = cmds.ls(sl = True)

moveObj = selection[0]
statObj = selection[1]

statObjPos = cmds.xform( selection[1], query = True, ws = True, t = True)
statObjPiv = cmds.xform( selection[1], query = True, rp = True )

#get exact position of pivot
loc = cmds.spaceLocator()
pc = cmds.pointConstraint(statObj, loc, mo = False)
pivLocation = cmds.xform( loc, ws = True, query = True, rp = True )

cmds.xform(moveObj, piv = [0,0,0])
moveObjLocation = cmds.xform( moveObj, ws = True, query = True, rp = True )

#find how much you have to move each coordinate
tx = pivLocation[0] - moveObjLocation[0]
ty = pivLocation[1] - moveObjLocation[1]
tz = pivLocation[2] - moveObjLocation[2]

#move the pivot to the location
cmds.xform( moveObj, piv = [ pivLocation[0], pivLocation[1], pivLocation[2] ], ws = True )

#delete the locator
cmds.delete(loc)