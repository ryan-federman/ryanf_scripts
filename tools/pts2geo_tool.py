import numpy as np
import copy

from Qt import QtCompat, QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance

from maya import OpenMayaUI as omui
import maya.cmds as cmds
import maya.api.OpenMaya as om


class IsoGeoWidget(QtWidgets.QWidget):
    # initialize class variables
    source_geo = None
    geo = None
    faces = None
    old_verts = []
    new_verts = []
    vtx_mapping = {}
    vector_mapping = {}
    position_mapping = {}

    def __init__(self, faces=None, geo=None, source_geo=None, vtx_mapping=None):
        # initialize class variables
        self.source_geo = None
        self.geo = None
        self.faces = None
        self.old_verts = []
        self.new_verts = []
        self.vtx_mapping = {}
        self.vector_mapping = {}
        self.position_mapping = {}

        if geo:
            self.source_geo = source_geo
            self.geo = geo
            self.vtx_mapping = vtx_mapping

            for new_vtx, old_vtx in self.vtx_mapping.items():
                self.old_verts.append(old_vtx)
                self.new_verts.append(new_vtx)

        else:
            self.source_geo = faces[0].split('.f')[0]
            self.faces = faces
            self.create_geo()

            self.old_verts = cmds.polyListComponentConversion(self.faces, tv=True)
            self.old_verts = cmds.ls(self.old_verts, fl=True)

            self.map_vertices()
            add_enum(self.geo, 'sourceGeo', [self.source_geo], visible=False)
        super(IsoGeoWidget, self).__init__()

        self.buildUI()

    def buildUI(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        self.layout_grp = QtWidgets.QGroupBox()
        self.layout_grp.setFixedHeight(220)
        self.layout_grp.setFixedWidth(250)
        self.layout_grp.setTitle(self.geo)
        top_grp = QtWidgets.QGroupBox()
        full_layout = QtWidgets.QVBoxLayout(self.layout_grp)
        top_layout = QtWidgets.QGridLayout(top_grp)
        bot_layout = QtWidgets.QHBoxLayout()

        main_layout.addWidget(self.layout_grp)
        main_layout.addLayout(full_layout)
        full_layout.addWidget(top_grp)
        full_layout.addLayout(bot_layout)

        # rename function
        self.rename_line = QtWidgets.QLineEdit()
        rename_button = QtWidgets.QPushButton('Set Name')
        rename_button.clicked.connect(self.rename_geo)

        # moving vertices to sources geo
        pin_label = QtWidgets.QLabel('Pin Options:')
        self.pin_select_button = QtWidgets.QRadioButton()
        self.pin_select_button.setText('Selection')
        self.pin_select_button.toggle()
        stored_button = QtWidgets.QRadioButton()
        stored_button.setText('Stored')
        pin_verts_grp = QtWidgets.QGroupBox()
        pin_verts_layout = QtWidgets.QHBoxLayout(pin_verts_grp)
        self.pin_verts_line = QtWidgets.QLineEdit()
        pin_verts_button = QtWidgets.QPushButton('Get verts')
        pin_verts_grp.setEnabled(False)
        self.pin_select_button.toggled.connect(lambda: self.enable_widget(pin_verts_grp))
        pin_verts_button.clicked.connect(self.store_vertices)

        # slider for moving verts back to source geo
        pin_text = QtWidgets.QLabel()
        pin_text.setText('To old mesh:')
        self.pin_percent_box = QtWidgets.QSpinBox()
        self.pin_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.pin_slider.valueChanged.connect(self.pin_percent_box.setValue)
        self.pin_percent_box.valueChanged.connect(self.pin_slider.setValue)
        self.pin_slider.valueChanged.connect(self.move_vertices)
        self.pin_slider.setMaximum(100)
        self.pin_percent_box.setMaximum(100)
        self.pin_percent_box.setValue(0)
        self.pin_slider.sliderPressed.connect(self.map_vectors)
        self.pin_slider.sliderPressed.connect(lambda: cmds.undoInfo(openChunk=True))
        self.pin_slider.sliderReleased.connect(self.release_pin_slider)
        self.pin_slider.sliderReleased.connect(lambda: cmds.undoInfo(closeChunk=True))

        # bottom buttons
        apply_button = QtWidgets.QPushButton('Apply')
        hide_button = QtWidgets.QPushButton('Hide/Show')
        delete_button = QtWidgets.QPushButton('Delete')
        hide_button.clicked.connect(lambda: self.enable_widget(top_grp))
        hide_button.clicked.connect(lambda: self.toggle_group(top_grp, 150, 0))
        hide_button.clicked.connect(lambda: self.toggle_group(self.layout_grp, 220, 80))
        hide_button.clicked.connect(self.hide_geo)
        apply_button.clicked.connect(self.apply_transformations)
        delete_button.clicked.connect(self.delete_widget)

        top_layout.addWidget(self.rename_line, 0, 0, 1, 2)
        top_layout.addWidget(rename_button, 0, 2, 1, 1)

        top_layout.addWidget(pin_label, 1, 0, 1, 1)
        top_layout.addWidget(self.pin_select_button, 1, 1, 1, 1)
        top_layout.addWidget(stored_button, 1, 2, 1, 1)

        top_layout.addWidget(pin_verts_grp, 2, 0, 1, 3)
        pin_verts_layout.addWidget(self.pin_verts_line)
        pin_verts_layout.addWidget(pin_verts_button)

        top_layout.addWidget(pin_text, 3, 0, 1, 1)
        top_layout.addWidget(self.pin_slider, 3, 1, 1, 1)
        top_layout.addWidget(self.pin_percent_box, 3, 2, 1, 1)

        bot_layout.addWidget(apply_button)
        bot_layout.addWidget(hide_button)
        bot_layout.addWidget(delete_button)

    def rename_geo(self):

        # change vertex mapping attribute of geo
        new_name = self.rename_line.text() + '_ISO_GEO'
        new_vtx_mapping = {}
        enum_list = []
        self.new_verts = []
        for new_vtx, old_vtx in self.vtx_mapping.items():
            new_vtx = new_name + '.' + new_vtx.split('.')[1]
            self.new_verts.append(new_vtx)
            new_vtx_mapping[new_vtx] = old_vtx
            enum_name = '{}-{}'.format(new_vtx, old_vtx)
            enum_list.append(enum_name)
        cmds.deleteAttr(self.geo, at='vtxMap')
        add_enum(self.geo, 'vtxMap', enum_list, visible=False)
        self.vtx_mapping = new_vtx_mapping

        # change name of geo
        if new_name:
            self.layout_grp.setTitle(new_name)
        self.geo = cmds.rename(self.geo, new_name)

    def enable_widget(self, widget):
        if widget.isEnabled():
            widget.setEnabled(False)
        else:
            widget.setEnabled(True)

    def toggle_group(self, widget, max_height, min_height):
        height = widget.height()
        if height == min_height:
            widget.setFixedHeight(max_height)
        else:
            widget.setFixedHeight(min_height)

    def create_geo(self):
        self.geo = cmds.duplicate(self.source_geo)[0]
        self.geo = cmds.rename(self.geo, self.geo + '_ISO_GEO')
        deleted_faces = cmds.ls(self.geo + '.f[*]', fl=True)
        new_geo_faces = []
        for each in self.faces:
            face = self.geo + '.' + each.split('.')[1]
            deleted_faces.remove(face)
            new_geo_faces.append(face)
        cmds.select(deleted_faces)
        cmds.delete()

    def store_vertices(self):
        '''
        Store the selected vertices inside the text box within the widget
        '''
        cmds.undoInfo(openChunk=True)
        selection = cmds.ls(sl=True, fl=True)
        vertices_string = ''
        if not selection:
            raise ValueError('Select vertices to be stored')
        for each in selection:
            if self.check_vertex(each):
                if each != selection[-1]:
                    vertices_string += each + ','
                else:
                    vertices_string += each
            else:
                raise ValueError('{} not in target geometry'.format(each))
        self.pin_verts_line.setText(vertices_string)
        cmds.undoInfo(closeChunk=True)

    def map_vertices(self):
        self.new_verts = cmds.ls(self.geo + '.vtx[*]', fl=True)
        enum_list = []
        for vtx in self.new_verts:
            pos = cmds.xform(vtx, t=True, ws=True, q=True)
            source_vtx = closest_vtx_on_mesh(self.source_geo, pos)
            self.vtx_mapping[vtx] = source_vtx
            enum_name = '{}-{}'.format(vtx, source_vtx)
            enum_list.append(enum_name)
        add_enum(self.geo, 'vtxMap', enum_list, visible=False)

    def map_vectors(self):
        if self.pin_select_button.isChecked():
            vertices = cmds.ls(sl=True, fl=True)
            # check verts to make sure they are on the right mesh
            if vertices:
                for each in vertices:
                    if not self.check_vertex(each):
                        raise ValueError('{} not in target geometry'.format(each))
            else:
                raise ValueError('Select vertices')
        else:
            vertices = self.pin_verts_line.text().split(',')
            if not vertices[0]:
                raise ValueError('Store vertices to be affected')

        self.vector_mapping = {}
        self.position_mapping = {}

        for vtx in vertices:
            posX1, posY1, posZ1 = cmds.xform(vtx, t=True, ws=True, q=True)
            posX2, posY2, posZ2 = cmds.xform(self.vtx_mapping[vtx], t=True, ws=True, q=True)
            first_pos = om.MVector(posX1, posY1, posZ1)
            second_pos = om.MVector(posX2, posY2, posZ2)
            self.vector_mapping[vtx] = second_pos - first_pos
            self.position_mapping[vtx] = first_pos

    def move_vertices(self):
        for vtx, vector in self.vector_mapping.items():
            percent = float(self.pin_slider.value())/100.00
            new_vector = vector * percent
            old_pos = self.position_mapping[vtx]
            new_pos = old_pos + new_vector
            cmds.move(new_pos[0], new_pos[1], new_pos[2], vtx, ws=True)

    def check_vertex(self, vertex):
        '''
        Checks to see if vertex is in the new geo
        Args:
            vertex (str): given vertex to check
        Return:
            bool: true or false, true being it is a vertex
        '''
        if vertex in self.new_verts:
            return True
        else:
            return False

    def release_pin_slider(self):
        self.vector_mapping = {}
        self.position_mapping = {}
        self.pin_slider.setValue(0)

    def apply_transformations(self):
        cmds.undoInfo(openChunk=True)
        for new_vtx, old_vtx in self.vtx_mapping.items():
            new_pos = cmds.xform(new_vtx, t=True, ws=True, q=True)
            cmds.move(new_pos[0], new_pos[1], new_pos[2], old_vtx, ws=True)
        cmds.undoInfo(closeChunk=True)

    def delete_widget(self):
        cmds.undoInfo(openChunk=True)
        self.setParent(None)
        self.setVisible(False)
        self.deleteLater()
        cmds.delete(self.geo)
        cmds.undoInfo(closeChunk=True)

    def hide_geo(self):
        '''
        Hide geo if the layout is collapsed
        '''

        height = self.layout_grp.height()
        if height == 80:
            cmds.setAttr(self.geo + '.v', 0)
        else:
            cmds.setAttr(self.geo + '.v', 1)


class PtsToGeoTool(QtWidgets.QWidget):
    mesh_widgets = []

    def __init__(self):
        self.namespace = None
        self.mesh_widgets = []

        # if the ui exists then delete it
        old_window = omui.MQtUtil_findWindow('ptsToGeoTool')
        if old_window:
            cmds.deleteUI('ptsToGeoTool')

        # create a new dialog and give it the main maya window as its parent
        # store it as the parent for our current UI to be put inside
        parent = QtWidgets.QDialog(parent=getMayaMainWindow())

        # set its name so that we can find and delete it later
        parent.setObjectName('ptsToGeoTool')
        parent.setWindowTitle('Points To Geo')

        super(PtsToGeoTool, self).__init__(parent=parent)

        QtWidgets.QVBoxLayout(parent)

        self.buildUI()

        self.parent().layout().addWidget(self)

        parent.show()

    def buildUI(self):

        # create main layouts
        main_layout = QtWidgets.QVBoxLayout(self)
        project_grp_button = QtWidgets.QPushButton('PROJECT GEOMETRY')
        project_grp_button.setStyleSheet("background-color: black")
        project_grp_button.setFixedHeight(20)
        iso_geo_button = QtWidgets.QPushButton('ISOLATE GEOMETRY')
        iso_geo_button.setStyleSheet("background-color: black")
        iso_geo_button.setFixedHeight(20)

        top_grp = QtWidgets.QGroupBox()
        mid_grp = QtWidgets.QGroupBox()

        top_layout = QtWidgets.QGridLayout(top_grp)
        mid_layout = QtWidgets.QGridLayout(mid_grp)
        bot_layout = QtWidgets.QHBoxLayout()

        main_layout.addWidget(project_grp_button)
        main_layout.addWidget(top_grp)
        main_layout.addWidget(iso_geo_button)
        main_layout.addWidget(mid_grp)
        main_layout.addLayout(bot_layout)

        # add toggles
        project_grp_button.clicked.connect(lambda: self.toggle_group(top_grp, 100))
        iso_geo_button.clicked.connect(lambda: self.toggle_group(mid_grp, 300))

        # text box for target mesh
        source_mesh_text = QtWidgets.QLabel()
        source_mesh_text.setText('Source Mesh:')
        self.source_mesh = QtWidgets.QLineEdit()
        source_mesh_button = QtWidgets.QPushButton('Get Mesh')
        source_mesh_button.clicked.connect(self.get_mesh)

        # radio buttons for project method
        proj_method_text = QtWidgets.QLabel()
        proj_method_text.setText('Project Method:')
        self.pnt_order_button = QtWidgets.QRadioButton()
        self.pnt_order_button.setText('Point Order')
        closest_pnt_button = QtWidgets.QRadioButton()
        closest_pnt_button.setText('Closest Point')
        closest_pnt_button.toggle()
        project_button = QtWidgets.QPushButton()
        project_button.setText('Project Mesh')
        project_button.clicked.connect(self.project_geo)

        # isolate geometry tool part of layout
        mesh_button = QtWidgets.QPushButton('Create Mesh')
        load_mesh_button = QtWidgets.QPushButton('Load Meshes')
        mesh_button.clicked.connect(self.create_iso_geo)
        load_mesh_button.clicked.connect(self.load_meshes)
        scrollWidget = QtWidgets.QWidget()
        self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget)

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setWidgetResizable(True)

        scrollArea.setWidget(scrollWidget)

        mid_layout.addWidget(mesh_button, 0, 0, 1, 1)
        mid_layout.addWidget(load_mesh_button, 0, 1, 1, 1)
        mid_layout.addWidget(scrollArea, 1, 0, 1, 2)

        top_layout.addWidget(source_mesh_text, 0, 0, 1, 1)
        top_layout.addWidget(self.source_mesh, 0, 1, 1, 1)
        top_layout.addWidget(source_mesh_button, 0, 2, 1, 1)

        top_layout.addWidget(proj_method_text, 1, 0, 1, 1)
        top_layout.addWidget(self.pnt_order_button, 1, 1, 1, 1)
        top_layout.addWidget(closest_pnt_button, 1, 2, 1, 1)

        top_layout.addWidget(project_button, 2, 0, 1, 3)

        top_grp.setFixedHeight(top_grp.sizeHint().height())

        self.load_meshes()

    def create_iso_geo(self):
        selection = cmds.ls(sl=True, fl=True)
        if '.f[' not in selection[0]:
            raise ValueError('Select faces of a geo')
        iso_geo = IsoGeoWidget(faces=selection)
        self.scrollLayout.addWidget(iso_geo)
        self.mesh_widgets.append(iso_geo)

    def get_mesh(self):
        selection = cmds.ls(sl=True)[0]
        shape = cmds.listRelatives(selection, s=True)[0]
        shape_type = cmds.nodeType(shape)
        if shape_type != 'mesh':
            raise ValueError('Select a piece of geometry')
        else:
            self.source_mesh.setText(selection)

    def toggle_group(self, widget, max_height):
        height = widget.height()
        if height < 1:
            # widget.setFixedHeight(widget.sizeHint().height())
            widget.setFixedHeight(max_height)
        else:
            widget.setFixedHeight(0)

    # main utility functions for module
    def project_geo(self):
        self.source_geo = self.get_geo(self.source_mesh.text())
        cmds.undoInfo(openChunk=True)
        if self.pnt_order_button.isChecked():
            self.match_point_order()
        else:
            self.match_closest_point()
        cmds.undoInfo(closeChunk=True)

    def closest_point_on_mesh(self, geo, point):
        obj = om.MSelectionList()
        obj.add(geo)
        mesh = om.MFnMesh(obj.getComponent(0)[0])

        pos = om.MPoint(point[0], point[1], point[2])
        point = mesh.getClosestPoint(pos, space=4)

        return point

    def match_point_order(self):
        selection = cmds.ls(sl=True, fl=True)
        if 'vtx' in selection[0]:
            target_geo = selection[0].split('.')[0]
            self.point_check(target_geo)
            for target_vtx in selection:
                source_vtx = '{}.{}'.format(self.source_geo, target_vtx.split('.')[1])
                pos = cmds.xform(source_vtx, t=True, ws=True, q=True)
                cmds.move(pos[0], pos[1], pos[2], [target_vtx], ws=True)
        else:
            self.geo_check(selection[0])
            vtxs = cmds.ls('{}.vtx[*]'.format(selection[0]), fl=True)
            for i, target_vtx in enumerate(vtxs):
                source_vtx = '{}.vtx[{}]'.format(self.source_geo, i)
                pos = cmds.xform(source_vtx, t=True, ws=True, q=True)
                cmds.move(pos[0], pos[1], pos[2], [target_vtx], ws=True)

    def match_closest_point(self):
        selection = cmds.ls(sl=True, fl=True)
        if 'vtx' in selection[0]:
            target_geo = selection[0].split('.')[0]
            self.point_check(target_geo)
            for target_vtx in selection:
                target_pos = cmds.xform(target_vtx, t=True, ws=True, q=True)
                pos = self.closest_point_on_mesh(self.source_geo, target_pos)[0]
                cmds.move(pos[0], pos[1], pos[2], [target_vtx], ws=True)
        else:
            self.geo_check(selection[0])
            vtxs = cmds.ls('{}.vtx[*]'.format(selection[0]), fl=True)
            for target_vtx in vtxs:
                target_pos = cmds.xform(target_vtx, t=True, ws=True, q=True)
                pos = self.closest_point_on_mesh(self.source_geo, target_pos)[0]
                cmds.move(pos[0], pos[1], pos[2], [target_vtx], ws=True)

    def point_check(self, target_geo):
        source_vtxs = cmds.ls('{}.vtx[*]'.format(self.source_geo), fl=True)
        target_vtxs = cmds.ls('{}.vtx[*]'.format(target_geo), fl=True)

        if len(source_vtxs) != len(target_vtxs):
            cmds.warning('Geos do not have the same amount of vertices')

    def geo_check(self, dag):
        shape = cmds.listRelatives(dag, s=True)[0]
        shape_type = cmds.nodeType(shape)
        if shape_type != 'mesh':
            raise ValueError('Select a piece of geometry')

    def get_geo(self, dag, shape=False):
        self.geo_check(dag)
        if shape:
            geo = cmds.listRelatives(dag, s=True)
        else:
            geo = dag
        return geo

    def load_meshes(self):
        self.clear_scroll_area()
        geos = cmds.ls('*ISO_GEO')
        if geos:
            for geo in geos:
                mapping = cmds.attributeQuery('vtxMap', node=geo, listEnum=True)[0].split(':')
                vtx_mapping = {}
                for map in mapping:
                    new_vtx, old_vtx = map.split('-')
                    vtx_mapping[new_vtx] = old_vtx
                source_geo = cmds.getAttr(geo + '.sourceGeo')
                geo_widget = IsoGeoWidget(geo=geo, source_geo=source_geo, vtx_mapping=vtx_mapping)
                self.scrollLayout.addWidget(geo_widget)
                self.mesh_widgets.append(geo_widget)

    def clear_scroll_area(self):
        for each in self.mesh_widgets:
            each.setParent(None)
            each.setVisible(False)
            each.deleteLater()
        self.mesh_widgets = []


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


