
import pymel.core as pm
import maya.mel as mel
import OFR_attrEdits as ae
import OFR_materialSetup as ms

cyan = (0,1,1)
green = (0,1,0)
magenta = (1,0,1)
purple = (.5,0,1)
yellow = (1,1,0)
blue = (0,0,1)
red = (1,0,0)
orange = (1,.5,0)
##create colors for left and right
Red = ms.create_material('Red', red)
Blue = ms.create_material('Blue', blue)
Yellow = ms.create_material('Yellow', yellow)
Orange = ms.create_material('Orange', orange)
##create needed colors
cyan_mat = ms.create_material('Cyan', cyan)
magenta_mat = ms.create_material('Magenta', magenta)
def setRGBColor(ctrl, color):
    
    rgb = ("R","G","B")
    
    pm.setAttr(ctrl + ".overrideEnabled",1)
    pm.setAttr(ctrl + ".overrideRGBColors",1)
    
    for channel, color in zip(rgb, color):
        
        pm.setAttr(ctrl + ".overrideColor%s" %channel, color)

def snap_to_pivot(source, targets):
    pivot = pm.xform(source, query=True, worldSpace=True, scalePivot=True)
    for tar in targets:
        pm.xform(tar, worldSpace=True, pivots=pivot)
        
def mirror_curves():
    ##create curve transform list
    transform_list = []
    ##grab all curves
    all_curves = pm.ls(type='nurbsCurve')
    ##grab the objects parent, the transform
    for each in all_curves:
        transform = pm.listRelatives(each, parent=True)
        if ae.check_side == 'Right' or 'Left':
            transform_list.append(transform)
    transform_list = ae.clean_list_doops(transform_list)
    ##duplicate the transfrom_list
    doops = pm.duplicate(transform_list)
    ##create an empty group
    trans_temp = pm.group(empty=True,name='TransformTemp')
    ##parent all doop curve transforms under the new temp parent
    pm.parent(doops, trans_temp)
    ##scale the trans temp to "mirror"
    trans_temp.attr('scaleX').set(-1)
    ##reparent all the curves to the world
    pm.parent(doops, world=True)
    ##delete the temp trans
    pm.delete(trans_temp)
    for doop in doops:
        ##grab the side lable attribute
        side_attr = doop + '.SideLabel'
        ##unlock the attr
        pm.setAttr(side_attr, lock=False)
        ##if left, rename right and vice versa
        if ae.check_side(doop)=='Right':
            pm.setAttr(side_attr, 'Left')
        if ae.check_side(doop)=='Left':
            pm.setAttr(side_attr, 'Right')
        ##relock attr
        pm.setAttr(side_attr, lock=True)
    ##return the curves parent for later use
    return 

def mirror_eye():
    ##search all joints for object labeled with Eye_jnt
    all_joints = pm.ls(type='joint')
    ##search over all joints
    for joint in all_joints:
        ##Create object attribute name
        #obj_attr = joint + '.ObjectLabel'
        ##check if object attribute == Eye_jnt
        if ae.check_object(joint) == 'Eye':
            new_joint = pm.duplicate(joint)
            if type(new_joint) == list:
                new_joint = new_joint[0]
            ##grab new side attr and X trans
            new_joint_side_attr = new_joint + '.SideLabel'
            ##unlock new joint side label attr
            pm.setAttr(new_joint_side_attr, lock=False)
            ##check and flip to correct side
            if ae.check_side(joint) == 'Left':
                pm.setAttr(new_joint_side_attr, 'Right')
            if ae.check_side(joint) == 'Right':
                pm.setAttr(new_joint_side_attr, 'Left')
            ##relock side attr
            pm.setAttr(new_joint_side_attr, lock=True)
            ##move joint to correct side through translate x
            ##crete the attribute name
            new_joint_transX = new_joint + '.translateX'
            ##get value
            xval = pm.getAttr(new_joint_transX)
            ##create new xval
            new_xval = float(xval) * -1
            ##set the new joints trans x to the new x val
            pm.setAttr(new_joint_transX, new_xval)

def create_lipParents():
    all_joints= pm.ls(type='joint')
    for joint in all_joints:
        if ae.check_object(joint) == 'LipParent':
            lowerLip = pm.duplicate(joint)
            if type(lowerLip) == list:
                lowerLip = lowerLip[0]
            ae.replace_labels(lowerLip, 'Center', 'LowerLipParent', 'jnt')
            ae.replace_labels(joint, 'Center', 'UpperLipParent', 'jnt')

def organize_joints():
    ##create joitn group
    joint_grp = pm.group(empty=True, name='BaseJoints_grp')
    ##label them
    ae.create_labels(joint_grp, 'NA', 'BaseJoints', 'base_grp')
    #pm.setAttr(str(joint_grp)+'.visibility', 0)
    ##eye joints
    eye_joints = []
    ##get joints
    joints = pm.ls(type='joint')
    ##loop through and grab each one
    for joint in joints:
        if ae.check_object(joint) == 'Neck':
            neck = joint
        if ae.check_object(joint) == 'Head':
            head = joint
        if ae.check_object(joint) == 'UpperLipParent':
            UpperLipParent = joint
        if ae.check_object(joint) == 'LowerLipParent':
            LowerLipParent = joint
        if ae.check_object(joint) == 'Jaw':
            jaw = joint
        if ae.check_object(joint) == 'Eye':
            eye_joints.append(joint)
    pm.select(clear=True)
    ##create root
    root = pm.joint(name='root')
    ae.create_labels(root, 'Center', 'Root', 'jnt')
    ##parent things the way needed
    pm.parent(neck, root)
    pm.parent(head, neck)
    pm.parent(jaw, head)
    pm.parent(UpperLipParent, head)
    pm.parent(LowerLipParent, jaw)
    pm.parent(root, joint_grp)
    pm.parent(eye_joints, head)
    return joint_grp

def organize_curves():
    curve_grp = pm.group(empty=True, name='BaseCurves_grp')
    ae.create_labels(curve_grp, 'NA', 'BaseCurves', 'base_grp')
    pm.setAttr(str(curve_grp)+'.visibility',0)
    ##list curves
    curve_trans =[]
    curves = pm.ls(type='nurbsCurve')
    for curve in curves:
        trans = pm.listRelatives(curve, parent=True)
        curve_trans.append(trans)
    curve_trans = ae.clean_list_doops(curve_trans)
    pm.parent(curve_trans, curve_grp)
    return curve_grp

def organize_meshes():
    mesh_grp = pm.group(empty=True, name='BaseMeshes_grp')
    ae.create_labels(mesh_grp, 'NA', 'BaseMeshes', 'base_grp')
    mesh_trans = []
    meshes = pm.ls(type='mesh')
    for mesh in meshes:
        trans = pm.listRelatives(mesh, parent=True)
        mesh_trans.append(trans)
    mesh_trans = ae.clean_list_doops(mesh_trans)
    pm.parent(mesh_trans, mesh_grp)
    return mesh_grp
                
def create_lip_curves():
    ##upper lip list
    upper_lip_curves = []
    ##lower lip list
    lower_lip_curves = []
    ##serch though all curves
    all_curves = pm.ls(type='nurbsCurve')
    ##iterate over curves
    for curve in all_curves:
        ##extract curve transform parent
        curve_trans = pm.listRelatives(curve, parent=True)
        ##extract node
        curve_trans = curve_trans[0]
        ##if upper lip add to upper lip
        if ae.check_object(curve_trans) == 'UpperLip':
            upper_lip_curves.append(curve_trans)
        ##if lower lip add to lower lip
        if ae.check_object(curve_trans) == 'LowerLip':
            lower_lip_curves.append(curve_trans)
    curve_trans = ae.clean_list_doops(curve_trans)
    ##attach the upper lip curves
    new_upper_lip = pm.attachCurve(upper_lip_curves[0], upper_lip_curves[1], method=1, replaceOriginal=0)
    ##delete original curves
    pm.delete(upper_lip_curves)
    ##label the new curve
    ae.create_labels(new_upper_lip, 'Center', 'UpperLip', 'curve')
    ##attach lower lip curves
    new_lower_lip = pm.attachCurve(lower_lip_curves[0], lower_lip_curves[1], method=1, replaceOriginal=0)
    ##delete original curves
    pm.delete(lower_lip_curves)
    ##label new lower lip curve
    ae.create_labels(new_lower_lip, 'Center', 'LowerLip', 'curve')

'''##possibly build a function to rebuild curves as desired.
##Rework labels for Object to match if it is an end, mid, or start '''     
def create_motionPath_groups(curves_list):
    ##grab start and end of timeframe for motionpaths
    startTime = pm.playbackOptions(query=True, minTime=True)
    endTime = pm.playbackOptions(query=True, maxTime=True)
    ##make an empty list to output all groups and all parent groups
    parent_groups=[]
    motionPath_groups=[]
    ##loop through all face curves
    for f_curve in curves_list:
        if type(f_curve) == list:
            f_curve = f_curve[0]
        ##if the path is a lip path, then build motionpaths and groups for 5 positions
        if ae.check_object(f_curve) == 'UpperLip':
            ##rebuild to be desired
            pm.rebuildCurve(f_curve, rebuildType=0, degree=2, spans=5)
            ##grab object label
            obj_label = ae.check_object(f_curve)
            ##create an organizational parent group
            parent_grp_name = f_curve.name() + '_elements_grp'
            parent_grp = pm.group(empty=True, name=parent_grp_name)
            ##label parent
            curve_side = ae.check_side(f_curve)
            obj = ae.check_object(f_curve)
            ae.create_labels(parent_grp, curve_side, obj, 'elements_grp')
            parent_groups.append(parent_grp)
            for x in range (0,7):
                ##for each iteration create a new name and UValue position, and label
                if x == 0:
                    grp_name = f_curve.name() + '_outer_motionPath_grp' 
                    UValue = 0 
                    new_obj_label = obj_label + '_outer_follow'
                if x == 1:
                    grp_name = f_curve.name() + '_inner_A_motionPath_grp' 
                    UValue = .1675
                    new_obj_label = obj_label + '_inner_A_follow'
                if x == 2:
                    grp_name = f_curve.name() + '_inner_B_motionPath_grp' 
                    UValue = .335  
                    new_obj_label = obj_label + '_inner_B_follow'
                if x == 3:
                    grp_name = f_curve.name() + '_mid_motionPath_grp' 
                    UValue = .5 
                    new_obj_label = obj_label + '_mid_follow'
                if x == 4:
                    grp_name = f_curve.name() + '_inner_B_motionPath_grp' 
                    UValue = .665  
                    new_obj_label = obj_label + '_inner_B_follow'
                if x == 5:
                    grp_name = f_curve.name() + '_inner_A_motionPath_grp' 
                    UValue = .8325
                    new_obj_label = obj_label + '_inner_A_follow'
                if x == 6:
                    grp_name = f_curve.name() + '_outer_motionPath_grp' 
                    UValue = 1
                    new_obj_label = obj_label + '_outer_follow'
                path_name = grp_name.replace('_grp','')
                new_group = pm.group(empty=True, name=grp_name)
                motionPath = pm.pathAnimation(new_group, c=f_curve, name=path_name, follow=True, fractionMode=True, followAxis='z', upAxis='y', startTimeU=startTime, endTimeU=endTime)
                UVAttr = motionPath + '.u' 
                pm.disconnectAttr(UVAttr)
                pm.setAttr(UVAttr, UValue)
                ##determine the side for the newly created group
                side = ae.determine_side(new_group)
                ##label the new group
                ae.create_labels(new_group, side, new_obj_label, 'motionPath_grp')
                ##parent new motion path group under organizational parent
                pm.parent(new_group, parent_grp)
                ##append motionpath group
                motionPath_groups.append(new_group)
        ##if the path is a lip path, then build motionpaths and groups for 5 positions
        if ae.check_object(f_curve) == 'LowerLip':
            ##rebuild to be desired
            pm.rebuildCurve(f_curve, rebuildType=0, degree=2, spans=5)
            ##grab object label
            obj_label = ae.check_object(f_curve)
            ##create an organizational parent group
            parent_grp_name = f_curve.name() + '_elements_grp'
            parent_grp = pm.group(empty=True, name=parent_grp_name)
            ##label parent
            curve_side = ae.check_side(f_curve)
            obj = ae.check_object(f_curve)
            ae.create_labels(parent_grp, curve_side, obj, 'elements_grp')
            parent_groups.append(parent_grp)
            for x in range (0,7):
                ##for each iteration create a new name and UValue position, and label
                if x == 0:
                    grp_name = f_curve.name() + '_outer_motionPath_grp' 
                    UValue = 0 
                    new_obj_label = obj_label + '_outer_follow'
                if x == 1:
                    grp_name = f_curve.name() + '_inner_A_motionPath_grp' 
                    UValue = .1675
                    new_obj_label = obj_label + '_inner_A_follow'
                if x == 2:
                    grp_name = f_curve.name() + '_inner_B_motionPath_grp' 
                    UValue = .335  
                    new_obj_label = obj_label + '_inner_B_follow'
                if x == 3:
                    grp_name = f_curve.name() + '_mid_motionPath_grp' 
                    UValue = .5 
                    new_obj_label = obj_label + '_mid_follow'
                if x == 4:
                    grp_name = f_curve.name() + '_inner_B_motionPath_grp' 
                    UValue = .665  
                    new_obj_label = obj_label + '_inner_B_follow'
                if x == 5:
                    grp_name = f_curve.name() + '_inner_A_motionPath_grp' 
                    UValue = .8325
                    new_obj_label = obj_label + '_inner_A_follow'
                if x == 6:
                    grp_name = f_curve.name() + '_outer_motionPath_grp' 
                    UValue = 1
                    new_obj_label = obj_label + '_outer_follow'
                path_name = grp_name.replace('_grp','')
                new_group = pm.group(empty=True, name=grp_name)
                motionPath = pm.pathAnimation(new_group, c=f_curve, name=path_name, follow=True, fractionMode=True, followAxis='z', upAxis='y', startTimeU=startTime, endTimeU=endTime)
                UVAttr = motionPath + '.u' 
                pm.disconnectAttr(UVAttr)
                pm.setAttr(UVAttr, UValue)
                ##determine the side for the newly created group
                side = ae.determine_side(new_group)
                ##label the new group
                ae.create_labels(new_group, side, new_obj_label, 'motionPath_grp')
                ##parent new motion path group under organizational parent
                pm.parent(new_group, parent_grp)
                ##append motionpath group
                motionPath_groups.append(new_group)
        if ae.check_object(f_curve) == 'Nostril':
            ##for all curves that are not nostril or lips, create three groups/motionpaths
            ##rebuild to be desired
            pm.rebuildCurve(f_curve, rebuildType=0, degree=2, spans=3)
            ##create an organizational parent group
            parent_grp_name = f_curve.name() + '_elements_grp'
            parent_grp = pm.group(empty=True, name=parent_grp_name)
            ##label parent
            curve_side = ae.check_side(f_curve)
            obj = ae.check_object(f_curve)
            ae.create_labels(parent_grp, curve_side, obj, 'elements_grp')
            parent_groups.append(parent_grp)
            ##grab object and side label from curve
            obj_label = ae.check_object(f_curve)
            side = ae.check_side(f_curve)
            for x in range (0,3):
                if x == 0:
                    grp_name = f_curve.name() + '_start_grp'
                    UValue = 0
                    new_obj_label = obj_label + '_start_follow'
                if x == 1:
                    grp_name = f_curve.name() + '_mid_grp'
                    UValue = .5          
                    new_obj_label = obj_label + '_mid_follow'
                if x == 2:
                    grp_name = f_curve.name() + '_end_grp'
                    UValue = 1          
                    new_obj_label = obj_label + '_end_follow'
                path_name = grp_name.replace('_grp','_motionPath')
                new_group = pm.group(empty=True, name=grp_name)
                motionPath = pm.pathAnimation(new_group, c=f_curve, name=path_name, follow=True, fractionMode=True, followAxis='z', upAxis='y', startTimeU=startTime, endTimeU=endTime)
                UVAttr = motionPath + '.u' 
                pm.disconnectAttr(UVAttr)
                pm.setAttr(UVAttr, UValue)
                ##create labels for new object
                ae.create_labels(new_group, side, new_obj_label, 'motionPath_grp')
                ##parent new motion path group under organizational parent
                pm.parent(new_group, parent_grp)
                ##append motionpath group                
                motionPath_groups.append(new_group)      
        if ae.check_side(f_curve) != 'Center' and ae.check_object(f_curve) != 'Nostril':
            ##for all curves that are not nostril or lips, create three groups/motionpaths
            ##rebuild to be desired
            pm.rebuildCurve(f_curve, rebuildType=0, degree=2, spans=3)
            ##create an organizational parent group
            parent_grp_name = f_curve.name() + '_elements_grp'
            parent_grp = pm.group(empty=True, name=parent_grp_name)
            ##label parent
            curve_side = ae.check_side(f_curve)
            obj = ae.check_object(f_curve)
            ae.create_labels(parent_grp, curve_side, obj, 'elements_grp')
            parent_groups.append(parent_grp)
            ##grab object and side label from curve
            obj_label = ae.check_object(f_curve)
            side = ae.check_side(f_curve)
            for x in range (0,5):
                if x == 0:
                    grp_name = f_curve.name() + '_start_grp'
                    UValue = 0
                    new_obj_label = obj_label + '_start_follow'
                if x == 1:
                    grp_name = f_curve.name() + '_lower_mid_grp'
                    UValue = .25 
                    new_obj_label = obj_label + '_lower_mid_follow'
                if x == 2:
                    grp_name = f_curve.name() + '_mid_grp'
                    UValue = .5          
                    new_obj_label = obj_label + '_mid_follow'
                if x == 3:
                    grp_name = f_curve.name() + '_upper_mid_grp'
                    UValue = .75 
                    new_obj_label = obj_label + '_upper_mid_follow'
                if x == 4:
                    grp_name = f_curve.name() + '_end_grp'
                    UValue = 1          
                    new_obj_label = obj_label + '_end_follow'
                path_name = grp_name.replace('_grp','_motionPath')
                new_group = pm.group(empty=True, name=grp_name)
                motionPath = pm.pathAnimation(new_group, c=f_curve, name=path_name, follow=True, fractionMode=True, followAxis='z', upAxis='y', startTimeU=startTime, endTimeU=endTime)
                UVAttr = motionPath + '.u' 
                pm.disconnectAttr(UVAttr)
                pm.setAttr(UVAttr, UValue)
                ##create labels for new object
                ae.create_labels(new_group, side, new_obj_label, 'motionPath_grp')
                ##parent new motion path group under organizational parent
                pm.parent(new_group, parent_grp)
                ##append motionpath group                
                motionPath_groups.append(new_group)
                  
    return parent_groups

def create_detail_ctrls(node_list):
    #print (node_list)
    ##list for ctrls to be added to and for the trans groups to be added to
    trans_list=[]
    ctrl_list = []
    for each in node_list:
        ##create unique joint name based off of object name
        #print (each)
        grp_name = each.name().replace('_grp','_trans')
        auto_name = each.name().replace('_grp','_auto')
        ctrl_name = each.name().replace('_grp','_ctrl')
        ##create new group and control shape
        new_grp = pm.group(empty=True, name=grp_name)
        auto_grp = pm.group(empty=True, name=auto_name)
        ctrl_shape = pm.sphere(radius=.125, name=ctrl_name)
        ##append ctrl to list
        ctrl_list.append(ctrl_shape)        
        ##move the cvs (apearance) of sphere forward to eventually offset from mesh.
        ctrl_shape = ctrl_shape[0]
        pm.move(0,0,.25, ctrl_shape.cv[0:6], relative=True, wd=True)  
        ##change line colour 
        setRGBColor(ctrl_shape, cyan)
        ##parent ctrl to group
        pm.parent(ctrl_shape, auto_grp)
        pm.parent(auto_grp, new_grp)
        ##constrain the new control to our group from the input list
        constraint = pm.pointConstraint(each, new_grp)
        ##now that ctrl is in correct location, delete constraint
        #pm.delete(constraint)
        ##correct position, no constraint, reparent under object from input list
        #pm.parent(new_grp, each) 
        trans_list.append(new_grp)
        ##create labels for everything
        side = ae.check_side(each)
        obj = ae.check_object(each)
        ae.create_labels(new_grp, side, obj, 'trans_grp')
        ae.create_labels(auto_grp, side, obj, 'detail_auto_grp')
        ae.create_labels(ctrl_shape, side, obj, 'detail_ctrl')
    return (trans_list, ctrl_list)

