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


import bpy
import os
from bpy_extras.io_utils import ImportHelper, ExportHelper
from . functions import *
from . operators import *
from . properties import *
from . ui import *
from . nodes import *
import json

#OPERATORS

class WORKFLOW_OT_Color(bpy.types.Operator):
    
    bl_idname = "workflow.color"
    bl_label = "Color Fill"
    bl_description = "Color faces with selected color"
    bl_options = {"REGISTER", "UNDO"}

    options: bpy.props.EnumProperty(
        name="Color Select",
        default=0,
        items = [
            ('color1', "Color 1", "", 0),
            ('color2', "Color 2", "", 1),
            ('color3', "Color 3", "", 2),
            ('color4', "Color 4", "", 3),
            ('color5', "Color 5", "", 4),
            ('random', "Random", "", 5),
            ]
        )
    @classmethod
    def poll(cls,context):
        context = bpy.context.mode
        is_edit_mode = (context in {'EDIT_MESH'})
        return is_edit_mode

    def execute(self, context):
        mask_list = ["color1", "color2", "color3", "color4", "color5", "random"]
        color_fill(self.options, mask_list)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class WORKFLOW_OT_delete_scenes(bpy.types.Operator):
    
    bl_idname = "workflow.delete_scenes"
    bl_label = "Delete Other Scenes"
    bl_options = {"REGISTER", "UNDO"}


    def execute(self, context):        
        delete_scenes()
        return {'FINISHED'}

class WORKFLOW_OT_projection_node(bpy.types.Operator):
    
    bl_idname = "workflow.projection_node"
    bl_label = "Create Projection Node"
    bl_description = "Create projection node from camera"
    bl_options = {"REGISTER", "UNDO"}    
    
    options: bpy.props.EnumProperty(
        name="Camera Select",
        default=0,
        items = enum_cameras,
        )

    @classmethod
    def poll(cls,context):
        obj = context.active_object
        obj_type = obj.type
        is_geometry = (obj_type in {'MESH',})

        return is_geometry
    
    def execute(self, context):
        camera = bpy.data.objects[self.options]
        shader_node_tree = bpy.context.space_data.edit_tree
        create_projection_node(shader_node_tree, camera)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

class WORKFLOW_OT_copy_material(bpy.types.Operator):
    
    bl_idname = "workflow.copy_material"
    bl_label = "Copy Material"
    bl_description = "Duplicate current material"
    bl_options = {"REGISTER", "UNDO"}


    @classmethod
    def poll(cls,context):
        obj = context.active_object
        obj_type = obj.type
        is_geometry = (obj_type in {'MESH',})

        return is_geometry
    
    def execute(self, context):
        obj = bpy.context.active_object
        mat = obj.active_material
        obj.active_material = mat.copy()

        return {'FINISHED'}
        
class WORKFLOW_OT_render_material(bpy.types.Operator):
    
    bl_idname = "workflow.render_material"
    bl_label = "Render Material"
    bl_description = "Render material in selected camera view"

    camera: bpy.props.EnumProperty(
        name="Camera Select",
        default=0,
        items = enum_cameras,
        )
    isolate: bpy.props.BoolProperty(
        name="Isolate Material",
        default=True,
        )    
    engine: bpy.props.EnumProperty(
        name="Render Engine",
        items = [
            ('BLENDER_EEVEE', "Eevee", "", 0),
            ('CYCLES', "Cycles", "", 1),
            ]
        )

    @classmethod
    def poll(cls,context):
        obj = context.active_object
        if obj is not None:
            obj_type = obj.type
            is_geometry = (obj_type in {'MESH',})
            return is_geometry

    def execute(self, context):
        if self.camera == "":
            self.report({'ERROR'}, 'Select a camera')
            return {'CANCELLED'}
        else:
            shader_node_tree = bpy.context.active_object.active_material.node_tree
            result = render_material(shader_node_tree, self.camera, self.isolate, self.engine)
            self.report({'INFO'}, '{} rendered'.format(result))
            return {'FINISHED'}


    def invoke(self, context, event):
        if context.preferences.addons['WorkFlow'].preferences.production_settings_file:
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        else:
            self.report({'ERROR'}, 'Load Settings before Render')
            return {'CANCELLED'}


class WORKFLOW_OT_publish_preview(bpy.types.Operator):
    
    bl_idname = "workflow.publish_preview"
    bl_label = "Publish Preview"
    bl_description = "Export preview with publish settings"

    def execute(self, context):
        if context.preferences.addons['WorkFlow'].preferences.production_settings_file:
            filepath = load_settings('preview_output')
            preview(filepath, publish = True)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, 'Load Settings before Playblast')
            return {'CANCELLED'}