def add_enum(node, name, enum_list, visible=True):
    '''Wrapper for making an enum attribute

    Args:
        node (str): node to add attribute to
        name (str): name of attribute
        visible (bool): whether the attribute will be visible in the chan
        *args: arguments that will be the enum names of the attribute
    Return:
         (str): attribute name
    '''

    enum_names = ''
    for i, arg in enumerate(enum_list):
        if arg != enum_list[-1]:
            enum_names += arg + ':'
        else:
            enum_names += arg

    cmds.addAttr(node,
                 shortName=name,
                 attributeType='enum',
                 enumName=enum_names,
                 keyable=visible)

    return '{}.{}'.format(node, name)


def closest_point_on_mesh(geo, point):
    obj = om.MSelectionList()
    obj.add(geo)
    mesh = om.MFnMesh(obj.getComponent(0)[0])

    pos = om.MPoint(point[0], point[1], point[2])
    point = mesh.getClosestPoint(pos, space=4)

    return point


def closest_vtx_on_mesh(geo, point):
    obj = om.MSelectionList()
    obj.add(geo)
    mesh = om.MFnMesh(obj.getComponent(0)[0])

    pos = om.MPoint(point[0], point[1], point[2])
    point, normal, face = mesh.getClosestPointAndNormal(pos, space=4)
    face = '{}.f[{}]'.format(geo, face)
    vertices = cmds.polyListComponentConversion(face, tv=True)
    vertices = cmds.ls(vertices, fl=True)
    start_pos = om.MVector(point[0], point[1], point[2])
    # find which vertex has the same position as the given point
    shortest_distance = None
    closest_vtx = None

    for i, vtx in enumerate(vertices):
        pos = cmds.xform(vtx, t=True, ws=True, q=True)
        end_pos = om.MVector(pos[0], pos[1], pos[2])
        distance = (start_pos - end_pos).length()
        if not closest_vtx:
            shortest_distance = distance
            closest_vtx = vtx
        elif distance < shortest_distance:
            shortest_distance = distance
            closest_vtx = vtx
        if distance == 0:
            break

    return closest_vtx
