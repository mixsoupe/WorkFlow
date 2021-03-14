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
import uuid

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
    bpy.context.scene.render.filepath = load_settings('render_material_path') + material_name
    bpy.context.scene.render.use_stamp = False

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

def load_settings(setting):
    production_settings_file = bpy.context.preferences.addons['WorkFlow'].preferences.production_settings_file
   
    filename =  bpy.path.basename(bpy.context.blend_data.filepath)
    filename = filename.rsplit(".", 1)[0]
    
    #CONFIG PARSER
    config = configparser.ConfigParser()
    config.read(production_settings_file)

    #GET SETTINGS
    return eval(config.get('SETTINGS', setting))


def preview(filepath, publish = False):
    scene = bpy.context.scene

    #Change Settings
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.ffmpeg.format = "QUICKTIME"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.ffmpeg.ffmpeg_preset = "GOOD"
    scene.render.ffmpeg.audio_codec = "MP3"

    scene.render.film_transparent = False

    scene.render.filepath = filepath

    #Metadata
    scene.render.use_stamp_date = False
    scene.render.use_stamp_time = False
    scene.render.use_stamp_render_time = False
    scene.render.use_stamp_frame = True
    scene.render.use_stamp_frame_range = False
    scene.render.use_stamp_memory = False
    scene.render.use_stamp_hostname = False
    scene.render.use_stamp_camera = False
    scene.render.use_stamp_lens = False
    scene.render.use_stamp_scene = False
    scene.render.use_stamp_marker = False
    scene.render.use_stamp_filename = False
    scene.render.use_stamp_note = True
    scene.render.use_stamp = True

    #Render
    if publish:
        for screen in bpy.data.screens:
            for area in screen.areas:
                    if area.type == 'VIEW_3D':
                        for space in area.spaces:
                            if space.type == 'VIEW_3D':
                                space.overlay.show_overlays = False    
                                space.shading.type = 'MATERIAL'                                
                    if area.type == 'DOPESHEET_EDITOR':                        
                        for region in area.regions:
                            if region.type == 'WINDOW':
                                override = bpy.context.copy()                               
                                override = {'region': region, 'area': area}
                                bpy.ops.anim.previewrange_clear(override)

        bpy.context.space_data.region_3d.view_perspective = 'CAMERA'

        filename =  bpy.path.basename(filepath)
        filename = filename.rsplit(".", 1)[0]        
        scene.render.stamp_note_text = filename
        
        bpy.ops.render.opengl('INVOKE_DEFAULT', animation = True)

        filepath = filepath.split('//')
        dir_path = os.path.dirname(bpy.context.blend_data.filepath)
        path = os.path.join(dir_path, filepath[1])
        path = os.path.normpath(path)

    else:
        filename =  bpy.path.basename(bpy.context.blend_data.filepath)
        filename = filename.rsplit(".", 1)[0]        
        scene.render.stamp_note_text = filename

        bpy.ops.render.opengl('INVOKE_DEFAULT', animation = True)
            



        path = filepath
    
    #Open Folder
    path = os.path.dirname(path)
    os.startfile(path)



def traverse_tree(t):
    yield t
    for child in t.children:
        yield from traverse_tree(child)

def traverse_node_tree(note_tree):
    yield note_tree
    for node in note_tree.nodes:
        if node.bl_idname =="ShaderNodeGroup":
            if node.node_tree is not None:
                yield from traverse_node_tree(node.node_tree)

def parent_lookup(coll):
    parent_lookup = {}
    for coll in traverse_tree(coll):
        for c in coll.children.keys():
            parent_lookup.setdefault(c, coll.name)
    return parent_lookup

def recurLayerCollection(layerColl, collName):
    found = None
    if (layerColl.name == collName):
        return layerColl
    for layer in layerColl.children:
        found = recurLayerCollection(layer, collName)
        if found:
            return found

def sync_visibility():
    #Get collection viewport visibility (from viewlayer)
    visibility = []
    master_collection = bpy.context.view_layer.layer_collection 
    for collection in traverse_tree(master_collection):      
        if collection.collection.hide_viewport:
            visibility.append(True)
        else:
            visibility.append(collection.hide_viewport)


    #Set collection render visibility (from scene)
    master_collection = bpy.context.scene.collection    
    for i, collection in enumerate(traverse_tree(master_collection)):
        collection.hide_render = visibility[i]

    #Set object render visibility
    for obj in bpy.context.scene.objects:
        if obj.hide_viewport:
            obj.hide_render = True
        else:
            obj.hide_render = obj.hide_get()



def get_asset(library_path, asset):
    

    config = configparser.ConfigParser()
    config.read(asset)

    shortcut_path = config.get('ASSET', 'relative_path')
    data_type = config.get('ASSET', 'data_type')
    name = config.get('ASSET', 'name')

    #Make path
    full_path = os.path.join(library_path, shortcut_path)
    full_path = os.path.normpath(full_path)

    return name, data_type, full_path


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

