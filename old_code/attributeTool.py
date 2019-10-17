import pymel.core as pm
import maya.cmds as cmds
import collections

#Dictionary for column of each attribute
cLDict = collections.OrderedDict()
#Dictionary for row of each attribute
rowDict = collections.OrderedDict()
#Dictionary of index option menu control for each attribute
indexDict = collections.OrderedDict()
#Dictionary of optionMenus
omDict = collections.OrderedDict()
#Dictionary of attribute value
attrDict = collections.OrderedDict()

winAttrID = 'attributeEdit'

if pm.window(winAttrID, exists = True):
    pm.deleteUI(winAttrID)

winAttrID = pm.window('attributeEdit', width = 200)
attrTopColumn = pm.columnLayout(adj = True, rs = 5)

attrTopRow = pm.rowLayout(nc = 4)

width = 108
newAttrButton = pm.button(label = 'Create New Attribute', h = 45, w = width, c = 'addAttrRow()')
loadAttrButton = pm.button(label = 'Load Attributes', h = 45, w = width)
reorderAttrButton = pm.button(label = 'Reorder Attributes', h = 45, w = width)
applyAttrButton = pm.button(label = 'Apply Attributes', h = 45, w = width)
pm.setParent('..')


pm.separator(style = 'in')

#attrListCL = pm.columnLayout()
topRL = pm.rowLayout(nc = 2, width = 800)

leftColumn = pm.columnLayout(parent = topRL)
pm.text(label = 'left', parent = leftColumn)
rightColumn = pm.columnLayout(parent = topRL, cat = ('both', 0))
pm.text(label = 'right2', parent = rightColumn)
pm.showWindow()

class CLnum:
    CL = 0

    def addColumn(self):
        self.CL += 1
    def resetColumn(self):
        self.CL = 0

num = CLnum()






#adds an attribute to the list
def addAttrRow():
    columnName = 'CL' + str(num.CL)
    cLDict[columnName] = pm.columnLayout(parent = attrListCL)

    rowDict[columnName] = pm.rowLayout(nc = 6)
    pm.button(label = 'Change Attribute', c = 'changeAttr("%s")' % (str(columnName)), h = 18)
    omDict['atType' + columnName] = pm.optionMenu()
    pm.menuItem(label = 'Float')
    pm.menuItem(label = 'Enum')
    pm.menuItem(label = 'Integer')
    pm.menuItem(label = 'Boolean')
    pm.menuItem(label = 'Vector')
    #create parent row to reparent the attribute rows under
    rowDict['atParRow' + columnName] = pm.rowLayout(nc = 1)
    floatAttr(columnName)
    indexDict[columnName] = pm.columnLayout(parent = rowDict[columnName])
    omDict['index' + columnName] = pm.optionMenu()
    indices = num.CL
    x = -1
    while x < num.CL:
        x = x + 1
        pm.menuItem(label = str(x))

    rebuildIndex(num.CL)
    #add the global variable of the number of columns
    num.addColumn()


#function to rebuild every index option menu with the right amount of indices
def rebuildIndex(numOfIndices):

    for each in indexDict:
        columnName = each
        columnNumber = int(each.split('CL')[1])

        par = pm.columnLayout(indexDict[each], query = True, parent = True)
        pm.deleteUI(indexDict[each])

        indexDict[each] = pm.columnLayout(parent = rowDict[each])
        omDict['index' + columnName] = pm.optionMenu()
        x = 0
        while x < (numOfIndices + 1):
            pm.menuItem(label = str(x))
            x = x + 1
        #change option menu to current index
        pm.optionMenu(omDict['index' + columnName], e = True, value = columnNumber)

def changeAttr(columnName):

    #query the type of attribute you will be changing to
    atType = pm.optionMenu(omDict['atType' + columnName], query = True, value = True)

    if atType == 'Float':
        floatAttr(columnName)
    elif atType == 'Enum':
        enumAttr(columnName)
    elif atType == 'Integer':
        intAttr(columnName)
    elif atType == 'Boolean':
        booleanAttr(columnName)
    elif atType == 'Vector':
        vectorAttr(columnName)


