# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# 
# 
#

import bpy
import bmesh
import mathutils
from . functions import *

def create_projection_node(shader_node_tree, camera):

    group_name = camera.name

    # NODES
    node_tree1 = bpy.data.node_groups.get(group_name)
    
    if node_tree1:
        for node in node_tree1.nodes:
            node_tree1.nodes.remove(node)
    else :    
        node_tree1 = bpy.data.node_groups.new(group_name, 'ShaderNodeTree')
        node_tree1.outputs.new('NodeSocketVector', 'Vector')

    # OUTPUTS
    
    # NODES
    location_1 = node_tree1.nodes.new('ShaderNodeCombineXYZ')        
    location_1.label = 'Location'
    location_1.location = (-2441.12451171875, 625.5968017578125)     
    location_1.name = 'Location'        
    location_1.inputs[0].default_value = 0.0
    location_1.inputs[1].default_value = 0.0
    location_1.inputs[2].default_value = 0.0
    location_1.outputs[0].default_value = (0.0, 0.0, 0.0)

    rotation_1 = node_tree1.nodes.new('ShaderNodeCombineXYZ')        
    rotation_1.label = 'Rotation'

    rotation_1.location = (-2436.473876953125, 486.5804443359375)        
    rotation_1.name = 'Rotation'        
    rotation_1.inputs[0].default_value = 0.0
    rotation_1.inputs[1].default_value = 0.0
    rotation_1.inputs[2].default_value = 0.0
    rotation_1.outputs[0].default_value = (0.0, 0.0, 0.0)

    lens_1 = node_tree1.nodes.new('ShaderNodeValue')        
    lens_1.label = 'Lens'
    lens_1.location = (-2437.97802734375, 354.61572265625)        
    lens_1.name = 'Lens'        
    lens_1.outputs[0].default_value = 0.5

    resolution_y_1 = node_tree1.nodes.new('ShaderNodeValue')        
    resolution_y_1.label = 'Resolution_Y'
    resolution_y_1.location = (-2435.26904296875, 86.18476104736328)        
    resolution_y_1.name = 'Resolution_Y'        
    resolution_y_1.outputs[0].default_value = 0.5

    resolution_x_1 = node_tree1.nodes.new('ShaderNodeValue')        
    resolution_x_1.label = 'Resolution X'
    resolution_x_1.location = (-2435.268798828125, 177.0174560546875)        
    resolution_x_1.name = 'Resolution_X'        
    resolution_x_1.outputs[0].default_value = 0.5

    sensor_width_1 = node_tree1.nodes.new('ShaderNodeValue')        
    sensor_width_1.label = 'Sensor Width'
    sensor_width_1.location = (-2435.26904296875, 263.78302001953125)        
    sensor_width_1.name = 'Sensor_Width'        
    sensor_width_1.outputs[0].default_value = 0.5

    vector_math_002_1 = node_tree1.nodes.new('ShaderNodeVectorMath')        
    vector_math_002_1.location = (-799.8863525390625, 621.7315673828125)        
    vector_math_002_1.name = 'Vector Math.002'
    vector_math_002_1.operation = 'CROSS_PRODUCT'        
    vector_math_002_1.inputs[0].default_value = (0.5, 0.5, 0.5)
    vector_math_002_1.inputs[1].default_value = (0.5, 0.5, 0.5)
    vector_math_002_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_002_1.inputs[3].default_value = 1.0
    vector_math_002_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_002_1.outputs[1].default_value = 0.0

    vector_math_016_1 = node_tree1.nodes.new('ShaderNodeVectorMath')       
    vector_math_016_1.location = (-635.5810546875, 613.7861328125)       
    vector_math_016_1.name = 'Vector Math.016'
    vector_math_016_1.operation = 'NORMALIZE'        
    vector_math_016_1.inputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_016_1.inputs[1].default_value = (0.0, 0.0, 0.0)
    vector_math_016_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_016_1.inputs[3].default_value = 1.0
    vector_math_016_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_016_1.outputs[1].default_value = 0.0

    vector_math_014_1 = node_tree1.nodes.new('ShaderNodeVectorMath')       
    vector_math_014_1.location = (-453.34539794921875, 601.2543334960938)       
    vector_math_014_1.name = 'Vector Math.014'
    vector_math_014_1.operation = 'NORMALIZE'       
    vector_math_014_1.inputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_014_1.inputs[1].default_value = (0.0, 0.0, 0.0)
    vector_math_014_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_014_1.inputs[3].default_value = 1.0
    vector_math_014_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_014_1.outputs[1].default_value = 0.0

    vector_math_005_1 = node_tree1.nodes.new('ShaderNodeVectorMath')        
    vector_math_005_1.location = (-218.06582641601562, 601.8170776367188)       
    vector_math_005_1.name = 'Vector Math.005'
    vector_math_005_1.operation = 'NORMALIZE'       
    vector_math_005_1.inputs[0].default_value = (0.5, 0.5, 0.5)
    vector_math_005_1.inputs[1].default_value = (0.5, 0.5, 0.5)
    vector_math_005_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_005_1.inputs[3].default_value = 1.0
    vector_math_005_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_005_1.outputs[1].default_value = 0.0

    vector_math_007_1 = node_tree1.nodes.new('ShaderNodeVectorMath')       
    vector_math_007_1.location = (67.37145233154297, 574.8206176757812)        
    vector_math_007_1.name = 'Vector Math.007'
    vector_math_007_1.operation = 'DOT_PRODUCT'       
    vector_math_007_1.inputs[0].default_value = (0.5, 0.5, 0.5)
    vector_math_007_1.inputs[1].default_value = (0.5, 0.5, 0.5)
    vector_math_007_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_007_1.inputs[3].default_value = 1.0
    vector_math_007_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_007_1.outputs[1].default_value = 0.0

    vector_math_010_1 = node_tree1.nodes.new('ShaderNodeVectorMath')        
    vector_math_010_1.location = (-975.5899047851562, 625.4449462890625)       
    vector_math_010_1.name = 'Vector Math.010'
    vector_math_010_1.operation = 'SUBTRACT'        
    vector_math_010_1.inputs[0].default_value = (0.5, 0.5, 0.5)
    vector_math_010_1.inputs[1].default_value = (0.5, 0.5, 0.5)
    vector_math_010_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_010_1.inputs[3].default_value = 1.0
    vector_math_010_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_010_1.outputs[1].default_value = 0.0

    vector_rotate_1 = node_tree1.nodes.new('ShaderNodeVectorRotate')        
    vector_rotate_1.invert = False
    vector_rotate_1.location = (-1147.794677734375, 631.3923950195312)        
    vector_rotate_1.name = 'Vector Rotate'
    vector_rotate_1.rotation_type = 'EULER_XYZ'       
    vector_rotate_1.inputs[0].default_value = (0.0, 0.0, 0.0)
    vector_rotate_1.inputs[1].default_value = (0.0, 0.0, 0.0)
    vector_rotate_1.inputs[2].default_value = (0.0, 0.0, 1.0)
    vector_rotate_1.inputs[3].default_value = 0.0
    vector_rotate_1.inputs[4].default_value = (0.0, 0.0, 0.0)
    vector_rotate_1.outputs[0].default_value = (0.0, 0.0, 0.0)

    vector_math_011_1 = node_tree1.nodes.new('ShaderNodeVectorMath')        
    vector_math_011_1.location = (-1364.437744140625, 637.164794921875)        
    vector_math_011_1.name = 'Vector Math.011'
    vector_math_011_1.operation = 'ADD'        
    vector_math_011_1.inputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_011_1.inputs[1].default_value = (0.0, 1.0, 0.0)
    vector_math_011_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_011_1.inputs[3].default_value = 1.0
    vector_math_011_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_011_1.outputs[1].default_value = 0.0

    math_1 = node_tree1.nodes.new('ShaderNodeMath')        
    math_1.location = (-1655.4462890625, 313.4727783203125)       
    math_1.name = 'Math'
    math_1.operation = 'MULTIPLY'
    math_1.use_clamp = False        
    math_1.inputs[0].default_value = 0.5
    math_1.inputs[1].default_value = -1.0
    math_1.inputs[2].default_value = 0.0
    math_1.outputs[0].default_value = 0.0

    math_004_1 = node_tree1.nodes.new('ShaderNodeMath')       
    math_004_1.location = (-1493.44384765625, 312.4825439453125)       
    math_004_1.name = 'Math.004'
    math_004_1.operation = 'DIVIDE'
    math_004_1.use_clamp = False       
    math_004_1.width = 140.0
    math_004_1.inputs[0].default_value = 0.5
    math_004_1.inputs[1].default_value = -1.0
    math_004_1.inputs[2].default_value = 0.0
    math_004_1.outputs[0].default_value = 0.0

    combine_xyz_1 = node_tree1.nodes.new('ShaderNodeCombineXYZ')        
    combine_xyz_1.location = (-1325.547119140625, 289.2916564941406)        
    combine_xyz_1.name = 'Combine XYZ'        
    combine_xyz_1.inputs[0].default_value = 0.0
    combine_xyz_1.inputs[1].default_value = 0.0
    combine_xyz_1.inputs[2].default_value = 0.0
    combine_xyz_1.outputs[0].default_value = (0.0, 0.0, 0.0)

    vector_math_013_1 = node_tree1.nodes.new('ShaderNodeVectorMath')        
    vector_math_013_1.location = (-1107.04443359375, 295.2362060546875)        
    vector_math_013_1.name = 'Vector Math.013'
    vector_math_013_1.operation = 'ADD'        
    vector_math_013_1.inputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_013_1.inputs[1].default_value = (0.0, 1.0, 0.0)
    vector_math_013_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_013_1.inputs[3].default_value = 1.0
    vector_math_013_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_013_1.outputs[1].default_value = 0.0

    vector_rotate_001_1 = node_tree1.nodes.new('ShaderNodeVectorRotate')        
    vector_rotate_001_1.invert = False
    vector_rotate_001_1.location = (-911.0789184570312, 296.08404541015625)        
    vector_rotate_001_1.name = 'Vector Rotate.001'
    vector_rotate_001_1.rotation_type = 'EULER_XYZ'        
    vector_rotate_001_1.inputs[0].default_value = (0.0, 0.0, 0.0)
    vector_rotate_001_1.inputs[1].default_value = (0.0, 0.0, 0.0)
    vector_rotate_001_1.inputs[2].default_value = (0.0, 0.0, 1.0)
    vector_rotate_001_1.inputs[3].default_value = 0.0
    vector_rotate_001_1.inputs[4].default_value = (0.0, 0.0, 0.0)
    vector_rotate_001_1.outputs[0].default_value = (0.0, 0.0, 0.0)

    vector_math_003_1 = node_tree1.nodes.new('ShaderNodeVectorMath')       
    vector_math_003_1.location = (-215.97061157226562, 307.2452392578125)        
    vector_math_003_1.name = 'Vector Math.003'
    vector_math_003_1.operation = 'CROSS_PRODUCT'       
    vector_math_003_1.inputs[0].default_value = (0.5, 0.5, 0.5)
    vector_math_003_1.inputs[1].default_value = (0.5, 0.5, 0.5)
    vector_math_003_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_003_1.inputs[3].default_value = 1.0
    vector_math_003_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_003_1.outputs[1].default_value = 0.0

    vector_math_015_1 = node_tree1.nodes.new('ShaderNodeVectorMath')        
    vector_math_015_1.location = (-41.912109375, 300.23974609375)        
    vector_math_015_1.name = 'Vector Math.015'
    vector_math_015_1.operation = 'NORMALIZE'        
    vector_math_015_1.inputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_015_1.inputs[1].default_value = (0.0, 0.0, 0.0)
    vector_math_015_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_015_1.inputs[3].default_value = 1.0
    vector_math_015_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_015_1.outputs[1].default_value = 0.0

    vector_math_012_1 = node_tree1.nodes.new('ShaderNodeVectorMath')        
    vector_math_012_1.location = (123.51138305664062, 297.98602294921875)       
    vector_math_012_1.name = 'Vector Math.012'
    vector_math_012_1.operation = 'NORMALIZE'        
    vector_math_012_1.inputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_012_1.inputs[1].default_value = (0.0, 0.0, 0.0)
    vector_math_012_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_012_1.inputs[3].default_value = 1.0
    vector_math_012_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_012_1.outputs[1].default_value = 0.0

    vector_math_004_1 = node_tree1.nodes.new('ShaderNodeVectorMath')       
    vector_math_004_1.location = (279.5755920410156, 293.62725830078125)        
    vector_math_004_1.name = 'Vector Math.004'
    vector_math_004_1.operation = 'NORMALIZE'       
    vector_math_004_1.inputs[0].default_value = (0.5, 0.5, 0.5)
    vector_math_004_1.inputs[1].default_value = (0.5, 0.5, 0.5)
    vector_math_004_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_004_1.inputs[3].default_value = 1.0
    vector_math_004_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_004_1.outputs[1].default_value = 0.0

    vector_math_008_1 = node_tree1.nodes.new('ShaderNodeVectorMath')        
    vector_math_008_1.location = (451.3398742675781, 276.4857482910156)        
    vector_math_008_1.name = 'Vector Math.008'
    vector_math_008_1.operation = 'DOT_PRODUCT'        

    vector_math_008_1.inputs[0].default_value = (0.5, 0.5, 0.5)
    vector_math_008_1.inputs[1].default_value = (0.5, 0.5, 0.5)
    vector_math_008_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_008_1.inputs[3].default_value = 1.0
    vector_math_008_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_008_1.outputs[1].default_value = 0.0

    vector_math_1 = node_tree1.nodes.new('ShaderNodeVectorMath')        
    vector_math_1.location = (-294.3377685546875, -130.13882446289062)        
    vector_math_1.name = 'Vector Math'
    vector_math_1.operation = 'SUBTRACT'        
    vector_math_1.inputs[0].default_value = (0.5, 0.5, 0.5)
    vector_math_1.inputs[1].default_value = (0.5, 0.5, 0.5)
    vector_math_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_1.inputs[3].default_value = 1.0
    vector_math_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_1.outputs[1].default_value = 0.0

    math_005_1 = node_tree1.nodes.new('ShaderNodeMath')        
    math_005_1.location = (-530.5385131835938, -481.6020812988281)        
    math_005_1.name = 'Math.005'
    math_005_1.operation = 'GREATER_THAN'
    math_005_1.use_clamp = False        
    math_005_1.inputs[0].default_value = 0.5
    math_005_1.inputs[1].default_value = 0.5
    math_005_1.inputs[2].default_value = 0.0
    math_005_1.outputs[0].default_value = 0.0

    math_006_1 = node_tree1.nodes.new('ShaderNodeMath')        
    math_006_1.location = (-883.1950073242188, -906.985595703125)        
    math_006_1.name = 'Math.006'
    math_006_1.operation = 'DIVIDE'
    math_006_1.use_clamp = False        
    math_006_1.inputs[0].default_value = 0.5
    math_006_1.inputs[1].default_value = 0.5
    math_006_1.inputs[2].default_value = 0.0
    math_006_1.outputs[0].default_value = 0.0

    math_007_1 = node_tree1.nodes.new('ShaderNodeMath')        
    math_007_1.location = (-878.3383178710938, -718.97900390625)        
    math_007_1.name = 'Math.007'
    math_007_1.operation = 'DIVIDE'
    math_007_1.use_clamp = False        
    math_007_1.inputs[0].default_value = 0.5
    math_007_1.inputs[1].default_value = 0.5
    math_007_1.inputs[2].default_value = 0.0
    math_007_1.outputs[0].default_value = 0.0

    combine_xyz_001_1 = node_tree1.nodes.new('ShaderNodeCombineXYZ')        
    combine_xyz_001_1.location = (-621.8829956054688, -745.4910888671875)        
    combine_xyz_001_1.name = 'Combine XYZ.001'       
    combine_xyz_001_1.inputs[0].default_value = 1.0
    combine_xyz_001_1.inputs[1].default_value = 0.0
    combine_xyz_001_1.inputs[2].default_value = 1.0
    combine_xyz_001_1.outputs[0].default_value = (0.0, 0.0, 0.0)

    combine_xyz_002_1 = node_tree1.nodes.new('ShaderNodeCombineXYZ')        
    combine_xyz_002_1.location = (-619.6718139648438, -907.10205078125)        
    combine_xyz_002_1.name = 'Combine XYZ.002'       
    combine_xyz_002_1.inputs[0].default_value = 0.0
    combine_xyz_002_1.inputs[1].default_value = 1.0
    combine_xyz_002_1.inputs[2].default_value = 1.0
    combine_xyz_002_1.outputs[0].default_value = (0.0, 0.0, 0.0)

    mix_002_1 = node_tree1.nodes.new('ShaderNodeMixRGB')
    mix_002_1.blend_type = 'MIX'        
    mix_002_1.location = (-299.7763366699219, -698.134033203125)        
    mix_002_1.name = 'Mix.002'
    mix_002_1.use_alpha = False
    mix_002_1.use_clamp = False        
    mix_002_1.inputs[0].default_value = 0.5
    mix_002_1.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
    mix_002_1.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
    mix_002_1.outputs[0].default_value = (0.0, 0.0, 0.0, 0.0)

    vector_transform_1 = node_tree1.nodes.new('ShaderNodeVectorTransform')        
    vector_transform_1.convert_from = 'OBJECT'
    vector_transform_1.convert_to = 'WORLD'        
    vector_transform_1.location = (-464.6912536621094, -137.8911895751953)       
    vector_transform_1.name = 'Vector Transform'        
    vector_transform_1.vector_type = 'POINT'        
    vector_transform_1.inputs[0].default_value = (0.5, 0.5, 0.5)
    vector_transform_1.outputs[0].default_value = (0.0, 0.0, 0.0)

    vector_math_001_1 = node_tree1.nodes.new('ShaderNodeVectorMath')        
    vector_math_001_1.location = (-708.84375, 176.55126953125)        
    vector_math_001_1.name = 'Vector Math.001'
    vector_math_001_1.operation = 'SUBTRACT'        
    vector_math_001_1.inputs[0].default_value = (0.5, 0.5, 0.5)
    vector_math_001_1.inputs[1].default_value = (0.5, 0.5, 0.5)
    vector_math_001_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_001_1.inputs[3].default_value = 1.0
    vector_math_001_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_001_1.outputs[1].default_value = 0.0

    combine_xyz_003_1 = node_tree1.nodes.new('ShaderNodeCombineXYZ')        
    combine_xyz_003_1.location = (980.5036010742188, 164.0612335205078)        
    combine_xyz_003_1.name = 'Combine XYZ.003'        
    combine_xyz_003_1.inputs[0].default_value = 0.0
    combine_xyz_003_1.inputs[1].default_value = 0.0
    combine_xyz_003_1.inputs[2].default_value = 0.0
    combine_xyz_003_1.outputs[0].default_value = (0.0, 0.0, 0.0)

    mix_1 = node_tree1.nodes.new('ShaderNodeMixRGB')
    mix_1.blend_type = 'ADD'        
    mix_1.location = (1400.05419921875, 292.0730285644531)        
    mix_1.name = 'Mix'
    mix_1.use_alpha = False
    mix_1.use_clamp = False        
    mix_1.inputs[0].default_value = 1.0
    mix_1.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
    mix_1.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
    mix_1.outputs[0].default_value = (0.0, 0.0, 0.0, 0.0)

    mix_001_1 = node_tree1.nodes.new('ShaderNodeMixRGB')
    mix_001_1.blend_type = 'DIVIDE'        
    mix_001_1.location = (1196.413818359375, 195.13536071777344)        
    mix_001_1.name = 'Mix.001'
    mix_001_1.use_alpha = False
    mix_001_1.use_clamp = False        
    mix_001_1.inputs[0].default_value = 1.0
    mix_001_1.inputs[1].default_value = (0.5, 0.5, 0.5, 1.0)
    mix_001_1.inputs[2].default_value = (0.5, 0.5, 0.5, 1.0)
    mix_001_1.outputs[0].default_value = (0.0, 0.0, 0.0, 0.0)

    math_002_1 = node_tree1.nodes.new('ShaderNodeMath')        
    math_002_1.location = (728.3179321289062, 135.6461639404297)        
    math_002_1.name = 'Math.002'
    math_002_1.operation = 'DIVIDE'
    math_002_1.use_clamp = False        
    math_002_1.inputs[0].default_value = 0.5
    math_002_1.inputs[1].default_value = 0.5
    math_002_1.inputs[2].default_value = 0.0
    math_002_1.outputs[0].default_value = 0.0

    math_003_1 = node_tree1.nodes.new('ShaderNodeMath')        
    math_003_1.location = (729.5640258789062, 296.1169128417969)        
    math_003_1.name = 'Math.003'
    math_003_1.operation = 'DIVIDE'
    math_003_1.use_clamp = False        
    math_003_1.inputs[0].default_value = 0.5
    math_003_1.inputs[1].default_value = 0.5
    math_003_1.inputs[2].default_value = 0.0
    math_003_1.outputs[0].default_value = 0.0

    texture_coordinate_1 = node_tree1.nodes.new('ShaderNodeTexCoord')        
    texture_coordinate_1.from_instancer = False        
    texture_coordinate_1.location = (-648.8167114257812, -130.78839111328125)        
    texture_coordinate_1.name = 'Texture Coordinate'        
    texture_coordinate_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    texture_coordinate_1.outputs[1].default_value = (0.0, 0.0, 0.0)
    texture_coordinate_1.outputs[2].default_value = (0.0, 0.0, 0.0)
    texture_coordinate_1.outputs[3].default_value = (0.0, 0.0, 0.0)
    texture_coordinate_1.outputs[4].default_value = (0.0, 0.0, 0.0)
    texture_coordinate_1.outputs[5].default_value = (0.0, 0.0, 0.0)
    texture_coordinate_1.outputs[6].default_value = (0.0, 0.0, 0.0)

    vector_math_006_1 = node_tree1.nodes.new('ShaderNodeVectorMath')        
    vector_math_006_1.location = (213.52259826660156, 33.54572296142578)       
    vector_math_006_1.name = 'Vector Math.006'
    vector_math_006_1.operation = 'DOT_PRODUCT'        
    vector_math_006_1.inputs[0].default_value = (0.5, 0.5, 0.5)
    vector_math_006_1.inputs[1].default_value = (0.5, 0.5, 0.5)
    vector_math_006_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_006_1.inputs[3].default_value = 1.0
    vector_math_006_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_006_1.outputs[1].default_value = 0.0

    vector_math_009_1 = node_tree1.nodes.new('ShaderNodeVectorMath')       
    vector_math_009_1.location = (212.0181884765625, -130.796875)       
    vector_math_009_1.name = 'Vector Math.009'
    vector_math_009_1.operation = 'DOT_PRODUCT'        
    vector_math_009_1.inputs[0].default_value = (0.5, 0.5, 0.5)
    vector_math_009_1.inputs[1].default_value = (0.5, 0.5, 0.5)
    vector_math_009_1.inputs[2].default_value = (0.0, 0.0, 0.0)
    vector_math_009_1.inputs[3].default_value = 1.0
    vector_math_009_1.outputs[0].default_value = (0.0, 0.0, 0.0)
    vector_math_009_1.outputs[1].default_value = 0.0

    math_001_1 = node_tree1.nodes.new('ShaderNodeMath')       
    math_001_1.location = (457.9128723144531, 30.074228286743164)       
    math_001_1.name = 'Math.001'
    math_001_1.operation = 'DIVIDE'
    math_001_1.use_clamp = False       
    math_001_1.inputs[0].default_value = 0.5
    math_001_1.inputs[1].default_value = 1.0
    math_001_1.inputs[2].default_value = 0.0
    math_001_1.outputs[0].default_value = 0.0

    group_output_1 = node_tree1.nodes.new('NodeGroupOutput')        
    group_output_1.is_active_output = True
    group_output_1.location = (1653.4639892578125, 286.638427734375)       
    group_output_1.name = 'Group Output'        
    group_output_1.inputs[0].default_value = (0.0, 0.0, 0.0)

    # LINKS
    node_tree1.links.new(texture_coordinate_1.outputs[3], vector_transform_1.inputs[0])
    node_tree1.links.new(vector_math_005_1.outputs[0], vector_math_007_1.inputs[0])
    node_tree1.links.new(vector_math_004_1.outputs[0], vector_math_008_1.inputs[0])
    node_tree1.links.new(combine_xyz_003_1.outputs[0], mix_001_1.inputs[1])
    node_tree1.links.new(vector_math_007_1.outputs[1], math_002_1.inputs[0])
    node_tree1.links.new(vector_math_008_1.outputs[1], math_003_1.inputs[0])
    node_tree1.links.new(math_002_1.outputs[0], combine_xyz_003_1.inputs[0])
    node_tree1.links.new(math_003_1.outputs[0], combine_xyz_003_1.inputs[1])
    node_tree1.links.new(math_001_1.outputs[0], math_002_1.inputs[1])
    node_tree1.links.new(math_001_1.outputs[0], math_003_1.inputs[1])
    node_tree1.links.new(vector_math_009_1.outputs[1], math_001_1.inputs[1])
    node_tree1.links.new(vector_math_001_1.outputs[0], vector_math_003_1.inputs[1])
    node_tree1.links.new(vector_transform_1.outputs[0], vector_math_1.inputs[0])
    node_tree1.links.new(vector_math_001_1.outputs[0], vector_math_002_1.inputs[0])
    node_tree1.links.new(vector_math_006_1.outputs[1], math_001_1.inputs[0])
    node_tree1.links.new(mix_001_1.outputs[0], mix_1.inputs[1])
    node_tree1.links.new(vector_math_010_1.outputs[0], vector_math_002_1.inputs[1])
    node_tree1.links.new(vector_math_012_1.outputs[0], vector_math_004_1.inputs[0])
    node_tree1.links.new(vector_math_014_1.outputs[0], vector_math_003_1.inputs[0])
    node_tree1.links.new(vector_math_014_1.outputs[0], vector_math_005_1.inputs[0])
    node_tree1.links.new(mix_1.outputs[0], group_output_1.inputs[0])
    node_tree1.links.new(vector_math_011_1.outputs[0], vector_rotate_1.inputs[0])
    node_tree1.links.new(vector_rotate_1.outputs[0], vector_math_010_1.inputs[0])
    node_tree1.links.new(math_1.outputs[0], math_004_1.inputs[0])
    node_tree1.links.new(vector_math_013_1.outputs[0], vector_rotate_001_1.inputs[0])
    node_tree1.links.new(combine_xyz_1.outputs[0], vector_math_013_1.inputs[1])
    node_tree1.links.new(math_004_1.outputs[0], combine_xyz_1.inputs[2])
    node_tree1.links.new(vector_rotate_001_1.outputs[0], vector_math_001_1.inputs[0])
    node_tree1.links.new(math_005_1.outputs[0], mix_002_1.inputs[0])
    node_tree1.links.new(math_006_1.outputs[0], combine_xyz_002_1.inputs[0])
    node_tree1.links.new(math_007_1.outputs[0], combine_xyz_001_1.inputs[1])
    node_tree1.links.new(combine_xyz_001_1.outputs[0], mix_002_1.inputs[2])
    node_tree1.links.new(combine_xyz_002_1.outputs[0], mix_002_1.inputs[1])
    node_tree1.links.new(mix_002_1.outputs[0], mix_001_1.inputs[2])
    node_tree1.links.new(vector_math_015_1.outputs[0], vector_math_012_1.inputs[0])
    node_tree1.links.new(vector_math_003_1.outputs[0], vector_math_015_1.inputs[0])
    node_tree1.links.new(vector_math_016_1.outputs[0], vector_math_014_1.inputs[0])
    node_tree1.links.new(vector_math_002_1.outputs[0], vector_math_016_1.inputs[0])
    node_tree1.links.new(location_1.outputs[0], vector_math_1.inputs[1])
    node_tree1.links.new(location_1.outputs[0], vector_math_001_1.inputs[1])
    node_tree1.links.new(location_1.outputs[0], vector_math_010_1.inputs[1])
    node_tree1.links.new(location_1.outputs[0], vector_math_011_1.inputs[0])
    node_tree1.links.new(location_1.outputs[0], vector_rotate_1.inputs[1])
    node_tree1.links.new(location_1.outputs[0], vector_math_013_1.inputs[0])
    node_tree1.links.new(location_1.outputs[0], vector_rotate_001_1.inputs[1])
    node_tree1.links.new(rotation_1.outputs[0], vector_rotate_1.inputs[4])
    node_tree1.links.new(rotation_1.outputs[0], vector_rotate_001_1.inputs[4])
    node_tree1.links.new(lens_1.outputs[0], math_1.inputs[0])
    node_tree1.links.new(sensor_width_1.outputs[0], math_004_1.inputs[1])
    node_tree1.links.new(resolution_x_1.outputs[0], math_005_1.inputs[0])
    node_tree1.links.new(resolution_x_1.outputs[0], math_007_1.inputs[1])
    node_tree1.links.new(resolution_x_1.outputs[0], math_006_1.inputs[0])
    node_tree1.links.new(resolution_y_1.outputs[0], math_005_1.inputs[1])
    node_tree1.links.new(resolution_y_1.outputs[0], math_007_1.inputs[0])
    node_tree1.links.new(resolution_y_1.outputs[0], math_006_1.inputs[1])
    node_tree1.links.new(vector_math_1.outputs[0], vector_math_006_1.inputs[1])
    node_tree1.links.new(vector_math_1.outputs[0], vector_math_007_1.inputs[1])
    node_tree1.links.new(vector_math_1.outputs[0], vector_math_008_1.inputs[1])
    node_tree1.links.new(vector_math_001_1.outputs[0], vector_math_006_1.inputs[0])
    node_tree1.links.new(vector_math_001_1.outputs[0], vector_math_009_1.inputs[0])
    node_tree1.links.new(vector_math_001_1.outputs[0], vector_math_009_1.inputs[1])

    #CREATE DRIVERS
    
    #Check/update camera resolution

    camera.data.render.resolution_x += 1
    camera.data.render.resolution_x -= 1
    camera.data.render.resolution_y += 1
    camera.data.render.resolution_y -= 1
    
    camera.data["resolution_x"] = camera.data.render.resolution_x
    camera.data["resolution_y"] = camera.data.render.resolution_y
    

    add_driver( location_1.inputs[0], camera, 'OBJECT', 'default_value', 'location[0]')
    add_driver( location_1.inputs[1], camera, 'OBJECT', 'default_value', 'location[1]')
    add_driver( location_1.inputs[2], camera, 'OBJECT', 'default_value', 'location[2]')

    add_driver( rotation_1.inputs[0], camera, 'OBJECT', 'default_value', 'rotation_euler[0]')
    add_driver( rotation_1.inputs[1], camera, 'OBJECT', 'default_value', 'rotation_euler[1]')
    add_driver( rotation_1.inputs[2], camera, 'OBJECT', 'default_value', 'rotation_euler[2]')

    add_driver( lens_1.outputs[0], camera.data, 'CAMERA','default_value', 'lens')
    add_driver( sensor_width_1.outputs[0], camera.data, 'CAMERA','default_value', 'sensor_width')
    driver_resolution_x = add_driver( resolution_x_1.outputs[0], camera.data, 'CAMERA','default_value', '["resolution_x"]')
    driver_resolution_y = add_driver( resolution_y_1.outputs[0], camera.data, 'CAMERA','default_value', '["resolution_y"]')

    
    driver_resolution_x.expression += " "
    driver_resolution_x.expression = driver_resolution_x.expression[:-1]

    driver_resolution_y.expression += " "
    driver_resolution_y.expression = driver_resolution_y.expression[:-1]
    

    #ADD GROUP TO MATERIAL
    group = shader_node_tree.nodes.new('ShaderNodeGroup')
    group.node_tree = bpy.data.node_groups.get(group_name)