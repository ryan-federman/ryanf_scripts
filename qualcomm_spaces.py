# run this code before
import maya.cmds as cmds
from rigging_utils.name import Name
from rigging_utils import shape


def create_dag(name, target, type='bone', control_type='circle'):
    """Creates a dag node at the given position and rotation of the given dag

    Args:
        name (str): name of bone
        target (str): dag node which the new dag will fit it's position and rotation to
    Returns:
        str: new dag node
    """
    namer = Name(name)
    if type == 'bone':
        dag = cmds.joint(name=namer.replace(suffix='joint'))
    if type == 'transform':
        dag = cmds.createNode('transform', name=namer.replace(suffix='transform'))
    if type == 'control':
        dag = shape.create_nurbscurve(name=namer.replace(suffix='CTRL'), shape_name=control_type)
        dag = cmds.listRelatives(dag, p=True)[0]

    zero = cmds.createNode('transform', name=namer.replace(suffix='ZERO'))
    ofs = cmds.createNode('transform', name=namer.replace(suffix='OFS'))

    cmds.parent(dag, ofs)
    cmds.parent(ofs, zero)

    pos = cmds.xform(target, t=True, ws=True, p=True)
    rot = cmds.xform(target, ro=True, ws=True, p=True)

    cmds.xform(zero, t=pos, ws=True)
    cmds.xform(zero, ro=rot, ws=True)

    return dag


def create_space(source1, source2, target):
    """Creates a space between two spaces and a target

    Args:
        source1 (str): First space source
        source2 (str): Second space source
        target (str): Target object for spaces

    """
    namer = Name(target)

    mm1 = cmds.createNode('multMatrix', name=namer.replace(suffix='multMatrix',
                                                           add_to_tags='firstSpace'))
    mm2 = cmds.createNode('multMatrix', name=namer.replace(suffix='multMatrix',
                                                           add_to_tags='secondSpace'))
    dm1 = cmds.createNode('decomposeMatrix', name=namer.replace(suffix='decomposeMatrix',
                                                                add_to_tags='firstSpace'))
    dm2 = cmds.createNode('decomposeMatrix', name=namer.replace(suffix='decomposeMatrix',
                                                                add_to_tags='secondSpace'))

    ofs = target + '_OFS'
    pb1 = cmds.createNode('pairBlend', name=namer.replace(suffix='pairBlend',
                                                          add_to_tags='firstSpace'))
    pb2 = cmds.createNode('pairBlend', name=namer.replace(suffix='pairBlend',
                                                          add_to_tags='secondSpace'))

    cmds.connectAttr(source1 + '.worldMatrix[0]', mm1 + '.matrixIn[0]')
    cmds.connectAttr(ofs + '.parentInverseMatrix[0]', mm1 + '.matrixIn[1]')
    cmds.connectAttr(mm1 + '.matrixSum', dm1 + '.inputMatrix')

    cmds.connectAttr(source2 + '.worldMatrix[0]', mm2 + '.matrixIn[0]')
    cmds.connectAttr(ofs + '.parentInverseMatrix[0]', mm2 + '.matrixIn[1]')
    cmds.connectAttr(mm2 + '.matrixSum', dm2 + '.inputMatrix')

    cmds.connectAttr(dm1 + '.outputTranslate', pb1 + '.inTranslate1')
    cmds.connectAttr(dm1 + '.outputRotate', pb1 + '.inRotate1')

    cmds.connectAttr(dm2 + '.outputTranslate', pb1 + '.inTranslate2')
    cmds.connectAttr(dm2 + '.outputRotate', pb1 + '.inRotate2')

    cmds.connectAttr(pb1 + '.outTranslate', pb2 + '.inTranslate2')
    cmds.connectAttr(pb1 + '.outRotate', pb2 + '.inRotate2')

    cmds.connectAttr(target + '.space', pb1 + '.weight')
    cmds.connectAttr(target + '.spaceOff', pb2 + '.weight')

    cmds.connectAttr(pb2 + '.outTranslate', ofs + '.translate')
    cmds.connectAttr(pb2 + '.outRotate', ofs + '.rotate')


def create_space_bone(name, source1, source2, target):
    """Wrapper for creating a bone that is controlled by two spaces
    """

    bone = create_dag(name, target)
    create_space(source1, source2, bone)

def store_position():
    dag = cmds.ls(sl=True)[0]
    pos = cmds.xform(dag, t=True, ws=True, q=True)
    rot = cmds.xform(dag, ro=True, ws=True, q=True)

    return (pos, rot)


def move_position(pos, rot):
    dag = cmds.ls(sl=True)[0]
    cmds.xform(dag, t=pos, ws=True)
    cmds.xform(dag, ro=rot, ws=True)