def create_atLoc_joints(node_list):
    ##create a list to append joints to
    joint_list=[]
    ##create a joint and constrain to control for each control given
    for each in node_list:
        if type(each) == list:
            each = each[0]
        pm.select(clear=True)
        joint_name = str(each)+'_jnt'
        new_joint = pm.joint(name=joint_name, radius=0.2)
        ##constrain joint to ctrl
        point_const = pm.pointConstraint(each, new_joint)
        orient_const = pm.orientConstraint(each, new_joint)
        ##append joint to joint list
        joint_list.append(new_joint)
        ##create labels
        side = ae.check_side(each)
        obj = ae.check_object(each)
        ae.create_labels(new_joint, side, obj, 'detail_jnt')
        ##clear selection to avoid joint parenting.
        pm.select(clear=True)
    return (joint_list)

def create_clusters_ctrls(curves_list):
    ##create cluster parent for organization
    clusterCtrls_parent = pm.group(empty=True, name='clusterCtrls_parent')
    ae.create_labels(clusterCtrls_parent, 'NA', 'clusterCtrls', 'parent_grp')
    cluster_parent = pm.group(empty = True, name = 'clusters_parent')
    ae.create_labels(cluster_parent, 'NA', 'clusters', 'parent_grp')
    pm.setAttr(str(cluster_parent) + '.visibility', 0)
    lip_point_parent = pm.group(empty=True, name='lipPointGroups_parent')
    ae.create_labels(lip_point_parent, 'NA', 'lipPoints', 'parent_grp')
    ##create list for ctrls 
    cluster_ctrls = []
    ##loop over curve list
    for curve in curves_list:
        ##find lip parents
        all_joints = pm.ls(type='joint')
        for joint in all_joints:
            if ae.check_object(joint) == 'UpperLipParent':
                upperLipParent = joint
            if ae.check_object(joint) == 'LowerLipParent':
                lowerLipParent = joint
            if ae.check_object(joint) == 'Eye':
                if ae.check_side(joint) == 'Right':
                    right_eye = joint
                if ae.check_side(joint) == 'Left':
                    left_eye = joint
        ##grab label info
        obj = ae.check_object(curve)
        ##grab the shape
        shape = ms.check_transform(curve)
        ##create variable for counting
        count = 0
        ##loop over all CVs in the given curve
        if ae.check_object(curve) == 'LowerLip':
            for cv in shape.cv[:]:
                ##add one to the count for naming purposes
                count += 1
                if type(curve) == list:
                    curve = curve[0]
                ##create cluster name and cluster on cv
                cluster_name = curve + '_cluster' + str(count)
                cluster = pm.cluster(cv, name=cluster_name)
                cluster_handle = cluster[1]
                side = ae.determine_side(cluster_handle)
                ae.create_labels(cluster, side, obj, 'cluster')
                ae.create_labels(cluster_handle, side, obj, 'cluster')
                ##create some joints for the purpose of orientation. 
                doop_jnt = pm.duplicate(lowerLipParent)
                end_jnt = pm.joint(name='temp')
                ##place end joint at cluster
                pm.matchTransform(end_jnt, cluster)
                pm.parent(end_jnt, doop_jnt)
                pm.joint(doop_jnt, edit=True, orientJoint='zyx', secondaryAxisOrient= 'yup', zeroScaleOrient=True)
                ##place controls and snap pivot to doop joint
                ##create control groups and cube control and name them all and label
                trans_name = curve + '_cluster' + str(count) + '_trans' 
                trans_grp = pm.group(empty=True, name = trans_name)
                ae.create_labels(trans_grp, side, obj+'_cluster'+str(count), 'trans_grp')
                auto_name = curve + '_cluster' + str(count) + '_auto'
                auto_grp = pm.group(empty=True, name = auto_name)
                ae.create_labels(auto_grp, side, obj+'_cluster'+str(count), 'auto_grp')
                auto2_name = curve + '_cluster' + str(count) + '_specialAuto'
                auto2_grp = pm.group(empty=True, name = auto2_name)
                ae.create_labels(auto2_grp, side, obj+'_cluster'+str(count), 'special_auto_grp')
                cube_name = curve + '_cluster' + str(count) + '_ctrl'
                cube = pm.polyCube(name=cube_name, height=.25, width=.25, depth=.25)
                ae.create_labels(cube, side, obj+'_cluster'+str(count), 'cluster_ctrl')
                ##now we need to create some offset groups to allow our cluster controls to follow the second face curves
                point_trans_name = curve + '_cluster' + str(count) + '_pointTrans' 
                point_trans_grp = pm.group(empty=True, name = point_trans_name)
                ae.create_labels(point_trans_grp, side, obj+'_cluster'+str(count), 'trans_grp')
                point_offset_name = curve + '_cluster' + str(count) + '_offset' 
                point_offset_grp = pm.group(empty=True, name = point_offset_name)
                ae.create_labels(point_offset_grp, side, obj+'_cluster'+str(count), 'point_grp')
                ##parent control elements correctly
                pm.parent(point_offset_grp, point_trans_grp)
                pm.parent(auto_grp, trans_grp)
                pm.parent(auto2_grp, auto_grp)
                pm.parent(cube, auto2_grp)
                ##constrain control to the cluster to move it to correct place
                constraint = pm.parentConstraint(doop_jnt, trans_grp)
                ##delete constraint
                pm.delete(constraint)
                ##point constraint to end joint
                constraintB = pm.pointConstraint(end_jnt, trans_grp)
                pm.delete(constraintB)
                ##move the offset and trans groups to end joint
                constraintC = pm.pointConstraint(end_jnt, point_trans_grp)
                pm.delete(constraintC)
                ##create some offset groups for the cluster
                cluster_trans = pm.group(empty=True, name= str(cluster_handle)+'_trans')
                cluster_auto = pm.group(empty=True, name=str(cluster_handle)+'_auto')
                pm.parent(cluster_auto, cluster_trans)
                pm.matchTransform(cluster_trans, doop_jnt)
                pm.parent(cluster, cluster_auto)
                ##snap the pivot to the doop
                snap_to_pivot(doop_jnt, [trans_grp, auto_grp, auto2_grp, cube, cluster_auto, cluster_trans])
                ##parent constriang the trans group to the pivot joint source
                pm.pointConstraint(lowerLipParent, trans_grp, mo=True)
                ##createconstraints
                pm.parentConstraint(cube, cluster_trans)
                pm.aimConstraint(point_offset_grp, auto_grp, maintainOffset=True, aimVector=(0,0,1), upVector=(0,1,0), worldUpType = 'vector', worldUpVector=(0,1,0))
                pm.pointConstraint(point_offset_grp, auto2_grp, maintainOffset=True)
                ##create multiply divide node
                multiDiv = pm.shadingNode('multiplyDivide', asUtility=True, name=obj+'_cluster'+str(count)+ '_multiDiv')
                ae.create_labels(multiDiv, side, obj+'_cluster'+str(count), 'multiDiv')
                plus_min = pm.shadingNode('plusMinusAverage', asUtility=True, name=obj+'_cluster'+str(count)+ '_plusMin')
                ae.create_labels(plus_min, side, obj+'_cluster'+str(count), 'plusMin')
                condition = pm.shadingNode('condition', asUtility = True, name=obj+'_cluster'+str(count)+ '_condition')
                negMulti = pm.shadingNode('multiplyDivide', asUtility=True, name=obj+'_cluster'+str(count)+ '_negMulti')
                ##grabing attributes
                ctrl_rotY = cube[0] + '.rotateY'
                multi_input1X = str(multiDiv) + '.input1X'
                multi_input2X = str(multiDiv) + '.input2X'
                multi_input1Y = str(multiDiv) + '.input1Y'
                multi_input2Y = str(multiDiv) + '.input2Y'
                multi_outputX = str(multiDiv) + '.outputX'
                multi_outputY = str(multiDiv) + '.outputY'
                cluster_auto_tranZ = str(cluster_auto) + '.translateZ'
                plus_inX = str(plus_min) + '.input1D[0]'
                plus_inY = str(plus_min) + '.input1D[1]'
                plus_out = str(plus_min) + '.output1D'
                negMulti_in1X = str(negMulti) + '.input1X'
                negMulti_in2X = str(negMulti) + '.input2X'
                negMulti_output = str(negMulti) + '.outputX'
                condition_false = str(condition) + '.colorIfFalseR'
                condition_true = str(condition) + '.colorIfTrueR'
                condition_first = str(condition) + '.firstTerm'
                condition_output = str(condition) + '.outColorR'
                condition_operation = str(condition) + '.operation'
                """ COME BACK AND ADD A FUNCTION FOR USER TO CHANGE THIS AMOUNT"""
                pm.setAttr(multi_input2X, -.015)
                pm.setAttr(multi_input2Y, -.015)
                pm.setAttr(negMulti_in2X, -1)
                pm.setAttr(condition_operation, 2)
                ##connect attributes
                pm.connectAttr(ctrl_rotY, multi_input1X)
                pm.connectAttr(multi_outputX, plus_inX)
                pm.connectAttr(multi_outputY, plus_inY)
                pm.connectAttr(plus_out, negMulti_in1X)
                pm.connectAttr(negMulti_output, condition_true)
                pm.connectAttr(plus_out, condition_false)
                pm.connectAttr(plus_out, condition_first)
                pm.connectAttr(condition_output, cluster_auto_tranZ)
                ##delete joints
                pm.delete(doop_jnt)
                ##parent controls under parent
                pm.parent(trans_grp, clusterCtrls_parent)
                pm.parent(cluster_trans, cluster_parent)
                pm.parent(point_trans_grp, lip_point_parent)
                ##append cluster controls
                cluster_ctrls.append(cube)
            continue
        if ae.check_object(curve) == 'UpperLip':
            for cv in shape.cv[:]:
                ##add one to the count for naming purposes
                count += 1
                if type(curve) == list:
                    curve = curve[0]
                ##create cluster name and cluster on cv
                cluster_name = curve + '_cluster' + str(count)
                cluster = pm.cluster(cv, name=cluster_name)
                cluster_handle = cluster[1]
                side = ae.determine_side(cluster_handle)
                ae.create_labels(cluster, side, obj, 'cluster')
                ae.create_labels(cluster_handle, side, obj, 'cluster')
                ##create some joints for the purpose of orientation. 
                doop_jnt = pm.duplicate(upperLipParent)
                end_jnt = pm.joint(name='temp')
                ##place end joint at cluster
                pm.matchTransform(end_jnt, cluster)
                pm.parent(end_jnt, doop_jnt)
                pm.joint(doop_jnt, edit=True, orientJoint='zyx', secondaryAxisOrient= 'yup', zeroScaleOrient=True)
                ##place controls and snap pivot to doop joint
                ##create control groups and cube control and name them all and label
                trans_name = curve + '_cluster' + str(count) + '_trans' 
                trans_grp = pm.group(empty=True, name = trans_name)
                ae.create_labels(trans_grp, side, obj+'_cluster'+str(count), 'trans_grp')
                auto_name = curve + '_cluster' + str(count) + '_auto'
                auto_grp = pm.group(empty=True, name = auto_name)
                ae.create_labels(auto_grp, side, obj+'_cluster'+str(count), 'auto_grp')
                auto2_name = curve + '_cluster' + str(count) + '_specialAuto'
                auto2_grp = pm.group(empty=True, name = auto2_name)
                ae.create_labels(auto2_grp, side, obj+'_cluster'+str(count), 'special_auto_grp')
                cube_name = curve + '_cluster' + str(count) + '_ctrl'
                cube = pm.polyCube(name=cube_name, height=.25, width=.25, depth=.25)
                ae.create_labels(cube, side, obj+'_cluster'+str(count), 'cluster_ctrl')
                ##now we need to create some offset groups to allow our cluster controls to follow the second face curves
                point_trans_name = curve + '_cluster' + str(count) + '_pointTrans' 
                point_trans_grp = pm.group(empty=True, name = point_trans_name)
                ae.create_labels(point_trans_grp, side, obj+'_cluster'+str(count), 'trans_grp')
                point_offset_name = curve + '_cluster' + str(count) + '_offset' 
                point_offset_grp = pm.group(empty=True, name = point_offset_name)
                ae.create_labels(point_offset_grp, side, obj+'_cluster'+str(count), 'point_grp')
                ##parent control elements correctly
                pm.parent(point_offset_grp, point_trans_grp)
                pm.parent(auto_grp, trans_grp)
                pm.parent(auto2_grp, auto_grp)
                pm.parent(cube, auto2_grp)
                ##constrain control to the cluster to move it to correct place
                constraint = pm.parentConstraint(doop_jnt, trans_grp)
                ##delete constraint
                pm.delete(constraint)
                ##point constraint to end joint
                constraintB = pm.pointConstraint(end_jnt, trans_grp)
                pm.delete(constraintB)
                ##move the offset and trans groups to end joint
                constraintC = pm.pointConstraint(end_jnt, point_trans_grp)
                pm.delete(constraintC)
                ##create some offset groups for the cluster
                cluster_trans = pm.group(empty=True, name= str(cluster_handle)+'_trans')
                cluster_auto = pm.group(empty=True, name=str(cluster_handle)+'_auto')
                pm.parent(cluster_auto, cluster_trans)
                pm.matchTransform(cluster_trans, doop_jnt)
                pm.parent(cluster, cluster_auto)
                ##snap the pivot to the doop
                snap_to_pivot(doop_jnt, [trans_grp, auto_grp, auto2_grp, cube, cluster_auto, cluster_trans])
                ##parent constriang the trans group to the pivot joint source
                pm.pointConstraint(upperLipParent, trans_grp, mo=True)
                ##createconstraints
                pm.parentConstraint(cube, cluster_trans)
                pm.aimConstraint(point_offset_grp, auto_grp, maintainOffset=True, aimVector=(0,0,1), upVector=(0,1,0), worldUpType = 'vector', worldUpVector=(0,1,0))
                pm.pointConstraint(point_offset_grp, auto2_grp, maintainOffset=True)
                ##create multiply divide node
                multiDiv = pm.shadingNode('multiplyDivide', asUtility=True, name=obj+'_cluster'+str(count)+ '_multiDiv')
                ae.create_labels(multiDiv, side, obj+'_cluster'+str(count), 'multiDiv')
                plus_min = pm.shadingNode('plusMinusAverage', asUtility=True, name=obj+'_cluster'+str(count)+ '_plusMin')
                ae.create_labels(plus_min, side, obj+'_cluster'+str(count), 'plusMin')
                condition = pm.shadingNode('condition', asUtility = True, name=obj+'_cluster'+str(count)+ '_condition')
                negMulti = pm.shadingNode('multiplyDivide', asUtility=True, name=obj+'_cluster'+str(count)+ '_negMulti')
                ##grabing attributes
                ctrl_rotY = cube[0] + '.rotateY'
                multi_input1X = str(multiDiv) + '.input1X'
                multi_input2X = str(multiDiv) + '.input2X'
                multi_input1Y = str(multiDiv) + '.input1Y'
                multi_input2Y = str(multiDiv) + '.input2Y'
                multi_outputX = str(multiDiv) + '.outputX'
                multi_outputY = str(multiDiv) + '.outputY'
                cluster_auto_tranZ = str(cluster_auto) + '.translateZ'
                plus_inX = str(plus_min) + '.input1D[0]'
                plus_inY = str(plus_min) + '.input1D[1]'
                plus_out = str(plus_min) + '.output1D'
                negMulti_in1X = str(negMulti) + '.input1X'
                negMulti_in2X = str(negMulti) + '.input2X'
                negMulti_output = str(negMulti) + '.outputX'
                condition_false = str(condition) + '.colorIfFalseR'
                condition_true = str(condition) + '.colorIfTrueR'
                condition_first = str(condition) + '.firstTerm'
                condition_output = str(condition) + '.outColorR'
                condition_operation = str(condition) + '.operation'
                """ COME BACK AND ADD A FUNCTION FOR USER TO CHANGE THIS AMOUNT"""
                pm.setAttr(multi_input2X, -.015)
                pm.setAttr(multi_input2Y, -.015)
                pm.setAttr(negMulti_in2X, -1)
                pm.setAttr(condition_operation, 2)
                ##connect attributes
                pm.connectAttr(ctrl_rotY, multi_input1X)
                pm.connectAttr(multi_outputX, plus_inX)
                pm.connectAttr(multi_outputY, plus_inY)
                pm.connectAttr(plus_out, negMulti_in1X)
                pm.connectAttr(negMulti_output, condition_true)
                pm.connectAttr(plus_out, condition_false)
                pm.connectAttr(plus_out, condition_first)
                pm.connectAttr(condition_output, cluster_auto_tranZ)
                ##delete joints
                pm.delete(doop_jnt)
                ##parent controls under parent
                pm.parent(trans_grp, clusterCtrls_parent)
                pm.parent(cluster_trans, cluster_parent)
                pm.parent(point_trans_grp, lip_point_parent)
                ##append cluster controls
                cluster_ctrls.append(cube)
            continue
        if ae.check_object(curve) == 'UpperEyelid':
            for cv in shape.cv[:]:
                ##add one to the count for naming purposes
                count += 1
                if type(curve) == list:
                    curve = curve[0]
                ##create cluster name and cluster on cv
                cluster_name = curve + '_cluster' + str(count)
                cluster = pm.cluster(cv, name=cluster_name)
                cluster_handle = cluster[1]
                side = ae.determine_side(cluster_handle)
                if side == 'Right':
                    eye_jnt = right_eye
                if side == 'Left':
                    eye_jnt = left_eye
                ae.create_labels(cluster, side, obj, 'cluster')
                ae.create_labels(cluster_handle, side, obj, 'cluster')
                ##create some joints for the purpose of orientation. 
                doop_jnt = pm.duplicate(eye_jnt)
                end_jnt = pm.joint(name='temp')
                ##place end joint at cluster
                pm.matchTransform(end_jnt, cluster)
                pm.parent(end_jnt, doop_jnt)
                pm.joint(doop_jnt, edit=True, orientJoint='zyx', secondaryAxisOrient= 'yup', zeroScaleOrient=True)
                ##place controls and snap pivot to doop joint
                ##create control groups and cube control and name them all and label
                trans_name = curve + '_cluster' + str(count) + '_trans' 
                trans_grp = pm.group(empty=True, name = trans_name)
                ae.create_labels(trans_grp, side, obj+'_cluster'+str(count), 'trans_grp')
                auto_name = curve + '_cluster' + str(count) + '_auto'
                auto_grp = pm.group(empty=True, name = auto_name)
                ae.create_labels(auto_grp, side, obj+'_cluster'+str(count), 'auto_grp')
                auto2_name = curve + '_cluster' + str(count) + '_specialAuto'
                auto2_grp = pm.group(empty=True, name = auto2_name)
                ae.create_labels(auto2_grp, side, obj+'_cluster'+str(count), 'special_auto_grp')
                cube_name = curve + '_cluster' + str(count) + '_ctrl'
                cube = pm.polyCube(name=cube_name, height=.25, width=.25, depth=.25)
                ae.create_labels(cube, side, obj+'_cluster'+str(count), 'cluster_ctrl')
                ##now we need to create some offset groups to allow our cluster controls to follow the second face curves
                point_trans_name = curve + '_cluster' + str(count) + '_pointTrans' 
                point_trans_grp = pm.group(empty=True, name = point_trans_name)
                ae.create_labels(point_trans_grp, side, obj+'_cluster'+str(count), 'trans_grp')
                point_offset_name = curve + '_cluster' + str(count) + '_offset' 
                point_offset_grp = pm.group(empty=True, name = point_offset_name)
                ae.create_labels(point_offset_grp, side, obj+'_cluster'+str(count), 'point_grp')
                ##parent control elements correctly
                pm.parent(point_offset_grp, point_trans_grp)
                pm.parent(auto_grp, trans_grp)
                pm.parent(auto2_grp, auto_grp)
                pm.parent(cube, auto2_grp)
                ##constrain control to the cluster to move it to correct place
                constraint = pm.parentConstraint(doop_jnt, trans_grp)
                ##delete constraint
                pm.delete(constraint)
                ##point constraint to end joint
                constraintB = pm.pointConstraint(end_jnt, trans_grp)
                pm.delete(constraintB)
                ##move the offset and trans groups to end joint
                constraintC = pm.pointConstraint(end_jnt, point_trans_grp)
                pm.delete(constraintC)
                ##create some offset groups for the cluster
                cluster_trans = pm.group(empty=True, name= str(cluster_handle)+'_trans')
                cluster_auto = pm.group(empty=True, name=str(cluster_handle)+'_auto')
                pm.parent(cluster_auto, cluster_trans)
                pm.matchTransform(cluster_trans, doop_jnt)
                pm.parent(cluster, cluster_auto)
                ##snap the pivot to the doop
                snap_to_pivot(doop_jnt, [trans_grp, auto_grp, auto2_grp, cube, cluster_auto, cluster_trans])
                ##parent constriang the trans group to the pivot joint source
                pm.pointConstraint(eye_jnt, trans_grp, mo=True)
                ##createconstraints
                pm.parentConstraint(cube, cluster_trans)
                pm.aimConstraint(point_offset_grp, auto_grp, maintainOffset=True, aimVector=(0,0,1), upVector=(0,1,0), worldUpType = 'vector', worldUpVector=(0,1,0))
                pm.pointConstraint(point_offset_grp, auto2_grp, maintainOffset=True)
                ##create multiply divide node
                multiDiv = pm.shadingNode('multiplyDivide', asUtility=True, name=obj+'_cluster'+str(count)+ '_multiDiv')
                ae.create_labels(multiDiv, side, obj+'_cluster'+str(count), 'multiDiv')
                plus_min = pm.shadingNode('plusMinusAverage', asUtility=True, name=obj+'_cluster'+str(count)+ '_plusMin')
                ae.create_labels(plus_min, side, obj+'_cluster'+str(count), 'plusMin')
                condition = pm.shadingNode('condition', asUtility = True, name=obj+'_cluster'+str(count)+ '_condition')
                negMulti = pm.shadingNode('multiplyDivide', asUtility=True, name=obj+'_cluster'+str(count)+ '_negMulti')
                ##grabing attributes
                ctrl_rotY = cube[0] + '.rotateY'
                multi_input1X = str(multiDiv) + '.input1X'
                multi_input2X = str(multiDiv) + '.input2X'
                multi_input1Y = str(multiDiv) + '.input1Y'
                multi_input2Y = str(multiDiv) + '.input2Y'
                multi_outputX = str(multiDiv) + '.outputX'
                multi_outputY = str(multiDiv) + '.outputY'
                cluster_auto_tranZ = str(cluster_auto) + '.translateZ'
                plus_inX = str(plus_min) + '.input1D[0]'
                plus_inY = str(plus_min) + '.input1D[1]'
                plus_out = str(plus_min) + '.output1D'
                negMulti_in1X = str(negMulti) + '.input1X'
                negMulti_in2X = str(negMulti) + '.input2X'
                negMulti_output = str(negMulti) + '.outputX'
                condition_false = str(condition) + '.colorIfFalseR'
                condition_true = str(condition) + '.colorIfTrueR'
                condition_first = str(condition) + '.firstTerm'
                condition_output = str(condition) + '.outColorR'
                condition_operation = str(condition) + '.operation'
                """ COME BACK AND ADD A FUNCTION FOR USER TO CHANGE THIS AMOUNT"""
                pm.setAttr(multi_input2X, -.015)
                pm.setAttr(multi_input2Y, -.015)
                pm.setAttr(negMulti_in2X, -1)
                pm.setAttr(condition_operation, 2)
                ##connect attributes
                pm.connectAttr(ctrl_rotY, multi_input1X)
                pm.connectAttr(multi_outputX, plus_inX)
                pm.connectAttr(multi_outputY, plus_inY)
                pm.connectAttr(plus_out, negMulti_in1X)
                pm.connectAttr(negMulti_output, condition_true)
                pm.connectAttr(plus_out, condition_false)
                pm.connectAttr(plus_out, condition_first)
                #pm.connectAttr(condition_output, cluster_auto_tranZ)
                ##delete joints
                pm.delete(doop_jnt)
                ##parent controls under parent
                pm.parent(trans_grp, clusterCtrls_parent)
                pm.parent(cluster_trans, cluster_parent)
                pm.parent(point_trans_grp, lip_point_parent)
                ##append cluster controls
                cluster_ctrls.append(cube)
            continue
        if ae.check_object(curve) == 'LowerEyelid':
            for cv in shape.cv[:]:
                ##add one to the count for naming purposes
                count += 1
                if type(curve) == list:
                    curve = curve[0]
                ##create cluster name and cluster on cv
                cluster_name = curve + '_cluster' + str(count)
                cluster = pm.cluster(cv, name=cluster_name)
                cluster_handle = cluster[1]
                side = ae.determine_side(cluster_handle)
                if side == 'Right':
                    eye_jnt = right_eye
                if side == 'Left':
                    eye_jnt = left_eye
                ae.create_labels(cluster, side, obj, 'cluster')
                ae.create_labels(cluster_handle, side, obj, 'cluster')
                ##create some joints for the purpose of orientation. 
                doop_jnt = pm.duplicate(eye_jnt)
                end_jnt = pm.joint(name='temp')
                ##place end joint at cluster
                pm.matchTransform(end_jnt, cluster)
                pm.parent(end_jnt, doop_jnt)
                pm.joint(doop_jnt, edit=True, orientJoint='zyx', secondaryAxisOrient= 'yup', zeroScaleOrient=True)
                ##place controls and snap pivot to doop joint
                ##create control groups and cube control and name them all and label
                trans_name = curve + '_cluster' + str(count) + '_trans' 
                trans_grp = pm.group(empty=True, name = trans_name)
                ae.create_labels(trans_grp, side, obj+'_cluster'+str(count), 'trans_grp')
                auto_name = curve + '_cluster' + str(count) + '_auto'
                auto_grp = pm.group(empty=True, name = auto_name)
                ae.create_labels(auto_grp, side, obj+'_cluster'+str(count), 'auto_grp')
                auto2_name = curve + '_cluster' + str(count) + '_specialAuto'
                auto2_grp = pm.group(empty=True, name = auto2_name)
                ae.create_labels(auto2_grp, side, obj+'_cluster'+str(count), 'special_auto_grp')
                cube_name = curve + '_cluster' + str(count) + '_ctrl'
                cube = pm.polyCube(name=cube_name, height=.25, width=.25, depth=.25)
                ae.create_labels(cube, side, obj+'_cluster'+str(count), 'cluster_ctrl')
                ##now we need to create some offset groups to allow our cluster controls to follow the second face curves
                point_trans_name = curve + '_cluster' + str(count) + '_pointTrans' 
                point_trans_grp = pm.group(empty=True, name = point_trans_name)
                ae.create_labels(point_trans_grp, side, obj+'_cluster'+str(count), 'trans_grp')
                point_offset_name = curve + '_cluster' + str(count) + '_offset' 
                point_offset_grp = pm.group(empty=True, name = point_offset_name)
                ae.create_labels(point_offset_grp, side, obj+'_cluster'+str(count), 'point_grp')
                ##parent control elements correctly
                pm.parent(point_offset_grp, point_trans_grp)
                pm.parent(auto_grp, trans_grp)
                pm.parent(auto2_grp, auto_grp)
                pm.parent(cube, auto2_grp)
                ##constrain control to the cluster to move it to correct place
                constraint = pm.parentConstraint(doop_jnt, trans_grp)
                ##delete constraint
                pm.delete(constraint)
                ##point constraint to end joint
                constraintB = pm.pointConstraint(end_jnt, trans_grp)
                pm.delete(constraintB)
                ##move the offset and trans groups to end joint
                constraintC = pm.pointConstraint(end_jnt, point_trans_grp)
                pm.delete(constraintC)
                ##create some offset groups for the cluster
                cluster_trans = pm.group(empty=True, name= str(cluster_handle)+'_trans')
                cluster_auto = pm.group(empty=True, name=str(cluster_handle)+'_auto')
                pm.parent(cluster_auto, cluster_trans)
                pm.matchTransform(cluster_trans, doop_jnt)
                pm.parent(cluster, cluster_auto)
                ##snap the pivot to the doop
                snap_to_pivot(doop_jnt, [trans_grp, auto_grp, auto2_grp, cube, cluster_auto, cluster_trans])
                ##parent constriang the trans group to the pivot joint source
                pm.pointConstraint(eye_jnt, trans_grp, mo=True)
                ##createconstraints
                pm.parentConstraint(cube, cluster_trans)
                pm.aimConstraint(point_offset_grp, auto_grp, maintainOffset=True, aimVector=(0,0,1), upVector=(0,1,0), worldUpType = 'vector', worldUpVector=(0,1,0))
                pm.pointConstraint(point_offset_grp, auto2_grp, maintainOffset=True)
                ##create multiply divide node
                multiDiv = pm.shadingNode('multiplyDivide', asUtility=True, name=obj+'_cluster'+str(count)+ '_multiDiv')
                ae.create_labels(multiDiv, side, obj+'_cluster'+str(count), 'multiDiv')
                plus_min = pm.shadingNode('plusMinusAverage', asUtility=True, name=obj+'_cluster'+str(count)+ '_plusMin')
                ae.create_labels(plus_min, side, obj+'_cluster'+str(count), 'plusMin')
                condition = pm.shadingNode('condition', asUtility = True, name=obj+'_cluster'+str(count)+ '_condition')
                negMulti = pm.shadingNode('multiplyDivide', asUtility=True, name=obj+'_cluster'+str(count)+ '_negMulti')
                ##grabing attributes
                ctrl_rotY = cube[0] + '.rotateY'
                multi_input1X = str(multiDiv) + '.input1X'
                multi_input2X = str(multiDiv) + '.input2X'
                multi_input1Y = str(multiDiv) + '.input1Y'
                multi_input2Y = str(multiDiv) + '.input2Y'
                multi_outputX = str(multiDiv) + '.outputX'
                multi_outputY = str(multiDiv) + '.outputY'
                cluster_auto_tranZ = str(cluster_auto) + '.translateZ'
                plus_inX = str(plus_min) + '.input1D[0]'
                plus_inY = str(plus_min) + '.input1D[1]'
                plus_out = str(plus_min) + '.output1D'
                negMulti_in1X = str(negMulti) + '.input1X'
                negMulti_in2X = str(negMulti) + '.input2X'
                negMulti_output = str(negMulti) + '.outputX'
                condition_false = str(condition) + '.colorIfFalseR'
                condition_true = str(condition) + '.colorIfTrueR'
                condition_first = str(condition) + '.firstTerm'
                condition_output = str(condition) + '.outColorR'
                condition_operation = str(condition) + '.operation'
                """ COME BACK AND ADD A FUNCTION FOR USER TO CHANGE THIS AMOUNT"""
                pm.setAttr(multi_input2X, -.015)
                pm.setAttr(multi_input2Y, -.015)
                pm.setAttr(negMulti_in2X, -1)
                pm.setAttr(condition_operation, 2)
                ##connect attributes
                pm.connectAttr(ctrl_rotY, multi_input1X)
                pm.connectAttr(multi_outputX, plus_inX)
                pm.connectAttr(multi_outputY, plus_inY)
                pm.connectAttr(plus_out, negMulti_in1X)
                pm.connectAttr(negMulti_output, condition_true)
                pm.connectAttr(plus_out, condition_false)
                pm.connectAttr(plus_out, condition_first)
                #pm.connectAttr(condition_output, cluster_auto_tranZ)
                ##delete joints
                pm.delete(doop_jnt)
                ##parent controls under parent
                pm.parent(trans_grp, clusterCtrls_parent)
                pm.parent(cluster_trans, cluster_parent)
                pm.parent(point_trans_grp, lip_point_parent)
                ##append cluster controls
                cluster_ctrls.append(cube)
            continue
        
        else:   
            side = ae.check_side(curve) 
            for cv in shape.cv[:]:
                ##add one to the count for naming purposes
                count += 1
                if type(curve) == list:
                    curve = curve[0]
                ##create cluster name and cluster on cv
                cluster_name = curve + '_cluster' + str(count)
                cluster = pm.cluster(cv, name=cluster_name)
                cluster_handle = cluster[1]
                ae.create_labels(cluster, side, obj, 'cluster')
                ae.create_labels(cluster_handle, side, obj, 'cluster')
                ##create control groups and cube control and name them all and label
                trans_name = curve + '_cluster' + str(count) + '_trans' 
                trans_grp = pm.group(empty=True, name = trans_name)
                ae.create_labels(trans_grp, side, obj+'_cluster'+str(count), 'trans_grp')
                auto_name = curve + '_cluster' + str(count) + '_auto'
                auto_grp = pm.group(empty=True, name = auto_name)
                ae.create_labels(auto_grp, side, obj+'_cluster'+str(count), 'auto_grp')
                cube_name = curve + '_cluster' + str(count) + '_ctrl'
                cube = pm.polyCube(name=cube_name, height=.25, width=.25, depth=.25)
                ae.create_labels(cube, side, obj+'_cluster'+str(count), 'cluster_ctrl')
                ##parent control elements correctly
                pm.parent(cube, auto_grp)
                pm.parent(auto_grp, trans_grp)
                ##constrain control to the cluster to move it to correclt place
                constraint = pm.parentConstraint(cluster, trans_grp)
                ##delete constraint
                pm.delete(constraint)
                ##constrain the cluster to the control
                pm.parentConstraint(cube, cluster)
                ##add the ctrl to a list
                cluster_ctrls.append(cube)
                ##parent controls under parent
                pm.parent(trans_grp, clusterCtrls_parent)
                pm.parent(cluster, cluster_parent)
    return cluster_ctrls

