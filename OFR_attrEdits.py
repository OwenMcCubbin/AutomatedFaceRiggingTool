import types
import pymel.core as pm
import OFR_materialSetup as ms

##create labels
'''##Add a check if a nurbsCurve is selected and to label it and its transform parent.
##also add a check if the child is a nurbsCurve to label it and said nurbsCurve child.'''
def create_labels(node, side, obj, obj_type):
    ##make sure inputs are strings
    side = str(side)
    obj = str(obj)
    obj_type = str(obj_type)
    ##check if the node is a list, if so extract the object
    #print(node)
    if type(node) == list:
        node = node[0]
    side_label = 'SideLabel'
    object_label = 'ObjectLabel'
    type_label = 'TypeLabel'
    ##add attributes to the selected object
    node.addAttr(side_label, dataType='string')
    node.addAttr(object_label, dataType='string')
    node.addAttr(type_label, dataType='string')
    ##set the label attributes based on input for function then lock
    node.attr(side_label).set(side)
    pm.setAttr(node+'.'+side_label, lock=True)
    node.attr(object_label).set(obj)
    pm.setAttr(node+'.'+object_label, lock=True)
    node.attr(type_label).set(obj_type)
    pm.setAttr(node+'.'+type_label, lock=True)
    
##Check Side Label
def check_side(node):
    ##check if the node is a list, if so extract the object
    if type(node) == list:
        node = node[0]
    ##generate the attribute name for the side label
    attr_name = node + '.SideLabel'
    ##Grab the attribute 
    side = pm.getAttr(attr_name)
    ##Return the attribute
    return side

def determine_side(node):
    ##check if the node is a list, if so extract the object
    if type(node) == list:
        node = node[0]
    ##create an empty group
    temp_group = pm.group(empty=True)
    ##constrain the temp group to the node without offset to place it
    constraint = pm.pointConstraint(node, temp_group)
    ##delete the constraint
    pm.delete(constraint)
    ##create transformX attribute name
    attr_name = temp_group + '.translateX'
    ##grab the X attribute
    x_val = pm.getAttr(attr_name)
    ##check x value, if it is positive then Left, if neg then Right
    pm.delete(temp_group)
    if x_val > 0.001:
        return 'Left'
    if x_val < -0.001:
        return 'Right'
    else:
        return 'Center'

##Check object label
def check_object(node):
    if type(node) == list:
        node = node[0]
    attr_name = node + '.ObjectLabel'
    obj = pm.getAttr(attr_name)
    return obj

def check_type(node):
    if type(node) == list:
        node = node[0]
    attr_name = node + '.TypeLabel'
    obj_type = pm.getAttr(attr_name)
    return obj_type

def check_attr_exists(node):
    if type(node) == list:
        #print(node)
        node = node[0]
    ##side label name
    #print(node)
    side_attr = 'SideLabel'
    if pm.attributeQuery(side_attr, node=node, exists=True) == True:
        return True
    if pm.attributeQuery(side_attr, node=node, exists=True) == False:
        return False

def replace_labels(node, side, obj, obj_type):
    ##make sure all attr as strigns
    side = str(side)
    obj = str(obj)
    obj_type = str(obj_type)
    ##check if the node is a list, if so extract the object
    if type(node) == list:
        node = node[0]
    ##create attribute names
    side_attr = node + '.SideLabel'
    obj_attr = node + '.ObjectLabel'
    type_attr = node + '.TypeLabel'
    ##unlock attributes
    pm.setAttr(side_attr, lock=False)
    pm.setAttr(obj_attr, lock=False)
    pm.setAttr(type_attr, lock=False)
    ##relabel attributes
    pm.setAttr(side_attr, side)
    pm.setAttr(obj_attr, obj)
    pm.setAttr(type_attr, obj_type)
    ##relock attributes
    pm.setAttr(side_attr, lock=True)
    pm.setAttr(obj_attr, lock=True)
    pm.setAttr(type_attr, lock=True)

def check_curves():
    curve_objs = []
    ##get all curves
    all_curves = pm.ls(type='nurbsCurve')
    ##grab the parent transform node for all parents
    for curve in all_curves:
        curve_trans = pm.listRelatives(curve, parent=True)
        ##extract the parent not
        curve_trans = curve_trans[0]
        #all_curve_trans.append(curve_trans)
        if check_attr_exists(curve_trans) == False:
            pm.warning(curve_trans + ' does not have needed labels. Please use UI to label this curve or delete it if it is unnecessary.')
            return False
        ##grab obj label
        obj_label = check_object(curve_trans)
        ##append to list 
        curve_objs.append(obj_label)
    ##check if all curves exsist
    if 'Brow' not in curve_objs:
        pm.warning('Brow curve does not exsist. Please create, label and attempt Build again')
        return False
    if 'Squint' not in curve_objs:
        pm.warning('Squint curve does not exsist. Please create, label and attempt Build again.')
        return False
    if 'Nostril' not in curve_objs:
        pm.warning('Nostril curve does not exsist. Please create, label and attempt Build again.')
        return False
    if 'Laugh' not in curve_objs: 
        pm.warning('Laugh curve does not exsist. Please create, label and attempt Build again.')
        return False
    if 'Cheek' not in curve_objs:
        pm.warning('Cheek curve does not exsist. Please create, label and attempt Build again')
        return False
    if 'LowerLip' not in curve_objs:
        pm.warning('Lower Lip curve deos not exsist. Please create, label and attempt Build again.')
        return False
    if 'UpperLip' not in curve_objs:
        pm.warning('Upper Lip curve does not exsist. Please create, label and attempt Build again.')
        return False
    if 'UpperEyelid' not in curve_objs:
        pm.warning('Upper Eyelid curve does not exsist. Please create, label and attempt Build again.')
        return False
    if 'LowerEyelid' not in curve_objs:
        pm.warning('Lower Eyelid curve does not exsist. Please create, label and attempt Build again.')
        return False

