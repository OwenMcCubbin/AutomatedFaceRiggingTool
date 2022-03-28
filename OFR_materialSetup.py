import pymel.core as pm
import OFR_attrEdits as ae



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
    ##create label for shader 
    ae.create_labels(shader, 'NA', name, 'shader')
    ##return shader for connecting to future nodes
    return shader

def check_transform(node):
    ##check if it is a transform which cannot take a material directly
    if pm.objectType(node) == 'transform':
        node = pm.listRelatives(node, children=True)[0]
        check_transform(node)
    return node

def apply_material(node, shader):
    #node = check_transform(node)
    ##apply the shader
    pm.sets(shader, edit=True, forceElement = node)

