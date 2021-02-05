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

bl_info = {
    "name" : "WorkFlow",
    "author" : "Paul",
    "description" : "",
    "blender" : (2, 91, 0),
    "version" : (1, 0, 6),
    "location" : "View3D",
    "warning" : "",
    "category" : "",
}

import bpy
import os
from bpy_extras.io_utils import ImportHelper
from . functions import *
from . operators import *
from . properties import *
from . ui import *
from bpy.app.handlers import persistent

#test
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

    def draw(self, context):
        layout = self.layout
        column = layout.column()
        column.prop(self, 'production_settings_file', expand=True)
        column.prop(self, 'asset_path', expand=True)

@persistent
def update_handler(dummy):
    resolution_from_camera()

#REGISTER UNREGISTER
classes = (
    WORKFLOW_Preferences,
    WORKFLOW_PROP_Palette,
    WORKFLOW_PROP_Render,
    WORKFLOW_PROP_production_settings,
    WORKFLOW_OT_Color,
    WORKFLOW_PT_view3d_production,    
    WORKFLOW_PT_view3d_layout_tools,
    WORKFLOW_PT_view3d_animation_tools,
    WORKFLOW_PT_view3d_palette,   
    WORKFLOW_PT_node_editor_tools,
    WORKFLOW_PT_object_palette,
    WORKFLOW_PT_camera_render,
    WORKFLOW_PT_import_anim,
    WORKFLOW_OT_delete_scenes,
    WORKFLOW_OT_render_material,
    WORKFLOW_OT_projection_node,
    WORKFLOW_OT_load_settings,
    WORKFLOW_OT_playblast,
    WORKFLOW_OT_sync_visibility,
    WORKFLOW_OT_load_asset,
    WORKFLOW_OT_export_anim,
    WORKFLOW_OT_import_anim,
    WORKFLOW_OT_apply_anim,
    WORKFLOW_OT_copy_material,
    )

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    if not hasattr(bpy.types.Object, 'Palette'):
        bpy.types.Object.Palette = bpy.props.PointerProperty(type=WORKFLOW_PROP_Palette, override={'LIBRARY_OVERRIDABLE'})
    
    if not hasattr(bpy.types.Camera, 'render'):
        bpy.types.Camera.render = bpy.props.PointerProperty(type=WORKFLOW_PROP_Render, override={'LIBRARY_OVERRIDABLE'})
    
    if not hasattr( bpy.types.Scene, 'previous_camera'):
        bpy.types.Scene.previous_camera = bpy.props.StringProperty(name="Previous Camera")
    
    if not hasattr( bpy.types.Scene, 'production_settings'):
        bpy.types.Scene.production_settings = bpy.props.PointerProperty(type=WORKFLOW_PROP_production_settings)
 
    if not hasattr( bpy.types.Scene, 'animation_filepath'):
        bpy.types.Scene.animation_filepath = bpy.props.StringProperty(name="Animation Filepath")

    bpy.app.handlers.depsgraph_update_post.append(update_handler)
def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Object.Palette
    del bpy.types.Camera.render
    del bpy.types.Scene.previous_camera
    del bpy.types.Scene.production_settings
    del bpy.types.Scene.animation_filepath

    bpy.app.handlers.depsgraph_update_post.remove(update_handler)