def floatAttr(columnName):
    #query the text in the previous text box
    try:
        oldText = pm.textField(attrDict['text' + columnName], query = True, tx = True)
    except:
        oldText = ''

    #query the min value of the previous box
    try:
        oldMin = pm.floatField(attrDict['floatMin' + columnName], query = True, value = True)
    except:
        oldMin = 0.0

    #query the max value of the previous box
    try:
        oldMax = pm.floatField(attrDict['floatMax' + columnName], query = True, value = True)
    except:
        oldMax = 0.0

    #delete the UI that houses the attribute type
    try:
        pm.deleteUI(rowDict['attrRow' + columnName])
    except:
        pass
    rowDict['attrRow' + columnName] = pm.rowLayout(nc = 6, parent = rowDict['atParRow' + columnName] )

    pm.text('Attribute Name')
    attrDict['text' + columnName] = pm.textField(tx = oldText)


    pm.text('Min')
    attrDict['floatMin' + columnName] = pm.floatField(value = oldMin)


    pm.text('Max')
    attrDict['floatMax' + columnName] = pm.floatField(value = oldMax)
    pm.setParent('..')


def enumAttr(columnName):
    #query the text in the previous text box
    try:
        oldText = pm.textField(attrDict['text' + columnName], query = True, tx = True)
    except:
        oldText = ''

    #delete the UI that houses the attribute type
    try:
        pm.deleteUI(rowDict['attrRow' + columnName])
    except:
        pass

    rowDict['attrRow' + columnName] = pm.rowLayout(nc = 7, parent = rowDict['atParRow' + columnName] )

    pm.text('Attribute Name')
    attrDict['text' + columnName] = pm.textField(tx = oldText)

    pm.text('New Option')
    pm.textField()
    pm.button(label = 'Add Option')
    pm.text('Options')
    pm.optionMenu()

def intAttr(columnName):
    #query the text in the previous text box
    try:
        oldText = pm.textField(attrDict['text' + columnName], query = True, tx = True)
    except:
        oldText = ''

    #query the min value of the previous box
    try:
        oldMin = pm.intField(attrDict['intMin' + columnName], query = True, value = True)
    except:
        oldMin = 0.0

    #query the max value of the previous box
    try:
        oldMax = pm.intField(attrDict['intMax' + columnName], query = True, value = True)
    except:
        oldMax = 0.0

    #delete the UI that houses the attribute type
    try:
        pm.deleteUI(rowDict['attrRow' + columnName])
    except:
        pass
    rowDict['attrRow' + columnName] = pm.rowLayout(nc = 6, parent = rowDict['atParRow' + columnName] )

    pm.text('Attribute Name')
    attrDict['text' + columnName] = pm.textField(tx = oldText)

    width = 60
    pm.text('Min')
    attrDict['intMin' + columnName] = pm.intField(value = oldMin, w = width)


    pm.text('Max')
    attrDict['intMax' + columnName] = pm.intField(value = oldMax, w = width)
    pm.setParent('..')

def booleanAttr(columnName):
    #query the text in the previous text box
    try:
        oldText = pm.textField(attrDict['text' + columnName], query = True, tx = True)
    except:
        oldText = ''

    #delete the UI that houses the attribute type
    try:
        pm.deleteUI(rowDict['attrRow' + columnName])
    except:
        pass
    rowDict['attrRow' + columnName] = pm.rowLayout(nc = 6, parent = rowDict['atParRow' + columnName] )

    pm.text('Attribute Name')
    attrDict['text' + columnName] = pm.textField(tx = oldText)