def create_path_elements():
    ##list for all controls created
    all_curve_ctrls=[]
    ##list for face curves
    face_curves = []
    ##grab the head joint 
    all_joints = pm.ls(type='joint')
    for joint in all_joints:
        if ae.check_object(joint) == 'Head':
            head_joint = joint
    ##grab all face curves transforms
    curves = pm.ls(type='nurbsCurve')
    for curve in curves:
        curve_trans = pm.listRelatives(curve, parent=True)
        face_curves.append(curve_trans)
    face_curves = ae.clean_list_doops(face_curves)
    ##create motionpath groups 
    detail_parent_list = create_motionPath_groups(face_curves)
    ##grab the children (motionpath_groups) of the parent node
    for parent in detail_parent_list:
        motionPath_grps = pm.listRelatives(parent, children=True)
        #print (motionPath_grps)
        ##Then make controls
        detail_ctrls_elements = create_detail_ctrls(motionPath_grps)
        ##seperate out ctrls list and trans list
        detail_ctrls = detail_ctrls_elements[1]
        for control in detail_ctrls:
            all_curve_ctrls.append(control)
        trans_grps = detail_ctrls_elements[0]
        ##apply color to detail controls
        ms.apply_material(detail_ctrls, cyan_mat)
        ##parent the trans groups under the parent group
        for trans in trans_grps:
            pm.parent(trans, parent)
    ##create detail_ctrls parent group for organization
    detail_parent = pm.group(empty=True, name='detailCtrls_parent')
    ae.create_labels(detail_parent, 'NA', 'detailCtrls','parent_grp')
    pm.parent(detail_parent_list, detail_parent)
    #print (all_curve_ctrls)
    ##create a joint group to parent things under
    #joint_grp = pm.group(empty=True, name='face_curve_joints_grp')
    ##create joints
    curve_joints = create_atLoc_joints(all_curve_ctrls)
    '''COME BACK TO PARENT JOINTS SOMEWHERE'''
    pm.parent(curve_joints, head_joint)
    ##create cluster controls
    cluster_ctrls = create_clusters_ctrls(face_curves)
    ms.apply_material(cluster_ctrls, magenta_mat)

def doop_curves():
    ##grab all curves to doop
    curve_trans = []
    all_curves = pm.ls(type='nurbsCurve')
    for curve in all_curves:
        trans = pm.listRelatives(curve, parent=True)
        if type(trans) == list:
            trans = trans[0]
        #if ae.check_object(trans) == 'Laugh' or ae.check_object(trans) == 'Cheek' or ae.check_object(trans) == 'LowerLip' or ae.check_object(trans) == 'UpperLip':
        curve_trans.append(trans)
    ##doop them
    curve_trans = ae.clean_list_doops(curve_trans)
    dynamic_curves = pm.duplicate(curve_trans)
    for curve in dynamic_curves:
        obj = ae.check_object(curve)
        side = ae.check_side(curve)
        ae.replace_labels(curve, side, obj, 'dynamic_curve')
    ##create a dynamic curves group to parent them under
    dynamic_parent = pm.group(empty=True, name='DynamicCurves_grp')
    ae.create_labels(dynamic_parent, 'NA', 'DynamicCurves', 'base_grp')
    pm.parent(dynamic_curves, dynamic_parent)
    pm.setAttr(str(dynamic_parent)+'.visibility',0)
    return (dynamic_curves)

