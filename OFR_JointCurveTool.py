import pymel.core as pm

cyan = (0,1,1)
green = (0,1,0)
magenta = (1,0,1)
purple = (.5,0,1)
yellow = (1,1,0)
blue = (0,0,1)
red = (1,0,0)
orange = (1,.5,0)

def create_material(name, color):
    name = str(name)
    ##create material
    mat = pm.shadingNode('lambert', name=name, asShader=True)
    ##get color attribute and set it and transparency
    color_attr = mat + '.color'
    transparency_attr = mat + '.transparency'
    pm.setAttr(color_attr, color[0], color[1], color[2], type='double3')
    pm.setAttr(transparency_attr, 0.5, 0.5, 0.5, type='double3')
    ##create a shader object for applying material
    shader = pm.sets(renderable=True, noSurfaceShader =True, empty=True, name=mat + '_SG')
    ##grab output from mat and input from shader and connect them
    output_attr = mat + '.outColor'
    surface_shader = shader  + '.surfaceShader'
    pm.connectAttr(output_attr, surface_shader, force=True)
    ##return shader for connecting to future nodes
    return shader

def apply_material(node, shader):
    #node = check_transform(node)
    ##apply the shader
    pm.sets(shader, edit=True, forceElement = node)

def check_transform(node):
    ##check if it is a transform which cannot take a material directly
    if pm.objectType(node) == 'transform':
        node = pm.listRelatives(node, children=True)[0]
        check_transform(node)
    return node

def create_motionPath_groups(curve, detail_count, cluster_count):
    span_num = int(cluster_count) - 2
    ##grab start and end of timeframe for motionpaths
    startTime = pm.playbackOptions(query=True, minTime=True)
    endTime = pm.playbackOptions(query=True, maxTime=True)
    ##make an empty list to output all groups and all parent groups
    motionPath_groups=[]
    ##loop through all face curves
    if type(curve) == list:
        curve = curve[0]
    ##rebuild to be desired
    pm.rebuildCurve(curve, rebuildType=0, degree=2, spans=span_num)
    ##create an organizational parent group
    #parent_grp_name = curve.name() + '_elements_grp'
    #parent_grp = pm.group(empty=True, name=parent_grp_name)
    detail_count = int(detail_count)
    for x in range (0, detail_count):
        ##for each iteration create a new name and UValue position, and label
        if x == 0:
            UValue = 0 
        if x == detail_count: 
            UValue = 1
        if x != 0 or detail_count:
            div_num = float(detail_count) -1
            fraction_val = 1/div_num
            UValue = fraction_val*x
            #print (UValue)

        path_name = curve.name() + '_motionPath_' + str(x)
        grp_name = curve.name() + '_motionGroup_' + str(x)
        new_group = pm.group(empty=True, name=grp_name)
        motionPath = pm.pathAnimation(new_group, c=curve, name=path_name, follow=True, fractionMode=True, followAxis='z', upAxis='y', startTimeU=startTime, endTimeU=endTime)
        UVAttr = motionPath + '.u' 
        pm.disconnectAttr(UVAttr)
        pm.setAttr(UVAttr, UValue)
        ##append motionpath group
        motionPath_groups.append(new_group)
    return (motionPath_groups)

def create_detail_ctrls_and_joints(curve, node_list):
    cyan_shader = create_material('Cyan', cyan)
    #print (node_list)
    ##list for ctrls to be added to and for the trans groups to be added to
    trans_list=[]
    ctrl_list = []
    if type(curve) == list:
        curve = curve[0]
    ##create a joint parent for organization
    joint_parent = pm.group(empty=True, name=str(curve)+'_JointParent')
    for each in node_list:
        ##create unique joint name based off of object name
        #print (each)
        grp_name = str(each)+'_trans'
        auto_name = str(each)+'_auto'
        ctrl_name = str(each) +'_ctrl'
        ##create new group and control shape
        new_grp = pm.group(empty=True, name=grp_name)
        auto_grp = pm.group(empty=True, name=auto_name)
        ctrl_shape = pm.sphere(radius=.75, name=ctrl_name)
        apply_material(ctrl_shape, cyan_shader)
        ##append ctrl to list
        ctrl_list.append(ctrl_shape)        
        ##move the cvs (apearance) of sphere forward to eventually offset from mesh.
        ctrl_shape = ctrl_shape[0]
        #pm.move(0,0,.25, ctrl_shape.cv[0:6], relative=True, wd=True)  
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
        ##create joints for each ctrl
        pm.select(clear=True)
        new_joint = pm.joint(name=each.name()+'_jnt')
        pm.select(clear=True)
        pm.parentConstraint(ctrl_shape, new_joint)
        pm.parent(new_joint, joint_parent)
    return (trans_list, ctrl_list, joint_parent)