def vectorAttr(columnName):
    #query the text in the previous text box
    try:
        oldText = pm.textField(attrDict['text' + columnName], query = True, tx = True)
    except:
        oldText = ''

    #delete the UI that houses the attribute type
    try:
        pm.deleteUI(rowDict['attrRow' + columnName])
    except:
        pass
    rowDict['attrRow' + columnName] = pm.rowLayout(nc = 6, parent = rowDict['atParRow' + columnName] )

    pm.text('Attribute Name')
    attrDict['text' + columnName] = pm.textField(tx = oldText)















import pymel.core as pm
import maya.cmds as cmds
import collections

from PySide import QtCore, QtGui
from shiboken import wrapInstance
from maya import OpenMayaUI as omui

mayaMainWindowPtr = omui.MQtUtil.mainWindow()
mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QtGui.QWidget)

MAIN_WINDOW_TITLE = 'Attribute Tool'
MAIN_WINDOW_NAME = 'attributeToolName'
VIEWPORT_LAYOUT_NAME = 'viewportLayout'

open_example_window()

def open_example_window():
    """
    check if the ui exists already. If it does delete it
    :return:
    """
    if cmds.window(MAIN_WINDOW_NAME, q=True, ex=True):
        cmds.deleteUI(MAIN_WINDOW_NAME, window=True)
    win = AttrTool()
    win.show()
    win.resetColumn()
class AttrTool(QtGui.QMainWindow):
    numAttrs = 0

    def addColumn(self):
        self.numAttrs += 1
    def resetColumn(self):
        self.numAttrs = 0


    def __init__(self, parent = mayaMainWindow):
        "Initialize the Window."

        super(AttrTool, self).__init__(parent)

        #Window Title
        self.setWindowTitle(MAIN_WINDOW_TITLE)
        self.setObjectName(MAIN_WINDOW_NAME)
        self.resize(1100,700)

        #create the main widget
        main_widget = QtGui.QWidget()
        self.setCentralWidget(main_widget)

        #create main layout
        main_layout = QtGui.QVBoxLayout(main_widget)

        #create layout for buttons
        buttonLayout = QtGui.QHBoxLayout()
        main_layout.addLayout(buttonLayout)

        #create layout for attributes
        attrLayout = QtGui.QVBoxLayout()
        main_layout.addLayout(attrLayout)



        #create first button row
        self.newAttrButton = QtGui.QPushButton("Add Attribute")
        self.newAttrButton.setObjectName("addAttributes")
        self.newAttrButton.clicked.connect(self.addAttrRow(self, attrLayout))

        self.loadAttrButton = QtGui.QPushButton("Load Attributes")
        self.loadAttrButton.setObjectName("loadAttributes")

        self.reorderAttrButton = QtGui.QPushButton("Reorder Attributes")
        self.reorderAttrButton.setObjectName("reorderAttributes")

        self.applyAttrButton = QtGui.QPushButton("Apply Attributes")
        self.applyAttrButton.setObjectName("applyAttributes")


        #add buttons in a row to layout
        buttonLayout.addWidget(self.newAttrButton)
        buttonLayout.addWidget(self.loadAttrButton)
        buttonLayout.addWidget(self.reorderAttrButton)
        buttonLayout.addWidget(self.applyAttrButton)


    def addAttrRow(self, parentLayout):

        attrRowName = 'ar' + str(self.numAttrs)

        #create new row for attribute
        self.attrRowLayout = QtGui.QHBoxLayout()
        self.parentLayout.addLayout(attrRowLayout)

        #create widgets for attribute row
        self.changeAttrButton = QtGui.QPushButton("Change Attribute")
        self.changeAttrButton.setObjectName(attrRowName + "_changeAttrs")

        self.changeAttrMenu = QtGui.QMenu()
        self.changeAttrMenu.addAction('Float')
        self.changeAttrMenu.addAction('Enum')
        self.changeAttrMenu.addAction('Integer')
        self.changeAttrMenu.addAction('Boolean')
        self.changeAttrMenu.addAction('Vector')

        self.changeAttrButton.setMenu(self.changeAttrMenu)

        #add widgets to layout
        self.attrRowLayout.addWidget(self.changeAttrButton)

        self.addColumn()






