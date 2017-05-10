bl_info = {
	"name": "GT Archviz Tools",
	"author": "Glynn Taylor",
	"version": (0, 1, 1),
	"blender": (2, 7, 8),
	"api": 35853,
	"location": "View > Tools > GT AV Tools",
	"description": "A collection of tools for archviz optimisation",
	"warning": "",
	"wiki_url": "",
	"tracker_url": "",
	"category": "Mesh"
	}

import bpy
from collections import defaultdict
import random
from mathutils import Color
import colorsys
import fnmatch
import math

class LayoutDemoPanel(bpy.types.Panel):
	"""Creates a Panel in the scene context of the properties editor"""
	bl_label = "GT AV Tools"
	bl_idname = "SCENE_GT_archviz"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "GT"

	#PROPERTIES
	bpy.types.Scene.scn_property= bpy.props.StringProperty( attr="inText", name="inText", description="GT AV Tools", default="*" )
	#bpy.types.Scene.scn_limitproperty = bpy.props.IntProperty(name = "inLimit",default=9999)

	bpy.types.Scene.scn_doubles = bpy.props.FloatProperty(name = "doubles",default=0.0001)
	bpy.types.Scene.scn_dissolveAngle = bpy.props.FloatProperty(name = "dissolveAngle",default=35)
	
	def draw(self, context):
		layout = self.layout

		scene = context.scene
		layout.label(text="Select by regex")
		
		row0 = layout.row()
		row0.scale_y = 1.0
		row0.prop( scene, "scn_property", text="Regex" )
		row0.operator("gt.select_by_regex")
		#col.prop( scene, "scn_limitproperty", text="Limit:" )
		
		layout.label(text="Other operators")
		row1 = layout.row()
		row1.scale_y = 1.0
		row1.prop( scene, "scn_doubles", text="Doubles Threshold" )
		row1.operator("gt.remove_doubles")
		
		row2 = layout.row()
		row2.scale_y = 1.0
		row2.prop( scene, "scn_dissolveAngle", text="Dissolve Angle" )
		row2.operator("gt.planar_dissolve")

def RunSelectByRegex(context):
	scene = bpy.context.scene
	bpy.context.scene.objects.active = None
	foo_objs = [obj for obj in scene.objects if fnmatch.fnmatchcase(obj.name, context.scene.scn_property)]
	#bpy.context.selected_objects = foo_objs
	for obj in foo_objs:
		bpy.data.objects[obj.name].select = True
	print("Finished SelectByRegex")

def RunRemoveDoubles(context):
	for ob in bpy.context.scene.objects:
		if ob.type == 'MESH':
			ob.select = True 
			bpy.context.scene.objects.active = ob
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.remove_doubles(threshold=context.scene.scn_doubles)
			bpy.ops.object.editmode_toggle()
	print("Finished RemoveDoubles")

def RunPlanarDissolve(context):
	for ob in bpy.context.scene.objects:
		if ob.type == 'MESH':
			ob.select = True 
			bpy.context.scene.objects.active = ob
			bpy.ops.object.editmode_toggle()
			bpy.ops.mesh.dissolve_limited(angle_limit=math.radians(context.scene.scn_dissolveAngle))
			bpy.ops.object.editmode_toggle()
	print("Finished RemoveDoubles")

class SelectByRegex(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.select_by_regex"
	bl_label = "Select By Regex"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunSelectByRegex(context)
		return {'FINISHED'}

class RemoveDoubles(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.remove_doubles"
	bl_label = "Merge nearby verts"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunRemoveDoubles(context)
		return {'FINISHED'}

class PlanarDissolve(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.planar_dissolve"
	bl_label = "Dissolve by angle"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunPlanarDissolve(context)
		return {'FINISHED'}

def register():
	bpy.utils.register_class(SelectByRegex)
	bpy.utils.register_class(RemoveDoubles)
	bpy.utils.register_class(PlanarDissolve)
	bpy.utils.register_class(LayoutDemoPanel)


def unregister():
	bpy.utils.unregister_class(LayoutDemoPanel)
	bpy.utils.unregister_class(PlanarDissolve)
	bpy.utils.unregister_class(RemoveDoubles)
	bpy.utils.unregister_class(SelectByRegex)

if __name__ == "__main__":
	register()