def mouth_corners():
    ##parent group
    parent_group = pm.group(empty=True, name='MouthControls_parent')
    ae.create_labels(parent_group, 'NA', 'MouthControls', 'follow_head_grp')
    ##get all transforms to sort through
    all_trans = pm.ls(type='transform')
    labeled_trans = []
    ##do a quick check to only grab labeled trans
    for possible_trans in all_trans:
        if ae.check_attr_exists(possible_trans) == True:
            labeled_trans.append(possible_trans)
    ##grab outer follow lip controls
    for trans in labeled_trans:
        if ae.check_object(trans) == 'UpperLip_outer_follow' and ae.check_type(trans) == 'detail_ctrl':
            if ae.check_side(trans) == 'Left':
                left_upper_detail = trans
            if ae.check_side(trans) == 'Right':
                right_upper_detail = trans
        if ae.check_object(trans) == 'LowerLip_outer_follow' and ae.check_type(trans) == 'detail_ctrl':
            if ae.check_side(trans) == 'Left':
                left_lower_detail = trans
            if ae.check_side(trans) == 'Right':
                right_lower_detail = trans
        if ae.check_object(trans) == 'UpperLip_cluster4' and ae.check_type(trans) == 'cluster_ctrl':
            upper_center_pivot = trans
        if ae.check_object(trans) == 'LowerLip_cluster4' and ae.check_type(trans) == 'cluster_ctrl':
            lower_center_pivot = trans
        if ae.check_object(trans) == 'UpperLip_mid_follow' and ae.check_type(trans) == 'detail_ctrl':
           upper_center = trans
        if ae.check_object(trans) == 'LowerLip_mid_follow' and ae.check_type(trans) == 'detail_ctrl':
            lower_center = trans
    ##grab lip parent joint
    all_joints = pm.ls(type='joint')
    for joint in all_joints:
        if ae.check_object(joint) == 'UpperLipParent':
            lipParent = joint
        if ae.check_object(joint) == 'Head':
            head_jnt = joint
        if ae.check_object(joint) == 'Jaw':
            jaw_jnt = joint
    ##create joint and constrain it to both upper, and lower outer lip follow controls on each side
    left_end = pm.joint()
    ##clear selection to avoid unwanted parenting of joints
    pm.select(clear=True)
    left_constraint = pm.parentConstraint(left_lower_detail, left_upper_detail, left_end)
    pm.delete(left_constraint)
    right_end = pm.joint()
    pm.select(clear=True)
    right_constraint = pm.parentConstraint(right_lower_detail, right_upper_detail, right_end)
    pm.delete(right_constraint)
    ##duplicate lip parent
    left_doop = pm.duplicate(lipParent)
    right_doop = pm.duplicate(lipParent)
    ##parent the joints
    pm.parent(right_end, right_doop)
    pm.parent(left_end, left_doop)
    ##orient the joints
    pm.joint(left_doop, edit=True, orientJoint='zyx', secondaryAxisOrient= 'yup', zeroScaleOrient=True)
    pm.joint(right_doop, edit=True, orientJoint='zyx', secondaryAxisOrient= 'yup', zeroScaleOrient=True)
    ##create a control object with all groups properly parented
    left_trans = pm.group(empty=True, name='MouthCorner_left_trans')
    ae.create_labels(left_trans, 'Left', 'MouthCorner', 'trans_grp')
    left_auto = pm.group(empty=True, name='MouthCorner_left_auto')
    ae.create_labels(left_auto, 'Left', 'MouthCorner', 'auto_grp')
    left_ctrl = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='MouthCorner_Left')
    ae.create_labels(left_ctrl, 'Left', 'MouthCorner', 'ctrl')
    ##apply material
    ms.apply_material(left_ctrl, Blue)
    ##place properly for orientation
    pm.rotate(left_ctrl, [-90,0,0])
    pm.makeIdentity(left_ctrl, apply=True, rotate=True)
    pm.parent(left_ctrl, left_auto)
    pm.parent(left_auto, left_trans)
    ##constrain trans
    left_constraint = pm.parentConstraint(left_doop, left_trans)
    pm.delete(left_constraint)
    ##do right side
    right_trans = pm.group(empty=True, name='MouthCorner_right_trans')
    ae.create_labels(right_trans, 'Right', 'MouthCorner', 'trans_grp')
    right_auto = pm.group(empty=True, name='MouthCorner_right_auto')
    ae.create_labels(right_auto, 'Right', 'MouthCorner', 'auto_grp')
    right_ctrl = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='MouthCorner_Right')
    ae.create_labels(right_ctrl, 'Right', 'MouthCorner', 'ctrl')
    ##apply color
    ms.apply_material(right_ctrl, Red)
    ##adjust shape for correct orientation
    pm.rotate(right_ctrl, [-90,0,0])
    pm.makeIdentity(right_ctrl, apply=True, rotate=True)
    pm.parent(right_ctrl, right_auto)
    pm.parent(right_auto, right_trans)
    right_constraint = pm.parentConstraint(right_doop, right_trans)
    pm.delete(right_constraint)
    ##create a control object with all groups properly parented for center upper lip
    upper_trans = pm.group(empty=True, name='MouthCenter_upper_trans')
    ae.create_labels(upper_trans, 'Center', 'MouthCenter_upper', 'trans_grp')
    upper_auto = pm.group(empty=True, name='MouthCenter_upper_auto')
    ae.create_labels(upper_auto, 'Center', 'MouthCenter_upper', 'auto_grp')
    upper_ctrl = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='MouthCenter_upper')
    ae.create_labels(upper_ctrl, 'Center', 'MouthCenter_upper', 'ctrl')
    ##apply material
    ms.apply_material(upper_ctrl, Yellow)
    ##place properly for orientation
    pm.rotate(upper_ctrl, [-90,0,0])
    pm.makeIdentity(upper_ctrl, apply=True, rotate=True)
    pm.parent(upper_ctrl, upper_auto)
    pm.parent(upper_auto, upper_trans)
    ##move control elements to lip parent doop to reorient and position
    upper_constraint = pm.parentConstraint(upper_center, upper_trans)
    pm.delete(upper_constraint)
    ##create a control object with all groups properly parented for center upper lip
    lower_trans = pm.group(empty=True, name='MouthCenter_lower_trans')
    ae.create_labels(lower_trans, 'Center', 'MouthCenter_lower', 'trans_grp')
    lower_auto = pm.group(empty=True, name='MouthCenter_lower_auto')
    ae.create_labels(lower_auto, 'Center', 'MouthCenter_lower', 'auto_grp')
    lower_ctrl = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='MouthCenter_lower')
    ae.create_labels(lower_ctrl, 'Center', 'MouthCenter_lower', 'ctrl')
    ##apply material
    ms.apply_material(lower_ctrl, Orange)
    ##place properly for orientation
    pm.rotate(lower_ctrl, [-90,0,0])
    pm.makeIdentity(lower_ctrl, apply=True, rotate=True)
    pm.parent(lower_ctrl, lower_auto)
    pm.parent(lower_auto, lower_trans)
    ##move control elements to lip parent doop to reorient and position
    lower_constraint = pm.parentConstraint(lower_center, lower_trans)
    pm.delete(lower_constraint)
    ##move just position to end joint
    left_point = pm.pointConstraint(left_end, left_trans)
    right_point = pm.pointConstraint(right_end, right_trans)
    pm.delete(left_point)
    pm.delete(right_point)
    ##move pivot back to lip parent doop
    snap_to_pivot(left_doop, [left_trans, left_auto, left_ctrl])
    snap_to_pivot(right_doop, [right_trans, right_auto, right_ctrl])
    snap_to_pivot(upper_center_pivot, [upper_trans, upper_auto, upper_ctrl])
    snap_to_pivot(lower_center_pivot, [lower_trans, lower_auto, lower_ctrl])
    ##delete any constraints and joints
    pm.delete(right_doop)
    pm.delete(left_doop)
    ####Constrain the lips auto groups to the jaw and to the head
    pm.parentConstraint(head_jnt, jaw_jnt, right_auto, mo=True)
    pm.parentConstraint(head_jnt, jaw_jnt, left_auto, mo=True)
    ##add attributes to middle mouth controls
    '''Adjust defaultValue later'''
    pm.addAttr(upper_ctrl[0], ln='Counteract_Jaw', attributeType='double', min=0, max=1, defaultValue=0.15, k=True)
    pm.addAttr(lower_ctrl[0], ln='Follow_Jaw', attributeType='double', min=0, max=1, defaultValue=1, k=True)
    #####Hook up rotate of Jaw to center lower####
    ##create needed shading node
    follow_jaw_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='FollowJaw_multi')
    counter_jaw_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='CounterJaw_mulit')
    inverse_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='CounterJawInverse_mulit')
    follow_increase_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='FollowJaw_increase_multi')
    ##grab attribute names
    follow_jaw_attr = str(lower_ctrl[0]) + '.Follow_Jaw'
    counter_jaw_attr = str(upper_ctrl[0]) + '.Counteract_Jaw'
    follow_multi_in1X = str(follow_jaw_multi) + '.input1X'
    follow_multi_in2X = str(follow_jaw_multi) + '.input2X'
    follow_multi_outX = str(follow_jaw_multi) + '.outputX'
    counter_jaw_in1X = str(counter_jaw_multi) + '.input1X'
    counter_jaw_in2X = str(counter_jaw_multi) + '.input2X'
    counter_jaw_outX = str(counter_jaw_multi) + '.outputX'
    inverse_in1X = str(inverse_multi) + '.input1X'
    inverse_in2X = str(inverse_multi) + '.input2X'
    inverse_outX = str(inverse_multi) + '.outputX'
    lower_auto_inX = str(lower_auto) + '.rotateX'
    upper_auto_inX = str(upper_auto) + '.rotateX'
    jaw_rotX = str(jaw_jnt) + '.rotateX'
    follow_increase_multi_in1Y = str(follow_increase_multi) + '.input1Y'
    follwo_increase_multi_in2Y = str(follow_increase_multi) + '.input2Y'
    follow_increase_multi_outY = str(follow_increase_multi) + '.outputY'
    ##hook up some automation for puckering
    pm.setAttr(inverse_in2X, -1)
    pm.connectAttr(follow_jaw_attr, follow_multi_in2X)
    pm.connectAttr(jaw_rotX, follow_multi_in1X)
    pm.connectAttr(follow_multi_outX, follow_increase_multi_in1Y)
    pm.setAttr(follwo_increase_multi_in2Y, 1.75)
    pm.connectAttr(follow_increase_multi_outY, lower_auto_inX)
    pm.connectAttr(counter_jaw_attr, counter_jaw_in2X)
    pm.connectAttr(jaw_rotX, counter_jaw_in1X)
    pm.connectAttr(counter_jaw_outX, inverse_in1X)
    pm.connectAttr(inverse_outX, upper_auto_inX)
    ####SET UP AUTOMATION IN PUCKER####
    ##add needed attributes
    pm.addAttr(upper_ctrl[0], ln='Upper_Automation', attributeType='double', min=0, max=1, defaultValue=1, k=True)
    pm.addAttr(lower_ctrl[0], ln='Lower_Automation', attributeType='double', min=0, max=1, defaultValue=1, k=True)
    upper_automation_attr = str(upper_ctrl[0]) + '.Upper_Automation'
    lower_automation_attr = str(lower_ctrl[0]) + '.Lower_Automation'
    ##create all needed math nodes
    UpperApplyAuto_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='UpperApplyAuto_multi')
    LowerApplyAuto_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='LowerApplyAuto_multi')
    LeftCorner_inverse_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='LeftCorner_inverse_multi')
    HalfCornerRotY_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='HalfCornerRotY_multi')
    HalfCornerRotYCombine_plusMin = pm.shadingNode('plusMinusAverage', asUtility=True, name='HalfCornerRotYCombine_plusMin')
    CornerRotYCombine_plusMin = pm.shadingNode('plusMinusAverage', asUtility=True, name='CornerRotYCombine_plusMin')
    ScalePercent_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='ScalePercent_multi')
    UpperOneMinusScalePercent_plusMin = pm.shadingNode('plusMinusAverage', asUtility=True, name='UpperOneMinusScalePercent_plusMin')
    LowerOneMinusScalePercent_plusMin = pm.shadingNode('plusMinusAverage', asUtility=True, name='LowerOneMinusScalePercent_plusMin')
    UpperCornerCloseness_condition = pm.shadingNode('condition', asUtility=True, name='UpperCornerCloseness_condition')
    LowerCornerCloseness_condition = pm.shadingNode('condition', asUtility=True, name='LowerCornerCloseness_condition')
    TransPercent_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='TransPercent_multi')
    ApplyTrans_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='ApplyTrans_mulit')
    #####grab all needed attributes###
    ##Mouth Corners
    MouthCorner_Left_RotY = str(left_ctrl[0]) + '.rotateY'
    MouthCorner_Right_RotY = str(right_ctrl[0]) + '.rotateY'
    upper_auto_transZ = str(upper_auto)+'.translateZ'
    upper_auto_rotY = str(upper_auto) + '.rotateY'
    lower_auto_transZ = str(lower_auto) + '.translateZ'
    lower_auto_rotY = str(lower_auto) + '.rotateY'
    ###LeftCorner_inverse_multi
    LeftCorner_inverse_in1X = str(LeftCorner_inverse_multi) + '.input1X'
    LeftCorner_inverse_in2X = str(LeftCorner_inverse_multi) + '.input2X'
    LeftCorner_inverse_outX = str(LeftCorner_inverse_multi) + '.outputX'
    ##HalfCornerRot_multi
    HalfCornerRotY_in1X = str(HalfCornerRotY_multi) + '.input1X'
    HalfCornerRotY_in2X = str(HalfCornerRotY_multi) + '.input2X'
    HalfCornerRotY_in1Y = str(HalfCornerRotY_multi) + '.input1Y'
    HalfCornerRotY_in2Y = str(HalfCornerRotY_multi) + '.input2Y'
    HalfCornerRotY_outX = str(HalfCornerRotY_multi) + '.outputX'
    HalfCornerRotY_outY = str(HalfCornerRotY_multi) + '.outputY'
    ##HalfCornerRotCombine_plusMin
    HalfCornerRotYCombine_in1D0 = str(HalfCornerRotYCombine_plusMin) + '.input1D[0]'
    HalfCornerRotYCombine_in1D1 = str(HalfCornerRotYCombine_plusMin) + '.input1D[1]'
    HalfCornerRotYCombine_out1D = str(HalfCornerRotYCombine_plusMin) + '.output1D'
    ##ScalePercent_multi
    ScalePercent_in1X = str(ScalePercent_multi) + '.input1X'
    ScalePercent_in2X = str(ScalePercent_multi) + '.input2X'
    ScalePercent_outX = str(ScalePercent_multi) + '.outputX'
    ##CornerRotYCombine_plusMin
    CornerRotYCombine_in1D0 = str(CornerRotYCombine_plusMin) + '.input1D[0]'
    CornerRotYCombine_in1D1 = str(CornerRotYCombine_plusMin) + '.input1D[1]'
    CornerRotYCombine_out1D = str(CornerRotYCombine_plusMin) + '.output1D'
    ##TransPercent_multi
    TransPercent_in1X = str(TransPercent_multi) + '.input1X'
    TransPercent_in2X = str(TransPercent_multi) + '.input2X'
    TransPercent_in1Y = str(TransPercent_multi) + '.input1Y'
    TransPercent_in2Y = str(TransPercent_multi) + '.input2Y'
    TransPercent_outX = str(TransPercent_multi) + '.outputX'
    TransPercent_outY = str(TransPercent_multi) + '.outputY'
    ##UpperApplyAuto_multi
    UpperApplyAuto_in1X = str(UpperApplyAuto_multi) + '.input1X'
    UpperApplyAuto_in2X = str(UpperApplyAuto_multi) + '.input2X'
    UpperApplyAuto_in1Y = str(UpperApplyAuto_multi) + '.input1Y'
    UpperApplyAuto_in2Y = str(UpperApplyAuto_multi) + '.input2Y'
    UpperApplyAuto_in1Z = str(UpperApplyAuto_multi) + '.input1Z'
    UpperApplyAuto_in2Z = str(UpperApplyAuto_multi) + '.input2Z'
    UpperApplyAuto_outX = str(UpperApplyAuto_multi) + '.outputX'
    UpperApplyAuto_outY = str(UpperApplyAuto_multi) + '.outputY'
    UpperApplyAuto_outZ = str(UpperApplyAuto_multi) + '.outputZ'
    ##LowerApplyAuto_multi
    LowerApplyAuto_in1X = str(LowerApplyAuto_multi) + '.input1X'
    LowerApplyAuto_in2X = str(LowerApplyAuto_multi) + '.input2X'
    LowerApplyAuto_in1Y = str(LowerApplyAuto_multi) + '.input1Y'
    LowerApplyAuto_in2Y = str(LowerApplyAuto_multi) + '.input2Y'
    LowerApplyAuto_in1Z = str(LowerApplyAuto_multi) + '.input1Z'
    LowerApplyAuto_in2Z = str(LowerApplyAuto_multi) + '.input2Z'
    LowerApplyAuto_outX = str(LowerApplyAuto_multi) + '.outputX'
    LowerApplyAuto_outY = str(LowerApplyAuto_multi) + '.outputY'
    LowerApplyAuto_outZ = str(LowerApplyAuto_multi) + '.outputZ'
    ##UpperOneMinusScalePercent_plusMin
    UpperOneMinusScalePercent_in1D0 = str(UpperOneMinusScalePercent_plusMin) + '.input1D[0]'
    UpperOneMinusScalePercent_in1D1 = str(UpperOneMinusScalePercent_plusMin) + '.input1D[1]'
    UpperOneMinusScalePercent_out1D = str(UpperOneMinusScalePercent_plusMin) + '.output1D'
    UpperOneMinusScalePercent_operation = str(UpperOneMinusScalePercent_plusMin) + '.operation'
    ##LowerOneMinusScalePercent_plusMin
    LowerOneMinusScalePercent_in1D0 = str(LowerOneMinusScalePercent_plusMin) + '.input1D[0]'
    LowerOneMinusScalePercent_in1D1 = str(LowerOneMinusScalePercent_plusMin) + '.input1D[1]'
    LowerOneMinusScalePercent_out1D = str(LowerOneMinusScalePercent_plusMin) + '.output1D'
    LowerOneMinusScalePercent_operation = str(LowerOneMinusScalePercent_plusMin) + '.operation'
    ##UpperCornerCloseness_condition
    UpperCornerCloseness_firstTerm = str(UpperCornerCloseness_condition) + '.firstTerm'
    UpperCornerCloseness_trueG = str(UpperCornerCloseness_condition) + '.colorIfTrueG'
    UpperCornerCloseness_trueR = str(UpperCornerCloseness_condition) + '.colorIfTrueR'
    UpperCornerCloseness_falseG = str(UpperCornerCloseness_condition) + '.colorIfFalseG'
    UpperCornerCloseness_falseR = str(UpperCornerCloseness_condition) + '.colorIfFalseR'
    UpperCornerCloseness_outR = str(UpperCornerCloseness_condition) + '.outColorR'
    UpperCornerCloseness_outG = str(UpperCornerCloseness_condition) + '.outColorG'
    pm.setAttr(str(UpperCornerCloseness_condition)+'.operation', 2)
    ##LowerCornerCloseness_condition
    LowerCornerCloseness_firstTerm = str(LowerCornerCloseness_condition) + '.firstTerm'
    LowerCornerCloseness_trueG = str(LowerCornerCloseness_condition) + '.colorIfTrueG'
    LowerCornerCloseness_trueR = str(LowerCornerCloseness_condition) + '.colorIfTrueR'
    LowerCornerCloseness_falseG = str(LowerCornerCloseness_condition) + '.colorIfFalseG'
    LowerCornerCloseness_falseR = str(LowerCornerCloseness_condition) + '.colorIfFalseR'
    LowerCornerCloseness_outR = str(LowerCornerCloseness_condition) + '.outColorR'
    LowerCornerCloseness_outG = str(LowerCornerCloseness_condition) + '.outColorG'
    pm.setAttr(str(LowerCornerCloseness_condition)+'.operation', 2)
    ####Connect All Attributes####
    pm.connectAttr(MouthCorner_Right_RotY, HalfCornerRotY_in1Y)
    pm.connectAttr(MouthCorner_Right_RotY, CornerRotYCombine_in1D0)
    pm.connectAttr(MouthCorner_Left_RotY, HalfCornerRotY_in1X)
    pm.connectAttr(MouthCorner_Left_RotY, LeftCorner_inverse_in1X)
    pm.setAttr(LeftCorner_inverse_in2X, -1)
    pm.connectAttr(LeftCorner_inverse_outX, CornerRotYCombine_in1D1)
    pm.connectAttr(CornerRotYCombine_out1D, ScalePercent_in1X)
    pm.setAttr(ScalePercent_in2X, 0.05)
    pm.connectAttr(CornerRotYCombine_out1D, UpperCornerCloseness_trueR)
    pm.connectAttr(CornerRotYCombine_out1D, UpperCornerCloseness_firstTerm)
    pm.connectAttr(CornerRotYCombine_out1D ,LowerCornerCloseness_firstTerm)
    pm.connectAttr(CornerRotYCombine_out1D, LowerCornerCloseness_trueR)
    pm.connectAttr(ScalePercent_outX, LowerApplyAuto_in1X)
    pm.connectAttr(ScalePercent_outX, UpperApplyAuto_in1X)
    pm.connectAttr(lower_automation_attr, LowerApplyAuto_in2X)
    pm.connectAttr(lower_automation_attr, str(ApplyTrans_multi)+'.input2Y')
    pm.connectAttr(lower_automation_attr, LowerApplyAuto_in2Z)
    pm.connectAttr(upper_automation_attr, UpperApplyAuto_in2X)
    pm.connectAttr(upper_automation_attr, str(ApplyTrans_multi)+'.input2X')
    pm.connectAttr(upper_automation_attr, UpperApplyAuto_in2Z)
    pm.connectAttr(HalfCornerRotY_outX, HalfCornerRotYCombine_in1D0)
    pm.connectAttr(HalfCornerRotY_outY, HalfCornerRotYCombine_in1D1)
    pm.connectAttr(HalfCornerRotYCombine_out1D, UpperApplyAuto_in1Z)
    pm.connectAttr(HalfCornerRotYCombine_out1D, LowerApplyAuto_in1Z)
    pm.connectAttr(UpperApplyAuto_outX, UpperOneMinusScalePercent_in1D0)
    pm.connectAttr(UpperApplyAuto_outX, UpperOneMinusScalePercent_in1D1)
    pm.disconnectAttr(UpperApplyAuto_outX, UpperOneMinusScalePercent_in1D0)
    pm.setAttr(UpperOneMinusScalePercent_in1D0, 1)
    pm.setAttr(UpperOneMinusScalePercent_operation, 2)
    pm.connectAttr(LowerApplyAuto_outX, LowerOneMinusScalePercent_in1D0)
    pm.connectAttr(LowerApplyAuto_outX, LowerOneMinusScalePercent_in1D1)
    pm.disconnectAttr(LowerApplyAuto_outX, LowerOneMinusScalePercent_in1D0)
    pm.setAttr(LowerOneMinusScalePercent_in1D0, 1)
    pm.setAttr(LowerOneMinusScalePercent_operation, 2)
    pm.connectAttr(LowerOneMinusScalePercent_out1D, LowerCornerCloseness_trueG)
    pm.connectAttr(UpperOneMinusScalePercent_out1D, UpperCornerCloseness_trueG)
    pm.connectAttr(LowerCornerCloseness_outR, TransPercent_in1Y)
    pm.connectAttr(UpperCornerCloseness_outR, TransPercent_in1X)
    pm.setAttr(TransPercent_in2X, 0.075)
    pm.setAttr(TransPercent_in2Y, 0.075)
    pm.connectAttr(TransPercent_outX, str(ApplyTrans_multi)+'.input1X')
    pm.connectAttr(TransPercent_outY, str(ApplyTrans_multi)+'.input1Y')
    pm.connectAttr(str(ApplyTrans_multi)+'.outputX', upper_auto_transZ)
    pm.connectAttr(UpperApplyAuto_outZ, upper_auto_rotY)
    pm.connectAttr(str(ApplyTrans_multi)+'.outputY', lower_auto_transZ)
    pm.connectAttr(LowerApplyAuto_outZ, lower_auto_rotY)
    pm.setAttr(HalfCornerRotY_in2X, 0.5)
    pm.setAttr(HalfCornerRotY_in2Y, 0.5)
    pm.setAttr(UpperCornerCloseness_falseR, 0)
    pm.setAttr(UpperCornerCloseness_falseG, 1)
    pm.setAttr(LowerCornerCloseness_falseG, 1)
    pm.setAttr(LowerCornerCloseness_falseR, 0)
    ##parent under parent group
    pm.parent(left_trans, parent_group)
    pm.parent(right_trans, parent_group)
    pm.parent(upper_trans, parent_group)
    pm.parent(lower_trans, parent_group)
    ###return all controls
    return (left_ctrl[0], right_ctrl[0], upper_ctrl[0], lower_ctrl[0], LowerCornerCloseness_outG, UpperCornerCloseness_outG)

