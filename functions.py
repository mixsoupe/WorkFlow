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
import os
import bmesh
import mathutils
import numpy as np
import configparser
import time
import json
import zipfile

def color_fill(mask, mask_list):
    white = mathutils.Vector((1, 1, 1, 1))
    black = mathutils.Vector((0, 0, 0, 1))

    obj = bpy.context.active_object  
    mesh = obj.data
    bm = bmesh.from_edit_mesh(mesh)

    #Current color layers
    if not bm.loops.layers.color.get(mask):
        color_layer = bm.loops.layers.color.new(mask)
        for face in bm.faces:
            for loop in face.loops:
                loop[color_layer] = black
    else:
        color_layer = bm.loops.layers.color.get(mask)

    #Other color layers
    mask_list.remove(mask)
    other_layers = []
    for m in mask_list:
        layer = bm.loops.layers.color.get(m)
        if layer is not None:
            other_layers.append(layer)
    
    #Set colors
    for face in bm.faces:
        for loop in face.loops:
            loop[color_layer] = white if face.select else loop[color_layer]
            for layer in other_layers:
                loop[layer] = black if face.select else loop[layer]
            
    #Update mesh
    if bm.is_wrapped:
        bmesh.update_edit_mesh(mesh, False, False)
    else:
        bm.to_mesh(mesh)
        mesh.update()

    bm.clear
            
def delete_scenes():

    current_scene = bpy.context.window.scene
    scenes = bpy.data.scenes

    for scene in scenes:
        if scene is not current_scene:
            bpy.data.scenes.remove(scene)

    #FIX trouver une solution avec un while
    for i in range(10):
        bpy.ops.outliner.orphans_purge()

def resolution_from_camera():
    #FIX trouver une solution pour éviter d'updater à chaque changement
    #FIX enregistrer la résolution dans une custom propertie

    scene = bpy.context.scene
    current_camera = scene.camera

    if current_camera is not None :
        previous_camera = scene.previous_camera

        if current_camera.name != previous_camera:
            scene.previous_camera = current_camera.name
            scene.render.resolution_x = current_camera.data.render.resolution_x
            scene.render.resolution_y = current_camera.data.render.resolution_y

def update_resolution(self, context):
    scene = bpy.context.scene
    camera = bpy.context.object

    if bpy.context.object.type == "CAMERA":
        camera.data["resolution_x"] = camera.data.render.resolution_x
        camera.data["resolution_y"] = camera.data.render.resolution_y

        if camera == scene.camera:
            scene.render.resolution_x = camera.data.render.resolution_x
            scene.render.resolution_y = camera.data.render.resolution_y

        bpy.context.view_layer.update()

def add_driver(
        source, target, id_type, prop, dataPath,
        index = -1, negative = False, func = ''
    ):
    ''' Add driver to source prop (at index), driven by target dataPath ''' 

    if index != -1:
        source.driver_remove( prop, index )
        d = source.driver_add( prop, index ).driver
    else:
        source.driver_remove( prop)
        d = source.driver_add( prop ).driver

    v = d.variables.new()
    v.name                 = prop
    v.targets[0].id_type   = id_type
    v.targets[0].id        = target
    v.targets[0].data_path = dataPath

    d.expression = func + "(" + v.name + ")" if func else v.name
    d.expression = d.expression if not negative else "-1 * " + d.expression

    return d

    
_enum_cameras = []

def enum_cameras(self, context):
    _enum_cameras.clear()

    bpy.data.objects
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            _enum_cameras.append((obj.name, obj.name, ""))
    return _enum_cameras
    
