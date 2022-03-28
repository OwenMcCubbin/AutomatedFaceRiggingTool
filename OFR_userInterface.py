##Import Packages

import maya.mel as mel
import pymel.core as pm
import os
import OFR_faceSetup as fs
reload(fs)
import OFR_attrEdits as ae
reload(ae)
import OFR_materialSetup as ms
reload(ms)
##import needed Qt packages
from PySide2 import QtCore, QtWidgets, QtUiTools

from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui


#### Create a file search function and UI ####
def get_maya_window():
    ##Return the main Maya window
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

def get_script_dir():
    ##Returns the directory where the current script lives
    script_file = os.path.abspath(__file__)
    return os.path.dirname(script_file)

def check_selection():
        ##grab selected item
    if pm.ls(selection=True) == [] or '':
        pm.warning('No object selected, plese select the desired object to label')
    else:
        selected = pm.ls(selection=True)
    return selected 

class OFR_Tool(QtWidgets.QDialog):
    
    def __init__(self, parent=get_maya_window()):
        ## Run the initialization on the inherited QDialog class
        super(OFR_Tool, self).__init__(parent)
        
        ## Set the window title
        self.setWindowTitle('OFR Tool')
        
        ## Create a flags object from WindowsFlags
        flags = QtCore.Qt.WindowFlags()
        ## Assign it to be of type "Dialog" (we are using QWidgets.QDialog above)
        flags = QtCore.Qt.Dialog
        ##Add the minimize button using the bitwise operator
        flags |= QtCore.Qt.WindowMinimizeButtonHint
        ## If you wanted, this is how to add a maximize (not common for Maya UIs so this is commented out)
        #flags |= QtCore.Qt.WindowMaximizeButtonHint
        ## Add a close button, as adding the flags overrides the default close that is there
        flags |= QtCore.Qt.WindowCloseButtonHint
        ## Set the flags to the current window object
        self.setWindowFlags(flags)
        
        ## Assemble the file path for the ui file and icons
        ui_file_path = os.path.join(get_script_dir(), 'OFR_ui.ui')
        frontFace_icon = (ui_file_path).replace('scripts\OFR_ui.ui', 'prefs\icons\OFR_icons\OFR_FaceFrontIcon.png')
        sideFace_icon = (ui_file_path).replace('scripts\OFR_ui.ui', 'prefs\icons\OFR_icons\OFR_FaceSideIcon.png')
        ## Create a QFile object form the file path
        qfile_object = QtCore.QFile(ui_file_path)
        ## Open the QFile object
        qfile_object.open(QtCore.QFile.ReadOnly)
        ## Create a QUI Loader
        loader = QtUiTools.QUiLoader()
        ## Load the file and save it to a property
        self.ui = loader.load(qfile_object, parentWidget=self)
        ##load icons into image labels
        self.ui.label_frontFace.setPixmap(frontFace_icon)
        self.ui.label_sideFace.setPixmap(sideFace_icon)

        ##combo box items
        self.ui.cmbSide.addItem('Left')
        self.ui.cmbSide.addItem('Center')
        self.ui.cmbSide.addItem('Right')
        self.ui.cmbSide_2.addItem('Left')
        self.ui.cmbSide_2.addItem('Center')
        self.ui.cmbSide_2.addItem('Right')    
        
        ##button links
        self.ui.btn_eye.clicked.connect(self.label_eye)
        self.ui.btn_head.clicked.connect(self.label_head)
        self.ui.btn_jaw.clicked.connect(self.label_jaw)
        self.ui.btn_neck.clicked.connect(self.label_neck)
        self.ui.btn_lipParent.clicked.connect(self.label_lipParent)
        self.ui.btn_brow.clicked.connect(self.label_brow)
        self.ui.btn_squint.clicked.connect(self.label_squint)
        self.ui.btn_nostril.clicked.connect(self.label_nostril)
        self.ui.btn_laugh.clicked.connect(self.label_laugh)
        self.ui.btn_cheek.clicked.connect(self.label_cheek)
        self.ui.btn_upperLip.clicked.connect(self.label_upperLip)
        self.ui.btn_lowerLip.clicked.connect(self.label_lowerLip)
        ###
        self.ui.btn_upperEyelid.clicked.connect(self.label_upperEyelid)
        self.ui.btn_lowerEyelid.clicked.connect(self.label_lowerEyelid)
        ###
        self.ui.btn_build.clicked.connect(self.build_face)

        ## Close the file handle
        qfile_object.close()
        
        ## Show the UI
        self.show() 
            
    def label_eye(self):
        #print('Label Eye')
        selection = check_selection()
        side = self.ui.cmbSide.currentText()
        obj = 'Eye'
        obj_type = 'jnt'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)
    
    def label_jaw(self):
        selection = check_selection()
        side = 'Center'
        obj = 'Jaw'
        obj_type = 'jnt'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)
    
    def label_head(self):
        selection = check_selection()
        side = 'Center'
        obj = 'Head'
        obj_type = 'jnt'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)
    
    def label_neck(self):
        selection = check_selection()
        side = 'Center'
        obj = 'Neck'
        obj_type = 'jnt'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)
        
    def label_lipParent(self):
        selection = check_selection()
        side = 'Center'
        obj = 'LipParent'
        obj_type = 'jnt'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)

    def label_brow(self):
        selection = check_selection()
        side = self.ui.cmbSide.currentText()
        obj = 'Brow'
        obj_type = 'curve'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)

    def label_squint(self):
        selection = check_selection()
        side = self.ui.cmbSide.currentText()
        obj = 'Squint'
        obj_type = 'curve'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)

    def label_nostril(self):
        selection = check_selection()
        side = self.ui.cmbSide.currentText()
        obj = 'Nostril'
        obj_type = 'curve'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)

    def label_laugh(self):
        selection = check_selection()
        side = self.ui.cmbSide.currentText()
        obj = 'Laugh'
        obj_type = 'curve'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)

    def label_cheek(self):
        selection = check_selection()
        side = self.ui.cmbSide.currentText()
        obj = 'Cheek'
        obj_type = 'curve'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)

    def label_lowerLip(self):
        selection = check_selection()
        side = self.ui.cmbSide.currentText()
        obj = 'LowerLip'
        obj_type = 'curve'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)

    def label_upperLip(self):
        selection = check_selection()
        side = self.ui.cmbSide.currentText()
        obj = 'UpperLip'
        obj_type = 'curve'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)

    def label_upperEyelid(self):
        selection = check_selection()
        side = self.ui.cmbSide.currentText()
        obj = 'UpperEyelid'
        obj_type = 'curve'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)

    def label_lowerEyelid(self):
        selection = check_selection()
        side = self.ui.cmbSide.currentText()
        obj = 'LowerEyelid'
        obj_type = 'curve'
        if ae.check_attr_exists(selection) == False:
            ae.create_labels(selection, side, obj, obj_type)
        if ae.check_attr_exists(selection) == True:
            ae.replace_labels(selection, side, obj, obj_type)

    def build_face(self):
        ##check if all curves are labeled
        ae.check_curves()
        if ae.check_curves() == False:
            return
        ae.check_joints()
        if ae.check_joints() == False:
            return
        fs.mirror_eye()
        fs.create_lipParents()
        fs.mirror_curves()
        fs.create_lip_curves()
        fs.organize_meshes()
        fs.organize_curves()
        fs.organize_joints()
        fs.create_path_elements()
        dynamic_doops = fs.doop_curves()
        mouth_elements = fs.mouth_corners()
        dynamic_nostril_ctrls = fs.create_dynamic_nostrils()
        dynamic_brow_ctrls = fs.create_dynamic_brows()
        dynamic_eyelid_ctrls = fs.create_dynamic_eyelids()
        dynamic_squint_ctrls = fs.create_dynamic_squint()
        fs.dynamic_setup(dynamic_doops, mouth_elements, dynamic_nostril_ctrls, dynamic_squint_ctrls, dynamic_brow_ctrls, dynamic_eyelid_ctrls)
        fs.dynamic_automation(mouth_elements, dynamic_nostril_ctrls, dynamic_squint_ctrls, dynamic_brow_ctrls)
        fs.link_dynamic()
        head_ctrl = fs.create_basejoint_controls()
        fs.adjust_detail_rot()
        fs.clean_up_hierachy(head_ctrl)


        
##Run script and UI
def run():
    ##check to see if the QT widget already exists
    for ui_item in QtWidgets.QApplication.allWidgets():
        ##If the QT item matches the one in this script than close it
        if type(ui_item).__name__ == 'OFR_Tool':
            ##Close file
            ui_item.close()
            
    OFR_Tool()