def create_clusters_ctrls(curve):
    magenta_shader = create_material('Magenta', magenta)
    ##create cluster parent for organization
    clusterCtrls_parent = pm.group(empty=True, name='clusterCtrls_parent')
    cluster_parent = pm.group(empty = True, name = 'clusters_parent')
    pm.setAttr(str(cluster_parent) + '.visibility', 0)
    ##shape node 
    shape = check_transform(curve)
    ##create list for ctrls 
    cluster_ctrls = []
    count = 0
    ##loop over all CVs in the given curve
    for cv in shape.cv[:]:
        ##add one to the count for naming purposes
        count += 1
        if type(curve) == list:
            curve = curve[0]
        ##create cluster name and cluster on cv
        cluster_name = curve + '_cluster' + str(count)
        cluster = pm.cluster(cv, name=cluster_name)
        cluster_handle = cluster[1]
        ##create control groups and cube control and name them all and label
        trans_name = curve + '_cluster' + str(count) + '_trans' 
        trans_grp = pm.group(empty=True, name = trans_name)
        auto_name = curve + '_cluster' + str(count) + '_auto'
        auto_grp = pm.group(empty=True, name = auto_name)
        cube_name = curve + '_cluster' + str(count) + '_ctrl'
        cube = pm.polyCube(name=cube_name, height=1.5, width=1.5, depth=1.5)
        ##apply colour
        apply_material(cube, magenta_shader)
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
    return (clusterCtrls_parent, cluster_parent)



class CurveTool_UI():    
    def __init__(self):
            # Window Handle
            self.handle = "CurveTool"

            # Check if already active, delete if true
            if pm.window(self.handle, exists=True):
                pm.deleteUI(self.handle)

            # Create Window
            with pm.window(self.handle, title="Joint Curve Creator", width=500, height=100):
                # Establish layout
                with pm.columnLayout(rs=10):
                    with pm.rowLayout(nc=2):
                        pm.text(label = "CV Control Count")
                        self.cluster_count = pm.intField(w=100, h=30, bgc = (0.9,0.9,0.85), hlc = (0.9,0.9,0))
                    with pm.rowLayout(nc=2):
                        pm.text(label = "Detail Control Count")
                        self.detail_count = pm.intField(w=100, h=30, bgc = (0.9,0.9,0.85), hlc = (0.9,0.9,0))
                    # Confirm and move forward button
                    pm.button(label="Create Joint Curve from Curve", w=500, h=40, command=pm.Callback(self.create_joint_curve), bgc = (0.9,0.9,0.1))
                # Show window
                pm.showWindow(self.handle)

                    
    def create_joint_curve(self):
        ##grab curve
        curve = pm.ls(selection=True)
        if curve == '' or []:
            pm.warning('NO CURVE SELECTED')
            return
        curve_shape = pm.listRelatives(curve, shapes=True)
        if pm.objectType(curve_shape[0], isType = 'nurbsCurve') == False:
            pm.warning('NO CURVE SELECTED')
            return
        ##grab input cluster count value
        cv_count = self.cluster_count.getValue()
        if int(cv_count) < 4:
            pm.warning(str(cv_count)+" is below minimum of 4. CV count set to 4")
            cv_count = 4
        #grab input detail count value
        detail_num = self.detail_count.getValue()
        if int(detail_num) < 3:
            pm.warning(str(detail_num)+" is below minimum of 3. Detail count set to 3")
            detail_num = 3
        parent_grp = pm.group(empty=True, name=str(curve[0])+'_elements_grp')
        motionpaths = create_motionPath_groups(curve, detail_num, cv_count)
        pm.parent(motionpaths, parent_grp)
        detail_elements = create_detail_ctrls_and_joints(curve, motionpaths)
        detail_trans = detail_elements[0]
        detail_ctrls = detail_elements[1]
        joint_parent = detail_elements[2]
        pm.parent(detail_trans, parent_grp)
        pm.parent(joint_parent, parent_grp)
        cluster_elements = create_clusters_ctrls(curve)
        clusterCtrl_parent = cluster_elements[0]
        cluster_parent = cluster_elements[1]
        pm.parent(clusterCtrl_parent, parent_grp)
        pm.parent(cluster_parent, parent_grp)
        pm.parent(curve, parent_grp)
        
def run():
    CurveTool_UI()