class WORKFLOW_OT_custom_preview(bpy.types.Operator, ExportHelper):
    
    bl_idname = "workflow.custom_preview"
    bl_label = "Custom Preview"
    bl_description = "Export preview with current settings and custom path"

    filter_glob: bpy.props.StringProperty( 
        default='*.mov', 
        options={'HIDDEN'} 
        )
    filepath: bpy.props.StringProperty(
        name="File Path", 
        description="File path used for export playblast", 
        maxlen= 1024
        )
    
    filename_ext = ".mov"

    def execute(self, context):
        preview(self.filepath, publish = False)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}




class WORKFLOW_OT_sync_visibility(bpy.types.Operator):
    
    bl_idname = "workflow.sync_visibility"
    bl_label = "Sync Visibility"
    bl_description = "Synchronise render visibility with viewport visibility"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        sync_visibility()
        return {'FINISHED'}


class WORKFLOW_OT_load_asset(bpy.types.Operator, ImportHelper):
    
    bl_idname = "workflow.load_asset"
    bl_label = "Load Asset"
    bl_description = "Load asset from shortcut"
    bl_options = {"REGISTER", "UNDO"}

    filter_glob: bpy.props.StringProperty( 
        default='*.ini', 
        options={'HIDDEN'} 
        )
    link: bpy.props.BoolProperty( 
        name='Link', 
        description='Link the asset', 
        default=False
        )
    active: bpy.props.BoolProperty( 
        name='Active Collection', 
        description='Put new objects on the active collection', 
        default=True
        )

    filepath: bpy.props.StringProperty(
        name="File Path", 
        description="File path used for importing the OBJ file", 
        maxlen= 1024
        )

    files: bpy.props.CollectionProperty(type=bpy.types.PropertyGroup)

    def execute(self, context):

        link = self.properties.link
        active = self.properties.active

        folder = (os.path.dirname(self.filepath))
        for i in self.files:
            asset = (os.path.join(folder, i.name))
            name, data_type, path = get_asset(folder, asset)
            if link:
                result = link_asset(name, data_type, path, active) 
            else:
                result, uid = append_asset(name, data_type, path, active)     
            self.report({'INFO'}, '{} successfully loaded'.format(result))
        return {'FINISHED'}

    def invoke(self, context, event):
         
        if context.preferences.addons['WorkFlow'].preferences.asset_path:
            self.filepath = context.preferences.addons['WorkFlow'].preferences.asset_path
        wm = context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}


class WORKFLOW_OT_export_keyframes(bpy.types.Operator, ExportHelper):
    
    bl_idname = "workflow.export_keyframes"
    bl_label = "Export Keyframes"
    

    filepath: bpy.props.StringProperty(
        name="File Path", 
        maxlen= 1024
        )

    filter_glob: bpy.props.StringProperty(
        default="*.png;*.mov",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    filename_ext = ""

    def execute(self, context):

        json_file = os.path.splitext(self.filepath)[0]+".json"
        thumbnail_file = os.path.splitext(self.filepath)[0]

        with open(json_file, 'w') as outfile:
            json.dump(self.anim, outfile)
        
        export_thumbnail(self.anim[-1][0], self.anim[-1][1], thumbnail_file) 

        self.report({'INFO'}, 'Keyframes exported')
        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.anim = get_animation()
        if self.anim == "error":
            self.report({'ERROR'}, 'No keyframe selected')
            return {'CANCELLED'}

        if context.preferences.addons['WorkFlow'].preferences.asset_path:
            self.filepath = context.preferences.addons['WorkFlow'].preferences.asset_path
        wm = context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}

class WORKFLOW_OT_export_dummy(bpy.types.Operator):
    
    bl_idname = "workflow.export_dummy"
    bl_label = "dummy"
    bl_description = "Export selected keyframes and take snapshot"

    @classmethod
    def poll(cls,context):
        obj = context.active_object
        if obj is not None:
            if obj.animation_data is not None:  
                if obj.animation_data.action is not None: 
                    return True

    def execute(self, context):
        screen = context.screen
        override = bpy.context.copy()

        # Update the context
        dopesheet_count = 0
        for area in screen.areas:
            if area.type == 'DOPESHEET_EDITOR':
                dopesheet_count += 1
                for region in area.regions:
                    if region.type == 'WINDOW':
                        override = {'region': region, 'area': area}
        if dopesheet_count>1:
            self.report({'ERROR'}, 'Too many dopesheets. Call the operator (F3 > Export Keyframes) from the dopesheet')
            return {'CANCELLED'}

        try:
            bpy.ops.workflow.export_keyframes(override, 'INVOKE_DEFAULT')
            return {'FINISHED'}
            
        except RuntimeError as ex:
            error_report = "\n".join(ex.args)
            self.report({'ERROR'}, error_report)
            return {'CANCELLED'}


