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

# type: ignore

bl_info = {
    "name" : "WorkFlow",
    "author" : "Paul",
    "description" : "",
    "blender" : (2, 91, 0),
    "version" : (1, 8, 4),
    "location" : "View3D",
    "warning" : "",
    "category" : "",
}

import bpy

from . import addon_updater_ops

import os
from bpy_extras.io_utils import ImportHelper
from . functions import *
from . operators import *
from . properties import *
from . ui import *
from bpy.app.handlers import persistent

#PREFERENCES
class WORKFLOW_Preferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    production_settings_file: bpy.props.StringProperty(
        name="Production Settings File",
        subtype= "FILE_PATH",
    )
    asset_path: bpy.props.StringProperty(
        name="Asset Library Path",
        subtype= "FILE_PATH",
    )
    #ADDON UPDATER PREFERENCES
    auto_check_update : bpy.props.BoolProperty(
    name = "Auto-check for Update",
    description = "If enabled, auto-check for updates using an interval",
    default = False,
    )

    updater_intrval_months : bpy.props.IntProperty(
        name='Months',
        description = "Number of months between checking for updates",
        default=0,
        min=0
    )
    updater_intrval_days : bpy.props.IntProperty(
        name='Days',
        description = "Number of days between checking for updates",
        default=7,
        min=0,
    )
    updater_intrval_hours : bpy.props.IntProperty(
        name='Hours',
        description = "Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    updater_intrval_minutes : bpy.props.IntProperty(
        name='Minutes',
        description = "Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )


    def draw(self, context):
        layout = self.layout
        column = layout.column()
        column.prop(self, 'production_settings_file', expand=True)
        column.prop(self, 'asset_path', expand=True)
        addon_updater_ops.update_settings_ui(self,context)

@persistent
def update_handler(dummy):
    resolution_from_camera()

@persistent
def load_handler(dummy):
    check_updates()
    update_cam_link()

#REGISTER UNREGISTER
classes = (
    WORKFLOW_Preferences,
    WORKFLOW_PROP_Palette,
    WORKFLOW_PROP_Render,
    RELINK_PROP_Scene,
    RELINK_PROP_Data,
    WORKFLOW_OT_Color,
    WORKFLOW_PT_view3d_asset, 
    WORKFLOW_PT_view3d_layout_tools,
    WORKFLOW_PT_view3d_animation_tools,
    WORKFLOW_PT_view3d_palette, 
    WORKFLOW_PT_node_editor_tools,
    WORKFLOW_PT_object_palette,
    WORKFLOW_PT_camera_render,
    WORKFLOW_PT_node_editor_relink,
    WORKFLOW_PT_view3d_rendering_tools,
    WORKFLOW_OT_delete_scenes,
    WORKFLOW_OT_render_material,
    WORKFLOW_OT_projection_node,
    WORKFLOW_OT_publish_preview,
    WORKFLOW_OT_custom_preview,
    WORKFLOW_OT_sync_visibility,
    WORKFLOW_OT_load_asset,
    WORKFLOW_OT_export_keyframes,
    WORKFLOW_OT_export_dummy,
    WORKFLOW_OT_import_keyframes,
    WORKFLOW_OT_apply_keyframes,
    WORKFLOW_OT_copy_material,
    WORKFLOW_OT_copy_previous_keyframe,
    WORKFLOW_OT_next_next_keyframe,
    WORKFLOW_OT_resync,
    WORKFLOW_OT_import_audio,
    WORKFLOW_OT_update_asset,
    WORKFLOW_OT_convert_asset,
    WORKFLOW_OT_reload_images,
    WORKFLOW_OT_load_image,
    WORKFLOW_OT_delete_hidden,
    WORKFLOW_OT_clean_up,
    WORKFLOW_OT_info,
    WORKFLOW_OT_node_switch,
    WORKFLOW_OT_update_cam_link,
    WORKFLOW_OT_render,
    )

relink_types = ["Object", "Collection", "Material", "Image", "Action", "NodeTree", "ParticleSettings", "PoseBone"]

def register():
    addon_updater_ops.register(bl_info)

    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    if not hasattr(bpy.types.Object, 'Palette'):
        bpy.types.Object.Palette = bpy.props.PointerProperty(type=WORKFLOW_PROP_Palette, override={'LIBRARY_OVERRIDABLE'})
    
    if not hasattr(bpy.types.Camera, 'render'):
        bpy.types.Camera.render = bpy.props.PointerProperty(type=WORKFLOW_PROP_Render, override={'LIBRARY_OVERRIDABLE'})
    
    if not hasattr( bpy.types.Scene, 'previous_camera'):
        bpy.types.Scene.previous_camera = bpy.props.StringProperty(name="Previous Camera")
     
    if not hasattr( bpy.types.Scene, 'animation_filepath'):
        bpy.types.Scene.animation_filepath = bpy.props.StringProperty(name="Animation Filepath")

    if not hasattr( bpy.types.Scene, 'relink'):
        bpy.types.Scene.relink = bpy.props.CollectionProperty(type=RELINK_PROP_Scene)
    
    if not hasattr( bpy.types.ShaderNodeGroup, 'override'):
        bpy.types.ShaderNodeGroup.override = bpy.props.BoolProperty(name="Override", default=False)
    
    for tp in relink_types:
        data = getattr(bpy.types, tp)
        if not hasattr(data, 'relink'):
            data.relink = bpy.props.PointerProperty(type=RELINK_PROP_Data)

    bpy.app.handlers.depsgraph_update_post.append(update_handler)
    bpy.app.handlers.load_post.append(load_handler)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Object.Palette
    del bpy.types.Camera.render
    del bpy.types.Scene.previous_camera
    del bpy.types.Scene.animation_filepath
    del bpy.types.Scene.relink
    del bpy.types.ShaderNodeGroup.override
    for tp in relink_types:
        data = getattr(bpy.types, tp)
        del data.relink
    

    bpy.app.handlers.depsgraph_update_post.remove(update_handler)
    bpy.app.handlers.load_post.remove(load_handler)