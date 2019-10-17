import maya.cmds as cmds

control = cmds.circle()
cmds.xform(control, ro = [-90, 0, 0])
cmds.makeIdentity(control, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)
cmds.xform(control, ro = [0, 0, 90])
cmds.makeIdentity(control, apply = True, t = 1, r = 1, s = 1, n = 0, pn = 1)


x = 0

while x < 8:
    cvName = control[0] + ".cv[" + str(x) + "]"
    if x == 0:
        cmds.move( 0, -0.0499, 0.0639, cvName, r = True)
    if x == 1:
        cmds.move( 0, -0.397, 0.384, cvName, r = True)
    if x == 2:
        cmds.move( 0, 1.093, 0.294, cvName, r = True)
    if x == 3:
        cmds.move( 0, 1.838, 0, cvName, r = True)
    if x == 4:
        cmds.move( 0, 1.093, -0.294, cvName, r = True)
    if x == 5:
        cmds.move( 0, -0.397, -0.384, cvName, r = True)
    if x == 6:
        cmds.move( 0, -0.0499, -0.0639, cvName, r = True)
    if x == 7:
        cmds.move( 0, -0.0499, 0, cvName, r = True)
    x = x + 1 