def render_material(shader_node_tree, render_camera, isolate, engine):  
    #Link transparent to material output

    link_list = []
    for material in bpy.data.materials:
        material.blend_method = 'HASHED'        
        if material.node_tree:
            if material.node_tree is not shader_node_tree:
                node_tree = material.node_tree
                for node in node_tree.nodes:
                    if node.type == "OUTPUT_MATERIAL":
                        if node.inputs[0].links:
                            transparent = node_tree.nodes.new('ShaderNodeBsdfTransparent')

                            output = node.inputs[0].links[0].from_socket
                            link = (node_tree, node, output, transparent)
                            link_list.append(link)                        

                            if isolate:
                                node_tree.links.new(transparent.outputs[0], node.inputs[0])
            else:
                material_name = material.name
    #Bake and set render settings    
    file_format = bpy.context.scene.render.image_settings.file_format
    current_engine = bpy.context.scene.render.engine
    filepath = bpy.context.scene.render.filepath
    current_camera = bpy.context.scene.camera

    bpy.context.scene.camera = bpy.data.objects[render_camera]
    bpy.context.scene.render.engine = engine
    bpy.context.scene.render.film_transparent = True
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.image_settings.color_mode = 'RGBA'
    bpy.context.scene.render.image_settings.color_depth = '8'
    bpy.context.scene.render.image_settings.compression = 0    
    bpy.context.scene.render.filepath = bpy.context.scene.production_settings.render_material_path + material_name

    #Render
    bpy.ops.render.render(write_still = 1)   

    #Reset render settings
    bpy.context.scene.render.image_settings.file_format = file_format
    bpy.context.scene.render.engine = current_engine
    bpy.context.scene.render.filepath = filepath
    bpy.context.scene.camera = current_camera
    

    #Reset material output
    for link in link_list:
        node_tree = link[0]
        node = link[1]
        output = link[2]
        transparent = link[3]
        #delete transparent
        
        node_tree.links.new(output, node.inputs[0])
        node_tree.nodes.remove(transparent)
    
    return material_name

def load_settings(production_settings_file):
    filename =  bpy.path.basename(bpy.context.blend_data.filepath)
    filename = filename.rsplit(".", 1)[0]

    settings = bpy.context.scene.production_settings
    
    #CONFIG PARSER
    config = configparser.ConfigParser()
    config.read(production_settings_file)

    #GET SETTINGS
    settings.production = config.get('SETTINGS', 'production')
    settings.status = "Loaded"
    settings.render_engine = config.get('SETTINGS', 'render_engine')
    settings.render_samples = config.getint('SETTINGS', 'render_samples')
    settings.film_transparent = config.getboolean('SETTINGS', 'film_transparent')
    settings.resolution_x = config.getint('SETTINGS', 'resolution_x')
    settings.resolution_y = config.getint('SETTINGS', 'resolution_y')
    settings.fps = config.getint('SETTINGS', 'fps')
    settings.file_format = config.get('SETTINGS', 'file_format')
    settings.color_mode = config.get('SETTINGS', 'color_mode')
    settings.color_depth = config.getint('SETTINGS', 'color_depth')
    settings.exr_codec = config.get('SETTINGS', 'exr_codec')
    settings.png_compression = config.getint('SETTINGS', 'png_compression')
    settings.overwrite = config.getboolean('SETTINGS', 'overwrite')

    settings.default_material_blend_method = config.get('SETTINGS', 'default_material_blend_method')

    settings.render_output = eval(config.get('SETTINGS', 'render_output'))
    settings.preview_output = eval(config.get('SETTINGS', 'preview_output'))
    settings.render_material_path = eval(config.get('SETTINGS', 'render_material_path'))

def playblast():  
    #Change Settings
    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    bpy.context.scene.eevee.taa_render_samples = 64
    bpy.context.scene.render.image_settings.file_format = "FFMPEG"
    bpy.context.scene.render.image_settings.color_mode = "RGB"
    bpy.context.scene.render.ffmpeg.format = "QUICKTIME"
    bpy.context.scene.render.ffmpeg.codec = "H264"
    bpy.context.scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    bpy.context.scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    bpy.context.scene.render.ffmpeg.audio_codec = "MP3"

    bpy.context.scene.render.film_transparent = False

    bpy.context.scene.render.filepath = bpy.context.scene.production_settings.preview_output

    #Render
    bpy.ops.render.render('INVOKE_DEFAULT', animation = True)