def copy_keyframe(previous = False, next = False, ):

    frame_current = bpy.context.scene.frame_current    
    obj = bpy.context.object

    #Get selected bones
    selected_bones = []
    if bpy.context.mode == 'POSE':
        for bone in obj.data.bones:
            if bone.select:
                selected_bones.append(bone.name)

    if obj.animation_data is not None:  
        if obj.animation_data.action is not None:           
            for fcu in obj.animation_data.action.fcurves:

                #Check if bone is selected
                if selected_bones:
                    anim_bone_name = fcu.data_path.split('"')[1]
                    if anim_bone_name not in selected_bones:
                        continue

                #Get keyframe
                frames = []
                is_key = False
                for keyframe in fcu.keyframe_points:
                    if previous:                
                        if keyframe.co[0] < frame_current:
                            is_key = True
                            frames.append(keyframe.co[0])
                        else:
                            frames.append(1000000)

                    if next:                
                        if keyframe.co[0] > frame_current:
                            is_key = True
                            frames.append(keyframe.co[0])
                        else:
                            frames.append(1000000)

                if is_key:
                    frames = np.asarray(frames)
                    index = (np.abs(frames-frame_current)).argmin()   
                    
                    keyframe = fcu.keyframe_points[index]
                    frame_delta = frame_current - keyframe.co[0]

                    new_keyframe = fcu.keyframe_points.insert(frame_current, keyframe.co[1])    

                    new_keyframe.handle_left_type = keyframe.handle_left_type
                    new_keyframe.handle_right_type = keyframe.handle_right_type

                    new_keyframe.handle_left = (keyframe.handle_left[0]+frame_delta, keyframe.handle_left[1])            
                    new_keyframe.handle_right = (keyframe.handle_right[0]+frame_delta, keyframe.handle_right[1])  

                    new_keyframe.interpolation = keyframe.interpolation
                    new_keyframe.easing = keyframe.easing

def resync():
    
    #Get armature object collection
    collection_list = []
    master_collection = bpy.context.scene.collection 
    for collection in traverse_tree(master_collection):
        for obj in collection.objects:
            if obj.type == "ARMATURE":
                collection_list.append(collection.name)

    
    override = bpy.context.copy()
    for area in bpy.context.screen.areas:
        if area.type == 'OUTLINER':
            override['area'] = area
            for space in area.spaces:
                if space.type == 'OUTLINER':
                    space.display_mode = "VIEW_LAYER"                    
                    space.use_filter_complete = True
                    space.use_filter_object = False
                    space.use_filter_collection = True

                    for collection in collection_list:
                        #space.filter_text = "mere"
                        bpy.ops.outliner.select_all(override, action='SELECT')
                        bpy.ops.outliner.id_operation (override, type = 'OVERRIDE_LIBRARY_RESYNC_HIERARCHY')                 


def link_asset(name, data_type, path, active):

    with bpy.data.libraries.load(path, link=True) as (data_from, data_to):

        asset = [a for a in getattr(data_from, data_type) if a == name]
        setattr(data_to, data_type, asset)
    
    #Process collection
    if data_type in 'collections':
        for collection in data_to.collections:  
            empty = bpy.data.objects.new( "empty", None )
            if active:
                bpy.context.collection.objects.link(empty)
            else:
                bpy.context.scene.collection.objects.link(empty)

            empty.instance_type = "COLLECTION"
            empty.instance_collection = collection

            bpy.context.view_layer.objects.active = empty
            bpy.ops.object.make_override_library(collection='DEFAULT')

    #Process object
    if data_type in 'objects':
        for obj in data_to.objects:
            if active:
                bpy.context.collection.objects.link(obj)
            else:
                bpy.context.scene.collection.objects.link(obj)
            obj.override_create(remap_local_usages=True)

    return asset[0].name
              