def check_joints():
    joint_objs = []
    all_joints = pm.ls(type = 'joint')
    for joint in all_joints:
        if check_attr_exists(joint) == False:
            pm.warning(joint + ' does not have needed labels. Please use UI to label this joint or delete it if it is unnecessary.')
            return False
        ##grab obj label 
        obj_label = check_object(joint)
        ##append to list
        joint_objs.append(obj_label)
    ##check if all joint objects exsit
    if 'Head' not in joint_objs:
        pm.warning('Head joint does not exsist. Please create, label and attempt Build again')
        return False
    if 'Jaw' not in joint_objs:
        pm.warning('Jaw joint does not exsist. Please create, label and attempt Build again')
        return False
    if 'Neck' not in joint_objs:
        pm.warning('Neck joint does not exsist. Please create, label and attempt Build again')
        return False
    if 'Eye' not in joint_objs:
        pm.warning('Eye joint does not exsist. Please create, label and attempt Build again.')
        return False
    if 'LipParent' not in joint_objs:
        pm.warning('Lip Parent joint does not exsist. Please create, label and attempt Build again.')
        return False

def get_low_cvs(curve):
    if type(curve) == list:
        curve = curve[0]
    ##Grab child shape node
    curve_shapes = pm.listRelatives(curve, shapes = True)
    curve_shape = curve_shapes[0]
    ##create curve info node
    temp_curve_info = pm.shadingNode('curveInfo', asUtility=True)
    ##grab attributes for connection
    shape_worldSpace_attr = str(curve_shape) + '.worldSpace[0]'
    inputCurve_attr = str(temp_curve_info) + '.inputCurve'
    ##connect nodes
    pm.connectAttr(shape_worldSpace_attr, inputCurve_attr)
    ##grab last cv number
    last_cv = curve.cv[-1]
    last_cv_num = str(last_cv)[-2]
    ##grab y values of points points 0 and -1
    first_cv_attr = temp_curve_info + '.controlPoints[0].yValue'
    last_cv_attr = temp_curve_info + '.controlPoints[' + str(last_cv_num) + '].yValue'
    ##get values of attributes
    first_val = pm.getAttr(first_cv_attr)
    last_val = pm.getAttr(last_cv_attr)
    if first_val < last_val:
        pm.delete(temp_curve_info)
        return 'Zero'
    if last_val < first_val:
        pm.delete(temp_curve_info)
        return 'One'

def get_xPos_cvs(curve):
    if type(curve) == list:
        curve = curve[0]
    ##Grab child shape node
    curve_shapes = pm.listRelatives(curve, shapes = True)
    curve_shape = curve_shapes[0]
    ##create curve info node
    temp_curve_info = pm.shadingNode('curveInfo', asUtility=True)
    ##grab attributes for connection
    shape_worldSpace_attr = str(curve_shape) + '.worldSpace[0]'
    inputCurve_attr = str(temp_curve_info) + '.inputCurve'
    ##connect nodes
    pm.connectAttr(shape_worldSpace_attr, inputCurve_attr)
    ##grab last cv number
    last_cv = curve.cv[-1]
    last_cv_num = str(last_cv)[-2]
    ##grab y values of points points 0 and -1
    first_cv_attr = temp_curve_info + '.controlPoints[0].xValue'
    last_cv_attr = temp_curve_info + '.controlPoints[' + str(last_cv_num) + '].xValue'
    ##get values of attributes
    first_val = pm.getAttr(first_cv_attr)
    last_val = pm.getAttr(last_cv_attr)
    if first_val < last_val:
        pm.delete(temp_curve_info)
        return 'LowerHalf'
    if last_val < first_val:
        pm.delete(temp_curve_info)
        return 'UpperHalf'

def get_xNeg_cvs(curve):
    if type(curve) == list:
        curve = curve[0]
    ##Grab child shape node
    curve_shapes = pm.listRelatives(curve, shapes = True)
    curve_shape = curve_shapes[0]
    ##create curve info node
    temp_curve_info = pm.shadingNode('curveInfo', asUtility=True)
    ##grab attributes for connection
    shape_worldSpace_attr = str(curve_shape) + '.worldSpace[0]'
    inputCurve_attr = str(temp_curve_info) + '.inputCurve'
    ##connect nodes
    pm.connectAttr(shape_worldSpace_attr, inputCurve_attr)
    ##grab last cv number
    last_cv = curve.cv[-1]
    last_cv_num = str(last_cv)[-2]
    ##grab y values of points points 0 and -1
    first_cv_attr = temp_curve_info + '.controlPoints[0].xValue'
    last_cv_attr = temp_curve_info + '.controlPoints[' + str(last_cv_num) + '].xValue'
    ##get values of attributes
    first_val = pm.getAttr(first_cv_attr)
    last_val = pm.getAttr(last_cv_attr)
    if first_val < last_val:
        pm.delete(temp_curve_info)
        return (curve.cv[0:3])
    if last_val < first_val:
        pm.delete(temp_curve_info)
        return curve.cv[3:]

def reverse_list(og_list):
    reversed_list = []
    for item in reversed(og_list):
        reversed_list.append(item)
    return reversed_list

def clean_list_doops(og_list):
    resolved_list = []
    for item in og_list:
        if item not in resolved_list:
            resolved_list.append(item)
    return (resolved_list)