def create_dynamic_nostrils():
    ##parent group
    parent_group = pm.group(empty=True, name='NostrilControls_parent')
    ae.create_labels(parent_group, 'NA', 'NostrilControls', 'follow_head_grp')
    ##go through curves
    face_curves = []
    ##find nostril curves
    curves = pm.ls(type='nurbsCurve')
    for curve in curves:
        curve_trans = pm.listRelatives(curve, parent=True)
        face_curves.append(curve_trans)
    face_curves = ae.clean_list_doops(face_curves)
    for curve in face_curves:
        if ae.check_type(curve) == 'curve':
            if ae.check_object(curve) == 'Nostril':
                if ae.check_side(curve) == 'Right':
                    right_nostril = curve
                if ae.check_side(curve) == 'Left':
                    left_nostril = curve
            ##grab upper lip for finding "sneer" lip controls
            if ae.check_object(curve) == 'UpperLip':
                upper_lip = curve 
    ##get all transforms to sort through
    all_trans = pm.ls(type='transform')
    labeled_trans = []
    ##do a quick check to only grab labeled trans
    for possible_trans in all_trans:
        if ae.check_attr_exists(possible_trans) == True:
            labeled_trans.append(possible_trans)
    for trans in labeled_trans:
        if ae.check_type(trans) == 'cluster_ctrl':
            if ae.check_object(trans) == 'Nostril_cluster1':
                if ae.check_side(trans) == 'Right':
                    right_start_ctrl = trans
                if ae.check_side(trans) == 'Left':
                    left_start_ctrl = trans
            if ae.check_object(trans) == 'Nostril_cluster5':
                if ae.check_side(trans) == 'Right':
                    right_end_ctrl = trans
                if ae.check_side(trans) == 'Left':
                    left_end_ctrl = trans
            ##grab "sneer" lip controls
        if ae.check_type(trans) == 'special_auto_grp':
            if ae.check_object(trans) == 'UpperLip_cluster5':
                if ae.check_side(trans) == 'Right':
                    right_sneer = trans
                if ae.check_side(trans) == 'Left':
                    left_sneer = trans
            if ae.check_object(trans) == 'UpperLip_cluster3':
                if ae.check_side(trans) == 'Right':
                    right_sneer = trans
                if ae.check_side(trans) == 'Left':
                    left_sneer = trans
    ##check how curve is made 
    if ae.get_low_cvs(right_nostril) == 'Zero':
        right_location = right_start_ctrl
    if ae.get_low_cvs(right_nostril) == 'One':
        right_location = right_end_ctrl
    if ae.get_low_cvs(left_nostril) == 'Zero':
        left_location = left_start_ctrl
    if ae.get_low_cvs(left_nostril) == 'One':
        left_location = left_end_ctrl
    ##create a control object with all groups properly parented
    left_trans = pm.group(empty=True, name='Nostil_left_trans')
    ae.create_labels(left_trans, 'Left', 'Nostril', 'trans_grp')
    left_auto = pm.group(empty=True, name='Nostril_left_auto')
    ae.create_labels(left_auto, 'Left', 'Nostril', 'auto_grp')
    left_ctrl = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='Nostril_Left')
    ae.create_labels(left_ctrl, 'Left', 'Nostril', 'ctrl')
    ##apply material
    ms.apply_material(left_ctrl, Blue)
    ##place properly for orientation
    pm.rotate(left_ctrl, [-90,0,0])
    pm.makeIdentity(left_ctrl, apply=True, rotate=True)
    pm.parent(left_ctrl, left_auto)
    pm.parent(left_auto, left_trans)
    ##constrain trans
    left_constraint = pm.parentConstraint(left_location, left_trans)
    pm.delete(left_constraint)
    ##do right side
    right_trans = pm.group(empty=True, name='Nostil_right_trans')
    ae.create_labels(right_trans, 'Right', 'Nostril', 'trans_grp')
    right_auto = pm.group(empty=True, name='Nostril_right_auto')
    ae.create_labels(right_auto, 'Right', 'Nostril', 'auto_grp')
    right_ctrl = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='Nostril_Left')
    ae.create_labels(right_ctrl, 'Right', 'Nostril', 'ctrl')
    ##apply material
    ms.apply_material(right_ctrl, Red)
    ##place properly for orientation
    pm.rotate(right_ctrl, [-90,0,0])
    pm.makeIdentity(right_ctrl, apply=True, rotate=True)
    pm.parent(right_ctrl, right_auto)
    pm.parent(right_auto, right_trans)
    ##constrain trans
    right_constraint = pm.parentConstraint(right_location, right_trans)
    pm.delete(right_constraint)
    ####Set Up automation####
    ##add needed atributes
    pm.addAttr(right_ctrl[0], ln='Sneer_Automation', attributeType='double', min=0, max=1, defaultValue=1, k=True)
    pm.addAttr(left_ctrl[0], ln='Sneer_Automation', attributeType='double', min=0, max=1, defaultValue=1, k=True)
    right_sneer_attr = str(right_ctrl[0])+'.Sneer_Automation'
    left_sneer_attr = str(left_ctrl[0]) + '.Sneer_Automation'
    ##create needed nodes
    left_condition = pm.shadingNode('condition', asUtility=True, name='LeftNostrilDown_condition')
    sneer_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='NostrilSneer_multi')
    exagurate_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='NostrilSneerExagurate_multi')
    right_condition = pm.shadingNode('condition', asUtility=True, name='RightNostrilDown_condition')
    ##grab needed attributes
    left_transY = str(left_ctrl[0]) + '.translateY'
    right_transY = str(right_ctrl[0]) + '.translateY'
    left_trueR = str(left_condition) + '.colorIfTrueR'
    left_falseR = str(left_condition) + '.colorIfFalseR'
    left_firstTerm = str(left_condition) + '.firstTerm'
    left_condition_outR = str(left_condition) + '.outColorR'
    left_sneerMulti_out = str(sneer_multi) + '.outputX'
    left_exagerate_out = str(exagurate_multi) + '.outputX'
    left_sneer_multi = str(sneer_multi) + '.input1X'
    left_sneer_apply = str(sneer_multi) + '.input2X'
    left_sneer_exagerate = str(exagurate_multi) + '.input1X'
    exagerate_multi2X = str(exagurate_multi) + '.input2X'
    exagerate_multi2Y = str(exagurate_multi) + '.input2Y'
    right_trueR = str(right_condition) + '.colorIfTrueR'
    right_falseR = str(right_condition) + '.colorIfFalseR'
    right_firstTerm = str(right_condition) + '.firstTerm'
    right_sneer_multi = str(sneer_multi) + '.input1Y'
    right_sneer_apply = str(sneer_multi) + '.input2Y'
    right_sneer_exagerate = str(exagurate_multi) + '.input1Y'
    right_condition_outR = str(right_condition) + '.outColorR'
    right_sneerMulti_out = str(sneer_multi) + '.outputY'
    right_exagerate_out = str(exagurate_multi) + '.outputY'
    left_cluster_inX = str(left_sneer) + '.rotateX'
    right_cluster_inX = str(right_sneer) + '.rotateX'
    ##apply connections
    pm.connectAttr(left_transY, left_trueR)
    pm.connectAttr(left_transY, left_firstTerm)
    pm.connectAttr(left_sneer_attr, left_sneer_apply)
    pm.connectAttr(left_condition_outR, left_sneer_multi)
    pm.connectAttr(left_sneerMulti_out, left_sneer_exagerate)
    pm.connectAttr(left_exagerate_out, left_cluster_inX)
    pm.setAttr(left_falseR, 0)
    pm.setAttr(exagerate_multi2X, -30)
    pm.setAttr(exagerate_multi2Y, -30)
    pm.connectAttr(right_transY, right_trueR)
    pm.connectAttr(right_transY, right_firstTerm)
    pm.connectAttr(right_sneer_attr, right_sneer_apply)
    pm.connectAttr(right_condition_outR, right_sneer_multi)
    pm.connectAttr(right_sneerMulti_out, right_sneer_exagerate)
    pm.connectAttr(right_exagerate_out, right_cluster_inX)
    pm.setAttr(right_falseR, 0)
    ##parent under parent
    pm.parent(left_trans, parent_group)
    pm.parent(right_trans, parent_group)
    ##return controls
    return (left_ctrl[0], right_ctrl[0])

def create_dynamic_brows():
    ##parent group
    parent_group = pm.group(empty=True, name='BrowControls_parent')
    ae.create_labels(parent_group, 'NA', 'BrowControls', 'follow_head_grp')
    ##gather needed elements
    face_curves = []
    left_ctrl_locations = []
    right_ctrl_locations = []
    ##find nostril curves
    curves = pm.ls(type='nurbsCurve')
    for curve in curves:
        curve_trans = pm.listRelatives(curve, parent=True)
        face_curves.append(curve_trans)
    face_curves = ae.clean_list_doops(face_curves)
    for curve in face_curves:
        if ae.check_type(curve) == 'curve':
            if ae.check_object(curve) == 'Brow':
                if ae.check_side(curve) == 'Right':
                    right_brow = curve
                if ae.check_side(curve) == 'Left':
                    left_brow = curve
    ##get all transforms to sort through
    all_trans = pm.ls(type='transform')
    labeled_trans = []
    ##do a quick check to only grab labeled trans
    for possible_trans in all_trans:
        if ae.check_attr_exists(possible_trans) == True:
            labeled_trans.append(possible_trans)
    ##grab start, end and middle cluster controls
    for trans in labeled_trans:
        if ae.check_type(trans) == 'cluster_ctrl':
            if ae.check_object(trans) == 'Brow_cluster1':
                if ae.check_side(trans) == 'Right':
                    right_start_ctrl = trans
                if ae.check_side(trans) == 'Left':
                    left_start_ctrl = trans
            if ae.check_object(trans) == 'Brow_cluster5':
                if ae.check_side(trans) == 'Right':
                    right_end_ctrl = trans
                if ae.check_side(trans) == 'Left':
                    left_end_ctrl = trans
            if ae.check_object(trans) == 'Brow_cluster3':
                if ae.check_side(trans) == 'Right':
                    right_mid_loc = trans
                if ae.check_side(trans) == 'Left':
                    left_mid_loc = trans
    ##determine order of cluster controls from inner to outer using same method as lips
    if ae.get_xPos_cvs(right_brow) == 'UpperHalf':
        right_outer_loc = right_end_ctrl
        right_inner_loc = right_start_ctrl
    if ae.get_xPos_cvs(right_brow) == 'LowerHalf':
        right_outer_loc = right_start_ctrl
        right_inner_loc = right_end_ctrl
    if ae.get_xPos_cvs(left_brow) == 'LowerHalf':
        left_outer_loc = left_end_ctrl
        left_inner_loc = left_start_ctrl
    if ae.get_xPos_cvs(left_brow) == 'UpperHalf':
        left_outer_loc = left_start_ctrl
        left_inner_loc = left_end_ctrl
    right_ctrl_locations.append(right_outer_loc)
    right_ctrl_locations.append(right_inner_loc)
    right_ctrl_locations.append(right_mid_loc)
    left_ctrl_locations.append(left_outer_loc)
    left_ctrl_locations.append(left_inner_loc)
    left_ctrl_locations.append(left_mid_loc)
    ##create contols for right side
    for loc in right_ctrl_locations:
        if loc == right_outer_loc:
            position = 'outer'
        if loc == right_mid_loc:
            position = 'mid'
        if loc == right_inner_loc:
            position = 'inner'
        trans_grp = pm.group(empty=True, name='Brow_right_'+position+'_trans')
        ae.create_labels(trans_grp, 'Right', 'Brow_'+position, 'trans_grp')
        auto_grp = pm.group(empty=True, name='Brow_right_'+position+'_auto')
        ae.create_labels(auto_grp, 'Right', 'Brow_'+position, 'auto_grp')
        ctrl_obj = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='Brow_right_'+position)
        ae.create_labels(ctrl_obj, 'Right', 'Brow_'+position, 'ctrl')
        if loc == right_mid_loc:
            right_mid_auto = auto_grp
            right_mid_ctrl = ctrl_obj
        if loc == right_inner_loc:
            right_inner_auto = auto_grp
            right_inner_ctrl = ctrl_obj
        if loc == right_outer_loc:
            right_outer_ctrl = ctrl_obj
        ##apply material
        ms.apply_material(ctrl_obj, Red)
        ##place properly for orientation
        pm.rotate(ctrl_obj, [-90,0,0])
        pm.makeIdentity(ctrl_obj, apply=True, rotate=True)
        pm.parent(ctrl_obj, auto_grp)
        pm.parent(auto_grp, trans_grp)
        ##constrain trans
        constraint = pm.parentConstraint(loc, trans_grp)
        pm.delete(constraint)
        ##parent trans under parent 
        pm.parent(trans_grp, parent_group)
    for loc in left_ctrl_locations:
        if loc == left_outer_loc:
            position = 'outer'
        if loc == left_mid_loc:
            position = 'mid'
        if loc == left_inner_loc:
            position = 'inner'
        trans_grp = pm.group(empty=True, name='Brow_left_'+position+'_trans')
        ae.create_labels(trans_grp, 'Left', 'Brow_'+position, 'trans_grp')
        auto_grp = pm.group(empty=True, name='Brow_left_'+position+'_auto')
        ae.create_labels(auto_grp, 'Left', 'Brow_'+position, 'auto_grp')
        ctrl_obj = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='Brow_left_'+position)
        ae.create_labels(ctrl_obj, 'Left', 'Brow_'+position, 'ctrl')
        if loc == left_mid_loc:
            left_mid_auto = auto_grp
            left_mid_ctrl = ctrl_obj
        if loc == left_inner_loc:
            left_inner_auto = auto_grp
            left_inner_ctrl = ctrl_obj
        if loc == left_outer_loc:
            left_outer_ctrl = ctrl_obj
        ##apply material
        ms.apply_material(ctrl_obj, Blue)
        ##place properly for orientation
        pm.rotate(ctrl_obj, [-90,0,0])
        pm.makeIdentity(ctrl_obj, apply=True, rotate=True)
        pm.parent(ctrl_obj, auto_grp)
        pm.parent(auto_grp, trans_grp)
        ##constrain trans
        constraint = pm.parentConstraint(loc, trans_grp)
        pm.delete(constraint)
        ##parent trans under parent 
        pm.parent(trans_grp, parent_group)
    ##Control in the middle
    trans_center = pm.group(empty=True, name='Brow_center_trans')
    ae.create_labels(trans_center, 'Center', 'Brow_center', 'trans_grp')
    auto_center = pm.group(empty=True, name='Brow_center_auto')
    ae.create_labels(auto_center, 'Center', 'Brow_center', 'auto_grp')
    ctrl_center = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='Brow_center')
    ae.create_labels(ctrl_center, 'Center', 'Brow_center', 'ctrl')
    ##apply material
    ms.apply_material(ctrl_center, Yellow)
    ##place properly for orientation
    pm.rotate(ctrl_center, [-90,0,0])
    pm.makeIdentity(ctrl_center, apply=True, rotate=True)
    pm.parent(ctrl_center, auto_center)
    pm.parent(auto_center, trans_center)
    ##constrain trans
    constraint = pm.parentConstraint(left_inner_loc, right_inner_loc, trans_center)
    pm.delete(constraint)
    ####Automation from the center brow
    ##lock center brow attributes that aren't needed
    pm.setAttr(str(ctrl_center[0])+'.tx', lock=True)
    pm.setAttr(str(ctrl_center[0])+'.tz', lock=True)
    pm.setAttr(str(ctrl_center[0])+'.rx', lock=True)
    pm.setAttr(str(ctrl_center[0])+'.ry', lock=True)
    pm.setAttr(str(ctrl_center[0])+'.rz', lock=True)
    ##Create needed nodes
    in_out_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='BrowFurrow_multi')
    in_out_condition = pm.shadingNode('condition', asUtility=True, name='BrowFurrowAmount_condition')
    reverse_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='BrowFurrow_reverse_multi')
    furrow_amount_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='BrowFurrowApply_multi')
    furrow_percent_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='BrowFurrowPercent_multi')
    up_down_percent_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='BrowFollowPercent_multi')
    ##Create attribute for furrow apply
    pm.addAttr(ctrl_center[0], ln='Furrow_Amount', attributeType='double', min=0, max=5, defaultValue=1, k=True)
    apply_furrow = str(ctrl_center[0]) + '.Furrow_Amount'
    ##connect needed attributes
    pm.connectAttr(str(ctrl_center[0])+'.ty', str(in_out_condition)+'.firstTerm')
    pm.setAttr(str(in_out_condition)+'.operation', 5)
    pm.setAttr(str(in_out_condition)+'.colorIfFalseR', 0.15)
    pm.setAttr(str(in_out_condition)+'.colorIfTrueR', 0.25)
    pm.connectAttr(str(in_out_condition)+'.outColorR', str(furrow_amount_multi)+'.input1X')
    pm.connectAttr(apply_furrow, str(furrow_amount_multi)+'.input2X')
    pm.connectAttr(str(furrow_amount_multi)+'.outputX', str(reverse_multi)+'.input1X')
    pm.setAttr(str(reverse_multi)+'.input2X', -1)
    pm.connectAttr(str(reverse_multi)+'.outputX', str(in_out_multi)+'.input2Y')
    pm.connectAttr(str(furrow_amount_multi)+'.outputX', str(in_out_multi)+'.input2X')
    pm.connectAttr(str(ctrl_center[0])+'.ty', str(in_out_multi)+'.input1X')
    pm.connectAttr(str(ctrl_center[0])+'.ty', str(in_out_multi)+'.input1Y')
    pm.connectAttr(str(in_out_multi)+'.outputX', str(left_inner_auto)+'.tx')
    pm.connectAttr(str(in_out_multi)+'.outputY', str(right_inner_auto)+'.tx')
    pm.connectAttr(str(ctrl_center[0])+'.ty', str(left_inner_auto)+'.ty')
    pm.connectAttr(str(ctrl_center[0])+'.ty', str(right_inner_auto)+'.ty')
    pm.connectAttr(str(reverse_multi)+'.outputX', str(furrow_percent_multi)+'.input1X')
    pm.connectAttr(str(furrow_amount_multi)+'.outputY', str(furrow_percent_multi)+'.input1Y')
    pm.setAttr(str(furrow_percent_multi)+'.input2X', 0.25)
    pm.setAttr(str(furrow_percent_multi)+'.input2Y', 0.25)
    #pm.connectAttr(str(furrow_percent_multi)+'.outputX', str(left_mid_auto)+'.tx')
    #pm.connectAttr(str(furrow_percent_multi)+'.outputY', str(right_mid_auto)+'.tx')
    pm.connectAttr(str(ctrl_center[0])+'.ty', str(up_down_percent_multi)+'.input1X')
    pm.setAttr(str(up_down_percent_multi)+'.input2X', .25)
    pm.connectAttr(str(up_down_percent_multi)+'.outputX', str(right_mid_auto)+'.ty')
    pm.connectAttr(str(up_down_percent_multi)+'.outputX', str(left_mid_auto)+'.ty')
    ##parent center to parent group
    pm.parent(trans_center, parent_group)
    ##return all controls
    return (left_inner_ctrl[0], left_mid_ctrl[0], left_outer_ctrl[0], right_inner_ctrl[0], right_mid_ctrl[0], right_outer_ctrl[0])

