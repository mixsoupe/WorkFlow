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
    

class WORKFLOW_OT_load_settings(bpy.types.Operator):
    
    bl_idname = "workflow.load_settings"
    bl_label = "Load Settings"

    def execute(self, context):        
        
        
        if context.preferences.addons['WorkFlow'].preferences.production_settings_file:
            load_settings(context.preferences.addons['WorkFlow'].preferences.production_settings_file)
            self.report({'INFO'}, 'Production settings loaded')
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, 'Select a production settings file in addon preferences')
            return {'CANCELLED'}
            
        """
        load_settings('D:/LaForge/Yuku/02-ASSETS/ADDONS/yuku.ini')
        return {'FINISHED'}
        """
        
class WORKFLOW_OT_render_material(bpy.types.Operator):
    
    bl_idname = "workflow.render_material"
    bl_label = "Render Material"

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
        if bpy.context.scene.production_settings.preview_output != "":
            wm = context.window_manager
            return wm.invoke_props_dialog(self)
        else:
            self.report({'ERROR'}, 'Load Settings before Render')
            return {'CANCELLED'}


class WORKFLOW_OT_playblast(bpy.types.Operator):
    
    bl_idname = "workflow.playblast"
    bl_label = "Playblast"

    def execute(self, context):
        if bpy.context.scene.production_settings.preview_output != "":
            playblast()
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, 'Load Settings before Playblast')
            return {'CANCELLED'}


class WORKFLOW_OT_sync_visibility(bpy.types.Operator):
    
    bl_idname = "workflow.sync_visibility"
    bl_label = "Sync Visibility"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        sync_visibility()
        return {'FINISHED'}


class WORKFLOW_OT_load_asset(bpy.types.Operator, ImportHelper):
    
    bl_idname = "workflow.load_asset"
    bl_label = "Load Asset"
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

    filepath = bpy.props.StringProperty(
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
            result = load_asset(folder, asset, link, active)     
            self.report({'INFO'}, '{} successfully loaded'.format(result))
        return {'FINISHED'}

    def invoke(self, context, event):
         
        if context.preferences.addons['WorkFlow'].preferences.asset_path:
            self.filepath = context.preferences.addons['WorkFlow'].preferences.asset_path
        wm = context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}


class WORKFLOW_OT_export_anim(bpy.types.Operator, ExportHelper):
    
    bl_idname = "workflow.export_anim"
    bl_label = "Export Animation"

    filepath = bpy.props.StringProperty(
        name="File Path", 
        maxlen= 1024
        )

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    filename_ext = ".json"

    def execute(self, context):


        with open(self.filepath, 'w') as outfile:
            json.dump(self.anim, outfile)

        self.report({'INFO'}, 'Animation exported')
        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.anim = get_animation()
        if self.anim == "error":
            self.report({'ERROR'}, 'No animation selected')
            return {'CANCELLED'}

        if context.preferences.addons['WorkFlow'].preferences.asset_path:
            self.filepath = context.preferences.addons['WorkFlow'].preferences.asset_path
        wm = context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}


class WORKFLOW_OT_import_anim(bpy.types.Operator, ImportHelper):
    
    bl_idname = "workflow.import_anim"
    bl_label = "Import Animation"

    filepath = bpy.props.StringProperty(
        name="File Path",
        maxlen= 1024
        )

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        bpy.context.scene.animation_filepath = self.filepath
        bpy.ops.workflow.apply_anim('INVOKE_DEFAULT')
        #bpy.ops.object.modal_operator('INVOKE_DEFAULT')
        #self.report({'INFO'}, 'Animation imported')        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        if context.preferences.addons['WorkFlow'].preferences.asset_path:
            self.filepath = context.preferences.addons['WorkFlow'].preferences.asset_path
        wm = context.window_manager.fileselect_add(self)
        
        return {'RUNNING_MODAL'}



class WORKFLOW_OT_apply_anim(bpy.types.Operator):
    
    bl_idname = "workflow.apply_anim"
    bl_label = "Apply Animation"
    bl_options = {"REGISTER", "UNDO"}

    mix_factor : bpy.props.FloatProperty(name = "Mix Factor", default = 1.0, min = 0, max = 1.0)

    def execute(self, context):    
        #browser = bpy.context.space_data.params
        #filepath = os.path.join(str(browser.directory, 'utf-8'), browser.filename)

        with open(self.filepath) as infile:
            anim = json.load(infile)
            set_animation(anim, self.mix_factor)

        return {'FINISHED'}
    
    def invoke(self, context, event):
        self.filepath = bpy.context.scene.animation_filepath
        wm = context.window_manager
        return wm.invoke_props_dialog(self)
    