def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

def sync_visibility():
    #Get collection viewport visibility (from viewlayer)
    visibility = []
    master_collection = bpy.context.view_layer.layer_collection 
    for collection in traverse_tree(master_collection):
        visibility.append(collection.hide_viewport)

    #Set collection render visibility (from scene)
    master_collection = bpy.context.scene.collection    
    for i, collection in enumerate(traverse_tree(master_collection)):
        collection.hide_render = visibility[i]

    #Set object render visibility
    for obj in bpy.context.scene.objects:
        obj.hide_render = obj.hide_get()

def load_asset(library_path, asset, link, active):
    config = configparser.ConfigParser()
    config.read(asset)

    relative_path = config.get('ASSET', 'relative_path')
    data_type = config.get('ASSET', 'data_type')
    name = config.get('ASSET', 'name')

    #Make path
    full_path = os.path.join(library_path, relative_path)
    full_path = os.path.normpath(full_path)

    #Append/link
    with bpy.data.libraries.load(full_path, link=link) as (data_from, data_to):

        asset = [a for a in getattr(data_from, data_type) if a == name]
        setattr(data_to, data_type, asset)
    
    #Link to scene
    if data_type in 'collections':
        for collection in data_to.collections:
            if active:
                bpy.context.collection.children.link(collection)
            else:
                bpy.context.scene.collection.children.link(collection)
            
            

    if data_type in 'objects':
        for obj in data_to.objects:
            if active:
                bpy.context.collection.objects.link(obj)
            else:
                 bpy.context.scene.collection.objects.link(obj)
            
    return asset[0].name

# chunk generator
def chunk_iter(data):
    total_length = len(data)
    end = 4

    while(end + 8 < total_length):     
        length = int.from_bytes(data[end + 4: end + 8], 'big')
        begin_chunk_type = end + 8
        begin_chunk_data = begin_chunk_type + 4
        end = begin_chunk_data + length

        yield (data[begin_chunk_type: begin_chunk_data],
               data[begin_chunk_data: end])

def read_metadata():
    png = "C:/Users/Paul/Desktop/lib/untitled.png"

    with open(png, 'rb') as fobj:
        data = fobj.read()

    # check signature
    assert data[:8] == b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'

    for chunk_type, chunk_data in chunk_iter(data):
        if chunk_type == b'tEXt':
            print(*chunk_data.decode('iso-8859-1').split('\0'))
                      
def get_animation():
    
    obj = bpy.context.object

    if obj.animation_data.action is not None:
        animation_data = []
        selection = False
        frame = []

        for fcu in bpy.context.visible_fcurves:
            keys = []   
            for keyframe in fcu.keyframe_points:
                if keyframe.select_control_point == True:
                    key = []
                    selection = True

                    frame.append(keyframe.co[0])
                    key.append(keyframe.co[:])                                       
                    key.append(keyframe.handle_left[:])                    
                    key.append(keyframe.handle_right[:])
                    key.append(keyframe.handle_left_type)
                    key.append(keyframe.handle_right_type)
                    key.append(keyframe.interpolation)
                    key.append(keyframe.easing)                   
                    keys.append(key)       

            if keys :     
                fcurve = (fcu.data_path, fcu.array_index, keys)
                animation_data.append(fcurve)        
        
        if frame:
            animation_data.append((min(frame), max(frame)))

        if selection:
            return animation_data
        else:
            return "error"
    else:
        return "error"