def append_asset(name, data_type, path, active):
    uid = uuid.uuid1()
    #Récupération des nom originaux grâce à un link, puis suppression de ce link
    if data_type in 'collections':
        with bpy.data.libraries.load(path, link=True) as (data_link_from, data_link_to):
            data_link_to.collections = [c for c in data_link_from.collections if c == name]   
    
        for collection in data_link_to.collections:
            if collection is not None:           
                original_object = []
                for obj in collection.all_objects:
                    original_object.append(obj.name)            
                bpy.data.libraries.remove(collection.library) 
    
    #Append/link
    with bpy.data.libraries.load(path, link=False) as (data_from, data_to):

        asset = [a for a in getattr(data_from, data_type) if a == name]
        setattr(data_to, data_type, asset)
    
    #Process collection
    if data_type in 'collections':
        for collection in data_to.collections:
            if active:
                bpy.context.collection.children.link(collection)
            else:
                bpy.context.scene.collection.children.link(collection)
            
            #Set uid
            collection.relink.master = True
            for child_collection in traverse_tree(collection):
                child_collection.relink.uid = str(uid)                    
            for i, obj in enumerate(collection.all_objects):
                obj.relink.uid = str(uid)
                obj.relink.original_name = original_object[i]
                for slot in obj.material_slots:
                    if slot.material is not None:
                        mat = slot.material
                        mat.relink.uid = str(uid)
                        for node_tree in traverse_node_tree(mat.node_tree):
                            node_tree.relink.uid = str(uid)
                            for node in node_tree.nodes:
                                if node.bl_idname=="ShaderNodeTexImage":
                                    if node.image is not None:
                                        node.image.relink.uid = str(uid)                            

                if obj.animation_data is not None:
                    if obj.animation_data.action is not None:
                        obj.animation_data.action.relink.uid = str(uid)

                for particles in obj.particle_systems:
                    particles.settings.relink.uid = str(uid)

                #Tag constraints
                if obj.type == "ARMATURE":
                    for bone in obj.pose.bones:
                        metadata = {}
                        c_names = []
                        for constraint in bone.constraints:
                            c_names.append(constraint.name)
                        metadata["constraints"] = c_names
                        bone.relink.metadata = json.dumps(metadata)
                metadata = {}
                c_names = []
                for constraint in obj.constraints:
                    c_names.append(constraint.name)
                metadata["constraints"] = c_names
                obj.relink.metadata = json.dumps(metadata)

    #Process object
    if data_type in 'objects':
        for obj in data_to.objects:
            if active:
                bpy.context.collection.objects.link(obj)
            else:
                bpy.context.scene.collection.objects.link(obj)
            """ Disable relink for single object
            #Set uid
            obj.relink.uid = str(uid)
            for slot in obj.material_slots:
                mat = slot.material
                mat.relink.uid = str(uid)
            """

    #Set Scene uid
    scene = bpy.context.scene
    new_item = scene.relink.add()
    new_item.uid = str(uid)
    new_item.path = bpy.path.relpath(path, start=None)   
    mod_time = os.path.getmtime(path)
    date = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(mod_time))
    new_item.version = date
    new_item.data_type = data_type
    new_item.data_name = name

    return asset[0].name, uid


def relink():
    #Get asset metadata
    uid = bpy.context.object.relink.uid 
    for item in bpy.context.scene.relink:
        if item.uid == uid:
            name = item.data_name
            data_type = item.data_type
            path = bpy.path.abspath(item.path)


    actions = {}
    #Remove objects
    for obj in bpy.data.objects:
        if obj.relink.uid == uid:
            if obj.animation_data is not None:
                if obj.animation_data.action is not None:
                    actions[obj.relink.original_name] = obj.animation_data.action
            if obj.data is not None:
                data_types = ["meshes", "armatures", "curves", "cameras", "grease_pencils", 
                    "lights", "lattices", "lightprobes", "metaballs", "volumes"]
                for data in data_types:
                    try:
                        eval("bpy.data.{}.remove(obj.data)".format(data))
                    except:
                        pass                
            try:
                bpy.data.objects.remove(obj)
            except:
                pass

    #Remove collections
    coll_scene = bpy.context.scene.collection
    coll_parents = parent_lookup(coll_scene)

    collection_delete = []
    for collection in bpy.data.collections:        
        if collection.relink.uid == uid and collection.relink.master:
            coll_parent = coll_parents.get(collection.name)
            for child_collection in traverse_tree(collection):
                collection_delete.append(child_collection)

    for collection in reversed(collection_delete):
        bpy.data.collections.remove(collection)
    
    for collection in bpy.data.collections:        
        if collection.relink.uid == uid:
            bpy.data.collections.remove(collection)  

    #Remove materials
    for material in bpy.data.materials:
        if material.relink.uid == uid:
            bpy.data.materials.remove(material)
    
    #Remove actions:
    for action in bpy.data.actions:
        if action.relink.uid == uid and action not in actions.values():
            bpy.data.actions.remove(action)
        
    #Remove images:
    for image in bpy.data.images:
        if image.relink.uid == uid:
            bpy.data.images.remove(image)
    
    #Remove nodes:
    for node in bpy.data.node_groups:
        if node.relink.uid == uid:
            bpy.data.node_groups.remove(node)
    
    #Remove particle settings:
    for particle in bpy.data.particles:
        if particle.relink.uid == uid:
            bpy.data.particles.remove(particle)

    #Remove scene uid
    for index, item in enumerate(bpy.context.scene.relink):
        if item.uid == uid:
            bpy.context.scene.relink.remove(index)
    
    #Reload
    
    layer_collection = bpy.context.view_layer.layer_collection
    layerColl = recurLayerCollection(layer_collection, coll_parent)
    bpy.context.view_layer.active_layer_collection = layerColl

    result, new_uid = append_asset(name, data_type, path, True)

    #Remap Actions
    for obj in bpy.data.objects:
        if obj.relink.uid == str(new_uid):
            if obj.relink.original_name in actions.keys():
                obj.animation_data.action = actions[obj.relink.original_name]

    