class WORKFLOW_OT_import_keyframes(bpy.types.Operator, ImportHelper):
    
    bl_idname = "workflow.import_keyframes"
    bl_label = "Import Keyframes"
    bl_description = "Import and mix keyframes"

    filepath: bpy.props.StringProperty(
        name="File Path",
        maxlen= 1024
        )

    filter_glob: bpy.props.StringProperty(
        default="*.png;*.mov",
        options={'HIDDEN'},
        maxlen=255,
    )

    @classmethod
    def poll(cls,context):
        obj = context.active_object
        if obj is not None:
            return True

    def execute(self, context):
        json_file = (os.path.splitext(self.filepath)[0] + ".json")
        bpy.context.scene.animation_filepath = json_file
        bpy.ops.workflow.apply_keyframes('INVOKE_DEFAULT')
     
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if context.preferences.addons['WorkFlow'].preferences.asset_path:
            self.filepath = context.preferences.addons['WorkFlow'].preferences.asset_path
        wm = context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}


class WORKFLOW_OT_apply_keyframes(bpy.types.Operator):
    
    bl_idname = "workflow.apply_keyframes"
    bl_label = "Apply Keyframes"
    bl_options = {"REGISTER", "UNDO"}

    mix_factor : bpy.props.FloatProperty(name = "Mix Factor", default = 1.0, min = 0, max = 1.0)

    def execute(self, context):    
        #browser = bpy.context.space_data.params
        #filepath = os.path.join(str(browser.directory, 'utf-8'), browser.filename)
        set_animation(self.anim, self.mix_factor)
        return {'FINISHED'}
    
    def modal(self, context, event):
        if event.type == 'MOUSEMOVE':
            set_animation(self.anim, self.mix_factor)
            return {'FINISHED'}

        return {'RUNNING_MODAL'}
    
    def invoke(self, context, event):
        filepath = bpy.context.scene.animation_filepath
        with open(filepath) as infile:
            self.anim = json.load(infile)
        
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def draw(self, context):
        self.layout.use_property_split = True

        row = self.layout.row()
        if self.anim[-1][0] == self.anim[-1][1]:
            row.prop(self, "mix_factor")


class WORKFLOW_OT_copy_previous_keyframe(bpy.types.Operator):
    
    bl_idname = "workflow.copy_previous_keyframe"
    bl_label = "Copy Previous Keyframe"
    bl_description = "Copy/paste previous keyframe"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls,context):
        obj = context.active_object
        if obj is not None:
            if obj.animation_data is not None:  
                if obj.animation_data.action is not None: 
                    return True

    def execute(self, context):
        copy_keyframe(previous = True)

        return {'FINISHED'}

class WORKFLOW_OT_next_next_keyframe(bpy.types.Operator):
    
    bl_idname = "workflow.copy_next_keyframe"
    bl_label = "Copy Next Keyframe"
    bl_description = "Copy/paste next keyframe"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls,context):
        obj = context.active_object
        if obj is not None:
            if obj.animation_data is not None:  
                if obj.animation_data.action is not None: 
                    return True
    
    def execute(self, context):
        copy_keyframe(next = True)

        return {'FINISHED'}


class WORKFLOW_OT_resync(bpy.types.Operator):
    
    bl_idname = "workflow.resync"
    bl_label = "Resync Overrides"
    bl_description = "Resync librairies overrides"
    
    def execute(self, context):
        override = bpy.context.copy()
        for area in bpy.context.screen.areas:
            if area.type == 'OUTLINER':
                override['area'] = area

                bpy.ops.outliner.id_operation (override, type = 'OVERRIDE_LIBRARY_RESYNC_HIERARCHY')                 
                
                return {'FINISHED'}
        
        self.report({'ERROR'}, "Outliner must be open")
        return {'CANCELLED'}


class WORKFLOW_OT_import_audio(bpy.types.Operator):
    
    bl_idname = "workflow.import_audio"
    bl_label = "Import Audio"
    bl_description = "Import audio and setup scene"
    
    def execute(self, context):
        if context.preferences.addons['WorkFlow'].preferences.production_settings_file:
            scene = bpy.context.scene

            if not scene.sequence_editor:
                scene.sequence_editor_create()

            for sequence in scene.sequence_editor.sequences:
                    if sequence.type == 'SOUND':
                        scene.sequence_editor.sequences.remove(sequence)

            audio_file = load_settings('audio_file')
            soundstrip = scene.sequence_editor.sequences.new_sound("audio", audio_file, 1, 1)

            scene.frame_start = 1
            scene.frame_end = soundstrip.frame_final_end

            bpy.context.scene.use_audio_scrub = True
            bpy.context.scene.sync_mode = 'AUDIO_SYNC'

            return {'FINISHED'}

        else:
            self.report({'ERROR'}, 'Load Settings before import audio')
            return {'CANCELLED'}

class WORKFLOW_OT_update_asset(bpy.types.Operator):
    
    bl_idname = "workflow.update_asset"
    bl_label = "Update Asset"
    bl_description = "Update Asset"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):

        status, message = relink()

        if status == "warning":
            self.report({'WARNING'}, message)
        else:
            self.report({'INFO'}, 'Asset updated')
        return {'FINISHED'}