def set_animation(anim, mix_factor):
    first_frame = anim[-1][0]
    last_frame = anim[-1][1]

    if first_frame == last_frame:
        mix = True
    else:
        mix = False

    frame_current = bpy.context.scene.frame_current
    frame_delta = frame_current - first_frame

    anim = anim[:-1]

    obj = bpy.context.object
    
    selected_bones = []
    if bpy.context.mode == 'POSE':
        for bone in obj.data.bones:
            if bone.select:
                selected_bones.append(bone.name)
    
    #Check if action exist
    if obj.animation_data.action is None:
        obj.animation_data.action = bpy.data.actions.new(obj.name+"Action")
    action = obj.animation_data.action
    
    for a in anim:        
        
        #Check if bone is selected
        if selected_bones:
            anim_bone_name = a[0].split('"')[1]
            if anim_bone_name not in selected_bones:
                continue
        
        #Check if fcurve exist
        fcu = action.fcurves.find(data_path=a[0], index=a[1])
        if fcu is None:
            fcu = action.fcurves.new(data_path=a[0], index=a[1])
        
        for key in a[2]:
            frame = key[0][0] + frame_delta
            value = key[0][1]
            if mix:
                value_current = fcu.evaluate(frame_current)
                value = (value*mix_factor + value_current*(1-mix_factor))
            else:
                handle_left_x = key[1][0] + frame_delta
                handle_left_y = key[1][1]
                handle_right_x = key[2][0] + frame_delta
                handle_right_y = key[2][1]
                handle_left_type = key[3]
                handle_right_type = key[4]
            interpolation = key[5]
            easing = key[6]

            keyframe = fcu.keyframe_points.insert(frame, value)

            if not mix:
                keyframe.handle_left_type = handle_left_type
                keyframe.handle_right_type = handle_right_type
                keyframe.handle_left = (handle_left_x, handle_left_y)            
                keyframe.handle_right = (handle_right_x, handle_right_y)            
            keyframe.interpolation = interpolation
            keyframe.easing = easing


def export_thumbnail(first_frame, last_frame, output_file):
    
    #Bake
    settings = (
        bpy.context.scene.render.resolution_x,
        bpy.context.scene.render.resolution_y,
        bpy.context.scene.frame_start,
        bpy.context.scene.frame_end,
        bpy.context.scene.render.film_transparent,
        )

    #Disable overlay
    overlays = []
    for screen in bpy.data.screens:
        for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            overlays.append(space.overlay.show_overlays)
                            space.overlay.show_overlays = False


    bpy.context.scene.render.resolution_x = 512
    bpy.context.scene.render.resolution_y = 512
    bpy.context.scene.frame_start = first_frame
    bpy.context.scene.frame_end = last_frame
    bpy.context.scene.render.film_transparent = False
    #bpy.context.screen

    #ANIMATION
    if first_frame == last_frame:
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.context.scene.render.image_settings.color_mode = "RGB"
        bpy.context.scene.render.image_settings.color_depth = "8"
        bpy.context.scene.render.image_settings.compression = 15
        bpy.context.scene.render.filepath = output_file + ".png"
        bpy.ops.render.opengl(write_still=True)

    else:
        bpy.context.scene.render.image_settings.file_format = "FFMPEG"
        bpy.context.scene.render.image_settings.color_mode = "RGB"
        bpy.context.scene.render.ffmpeg.format = "QUICKTIME"
        bpy.context.scene.render.ffmpeg.codec = "H264"
        bpy.context.scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
        bpy.context.scene.render.ffmpeg.ffmpeg_preset = "GOOD"
        bpy.context.scene.render.ffmpeg.audio_codec = "NONE"
        bpy.context.scene.render.filepath = output_file + ".mov"
        
        bpy.ops.render.opengl(animation=True)

    #Restore
    (bpy.context.scene.render.resolution_x,
    bpy.context.scene.render.resolution_y,
    bpy.context.scene.frame_start,
    bpy.context.scene.frame_end,
    bpy.context.scene.render.film_transparent) = settings

    #Restore overlays
    i = 0
    for screen in bpy.data.screens:
        for area in screen.areas:
                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.overlay.show_overlays = overlays[i]
                            i += 1