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

from . import addon_updater_ops

import os
from bpy_extras.io_utils import ImportHelper
from . functions import *
from . operators import *
from . properties import *
from . ui import *

#test
#VIEW3D PANELS
class WORKFLOW_PT_view3d_palette(bpy.types.Panel):
    bl_label = "Palette"
    bl_idname = "WORKFLOW_PT_view3d_palette"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "WorkFlow"

    @classmethod
    def poll(cls,context):
        obj = context.active_object
        if obj is not None:
            obj_type = obj.type
            is_geometry = (obj_type in {'MESH',})         
            return is_geometry

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        
        obj = context.active_object
        
        layout.prop(obj.Palette, "color1")
        layout.prop(obj.Palette, "color2")
        layout.prop(obj.Palette, "color3")
        layout.prop(obj.Palette, "color4")
        layout.prop(obj.Palette, "color5")
        layout.prop(obj.Palette, "randomA")
        layout.prop(obj.Palette, "randomB")
        
        if bpy.context.mode == 'EDIT_MESH':
            layout.operator("workflow.color")

class WORKFLOW_PT_view3d_asset(bpy.types.Panel):
    bl_label = "Asset"
    bl_idname = "WORKFLOW_PT_view_3D_asset"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "WorkFlow"
    #bl_options = {'DEFAULT_CLOSED'}
        
    @classmethod
    def poll(cls,context):
        obj = context.active_object
        if obj is not None:
            if obj.relink.uid != "":       
                return True


    def draw(self, context):
        obj = context.active_object
        layout = self.layout
        for item in context.scene.relink:            
            if item.uid == obj.relink.uid:
                layout.label(text = item.data_name )
                layout.label(text = item.uid ) 
                layout.prop(item, "path", text="Path")   
                layout.label(text = "VERSION: " + item.version)
                layout.operator("workflow.update_asset")
                if check_asset(item.path, item.version):
                    layout.label(text = "NEW VERSION AVAILABLE", icon ="ERROR")


class WORKFLOW_PT_view3d_layout_tools(bpy.types.Panel):
    bl_label = "Layout Tools"
    bl_idname = "WORKFLOW_PT_view_3D_layout_tools"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "WorkFlow"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.operator("workflow.load_asset")
        layout.operator("workflow.import_audio")
        layout.row().separator()
        layout.operator("workflow.render_material")
        layout.operator("workflow.sync_visibility")
        layout.row().separator()
        layout.operator("workflow.resync")

class WORKFLOW_PT_view3d_animation_tools(bpy.types.Panel):
    bl_label = "Animation Tools"
    bl_idname = "WORKFLOW_PT_view_3D_animation_tools"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "WorkFlow"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        #Check for update
        addon_updater_ops.check_for_update_background()
        if addon_updater_ops.updater.update_ready == True:
            layout.label(text = "New addon version available", icon="INFO")

        layout.operator("workflow.custom_preview")
        layout.operator("workflow.publish_preview")
        layout.row().separator()
        layout.operator("workflow.export_dummy", text="Export Keyframes")
        layout.operator("workflow.import_keyframes")
        layout.row().separator()
        layout.operator("workflow.copy_previous_keyframe")
        layout.operator("workflow.copy_next_keyframe")

class WORKFLOW_PT_view3d_production(bpy.types.Panel):
    bl_label = "Production"
    bl_idname = "WORKFLOW_PT_production"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "WorkFlow"

    def draw(self, context):        
        layout = self.layout
        layout.use_property_split = True
        scene = bpy.context.scene
        layout.operator("workflow.load_settings")
        column = layout.column()
        column.prop(scene.production_settings, "production")
        column.prop(scene.production_settings, "status")
        column.enabled = False


#PROPERTIES PANELS
class WORKFLOW_PT_object_palette(bpy.types.Panel):
    bl_label = "Palette"
    bl_idname = "WORKFLOW_PT_object_palette"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'    
    bl_context = "object"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls,context):
        obj = context.active_object
        obj_type = obj.type
        is_geometry = (obj_type in {'MESH', 'CURVE', 'SURFACE', 'META', 'FONT', 'VOLUME', 'HAIR', 'POINTCLOUD'})
        
        return is_geometry

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        obj = context.active_object        
        layout.prop(obj.Palette, "color1")
        layout.prop(obj.Palette, "color2")
        layout.prop(obj.Palette, "color3")
        layout.prop(obj.Palette, "color4")
        layout.prop(obj.Palette, "color5")
        layout.prop(obj.Palette, "randomA")
        layout.prop(obj.Palette, "randomB")  

class WORKFLOW_PT_camera_render(bpy.types.Panel):
    bl_label = "Render"
    bl_idname = "WORKFLOW_PT_camera_render"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'    
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls,context):
        obj = context.active_object
        obj_type = obj.type
        is_camera = (obj_type in {'CAMERA', })
        
        return is_camera

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        obj = context.active_object        
        layout.prop(obj.data.render, "resolution_x")
        layout.prop(obj.data.render, "resolution_y")

#NODE EDITOR PANEL

class WORKFLOW_PT_node_editor_tools(bpy.types.Panel):
    bl_label = "Tools"
    bl_idname = "WORKFLOW_PT_node_tools"
    bl_space_type = "NODE_EDITOR"   
    bl_region_type = "UI"
    bl_category = "WorkFlow"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.operator("workflow.copy_material")
        layout.operator("workflow.projection_node")
        layout.operator("workflow.render_material")


#FILE BROWSER PANEL

class WORKFLOW_PT_import_anim(bpy.types.Panel):
    bl_label = "Workflow"
    bl_idname = "WORKFLOW_PT_import_anim"
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOLS'    
    bl_category = "WorkFlow"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.operator("workflow.apply_anim")