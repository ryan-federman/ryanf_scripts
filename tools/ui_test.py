import json
import os

import Qt

# I will use the following modules more often, so let me import them directly
import time
from Qt import QtCompat, QtWidgets, QtCore, QtGui
from maya import OpenMayaUI as omui
import maya.cmds as cmds
from shiboken2 import wrapInstance
from Qt.QtCore import Signal

from functools import partial


class MainUI(QtWidgets.QWidget):
    def __init__(self):
        # check to see if window exists, if not delete it
        old_window = omui.MQtUtil_findWindow('testUI')
        if old_window:
            cmds.deleteUI('testUI')
        # Then we create a new dialog and give it the main maya window as its parent
        # we also store it as the parent for our current UI to be put inside
        parent = QtWidgets.QDialog(parent=getMayaMainWindow())
        # We set its name so that we can find and delete it later
        parent.setObjectName('testUI')
        # Then we set the title
        parent.setWindowTitle('Test UI')
        # look up pyqt documentation to see what QWidget's init method takes
        super(MainUI, self).__init__(parent=parent)

        dlgLayout = QtWidgets.QVBoxLayout(parent)

        # We call our buildUI method to construct our UI
        self.buildUI()

        self.parent().layout().addWidget(self)

        parent.show()

    def buildUI(self):
        layout = QtWidgets.QGridLayout(self)
        layout.setColumnMinimumWidth(1, 200)
        layout.setRowMinimumHeight(1, 10)

        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.addItems(['one', 'two', 'three'])
        # Finally we add it to the layout in row 0, column 0
        # We tell it take 1 row and two columns worth of space
        layout.addWidget(self.combo_box, 0, 0, 1, 2)

        # We create a button to create the chosen lights
        createBtn = QtWidgets.QPushButton('Create')
        # We connect the button so it calls the clickFunction method when its clicked
        createBtn.clicked.connect(self.add_text_widget)
        # We add it to the layout in row 0, column 2
        layout.addWidget(createBtn, 0, 2)

        # We want to put all the LightWidgets inside a scrolling container
        # We first need a container widget
        scrollWidget = QtWidgets.QWidget()
        # We want to make sure this widget only tries to be the maximum size of its contents
        scrollWidget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        # Then we give it a vertical layout because we want everything arranged vertically
        self.scrollLayout = QtWidgets.QVBoxLayout(scrollWidget)

        # Finally we create a scrollArea that will be in charge of scrolling its contents
        scrollArea = QtWidgets.QScrollArea()
        # Make sure it's resizable so it resizes as the UI grows or shrinks
        scrollArea.setWidgetResizable(True)
        # Then we set it to use our container widget to scroll
        scrollArea.setWidget(scrollWidget)
        # Then we add this scrollArea to the main layout, at row 1, column 0
        # We tell it to take 1 row and 3 columns of space
        layout.addWidget(scrollArea, 1, 0, 1, 3)

    def click_function(self, text):
        print text

    def add_text_widget(self):

        text = self.combo_box.currentText()
        button = QtWidgets.QPushButton(text)
        button.clicked.connect(partial(self.click_function, text))

        self.scrollLayout.addWidget(button)


def getMayaMainWindow():
    """
    Since Maya is Qt, we can parent our UIs to it.
    This means that we don't have to manage our UI and can leave it to Maya.
    Returns:
        QtWidgets.QMainWindow: The Maya MainWindow
    """
    # We use the OpenMayaUI API to get a reference to Maya's MainWindow
    win = omui.MQtUtil_mainWindow()
    # Then we can use the wrapInstance method to convert it to something python can understand
    # In this case, we're converting it to a QMainWindow
    ptr = wrapInstance(long(win), QtWidgets.QMainWindow)
    # Finally we return this to whoever wants it
    return ptr
