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
from bpy_extras.io_utils import ImportHelper
from . functions import *
from . operators import *
from . properties import *
from . ui import *

#PROPS
class WORKFLOW_PROP_Palette(bpy.types.PropertyGroup):
    color1: bpy.props.FloatVectorProperty(
        name="Color 1",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        override={'LIBRARY_OVERRIDABLE'},
        )
    color2: bpy.props.FloatVectorProperty(
        name="Color 2",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        override={'LIBRARY_OVERRIDABLE'},
        )
    color3: bpy.props.FloatVectorProperty(
        name="Color 3",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        override={'LIBRARY_OVERRIDABLE'},
        ) 
    color4: bpy.props.FloatVectorProperty(
        name="Color 4",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        override={'LIBRARY_OVERRIDABLE'},
        )
    color5: bpy.props.FloatVectorProperty(
        name="Color 5",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        override={'LIBRARY_OVERRIDABLE'},
        )
    randomA: bpy.props.FloatVectorProperty(
        name="Random A",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        override={'LIBRARY_OVERRIDABLE'},
        )
    randomB: bpy.props.FloatVectorProperty(
        name="Random B",
        subtype='COLOR',
        default=(0.0, 0.0, 0.0),
        min=0.0, max=1.0,
        override={'LIBRARY_OVERRIDABLE'},
        )

class WORKFLOW_PROP_Render(bpy.types.PropertyGroup):
    resolution_x: bpy.props.IntProperty(
        name="Resolution X",        
        default = 2048,
        min=1, max=15000,
        override={'LIBRARY_OVERRIDABLE'},
        update = update_resolution,
        )
        
    resolution_y: bpy.props.IntProperty(
        name="Y",        
        default = 872,
        min=1, max=15000,
        override={'LIBRARY_OVERRIDABLE'},
        update = update_resolution,
        )

class RELINK_PROP_Scene(bpy.types.PropertyGroup):

    uid: bpy.props.StringProperty(
        name="uid",
        )
    path: bpy.props.StringProperty(
        name="path",
        )
    version: bpy.props.StringProperty(
        name="version",
        )
    data_type: bpy.props.StringProperty(
        name="data_type",
        )
    data_name: bpy.props.StringProperty(
        name="data_name",
        )      
    
class RELINK_PROP_Data(bpy.types.PropertyGroup):

    uid: bpy.props.StringProperty(
        name="uid",
        )
    original_name: bpy.props.StringProperty(
        name="original_name",
        )
    master: bpy.props.BoolProperty(
        name="master",
        )
