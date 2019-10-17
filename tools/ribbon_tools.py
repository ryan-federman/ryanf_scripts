import numpy as np
import copy

from Qt import QtCompat, QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance

from maya import OpenMayaUI as omui
import maya.cmds as cmds
import maya.api.OpenMaya as om

from rigging_utils import constraint
from rigging_utils import shape
from rigging_utils.create import curves


class RibbonTools(QtWidgets.QWidget):
    def __init__(self):
        self.namespace = None

        # if the ui exists then delete it
        old_window = omui.MQtUtil_findWindow('ribbonTools')
        if old_window:
            cmds.deleteUI('ribbonTools')

        # create a new dialog and give it the main maya window as its parent
        # store it as the parent for our current UI to be put inside
        parent = QtWidgets.QDialog(parent=getMayaMainWindow())

        # set its name so that we can find and delete it later
        parent.setObjectName('ribbonTools')
        parent.setWindowTitle('Ribbon Tools')

        super(RibbonTools, self).__init__(parent=parent)

        dlgLayout = QtWidgets.QVBoxLayout(parent)

        self.buildUI()

        self.parent().layout().addWidget(self)

        parent.show()

    def buildUI(self):

        # create main layouts
        main_layout = QtWidgets.QVBoxLayout(self)
        top_layout = QtWidgets.QHBoxLayout()
        mid_layout = QtWidgets.QGridLayout()
        bot_layout = QtWidgets.QHBoxLayout()

        # Line space
        space_1 = QtWidgets.QFrame()
        space_1.setFrameShape(QtWidgets.QFrame.HLine)
        space_2 = QtWidgets.QFrame()
        space_2.setFrameShape(QtWidgets.QFrame.HLine)

        main_layout.addLayout(top_layout)
        main_layout.addWidget(space_1)
        main_layout.addLayout(mid_layout)
        main_layout.addWidget(space_2)
        main_layout.addLayout(bot_layout)

        # Combo box for choosing which ribbon you are affection
        rc_text = QtWidgets.QLabel()
        rc_text.setText('Current Ribbon:')
        self.ribbon_choice = QtWidgets.QComboBox()
        self.gather_rigs()
        choice_update = QtWidgets.QPushButton('Update')
        choice_update.clicked.connect(self.gather_rigs)

        # text box for name of curve
        self.curve_text = QtWidgets.QLabel()
        self.curve_text.setText('Curve:')
        self.curve_line_text = QtWidgets.QLineEdit()
        curve_button = QtWidgets.QPushButton('Get Curve')
        curve_button.clicked.connect(self.get_curve)

        # slider for number of upvector controls
        up_vec_text = QtWidgets.QLabel()
        up_vec_text.setText('Up Vectors:')
        self.up_num_box = QtWidgets.QSpinBox()
        up_num_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        up_num_slider.valueChanged.connect(self.up_num_box.setValue)
        self.up_num_box.valueChanged.connect(up_num_slider.setValue)
        up_num_slider.setMaximum(50)
        self.up_num_box.setMaximum(50)
        self.up_num_box.setValue(9)

        # slider for number of controls moved to the curve
        crv_ctrl_text = QtWidgets.QLabel()
        crv_ctrl_text.setText('Controls To Curve:')
        self.crv_ctrl_box = QtWidgets.QSpinBox()
        crv_ctrl_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        crv_ctrl_slider.valueChanged.connect(self.crv_ctrl_box.setValue)
        self.crv_ctrl_box.valueChanged.connect(crv_ctrl_slider.setValue)
        crv_ctrl_slider.setMaximum(50)
        self.crv_ctrl_box.setMaximum(50)
        self.crv_ctrl_box.setValue(50)

        # checkbox for resetting control transforms
        reset_transforms_text = QtWidgets.QLabel()
        reset_transforms_text.setText('Reset Transforms:')
        self.reset_transforms_cb = QtWidgets.QCheckBox()

        # buttons for setting ribbon to curve and resetting it
        rb2crv_button = QtWidgets.QPushButton('Rig to Curve')
        reset_button = QtWidgets.QPushButton('Reset Rig')
        rb2crv_button.clicked.connect(self.rig_to_curve)
        reset_button.clicked.connect(self.reset_controls)

        top_layout.addWidget(rc_text)
        top_layout.addWidget(self.ribbon_choice)
        top_layout.addSpacing(100)
        top_layout.addWidget(choice_update)

        mid_layout.addWidget(self.curve_text, 0, 0, 1, 1)
        mid_layout.addWidget(self.curve_line_text, 0, 1, 1, 3)
        mid_layout.addWidget(curve_button, 0, 4, 1, 1)

        mid_layout.addWidget(up_vec_text, 1, 0, 1, 1)
        mid_layout.addWidget(up_num_slider, 1, 1, 1, 3)
        mid_layout.addWidget(self.up_num_box, 1, 4, 1, 1)

        mid_layout.addWidget(crv_ctrl_text, 2, 0, 1, 1)
        mid_layout.addWidget(crv_ctrl_slider, 2, 1, 1, 3)
        mid_layout.addWidget(self.crv_ctrl_box, 2, 4, 1, 1)

        mid_layout.addWidget(reset_transforms_text, 3, 0, 1, 1)
        mid_layout.addWidget(self.reset_transforms_cb, 3, 1, 1, 1)

        bot_layout.addWidget(rb2crv_button)
        bot_layout.addWidget(reset_button)

    def gather_rigs(self):
        '''
        Load available ribbon rigs into the combo box
        '''
        self.ribbon_choice.clear()
        ribbon_rigs = []
        no_reference = cmds.ls('C_ribbon_root_CTRL')
        referenced = cmds.ls('*:C_ribbon_root_CTRL')

        if no_reference:
            ribbon_rigs.append('local')
        if referenced:
            for rig in referenced:
                namespace = rig.split(':')[0]
                ribbon_rigs.append(namespace + ':')

        self.ribbon_choice.addItems(ribbon_rigs)

    def get_curve(self):
        '''
        Loads selected curve into curve text box
        '''
        try:
            selection = cmds.ls(sl=True)[0]
        except IndexError:
            raise RuntimeError('Select a valid nurbs curve')
        shape = cmds.listRelatives(selection, s=True)[0]
        shape_type = cmds.nodeType(shape)
        if shape_type == 'nurbsCurve':
            self.curve_line_text.setText(shape)
        else:
            raise RuntimeError('Select a valid nurbs curve')

    def rig_to_curve(self):
        '''
        Moves ribbon rig to the selected curve
        '''
        # check for namespace of rig, change to blank string if rig is localized
        self.namespace = self.ribbon_choice.currentText()
        if not self.namespace:
            raise ValueError('No ribbon rigs in scene')
        elif self.namespace == 'local':
            self.namespace = ''

        # check to see if a curve is selected
        curve = self.curve_line_text.text()
        if not curve:
            raise ValueError('Select a curve')
        num_controls = self.up_num_box.value()

        # reset rig
        self.reset_controls()

        self.move_to_curve(curve, num_controls)

    def linspace_bones(self, curve, bones):
        ''' Provide matrices that are an equal distribution along a curve

        Args:
            curve (str): name of curve to get information from
            bones (list[str]): number of controls to be created for up vec of curve
        '''
        sel = om.MSelectionList()
        sel.add(curve)

        crv = om.MFnNurbsCurve()
        crv.setObject(sel.getDagPath(0))

        curve_length = crv.length()
        lengths = np.linspace(0, curve_length, len(bones))

        # create instance to control pos and rot of controls being attached
        for i, length in enumerate(lengths):
            bone = bones[i]
            poci = cmds.createNode('pointOnCurveInfo', name=bone + '_POCI')

            param = crv.findParamFromLength(length)
            if param == 0:
                param = .001
            if length == lengths[-1]:
                param -= .001

            cmds.connectAttr(curve + '.worldSpace[0]', poci + '.inputCurve')
            cmds.setAttr(poci + '.parameter', param)
            cmds.connectAttr(poci + '.position', bone + '.translate')

    def linspace_curve(self, curve, num, num_ctrls):
        ''' Provide matrices that are an equal distribution along a curve

        Args:
            curve (str): name of curve to get information from
            num (int): number of matrices to be returned
            num_ctrls (int): number of controls to be created for up vec of curve
        Return:
             list[om.MMatrix()]: list of matrices
        '''
        top_grp = cmds.createNode('transform', name='{}_ribbon_GRP'.format(curve))
        add_enum(top_grp, 'ribbonGRP', 'exists')

        sel = om.MSelectionList()
        sel.add(curve)

        crv = om.MFnNurbsCurve()
        crv.setObject(sel.getDagPath(0))

        curve_length = crv.length()
        lengths = np.linspace(0, curve_length, num)
        ctrl_lengths = np.linspace(0, curve_length, num_ctrls)

        mscs = []
        up_vecs = []
        ctrl_params = []

        # create controls to control up vector of curve
        for i, length in enumerate(ctrl_lengths):
            ctrl_height = curve_length/10.0
            param = crv.findParamFromLength(length)
            ctrl = create_dag('{}C_crv_{}'.format(self.namespace, str(i)), type='control', ctrl_type='triangle')
            lock_attributes(ctrl, ['rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'])
            ctrl_ofs = ctrl + '_OFS'
            ctrl_zero = ctrl + '_ZERO'
            line_loc = cmds.spaceLocator(name='{}C_crv_{}_LOC'.format(self.namespace, str(i)))[0]
            poci = cmds.createNode('pointOnCurveInfo', name=self.namespace + ctrl + '_POCI')
            dm = cmds.createNode('decomposeMatrix', name=self.namespace + ctrl + '_DM')
            sub_vec = cmds.createNode('math_SubtractVector', name=self.namespace + ctrl + '_SV')
            normalize = cmds.createNode('math_NormalizeVector', name=self.namespace + ctrl + '_NV')
            ctrl_params.append(param)

            cmds.connectAttr(curve + '.worldSpace[0]', poci + '.inputCurve')
            cmds.setAttr(poci + '.parameter', param)

            cmds.connectAttr(poci + '.position', ctrl_zero + '.translate')
            cmds.connectAttr(poci + '.position', line_loc + '.translate')

            cmds.setAttr(ctrl_ofs + '.ty', ctrl_height)
            cmds.connectAttr(ctrl + '.worldMatrix[0]', dm + '.inputMatrix')

            cmds.connectAttr(dm + '.outputTranslate', sub_vec + '.input1')
            cmds.connectAttr(line_loc + '.translate', sub_vec + '.input2')

            cmds.connectAttr(sub_vec + '.output', normalize + '.input')

            line_curve = curves.curve_from_objects([ctrl, line_loc], name=self.namespace + ctrl + '_vec_CRV')
            cmds.setAttr(line_curve + '.overrideEnabled', 1)
            cmds.setAttr(line_curve + '.overrideDisplayType', 2)

            up_vecs.append(normalize)

            cmds.parent(ctrl_zero, top_grp)
            cmds.parent(line_loc, top_grp)
            cmds.parent(line_curve, top_grp)

        # create instance to control pos and rot of controls being attached
        for length in lengths:
            poci = cmds.createNode('pointOnCurveInfo')
            fbf = cmds.createNode('fourByFourMatrix')
            msc = cmds.createNode('millSimpleConstraint')
            pblnd = cmds.createNode('pairBlend')
            z_vec = cmds.createNode('vectorProduct')
            mscs.append(msc)

            param = crv.findParamFromLength(length)

            # find the two up vecs the current param is between
            param_differences = []
            par_list = copy.deepcopy(ctrl_params)
            vec_list = copy.deepcopy(up_vecs)
            closest_vecs = {}
            for par in par_list:
                par_dif = abs(param - par)
                param_differences.append(par_dif)

            # iterate through the parameter list twice to get the two closest pars
            def closest_vec():
                closest_par = None
                close_index = None
                for i, par in enumerate(param_differences):
                    if i == 0:
                        closest_par = par
                        close_index = i
                    elif par < closest_par:
                        closest_par = par
                        close_index = i

                closest_vecs[par_list[close_index]] = vec_list[close_index]
                param_differences.remove(closest_par)
                par_list.remove(par_list[close_index])
                vec_list.remove(vec_list[close_index])

            closest_vec()
            closest_vec()

            close_pars = []
            close_vecs = []
            for key, value in closest_vecs.items():
                close_pars.append(key)
                close_vecs.append(value)

            blend_value = remap_values(close_pars[0], close_pars[1], 0, 1, param)

            # connect vecs to pair blend
            cmds.connectAttr(close_vecs[0] + '.output', pblnd + '.inTranslate1')
            cmds.connectAttr(close_vecs[1] + '.output', pblnd + '.inTranslate2')
            cmds.setAttr(pblnd + '.weight', blend_value)

            cmds.setAttr(z_vec + '.operation', 2)
            cmds.connectAttr(pblnd + '.outTranslate', z_vec + '.input1')
            cmds.connectAttr(poci + '.normalizedTangent', z_vec + '.input2')

            cmds.connectAttr(curve + '.worldSpace[0]', poci + '.inputCurve')
            cmds.setAttr(poci + '.parameter', param)
            cmds.connectAttr(poci + '.normalizedTangentX', fbf + '.in00')
            cmds.connectAttr(poci + '.normalizedTangentY', fbf + '.in01')
            cmds.connectAttr(poci + '.normalizedTangentZ', fbf + '.in02')
            cmds.connectAttr(pblnd + '.outTranslateX', fbf + '.in10')
            cmds.connectAttr(pblnd + '.outTranslateY', fbf + '.in11')
            cmds.connectAttr(pblnd + '.outTranslateZ', fbf + '.in12')
            cmds.connectAttr(z_vec + '.outputX', fbf + '.in20')
            cmds.connectAttr(z_vec + '.outputY', fbf + '.in21')
            cmds.connectAttr(z_vec + '.outputZ', fbf + '.in22')
            cmds.connectAttr(poci + '.positionX', fbf + '.in30')
            cmds.connectAttr(poci + '.positionY', fbf + '.in31')
            cmds.connectAttr(poci + '.positionZ', fbf + '.in32')
            cmds.connectAttr(fbf + '.output', msc + '.inMatrix')

        return mscs

    def gather_controls(self):
        '''
        Gather all dags that are needed to create and reset the rig
        '''
        namespace_ctrls = cmds.ls(self.namespace + '*CTRL')
        regular_ctrls = cmds.ls('*CTRL')
        grps = cmds.ls('*GRP')
        grps = cmds.ls(self.namespace + '*GRP') + grps
        bones = cmds.ls('C_ribbon_*_CRV_BONE')
        bones = cmds.ls(self.namespace + 'C_ribbon_*_CRV_BONE') + bones
        all_controls = namespace_ctrls + regular_ctrls
        num_ctrls = None
        ribbon_ctrls = []
        ribbon_grps = []
        ctrl_order = {}
        for ctrl in all_controls:
            if 'bank' or 'sub' not in ctrl:
                if cmds.ls(ctrl + '.ribbonCtrl'):
                    i = cmds.getAttr(ctrl + '.ribbonCtrl')
                    ctrl_order[i] = ctrl
                elif cmds.ls(ctrl + '.ribbonRoot'):
                    num_ctrls = self.crv_ctrl_box.value()
        for i in range(len(ctrl_order)):
            if 'bank' or 'sub' not in ctrl_order[i]:
                ribbon_ctrls.append(ctrl_order[i])
        for grp in grps:
            if cmds.ls(grp + '.ribbonGRP'):
                ribbon_grps.append(grp)
        return ribbon_ctrls, num_ctrls, ribbon_grps, bones

    def reset_controls(self):
        '''
        Reset rig, un-attaches the rig from the curve
        '''
        self.namespace = self.ribbon_choice.currentText()
        ctrls, num_dags, grps, bones = self.gather_controls()

        # reset curve bones
        for bone in bones:
            poci = cmds.listConnections(bone + '.translate', source=True)
            cmds.delete(poci)
        lengths = np.linspace(0, 68.853, len(bones))
        for i, each in enumerate(lengths):
            cmds.xform(bones[i], t=(0, 0, each))

        # reset controls
        for i, dag in enumerate(ctrls):
            ofs = dag + '_OFS'
            if cmds.ls(ofs + '.curveMSC'):
                msc = cmds.getAttr(ofs + '.curveMSC', asString=True)
                cmds.deleteAttr(ofs + '.curveMSC')
                cmds.delete(msc)
            cmds.setAttr(ofs + '.t', 0, 0, 0)
            cmds.setAttr(ofs + '.r', 0, 0, 0)
            cmds.setAttr(dag + '.r', 0, 0, 0)
        # if the reset transforms is checked reset all controls transforms
        if self.reset_transforms_cb.isChecked():
            all_ctrls = cmds.ls(self.namespace + '*CTRL')
            for ctrl in all_ctrls:
                for attr in ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz']:
                    try:
                        cmds.setAttr(ctrl + attr, 0)
                    except RuntimeError:
                        pass
        for dag in grps:
            cmds.delete(dag)

    def move_to_curve(self, curve, num_ctrls):
        '''

        Args:
            curve (str): name of curve to attach rig to
            num_ctrls (int): number of up vector controls created
        :return:
        '''
        ctrls, num_dags, grps, bones = self.gather_controls()
        rig_crv = self.namespace + 'C_ribbon_CRV'
        dags = []
        for i in range(num_dags):
            dags.append(ctrls[i])
        self.linspace_bones(curve, bones)

        mscs = self.linspace_curve(rig_crv, num_dags, num_ctrls)

        if cmds.ls(ctrls[0] + '_OFS.curveMSC'):
            self.reset_controls()

        for i, dag in enumerate(dags):
            ofs = dag + '_OFS'
            cmds.connectAttr(ofs + '.parentInverseMatrix[0]', mscs[i] + '.parentInverseMatrix')
            cmds.connectAttr(mscs[i] + '.outTranslate', ofs + '.translate')
            cmds.connectAttr(mscs[i] + '.outRotate', ofs + '.rotate')

            add_enum(ofs, 'curveMSC', mscs[i])