def create_dynamic_eyelids():
    ##parent group
    parent_group = pm.group(empty=True, name='EyelidControls_parent')
    ae.create_labels(parent_group, 'NA', 'EyelidControls', 'follow_head_grp')
    ##grab needed elements
    face_curves=[]
    ##find nostril curves
    curves = pm.ls(type='nurbsCurve')
    for curve in curves:
        curve_trans = pm.listRelatives(curve, parent=True)
        face_curves.append(curve_trans)
    face_curves = ae.clean_list_doops(face_curves)
    for curve in face_curves:
        if ae.check_type(curve) == 'curve':
            if ae.check_object(curve) == 'UpperEyelid':
                if ae.check_side(curve) == 'Right':
                    right_upper_lid = curve
                if ae.check_side(curve) == 'Left':
                    left_upper_lid = curve
            if ae.check_object(curve) == 'LowerEyelid':
                if ae.check_side(curve) == 'Right':
                    right_lower_lid = curve
                if ae.check_side(curve) == 'Left':
                    left_lower_lid = curve
    ##get all transforms to sort through
    all_trans = pm.ls(type='transform')
    labeled_trans = []
    ##do a quick check to only grab labeled trans
    for possible_trans in all_trans:
        if ae.check_attr_exists(possible_trans) == True:
            labeled_trans.append(possible_trans)
    ##grab start, end and middle cluster controls
    for trans in labeled_trans:
        if ae.check_type(trans) == 'detail_ctrl':
            if ae.check_object(trans) == 'UpperEyelid_mid_follow':
                if ae.check_side(trans) == 'Right':
                    right_upper_loc = trans
                if ae.check_side(trans) == 'Left':
                    left_upper_loc = trans
            if ae.check_object(trans) == 'LowerEyelid_mid_follow':
                if ae.check_side(trans) == 'Right':
                    right_lower_loc = trans
                if ae.check_side(trans) == 'Left':
                    left_lower_loc = trans
     ##grab lip parent joint
    all_joints = pm.ls(type='joint')
    for joint in all_joints:
        if ae.check_object(joint) == 'Eye':
            if ae.check_side(joint) == 'Right':
                right_eye = joint
            if ae.check_side(joint) == 'Left':
                left_eye = joint
    ##create joint and constrain it to both upper, and lower outer lip follow controls on each side
    left_upper_end = pm.joint()
    ##clear selection to avoid unwanted parenting of joints
    pm.select(clear=True)
    left_constraint = pm.parentConstraint(left_upper_loc, left_upper_end)
    pm.delete(left_constraint)
    right_upper_end = pm.joint()
    pm.select(clear=True)
    right_constraint = pm.parentConstraint(right_upper_loc, right_upper_end)
    pm.delete(right_constraint)
    ##duplicate lip parent
    left_upper_doop = pm.duplicate(left_eye)
    right_upper_doop = pm.duplicate(right_eye)
    ##parent the joints
    pm.parent(right_upper_end, right_upper_doop)
    pm.parent(left_upper_end, left_upper_doop)
    ##orient the joints
    pm.joint(left_upper_doop, edit=True, orientJoint='zyx', secondaryAxisOrient= 'yup', zeroScaleOrient=True)
    pm.joint(right_upper_doop, edit=True, orientJoint='zyx', secondaryAxisOrient= 'yup', zeroScaleOrient=True)
    ##create a control object with all groups properly parented
    left_upper_trans = pm.group(empty=True, name='UpperEyelid_left_trans')
    ae.create_labels(left_upper_trans, 'Left', 'UpperEyelid', 'trans_grp')
    left_upper_auto = pm.group(empty=True, name='UpperEyelid_left_auto')
    ae.create_labels(left_upper_auto, 'Left', 'UpperEyelid', 'auto_grp')
    left_upper_ctrl = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='UpperEyelid_Left')
    ae.create_labels(left_upper_ctrl, 'Left', 'UpperEyelid', 'ctrl')
    ##apply material
    ms.apply_material(left_upper_ctrl, Blue)
    ##place properly for orientation
    pm.rotate(left_upper_ctrl, [-90,0,0])
    pm.makeIdentity(left_upper_ctrl, apply=True, rotate=True)
    pm.parent(left_upper_ctrl, left_upper_auto)
    pm.parent(left_upper_auto, left_upper_trans)
    ##constrain trans
    left_constraint = pm.parentConstraint(left_upper_doop, left_upper_trans)
    pm.delete(left_constraint)
    pm.matchTransform(left_upper_trans, left_upper_end)
    ##do right side
    right_upper_trans = pm.group(empty=True, name='UpperEyelid_right_trans')
    ae.create_labels(right_upper_trans, 'Right', 'UpperEyelid', 'trans_grp')
    right_upper_auto = pm.group(empty=True, name='UpperEyelid_right_auto')
    ae.create_labels(right_upper_auto, 'Right', 'UpperEyelid', 'auto_grp')
    right_upper_ctrl = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='UpperEyelid_Right')
    ae.create_labels(right_upper_ctrl, 'Right', 'UpperEyelid', 'ctrl')
    ##apply material
    ms.apply_material(right_upper_ctrl, Red)
    ##place properly for orientation
    pm.rotate(right_upper_ctrl, [-90,0,0])
    pm.makeIdentity(right_upper_ctrl, apply=True, rotate=True)
    pm.parent(right_upper_ctrl, right_upper_auto)
    pm.parent(right_upper_auto, right_upper_trans)
    ##constrain trans
    right_constraint = pm.parentConstraint(right_upper_doop, right_upper_trans)
    pm.delete(right_constraint)
    pm.matchTransform(right_upper_trans, right_upper_end)
    ##move just position to end joint
    left_point = pm.pointConstraint(left_upper_end, left_upper_trans)
    right_point = pm.pointConstraint(right_upper_end, right_upper_trans)
    pm.delete(left_point)
    pm.delete(right_point)
    ##move pivot back to lip parent doop
    snap_to_pivot(left_upper_doop, [left_upper_trans, left_upper_auto, left_upper_ctrl])
    snap_to_pivot(right_upper_doop, [right_upper_trans, right_upper_auto, right_upper_ctrl])
    ##delete any constraints and joints
    pm.delete(right_upper_doop)
    pm.delete(left_upper_doop)

    ##create joint and constrain it to both upper, and lower outer lip follow controls on each side
    left_lower_end = pm.joint()
    ##clear selection to avoid unwanted parenting of joints
    pm.select(clear=True)
    left_constraint = pm.parentConstraint(left_lower_loc, left_lower_end)
    pm.delete(left_constraint)
    right_lower_end = pm.joint()
    pm.select(clear=True)
    right_constraint = pm.parentConstraint(right_lower_loc, right_lower_end)
    pm.delete(right_constraint)
    ##duplicate lip parent
    left_lower_doop = pm.duplicate(left_eye)
    right_lower_doop = pm.duplicate(right_eye)
    ##parent the joints
    pm.parent(right_lower_end, right_lower_doop)
    pm.parent(left_lower_end, left_lower_doop)
    ##orient the joints
    pm.joint(left_lower_doop, edit=True, orientJoint='zyx', secondaryAxisOrient= 'yup', zeroScaleOrient=True)
    pm.joint(right_lower_doop, edit=True, orientJoint='zyx', secondaryAxisOrient= 'yup', zeroScaleOrient=True)
    ##create a control object with all groups properly parented
    left_lower_trans = pm.group(empty=True, name='LowerEyelid_left_trans')
    ae.create_labels(left_lower_trans, 'Left', 'LowerEyelid', 'trans_grp')
    left_lower_auto = pm.group(empty=True, name='LowerEyelid_left_auto')
    ae.create_labels(left_lower_auto, 'Left', 'LowerEyelid', 'auto_grp')
    left_lower_ctrl = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='LowerEyelid_Left')
    ae.create_labels(left_lower_ctrl, 'Left', 'LowerEyelid', 'ctrl')
    ##apply material
    ms.apply_material(left_lower_ctrl, Blue)
    ##place properly for orientation
    pm.rotate(left_lower_ctrl, [-90,0,0])
    pm.makeIdentity(left_lower_ctrl, apply=True, rotate=True)
    pm.parent(left_lower_ctrl, left_lower_auto)
    pm.parent(left_lower_auto, left_lower_trans)
    ##constrain trans
    left_constraint = pm.parentConstraint(left_lower_doop, left_lower_trans)
    pm.delete(left_constraint)
    pm.matchTransform(left_lower_trans, left_lower_end)
    ##do right side
    right_lower_trans = pm.group(empty=True, name='LowerEyelid_right_trans')
    ae.create_labels(right_lower_trans, 'Right', 'LowerEyelid', 'trans_grp')
    right_lower_auto = pm.group(empty=True, name='LowerEyelid_right_auto')
    ae.create_labels(right_lower_auto, 'Right', 'LowerEyelid', 'auto_grp')
    right_lower_ctrl = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='LowerEyelid_Right')
    ae.create_labels(right_lower_ctrl, 'Right', 'LowerEyelid', 'ctrl')
    ##apply material
    ms.apply_material(right_lower_ctrl, Red)
    ##place properly for orientation
    pm.rotate(right_lower_ctrl, [-90,0,0])
    pm.makeIdentity(right_lower_ctrl, apply=True, rotate=True)
    pm.parent(right_lower_ctrl, right_lower_auto)
    pm.parent(right_lower_auto, right_lower_trans)
    ##constrain trans
    right_constraint = pm.parentConstraint(right_lower_doop, right_lower_trans)
    pm.delete(right_constraint)
    pm.matchTransform(right_lower_trans, right_lower_end)
    ##move just position to end joint
    left_point = pm.pointConstraint(left_lower_end, left_lower_trans)
    right_point = pm.pointConstraint(right_lower_end, right_lower_trans)
    pm.delete(left_point)
    pm.delete(right_point)
    ##move pivot back to lip parent doop
    snap_to_pivot(left_lower_doop, [left_lower_trans, left_lower_auto, left_lower_ctrl])
    snap_to_pivot(right_lower_doop, [right_lower_trans, right_lower_auto, right_lower_ctrl])
    ##delete any constraints and joints
    pm.delete(right_lower_doop)
    pm.delete(left_lower_doop)
    
    ####Create automation in the rotation of the eye controls
    ##create attributes
    pm.addAttr(right_upper_ctrl[0], ln='Eye_Follow_Amount', attributeType='double', min=0, max=1, defaultValue=.5, k=True)
    pm.addAttr(left_upper_ctrl[0], ln='Eye_Follow_Amount', attributeType='double', min=0, max=1, defaultValue=.5, k=True)
    pm.addAttr(right_lower_ctrl[0], ln='Eye_Follow_Amount', attributeType='double', min=0, max=1, defaultValue=.5, k=True)
    pm.addAttr(left_lower_ctrl[0], ln='Eye_Follow_Amount', attributeType='double', min=0, max=1, defaultValue=.5, k=True)
    right_upper_follow_attr = str(right_upper_ctrl[0])+'.Eye_Follow_Amount'
    left_upper_follow_attr = str(left_upper_ctrl[0])+'.Eye_Follow_Amount'
    right_lower_follow_attr = str(right_lower_ctrl[0])+'.Eye_Follow_Amount'
    left_lower_follow_attr = str(left_lower_ctrl[0])+'.Eye_Follow_Amount'
    ##Create needed node
    right_upper_multi = pm.shadingNode('multiplyDivide', asUtility = True, name='Right_UpperEyelid_follow_multi')
    left_upper_multi = pm.shadingNode('multiplyDivide', asUtility = True, name='Left_UpperEyelid_follow_multi')
    right_lower_multi = pm.shadingNode('multiplyDivide', asUtility = True, name='Right_LowerEyelid_follow_multi')
    left_lower_multi = pm.shadingNode('multiplyDivide', asUtility = True, name='Left_LowerEyelid_follow_multi')
    ##Connect nodes
    pm.connectAttr(right_upper_follow_attr, str(right_upper_multi)+'.input2X')
    pm.connectAttr(right_upper_follow_attr, str(right_upper_multi)+'.input2Y')
    pm.connectAttr(right_upper_follow_attr, str(right_upper_multi)+'.input2Z')
    pm.connectAttr(str(right_eye)+'.rotate', str(right_upper_multi)+'.input1')
    pm.connectAttr(str(right_upper_multi)+'.output', str(right_upper_auto)+'.rotate')

    pm.connectAttr(left_upper_follow_attr, str(left_upper_multi)+'.input2X')
    pm.connectAttr(left_upper_follow_attr, str(left_upper_multi)+'.input2Y')
    pm.connectAttr(left_upper_follow_attr, str(left_upper_multi)+'.input2Z')
    pm.connectAttr(str(left_eye)+'.rotate', str(left_upper_multi)+'.input1')
    pm.connectAttr(str(left_upper_multi)+'.output', str(left_upper_auto)+'.rotate')

    pm.connectAttr(right_lower_follow_attr, str(right_lower_multi)+'.input2X')
    pm.connectAttr(right_lower_follow_attr, str(right_lower_multi)+'.input2Y')
    pm.connectAttr(right_lower_follow_attr, str(right_lower_multi)+'.input2Z')
    pm.connectAttr(str(right_eye)+'.rotate', str(right_lower_multi)+'.input1')
    pm.connectAttr(str(right_lower_multi)+'.output', str(right_lower_auto)+'.rotate')

    pm.connectAttr(left_lower_follow_attr, str(left_lower_multi)+'.input2X')
    pm.connectAttr(left_lower_follow_attr, str(left_lower_multi)+'.input2Y')
    pm.connectAttr(left_lower_follow_attr, str(left_lower_multi)+'.input2Z')
    pm.connectAttr(str(left_eye)+'.rotate', str(left_lower_multi)+'.input1')
    pm.connectAttr(str(left_lower_multi)+'.output', str(left_lower_auto)+'.rotate')
    ##parent controls 
    pm.parent(left_upper_trans, parent_group)
    pm.parent(left_lower_trans, parent_group)
    pm.parent(right_upper_trans, parent_group)
    pm.parent(right_lower_trans, parent_group)
    ##return controls
    return (left_upper_ctrl[0], left_lower_ctrl[0], right_upper_ctrl[0], right_lower_ctrl[0])

def create_dynamic_squint():
    ##squint parent group
    squint_parent = pm.group(empty=True, name='SquintControls_parent')
    ae.create_labels(squint_parent, 'NA', 'SquintControls', 'follow_head_grp')
    face_curves=[]
    ##find nostril curves
    curves = pm.ls(type='nurbsCurve')
    for curve in curves:
        curve_trans = pm.listRelatives(curve, parent=True)
        face_curves.append(curve_trans)
    face_curves = ae.clean_list_doops(face_curves)
    for curve in face_curves:
        if ae.check_type(curve) == 'curve':
            if ae.check_object(curve) == 'Squint':
                if ae.check_side(curve) == 'Right':
                    right_squint = curve
                if ae.check_side(curve) == 'Left':
                    left_squint = curve
    ##get all transforms to sort through
    all_trans = pm.ls(type='transform')
    labeled_trans = []
    ##do a quick check to only grab labeled trans
    for possible_trans in all_trans:
        if ae.check_attr_exists(possible_trans) == True:
            labeled_trans.append(possible_trans)
    ##grab start, end and middle cluster controls
    for trans in labeled_trans:
        if ae.check_type(trans) == 'cluster_ctrl':
            if ae.check_object(trans) == 'Squint_cluster3':
                if ae.check_side(trans) == 'Right':
                    right_loc = trans
                if ae.check_side(trans) == 'Left':
                    left_loc = trans
    ##Right Controller
    right_trans = pm.group(empty=True, name='Squint_right_trans')
    ae.create_labels(right_trans, 'Right', 'Squint', 'trans_grp')
    right_auto = pm.group(empty=True, name='Brow_right_auto')
    ae.create_labels(right_auto, 'Right', 'Squint', 'auto_grp')
    right_ctrl = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='Squint_right')
    ae.create_labels(right_ctrl, 'Right', 'Squint', 'ctrl')
    ##apply material
    ms.apply_material(right_ctrl, Red)
    ##place properly for orientation
    pm.rotate(right_ctrl, [-90,0,0])
    pm.makeIdentity(right_ctrl, apply=True, rotate=True)
    pm.parent(right_ctrl, right_auto)
    pm.parent(right_auto, right_trans)
    ##constrain trans
    constraint = pm.parentConstraint(right_loc, right_trans)
    pm.delete(constraint)
    ##Left Contoller
    left_trans = pm.group(empty=True, name='Squint_left_trans')
    ae.create_labels(left_trans, 'Left', 'Squint', 'trans_grp')
    left_auto = pm.group(empty=True, name='Brow_left_auto')
    ae.create_labels(left_auto, 'Left', 'Squint', 'auto_grp')
    left_ctrl = pm.polyCone(radius=.3, height=.75, subdivisionsX=10, name='Squint_left')
    ae.create_labels(left_ctrl, 'Left', 'Squint', 'ctrl')
    ##apply material
    ms.apply_material(left_ctrl, Blue)
    ##place properly for orientation
    pm.rotate(left_ctrl, [-90,0,0])
    pm.makeIdentity(left_ctrl, apply=True, rotate=True)
    pm.parent(left_ctrl, left_auto)
    pm.parent(left_auto, left_trans)
    ##constrain trans
    constraint = pm.parentConstraint(left_loc, left_trans)
    pm.delete(constraint)
    ###Hook up automation in link dynamic controls
    pm.parent(left_trans, squint_parent)
    pm.parent(right_trans, squint_parent)
    return (left_ctrl[0], right_ctrl[0])

