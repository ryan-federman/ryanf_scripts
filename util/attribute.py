import maya.cmds as cmds

from rigging_utils import attribute


def break_attr_conn(attr):
    """Breaks connections to the given attribute

    Args:
        attr(str): Attribute to delete connections to
    """

    source = cmds.listConnections(attr, d=False, s=True, plugs=True)[0]
    cmds.disconnectAttr(source, attr)


def force_visibility_attr(node, name, items):
    attr = attribute.add_visibility_attr(node, name)
    for each in items:
        conn = cmds.listConnections(each + '.v', source=True, destination=False, plugs=True)
        if conn:
            cmds.disconnectAttr(conn[0], each + '.v')
        cmds.connectAttr(attr, each + '.v')


def connect_visibility(attribute, dags, force=False):
    '''Connects a given attribute to dag nodes

    Args:
        attribute (str): attribute to control visibility
        dags list[(str)]: dags whose visibility is being controlled
    '''

    for each in dags:
        connected = cmds.listConnections(each + '.v', d=False, s=True, plugs=True)
        if connected:
            if force:
                break_attr_conn(each + '.v')
        cmds.connectAttr(attribute, each + '.v')


def multiple_visibility(attr, name, *args):
    '''Attaches an attributes indices to the visibility of objects

    Args:
         attr (str): name of attribute to drive visibility
         name (str): base name of condition node
         *args [(str)]: objects whose visibility is being driven
    '''

    objects = ['none']
    for each in args:
        objects.append(each)

    for i, dags in enumerate(objects):
        if i > 0:
            condition = cmds.createNode('condition', name='{}_{}_VIS_COND'.format(name, str(i)))

            cmds.connectAttr(attr, condition + '.firstTerm')
            cmds.setAttr(condition + '.secondTerm', i)
            cmds.setAttr(condition + '.colorIfTrueR', 1)
            cmds.setAttr(condition + '.colorIfFalseR', 0)

            for dag in dags:
                cmds.connectAttr(condition + '.outColorR', dag + '.visibility')


def add_proxy(node, proxy_attr, name):
    ''' Creates proxy attribute to another attribute

    Args:
        node (str): node in which to put the new attribute on
        proxy_attr (str): attribute to be proxied
        name (str): name of new attribute
    Returns:
        str: proxy attribute
    '''
    attr = cmds.addAttr(node, proxy=proxy_attr, shortName=name)
    return attr


def lock_attributes(dag, attrs, channelbox=False):
    """Wrapper for locking attributes

    Args:
        dag (str): dag to lock attributes on
        attrs list[(str)]: attributes to lock
        channelbox (bool): whether to hide the attributes being locked from the channelbox
    """

    for attr in attrs:
        attribute = '{}.{}'.format(dag, attr)
        cmds.setAttr(attribute, keyable=channelbox, lock=True)


def add_enum(node, name, *args):
    '''Wrapper for making an enum attribute

    Args:
        node (str): node to add attribute to
        name (str): name of attribute
        *args: arguments that will be the enum names of the attribute
    Return:
         (str): attribute name
    '''

    enum_names = ''
    for i, arg in enumerate(args):
        if arg != args[-1]:
            enum_names += arg + ':'
        else:
            enum_names += arg

    cmds.addAttr(node,
                 shortName=name,
                 attributeType='enum',
                 enumName=enum_names,
                 keyable=True)

    return '{}.{}'.format(node, name)


def copy_attributes(source, target):

    attrs = cmds.listAttr(v=True, u=True, k=True)
    for attr in attrs:
        value = cmds.getAttr('{}.{}'.format(source, attr))
        cmds.setAttr('{}.{}'.format(target, attr), value)