def getMayaMainWindow():
    """
    Since Maya is Qt, we can parent our UIs to it.
    This means that we don't have to manage our UI and can leave it to Maya.
    Returns:
        QtWidgets.QMainWindow: The Maya MainWindow
    """
    # Get a reference to Maya's MainWindow
    win = omui.MQtUtil_mainWindow()

    # Wrap the window reference into Qt
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)

    return ptr


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


def remap_values(OldMin, OldMax, NewMin, NewMax, input):
    OldRange = (OldMax - OldMin)
    NewRange = (NewMax - NewMin)
    NewValue = (((input - OldMin) * NewRange) / OldRange) + NewMin

    return NewValue


def create_dag(name, source=None, connect='srt', snap=True, position=None, type='bone', ctrl_type='circle', size=1.0):
    '''Creates a dag object of the given type

    Args:
         name (str): base name of node
         source (str): source dag object for constraining the object to
         connect (str): connect scale, translation, rotation of new dag to source
         snap (bool): whether the object will be moved to the source object
         position (om.MMatrix): matrix for object to be positioned at
         type (str): type of dag object created
         size (float): how large the dag will be
    Returns:
        (str): dag object created
    '''
    cmds.select(clear=True)

    # create dag based on the type flag
    dag = None
    if type == 'bone':
        dag = cmds.joint(name=name + '_BONE')
        cmds.setAttr(dag + '.radius', size)
    if type == 'control':
        dag = shape.create_nurbscurve(ctrl_type, name=name + '_CTRL', size=size)
        dag = cmds.listRelatives(dag, p=True)[0]
    if type == 'locator':
        dag = cmds.spaceLocator(name=name + '_CTRL')[0]
    ofs = cmds.createNode('transform', name=dag + '_OFS')
    zero = cmds.createNode('transform', name=dag + '_ZERO')
    cmds.parent(dag, ofs)
    cmds.parent(ofs, zero)

    # position and constrain the dag accordingly
    if position:
        cmds.xform(zero, matrix=position, ws=True)
    if source:
        if snap:
            snap_to_dag(source, zero)
        if connect:
            constraint.simple_constraint(source, zero, connect=connect)

    return dag


def snap_to_dag(source, target):
    '''Moves one dag object to the position and rotation of another

    Args:
         source (str): object to reference for transforms
         target (str): object to move to source object
    '''

    pos = cmds.xform(source, t=True, ws=True, q=True)
    rot = cmds.xform(source, ro=True, ws=True, q=True)

    cmds.xform(target, t=pos, ws=True)
    cmds.xform(target, ro=rot, ws=True)


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