##create clusters that aid in the dynamic editing of this rig, also adjusts weights for clusters
def dynamic_setup(doop_curves, mouth_elements, nostril_elements, squint_elements, brow_elements, eyelid_elements): 
    ##dynamic clusters group and list
    dynamic_clusters_grp = pm.group(empty=True, name='CurveClusters_grp')
    ae.create_labels(dynamic_clusters_grp, 'NA', 'CurveJoints', 'parent_grp')
    pm.setAttr(str(dynamic_clusters_grp) + '.visibility', 0)
    ##grab mouth elements
    corner_ctrls = mouth_elements
    left_corner = corner_ctrls[0]
    right_corner = corner_ctrls[1]
    upper_center = corner_ctrls[2]
    lower_center = corner_ctrls[3]
    lower_outG_attr = corner_ctrls[4]
    upper_outG_attr = corner_ctrls[5]
    ##grab nostril elements
    right_nostril_ctrl = nostril_elements[1]
    left_nostril_ctrl = nostril_elements[0]
    ##grab squint elements
    left_squint_ctrl = squint_elements[0]
    right_squint_ctrl = squint_elements[1]
    ##grab brow elements 
    left_inner_brow = brow_elements[0]
    left_mid_brow = brow_elements[1]
    left_outer_brow = brow_elements[2]
    right_inner_brow = brow_elements[3]
    right_mid_brow = brow_elements[4]
    right_outer_brow = brow_elements[5]
    #grab eyelid elements
    left_upperLid_ctrl = eyelid_elements[0]
    left_lowerLid_ctrl = eyelid_elements[1]
    right_upperLid_ctrl = eyelid_elements[2]
    right_lowerLid_ctrl = eyelid_elements[3]
    ##grab needed elements of mouth and eyelids for properly placing joints
    all_joints = pm.ls(type='joint')
    for jnt in all_joints:
        if ae.check_object(jnt) == 'Head':
            head_joint = jnt
        '''
        if ae.check_type(jnt) == 'detail_jnt':
            if ae.check_object(jnt) == 'LowerLip_outer_follow':
                if ae.check_side(jnt) == 'Left':
                    left_lower_lip_outer_loc = jnt
                if ae.check_side(jnt) == 'Right':
                    right_lower_lip_outer_loc = jnt
            if ae.check_object(jnt) == 'UpperLip_outer_follow':
                if ae.check_side(jnt) == 'Left':
                    left_upper_lip_outer_loc = jnt
                if ae.check_side(jnt) == 'Right':
                    right_upper_lip_outer = jnt
            if ae.check_object(jnt) == 'UpperLip_mid_follow':
                upper_lip_center_loc = jnt
            if ae.check_object(jnt) == 'LowerLip_mid_follow':
                lower_lip_center_loc = jnt
            ##Eyelid joints needed
            if ae.check_object(jnt) == 'LowerEyelid_mid_follow':
                if ae.check_side(jnt) == 'Left':
                    left_eye_lowerLid_loc = jnt
                if ae.check_side(jnt) == 'Right':
                    right_eye_lowerLid_loc = jnt
            if ae.check_object(jnt) == 'UpperEyelid_mid_follow':
                if ae.check_side(jnt) == 'Left':
                    left_eye_upperLid_loc = jnt
        '''
    ##crete two joints for lip corners
    left_mouth_joint = pm.joint(name='LeftMouthCorner_jnt')
    ae.create_labels(left_mouth_joint, 'Left', 'LeftMouthCorner', 'curve_jnt')
    pm.select(clear=True)
    right_mouth_joint = pm.joint(name='RightMouthCorner_jnt')
    ae.create_labels(right_mouth_joint, 'Right', 'RightMouthCorner', 'curve_jnt')
    pm.select(clear=True)
    pm.parent(left_mouth_joint, dynamic_clusters_grp)
    pm.parent(right_mouth_joint, dynamic_clusters_grp)
    pm.pointConstraint(right_corner, right_mouth_joint)
    pm.pointConstraint(left_corner, left_mouth_joint)
    pm.orientConstraint(right_corner, right_mouth_joint, mo=True)
    pm.orientConstraint(left_corner, left_mouth_joint, mo=True)

    ##create a doop of the head joint to hold static skin weights
    static_joint = pm.duplicate(head_joint)
    ae.replace_labels(static_joint, 'Center', 'StaticHolder', 'curve_jnt')
    ##delete duplicated children
    for child in pm.listRelatives(static_joint, children=True):
        pm.delete(child)
    static_joint = static_joint[0]
    pm.parent(static_joint, w=True)
    pm.parent(static_joint, dynamic_clusters_grp)
    pm.parentConstraint(head_joint, static_joint)

    for curve in doop_curves:
        ##get labels for the curve being operated on
        #print (curve)
        obj = ae.check_object(curve)
        side = ae.check_side(curve)
        ##for upper lip do certain clustering, and adjust cv cluster weight 
        if obj == 'UpperLip':
            ##create center joint
            center_joint = pm.joint(name='UpperLip_jnt')
            ae.create_labels(center_joint, 'Center', 'UpperLip', 'curve_jnt')
            pm.select(clear=True)
            ##parent clusters under cluster group
            pm.parent(center_joint, dynamic_clusters_grp)
            ##change the pivot of the clusters to the lip corners
            pm.pointConstraint(upper_center, center_joint)
            pm.orientConstraint(upper_center, center_joint, mo=True)
            ##skin the upper lip curve to the joints
            curve_skin = pm.skinCluster(left_mouth_joint, right_mouth_joint, center_joint, curve, mi=3)
            ##if the lower cv values are positive weight them one way
            if ae.get_xPos_cvs(curve) == 'UpperHalf':
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(left_mouth_joint), 1),(str(center_joint),0),(str(right_mouth_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(left_mouth_joint), .65),(str(center_joint),.35),(str(right_mouth_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(left_mouth_joint), .25),(str(center_joint),.75),(str(right_mouth_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(left_mouth_joint), .05),(str(center_joint),.9),(str(right_mouth_joint),.05)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(left_mouth_joint), 0),(str(center_joint),.75),(str(right_mouth_joint),.25)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[5]', transformValue = [(str(left_mouth_joint), 0),(str(center_joint),.35),(str(right_mouth_joint),.65)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[6]', transformValue = [(str(left_mouth_joint), 0),(str(center_joint),0),(str(right_mouth_joint),1)])
            if ae.get_xPos_cvs(curve) == 'LowerHalf':
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[6]', transformValue = [(str(left_mouth_joint), 1),(str(center_joint),0),(str(right_mouth_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[5]', transformValue = [(str(left_mouth_joint), .65),(str(center_joint),.35),(str(right_mouth_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(left_mouth_joint), .25),(str(center_joint),.75),(str(right_mouth_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(left_mouth_joint), .05),(str(center_joint),.9),(str(right_mouth_joint),.05)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(left_mouth_joint), 0),(str(center_joint),.75),(str(right_mouth_joint),.25)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(left_mouth_joint), 0),(str(center_joint),.35),(str(right_mouth_joint),.65)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(left_mouth_joint), 0),(str(center_joint),0),(str(right_mouth_joint),1)])
            ##connect attribute from automation
            pm.connectAttr(upper_outG_attr, str(center_joint)+'.scaleX')
            continue
        if obj == 'LowerLip':
            ##crete two clusters for lip curves
            center_joint = pm.joint(name='LowerLip_jnt')
            ae.create_labels(center_joint, 'Center', 'LowerLip', 'curve_jnt')
            pm.select(clear=True)
            ##parent clusters under cluster group
            pm.parent(center_joint, dynamic_clusters_grp)
            ##change the pivot of the clusters to the lip corners
            pm.pointConstraint(lower_center, center_joint)
            pm.orientConstraint(lower_center, center_joint, mo=True)
            ##skin the upper lip curve to the joints
            curve_skin = pm.skinCluster(left_mouth_joint, right_mouth_joint, center_joint, curve, mi=3)
            ##if the lower cv values are positive weight them one way
            if ae.get_xPos_cvs(curve) == 'UpperHalf':
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(left_mouth_joint), 1),(str(center_joint),0),(str(right_mouth_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(left_mouth_joint), .65),(str(center_joint),.35),(str(right_mouth_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(left_mouth_joint), .25),(str(center_joint),.75),(str(right_mouth_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(left_mouth_joint), .05),(str(center_joint),.9),(str(right_mouth_joint),.05)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(left_mouth_joint), 0),(str(center_joint),.75),(str(right_mouth_joint),.25)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[5]', transformValue = [(str(left_mouth_joint), 0),(str(center_joint),.35),(str(right_mouth_joint),.65)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[6]', transformValue = [(str(left_mouth_joint), 0),(str(center_joint),0),(str(right_mouth_joint),1)])
            if ae.get_xPos_cvs(curve) == 'LowerHalf':
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[6]', transformValue = [(str(left_mouth_joint), 1),(str(center_joint),0),(str(right_mouth_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[5]', transformValue = [(str(left_mouth_joint), .65),(str(center_joint),.35),(str(right_mouth_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(left_mouth_joint), .25),(str(center_joint),.75),(str(right_mouth_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(left_mouth_joint), .05),(str(center_joint),.9),(str(right_mouth_joint),.05)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(left_mouth_joint), 0),(str(center_joint),.75),(str(right_mouth_joint),.25)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(left_mouth_joint), 0),(str(center_joint),.35),(str(right_mouth_joint),.65)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(left_mouth_joint), 0),(str(center_joint),0),(str(right_mouth_joint),1)])
            ##connect attribute from automation
            pm.connectAttr(lower_outG_attr, str(center_joint)+'.scaleX')
            continue
        if obj == 'Cheek':
            if side == 'Right': 
                side_joint = right_mouth_joint
            if side == 'Left':
                side_joint = left_mouth_joint
            ##create skin cluster
            curve_skin = pm.skinCluster(side_joint, static_joint, curve, mi=3)
            ##weight skin cluster based on construction
            if ae.get_low_cvs(curve) == 'Zero': 
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(side_joint), .8),(str(static_joint),.2)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(side_joint), .6),(str(static_joint),.4)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(side_joint), .4),(str(static_joint),.6)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(side_joint), .2),(str(static_joint),.8)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(side_joint), 0),(str(static_joint),1)])
            if ae.get_low_cvs(curve) == 'One': 
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(side_joint), .8),(str(static_joint),.2)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(side_joint), .6),(str(static_joint),.4)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(side_joint), .4),(str(static_joint),.6)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(side_joint), .2),(str(static_joint),.8)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(side_joint), 0),(str(static_joint),1)])
            continue
        if obj == 'Laugh':
            if side == 'Right': 
                side_joint = right_mouth_joint
            if side == 'Left':
                side_joint = left_mouth_joint
            ##create skin cluster
            curve_skin = pm.skinCluster(side_joint, static_joint, curve, mi=3)
            ##weight skin cluster based on construction
            if ae.get_low_cvs(curve) == 'Zero': 
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(side_joint), .8),(str(static_joint),.2)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(side_joint), .6),(str(static_joint),.4)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(side_joint), .4),(str(static_joint),.6)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(side_joint), .2),(str(static_joint),.8)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(side_joint), 0),(str(static_joint),1)])
            if ae.get_low_cvs(curve) == 'One': 
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(side_joint), .8),(str(static_joint),.2)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(side_joint), .6),(str(static_joint),.4)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(side_joint), .4),(str(static_joint),.6)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(side_joint), .2),(str(static_joint),.8)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(side_joint), 0),(str(static_joint),1)])
            continue
        if obj == 'Nostril':
            nostril_joint = pm.joint(name=side+'_Nostril_jnt')
            ae.create_labels(nostril_joint, side, 'Nostril', 'curve_jnt')
            pm.select(clear=True)
            pm.parent(nostril_joint, dynamic_clusters_grp)
            ##static cluster
            if side == 'Right': 
                pm.pointConstraint(right_nostril_ctrl, nostril_joint)
                pm.orientConstraint(right_nostril_ctrl, nostril_joint, mo=True)
            if side == 'Left':
                pm.pointConstraint(left_nostril_ctrl, nostril_joint)
                pm.orientConstraint(left_nostril_ctrl, nostril_joint, mo=True)
             ##create skin cluster
            curve_skin = pm.skinCluster(nostril_joint, static_joint, curve, mi=3)
            ##if cv0 is lower, weight the cluster one way and differently if not
            if ae.get_low_cvs(curve) == 'Zero': 
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(nostril_joint), 1),(str(static_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(nostril_joint), .75),(str(static_joint),.25)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(nostril_joint), .5),(str(static_joint),.5)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(nostril_joint), .25),(str(static_joint),.75)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(nostril_joint), 0),(str(static_joint),1)])
            if ae.get_low_cvs(curve) == 'One': 
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(nostril_joint), 1),(str(static_joint),0)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(nostril_joint), .75),(str(static_joint),.25)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(nostril_joint), .5),(str(static_joint),.5)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(nostril_joint), .25),(str(static_joint),.75)])
                pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(nostril_joint), 0),(str(static_joint),1)])
            continue
        if obj == 'Squint':
            squint_joint = pm.joint(name=side+'_Squint_jnt')
            ae.create_labels(squint_joint, side, 'Squint', 'curve_jnt')
            pm.select(clear=True)
            pm.parent(squint_joint, dynamic_clusters_grp)
            ##constriant clusters to correct sides
            if side == 'Right': 
                pm.pointConstraint(right_squint_ctrl, squint_joint)
                pm.orientConstraint(right_squint_ctrl, squint_joint, mo=True)
            if side == 'Left':
                pm.pointConstraint(left_squint_ctrl, squint_joint)
                pm.orientConstraint(left_squint_ctrl, squint_joint, mo=True)
             ##create skin cluster
            curve_skin = pm.skinCluster(squint_joint, static_joint, curve, mi=3)
            ##edit skin weights
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(squint_joint), 0),(str(static_joint),1)])
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(squint_joint), .7),(str(static_joint),.3)])
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(squint_joint), 1),(str(static_joint),0)])
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(squint_joint), .7),(str(static_joint),.3)])
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(squint_joint), 0),(str(static_joint),1)])
            continue

        if obj == 'Brow':
            ##create cluster
            brow_mid_joint = pm.joint(name=side+'_'+obj+'_mid')
            ae.create_labels(brow_mid_joint, side, obj+'_mid', 'curve_joint')
            pm.select(clear=True)
            brow_inner_joint = pm.joint(name=side+'_'+obj+'_inner')
            ae.create_labels(brow_inner_joint, side, obj+'_inner', 'curve_joint')
            pm.select(clear=True)
            brow_outer_joint = pm.joint(name=side+'_'+obj+'_outer')
            ae.create_labels(brow_outer_joint, side, obj+'_outer', 'curve_joint')
            pm.select(clear=True)
            brow_side = side
            if brow_side == 'Right':
                ##parent constrian the clusters
                pm.parentConstraint(right_inner_brow, brow_inner_joint)
                pm.parentConstraint(right_mid_brow, brow_mid_joint)
                pm.parentConstraint(right_outer_brow, brow_outer_joint)
                ##parent the joints
                pm.parent(brow_mid_joint, dynamic_clusters_grp)
                pm.parent(brow_inner_joint, dynamic_clusters_grp)
                pm.parent(brow_outer_joint, dynamic_clusters_grp)
                ##bind the joints to the curve
                curve_skin = pm.skinCluster(brow_inner_joint, brow_mid_joint, brow_outer_joint, curve, mi=3)
                if ae.get_xPos_cvs(curve) == 'LowerHalf': 
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(brow_inner_joint), 0),(str(brow_mid_joint),0),(str(brow_outer_joint),1)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(brow_inner_joint), 0),(str(brow_mid_joint),.5),(str(brow_outer_joint),.5)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(brow_inner_joint), .125),(str(brow_mid_joint),.75),(str(brow_outer_joint),.125)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(brow_inner_joint), .5),(str(brow_mid_joint),.5),(str(brow_outer_joint),0)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(brow_inner_joint), 1),(str(brow_mid_joint),0),(str(brow_outer_joint),0)])
                if ae.get_xPos_cvs(curve) == 'UpperHalf': 
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(brow_inner_joint), 0),(str(brow_mid_joint),0),(str(brow_outer_joint),1)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(brow_inner_joint), 0),(str(brow_mid_joint),.5),(str(brow_outer_joint),.5)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(brow_inner_joint), .125),(str(brow_mid_joint),.75),(str(brow_outer_joint),.125)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(brow_inner_joint), .5),(str(brow_mid_joint),.5),(str(brow_outer_joint),0)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(brow_inner_joint), 1),(str(brow_mid_joint),0),(str(brow_outer_joint),0)])
            if brow_side == 'Left': 
                pm.parentConstraint(left_inner_brow, brow_inner_joint, mo=True)
                pm.parentConstraint(left_mid_brow, brow_mid_joint, mo=True)
                pm.parentConstraint(left_outer_brow, brow_outer_joint, mo=True)
                ##parent the joints
                pm.parent(brow_mid_joint, dynamic_clusters_grp)
                pm.parent(brow_inner_joint, dynamic_clusters_grp)
                pm.parent(brow_outer_joint, dynamic_clusters_grp)
                ##bind the joints to the curve
                curve_skin = pm.skinCluster(brow_inner_joint, brow_mid_joint, brow_outer_joint, curve, mi=3)
                if ae.get_xPos_cvs(curve) == 'LowerHalf': 
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(brow_inner_joint), 0),(str(brow_mid_joint),0),(str(brow_outer_joint),1)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(brow_inner_joint), 0),(str(brow_mid_joint),.5),(str(brow_outer_joint),.5)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(brow_inner_joint), .125),(str(brow_mid_joint),.75),(str(brow_outer_joint),.125)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(brow_inner_joint), .5),(str(brow_mid_joint),.5),(str(brow_outer_joint),0)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(brow_inner_joint), 1),(str(brow_mid_joint),0),(str(brow_outer_joint),0)])
                if ae.get_xPos_cvs(curve) == 'UpperHalf': 
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(brow_inner_joint), 0),(str(brow_mid_joint),0),(str(brow_outer_joint),1)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(brow_inner_joint), 0),(str(brow_mid_joint),.5),(str(brow_outer_joint),.5)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(brow_inner_joint), .125),(str(brow_mid_joint),.75),(str(brow_outer_joint),.125)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(brow_inner_joint), .5),(str(brow_mid_joint),.5),(str(brow_outer_joint),0)])
                    pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(brow_inner_joint), 1),(str(brow_mid_joint),0),(str(brow_outer_joint),0)])
            continue

        if obj == 'UpperEyelid':
            eyelid_joint = pm.joint(name=side+'_UpperEyelid_jnt')
            ae.create_labels(eyelid_joint, side, obj, 'curve_jnt')
            pm.select(clear=True)
            pm.parent(eyelid_joint, dynamic_clusters_grp)
            ##constrain to correct side
            if side == 'Right': 
                pm.pointConstraint(right_upperLid_ctrl, eyelid_joint)
                pm.orientConstraint(right_upperLid_ctrl, eyelid_joint, mo=True)
            if side == 'Left':
                pm.pointConstraint(left_upperLid_ctrl, eyelid_joint)
                pm.orientConstraint(left_upperLid_ctrl, eyelid_joint, mo=True)
            ##create skin cluster
            curve_skin = pm.skinCluster(eyelid_joint, static_joint, curve, mi=3)
            ##edit skin weights
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(eyelid_joint), 0),(str(static_joint),1)])
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(eyelid_joint), .7),(str(static_joint),.3)])
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(eyelid_joint), 1),(str(static_joint),0)])
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(eyelid_joint), .7),(str(static_joint),.3)])
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(eyelid_joint), 0),(str(static_joint),1)])
            continue


        if obj == 'LowerEyelid':
            eyelid_joint = pm.joint(name=side+'_LowerEyelid_jnt')
            ae.create_labels(eyelid_joint, side, obj, 'curve_jnt')
            pm.select(clear=True)
            pm.parent(eyelid_joint, dynamic_clusters_grp)
            ##constrain to correct side
            if side == 'Right': 
                pm.pointConstraint(right_lowerLid_ctrl, eyelid_joint)
                pm.orientConstraint(right_lowerLid_ctrl, eyelid_joint, mo=True)
            if side == 'Left':
                pm.pointConstraint(left_lowerLid_ctrl, eyelid_joint)
                pm.orientConstraint(left_lowerLid_ctrl, eyelid_joint, mo=True)
            ##create skin cluster
            curve_skin = pm.skinCluster(eyelid_joint, static_joint, curve, mi=3)
            ##edit skin weights
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[0]', transformValue = [(str(eyelid_joint), 0),(str(static_joint),1)])
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[1]', transformValue = [(str(eyelid_joint), .7),(str(static_joint),.3)])
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[2]', transformValue = [(str(eyelid_joint), 1),(str(static_joint),0)])
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[3]', transformValue = [(str(eyelid_joint), .7),(str(static_joint),.3)])
            pm.skinPercent(str(curve_skin), str(curve)+'.cv[4]', transformValue = [(str(eyelid_joint), 0),(str(static_joint),1)])
            continue
    return

def dynamic_automation(mouth_elements, nostril_elements, squint_elements, brow_elements):
    ##grab mouth elements
    corner_ctrls = mouth_elements
    left_corner = corner_ctrls[0]
    right_corner = corner_ctrls[1]
    upper_center = corner_ctrls[2]
    upper_center_auto = pm.listRelatives(upper_center, parent=True)
    upper_center_auto = upper_center_auto[0]
    lower_center = corner_ctrls[3]
    lower_outG_attr = corner_ctrls[4]
    upper_outG_attr = corner_ctrls[5]
    ##grab nostril elements
    right_nostril_ctrl = nostril_elements[1]
    right_nostril_auto = pm.listRelatives(right_nostril_ctrl, parent=True)
    right_nostril_auto = right_nostril_auto[0]
    left_nostril_ctrl = nostril_elements[0]
    left_nostril_auto = pm.listRelatives(left_nostril_ctrl, parent=True)
    left_nostril_auto = left_nostril_auto[0]
    ##grab squint elements
    left_squint_ctrl = squint_elements[0]
    left_squint_auto = pm.listRelatives(left_squint_ctrl, parent=True)
    left_squint_auto = left_squint_auto[0]
    right_squint_ctrl = squint_elements[1]
    right_squint_auto = pm.listRelatives(right_squint_ctrl, parent=True)
    right_squint_auto = right_squint_auto[0]
    ##grab brow elements 
    left_inner_brow = brow_elements[0]
    left_mid_brow = brow_elements[1]
    left_outer_brow = brow_elements[2]
    right_inner_brow = brow_elements[3]
    right_mid_brow = brow_elements[4]
    right_outer_brow = brow_elements[5]
    ####link nostril left and right auto grps to upper lip to pull down
    ##create nostril follow attribute on upper lip
    pm.addAttr(upper_center, ln='Nostril_Follow_Lip', attributeType='double', min=0, max=1, defaultValue=.75, k=True)
    follow_lip = str(upper_center)+'.Nostril_Follow_Lip'
    ##create needed nodes
    upperCenter_sumRot = pm.shadingNode('plusMinusAverage', asUtility=True, name='upperCenter_rotSum_plusMin')
    upperCenter_rotCondition = pm.shadingNode('condition', asUtility=True, name='NostrilStretch_condition')
    upperCenter_rotPercent = pm.shadingNode('multiplyDivide', asUtility=True, name='upperCenter_rotPercent')
    applyFollowLip_multi = pm.shadingNode('multiplyDivide', asUtility=True, name='applyFollwoLip_multi')
    ##connect needed attributes
    pm.connectAttr(str(upper_center_auto)+'.rx', str(upperCenter_sumRot)+'.input1D[0]')
    pm.connectAttr(str(upper_center)+'.rx', str(upperCenter_sumRot)+'.input1D[1]')
    pm.connectAttr(str(upperCenter_sumRot)+'.output1D', str(upperCenter_rotCondition)+'.firstTerm')
    pm.connectAttr(str(upperCenter_sumRot)+'.output1D', str(upperCenter_rotCondition)+'.colorIfTrueR')
    pm.setAttr(str(upperCenter_rotCondition)+'.colorIfFalseR', 0)
    pm.connectAttr(str(upperCenter_rotCondition)+'.outColorR',str(upperCenter_rotPercent)+'.input1X')
    pm.setAttr(str(upperCenter_rotCondition)+'.operation', 2)
    pm.setAttr(str(upperCenter_rotPercent)+'.input2X', -0.01)
    pm.connectAttr(follow_lip, str(applyFollowLip_multi)+'.input2X')
    pm.connectAttr(str(upperCenter_rotPercent)+'.outputX', str(applyFollowLip_multi)+'.input1X')
    pm.connectAttr(str(applyFollowLip_multi)+'.outputX', str(right_nostril_auto)+'.ty')
    pm.connectAttr(str(applyFollowLip_multi)+'.outputX', str(left_nostril_auto)+'.ty')
    ####link squint controls to lip corners to push up
    ##create needed nodes
    lipCorner_rotPercent = pm.shadingNode('multiplyDivide', asUtility=True, name='lipCorners_rotPercent_multi')
    ##conenct needed attributes
    pm.connectAttr(str(left_corner)+'.rx', str(lipCorner_rotPercent)+'.input1X')
    pm.connectAttr(str(right_corner)+'.rx', str(lipCorner_rotPercent)+'.input1Y')
    pm.setAttr(str(lipCorner_rotPercent)+'.input2X', -.01)
    pm.setAttr(str(lipCorner_rotPercent)+'.input2Y', -.01)
    pm.connectAttr(str(lipCorner_rotPercent)+'.outputX', str(left_squint_auto)+'.ty')
    pm.connectAttr(str(lipCorner_rotPercent)+'.outputY', str(right_squint_auto)+'.ty')
    return

##links the cvs of the dynamic curve to the auto groups (or point_grps for lips) of the regular curve
def link_dynamic():
    ##create dynamic and regular curve lists
    dynamic_curves = []
    regular_curves = []
    ##grab all curves
    all_curves = pm.ls(type='nurbsCurve')
    ##seperate out dynamic and regular curves into seperate lists
    for curve in all_curves:
        curve_trans = pm.listRelatives(curve, parent=True)
        if ae.check_type(curve_trans) == 'curve':
            regular_curves.append(curve_trans)
        if ae.check_type(curve_trans) == 'dynamic_curve':
            dynamic_curves.append(curve_trans)
    regular_curves = ae.clean_list_doops(regular_curves)
    dynamic_curves = ae.clean_list_doops(dynamic_curves)
    ##for curve in regular list
    for dynamic in dynamic_curves:
        #print(dynamic)
        count = 0 
        ##curve shape node
        dynamic_shape = pm.listRelatives(dynamic, shapes=True)
        dynamic_shape = dynamic_shape[0]
        if type(dynamic_shape) == list:
            dynamic_shape = dynamic_shape[0]
        ##create needed empty lists for things like cluster grps
        cluster_auto_grps = []
        ##grab curve labels
        dynamic_obj = ae.check_object(dynamic)
        dynamic_side = ae.check_side(dynamic)
        ##for dynamic_curve in dynamic list 
        for curve in regular_curves:
            ##check if curve obj label equal dynamic curve obj
            if ae.check_object(curve) == dynamic_obj:
                ##check if side is the same
                if ae.check_side(curve) == dynamic_side:
                    curve_match = curve
                    curve_shape = pm.listRelatives(curve, shapes=True)
                    curve_shape = curve_shape[0]
                    if type(curve_shape) == list:
                        curve_shape = curve_shape[0]
        ##create curve info node
        info_name = dynamic_obj + dynamic_side + '_info'
        curve_info = pm.shadingNode('curveInfo', asUtility=True, name=info_name)
        ##create attriubes for connecting dynamic curve and info
        shape_worldSpace_attr = str(dynamic_shape) + '.worldSpace[0]'
        inputCurve_attr = str(curve_info) + '.inputCurve'
        ##connect the two nodes
        pm.connectAttr(shape_worldSpace_attr, inputCurve_attr)
        ##grab all transforms 
        all_transforms = pm.ls(type='transform')
        ##if lip curves find point_grps
        if dynamic_obj == 'UpperLip' or dynamic_obj == 'LowerLip' or dynamic_obj == 'UpperEyelid' or dynamic_obj == 'LowerEyelid':
            #print(dynamic_obj)
            for trans in all_transforms:
                if ae.check_attr_exists(trans) == False:
                    continue
                ##if type label == auto_grp
                if ae.check_type(trans) == 'point_grp':
                    ##if side label == curve side label
                    if dynamic_obj in ae.check_object(trans):
                        if dynamic_obj == 'UpperLip' or dynamic_obj == 'LowerLip':
                            cluster_auto_grps.append(trans)
                        else: 
                            if ae.check_side(trans) == dynamic_side:
                            ##if curve obj label is in transform label
                                ##Add the items to a list
                                cluster_auto_grps.append(trans)

        ##else find auto_grps
        else: 
            #print(dynamic_obj + '_ELSE_CASE')
            for trans in all_transforms:
                ##if type label == auto_grp
                if ae.check_attr_exists(trans) == False:
                    continue
                if ae.check_type(trans) == 'auto_grp':
                    ##if side label == curve side label 
                    if ae.check_side(trans) == dynamic_side:
                        ##if curve obj label is in transform label
                        if dynamic_obj in ae.check_object(trans):
                            ##Add the items to a list
                            cluster_auto_grps.append(trans)
        ##for cv in dynamic curve
        for cv in dynamic_shape.cv[:]:
            ##grab cv number + 1 for matching with cluster group
            count += 1
            cv_count = count - 1
            ##if cv number in group name grab it
            #print(cluster_auto_grps) 
            for auto in cluster_auto_grps:
                #print(auto + '_AUTO')
                #print(auto)
                auto_obj = ae.check_object(auto)
                if str(count) in auto_obj:
                    auto_match = auto
                    #print(auto_match + '_MATCH')
            ##create plus minus 
            plusMin_name = dynamic_obj + dynamic_side + '_cv' + str(cv_count) + '_plusMinus'
            plusMin = pm.shadingNode('plusMinusAverage', asUtility=True, name=plusMin_name)
            ##create output attribute from info curve for connection
            #print(dynamic_obj)
            control_point_attr = curve_info + '.controlPoints[' + str(cv_count) + ']'
            plusMin_in1 = plusMin + '.input3D[0]'
            plusMin_in2 = plusMin + '.input3D[1]'
            plusMin_operation = plusMin + '.operation'
            plusMin_out = plusMin + '.output3D'
            trans_in = auto_match + '.translate'
            ##connect output to trans of group
            pm.connectAttr(control_point_attr, plusMin_in1)
            pm.connectAttr(control_point_attr, plusMin_in2)
            pm.disconnectAttr(control_point_attr, plusMin_in2)
            pm.setAttr(plusMin_operation, 2)
            pm.connectAttr(plusMin_out, trans_in)
        continue
    return

def create_neck_dynamics(head_ctrl, neck_ctrl):
    ##grab neck auto node
    neck_auto = pm.listRelatives(neck_ctrl, parent=True)
    ## create a parameter on neck control for follow
    pm.addAttr(neck_ctrl, ln='Follow_Head', attributeType='double', min=0, max=1, defaultValue=1, k=True)
    follow_head_attr = str(neck_ctrl) + '.Follow_Head'
    ##create shading node for applying follow attr
    apply_follow = pm.shadingNode('multiplyDivide', asUtility=True, name='Follow_head_multi')
    ##hook up attr
    pm.connectAttr(str(head_ctrl[0])+'.rotate', str(apply_follow)+'.input1')
    pm.connectAttr(follow_head_attr, str(apply_follow)+'.input2X')
    pm.connectAttr(follow_head_attr, str(apply_follow)+'.input2Y')
    pm.connectAttr(follow_head_attr, str(apply_follow)+'.input2Z')
    pm.connectAttr(str(apply_follow)+'.output', str(neck_auto[0])+'.rotate')
    return

##create controls for the Jaw, eyes, head, neck
# pm.move(0,0,.25, ctrl_shape.cv[0:6], relative=True, wd=True) 
def create_basejoint_controls():
    joint_controls_parent = pm.group(empty=True, name='Joint_Controls')
    ae.create_labels(joint_controls_parent, 'NA', 'JointControlsParent', 'base_grp')
    ##find and grab all needed joints
    all_joints = pm.ls(type='joint')
    eye_joints = []
    neck_joints = []
    for joint in all_joints:
        if ae.check_object(joint) == 'Eye':
                eye_joints.append(joint)
        if ae.check_object(joint) == 'Head':
            head_joint = joint
            neck_joints.append(head_joint)
        if ae.check_object(joint) == 'Jaw':
            jaw_joint = joint
        if ae.check_object(joint) == 'Neck':
            neck_base_joint = joint
            neck_joints.append(neck_base_joint)
    for each in neck_joints:
        obj = ae.check_object(each)
        side = ae.check_side(each)
        ##trans group
        trans = pm.group(empty=True, name=obj+'_'+side+'_trans')
        ae.create_labels(trans, side, obj, 'trans_grp')
        ##auto
        auto = pm.group(empty=True, name=obj+'_'+side+'_auto')
        ae.create_labels(auto, side, obj, 'auto_grp')
        ##ctrl
        ctrl = pm.torus(radius=6.5, heightRatio=.1, name=obj+'_'+side)
        ae.create_labels(ctrl, side, obj, 'ctrl')
        if ae.check_object(each) == 'Head':
            head_ctrl = ctrl
            head_trans = trans
        if ae.check_object(each) == 'Neck':
            neck_ctrl = ctrl
            neck_trans = trans
        ##apply material
        ms.apply_material(ctrl, Yellow)
        ##place properly for orientation
        pm.rotate(ctrl, [0,0,-90])
        pm.makeIdentity(ctrl, apply=True, rotate=True)
        #pm.move(0,0,3, ctrl.cv[:], relative=True, wd=True)
        pm.parent(ctrl, auto)
        pm.parent(auto, trans)
        pm.matchTransform(trans, each)
        pm.parentConstraint(ctrl, each, mo=True)
    ##parent head under neck
    pm.parent(head_trans, neck_ctrl)
    ##create eye ctrls
    eye_joints = ae.clean_list_doops(eye_joints)
    for each in eye_joints:
        #print(each)
        obj = ae.check_object(each)
        side = ae.check_side(each)
        ##trans group
        trans = pm.group(empty=True, name=obj+'_'+side+'_trans')
        ae.create_labels(trans, side, obj, 'trans_grp')
        ##auto
        auto = pm.group(empty=True, name=obj+'_'+side+'_auto')
        ae.create_labels(auto, side, obj, 'auto_grp')
        ##ctrl
        ctrl = pm.torus(radius=.5, heightRatio=.1, name=obj+'_'+side)
        ae.create_labels(ctrl, side, obj, 'ctrl')
        ##apply material
        if side == 'Left':
            ms.apply_material(ctrl, Blue)
        if side == 'Right':
            ms.apply_material(ctrl, Red)
        ##place properly for orientation
        pm.rotate(ctrl, [0,-90, 0])
        pm.makeIdentity(ctrl, apply=True, rotate=True)
        pm.move(0,0,3, ctrl[0].cv[:], relative=True, wd=True)
        pm.parent(ctrl, auto)
        pm.parent(auto, trans)
        pm.matchTransform(trans, each)
        pm.parentConstraint(ctrl, each, mo=True)
        pm.parent(trans, head_ctrl)

    obj = ae.check_object(jaw_joint)
    side = ae.check_side(jaw_joint)
    ##trans group
    trans = pm.group(empty=True, name=obj+'_'+side+'_trans')
    ae.create_labels(trans, side, obj, 'trans_grp')
    ##auto
    auto = pm.group(empty=True, name=obj+'_'+side+'_auto')
    ae.create_labels(auto, side, obj, 'auto_grp')
    ##ctrl
    ctrl = pm.torus(radius=6, heightRatio=.1, name=obj+'_'+side)
    ae.create_labels(ctrl, side, obj, 'ctrl')
    ##apply material
    ms.apply_material(ctrl, Orange)
    ##place properly for orientation
    pm.rotate(ctrl, [0,-45,90])
    pm.makeIdentity(ctrl, apply=True, rotate=True)
    #pm.move(0,0,3, ctrl.cv[:], relative=True, wd=True)
    pm.parent(ctrl, auto)
    pm.parent(auto, trans)
    pm.matchTransform(trans, jaw_joint)
    pm.parentConstraint(ctrl, jaw_joint, mo=True)
    pm.parent(trans, head_ctrl)
    pm.parent(neck_trans, joint_controls_parent)
    create_neck_dynamics(head_ctrl, neck_ctrl[0])
    return (head_ctrl[0])

def adjust_detail_rot():
    ##for all detail_auto transforms add an orient constraint via the head jnt
    ##grab head jnt
    all_joints = pm.ls(type = 'joint')
    for jnt in all_joints:
        if ae.check_object(jnt) == 'Head':
            head_jnt = jnt
    ##grab all auto detail
    all_trans = pm.ls(type='transform')
    labeled_trans = []
    ##do a quick check to only grab labeled trans
    for possible_trans in all_trans:
        if ae.check_attr_exists(possible_trans) == True:
            labeled_trans.append(possible_trans)
    ##grab start, end and middle cluster controls
    for trans in labeled_trans:
        if ae.check_type(trans) == 'detail_auto_grp':
            pm.orientConstraint(head_jnt, trans, mo=True)
    return

def clean_up_hierachy(head_ctrl):
    ##create an overaching parent
    overall_parent = pm.group(empty=True, name='OFR_Rig')
    ##create a DONT TOUCH as a base_grp
    no_touch = pm.group(empty=True, name='DO_NOT_TOUCH')
    ae.create_labels(no_touch, 'NA', 'NO_TOUCH', 'base_grp')
    ##parent all 'parent_grp' to DONT TOUCH
    all_trans = pm.ls(type='transform')
    labeled_trans = []
    ##do a quick check to only grab labeled trans
    for possible_trans in all_trans:
        if ae.check_attr_exists(possible_trans) == True:
            labeled_trans.append(possible_trans)
    ##grab start, end and middle cluster controls
    for trans in labeled_trans:
        if ae.check_type(trans) == 'parent_grp':
            pm.parent(trans, no_touch)
            if ae.check_object(trans) == 'detailCtrls':
                detail_grp = trans
            if ae.check_object(trans) == 'clusterCtrls':
                cluster_grp = trans
        ##parent all 'follow_head_grp' to head_ctrl
        if ae.check_type(trans) == 'follow_head_grp':
            pm.parent(trans, head_ctrl)
        ##parent all base_grps under the big parent
        if ae.check_type(trans) == 'base_grp':
            pm.parent(trans, overall_parent)
    ##create attributes to turn on and off the cluster ctrls and the detail ctrls
    pm.addAttr(head_ctrl, ln='Detail_Controls', attributeType='bool', defaultValue=1, k=True)
    pm.addAttr(head_ctrl, ln='Cluster_Controls', attributeType='bool', defaultValue=1, k=True)
    detail_ctrl_attr = str(head_ctrl)+'.Detail_Controls'
    cluster_ctrl_attr = str(head_ctrl) + '.Cluster_Controls'
    ##hook up attributes
    pm.connectAttr(detail_ctrl_attr, str(detail_grp)+'.visibility')
    pm.connectAttr(cluster_ctrl_attr, str(cluster_grp)+'.visibility')
    return