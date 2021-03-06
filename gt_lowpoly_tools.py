bl_info = {
	"name": "GT Lowpoly Tools",
	"author": "Glynn Taylor",
	"version": (0, 1, 3),
	"blender": (2, 7, 8),
	"api": 35853,
	"location": "View > Tools > GT Tools",
	"description": "A collection of tools for low poly",
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
import os

#-------------------------------------------
# PANEL


class LayoutDemoPanel(bpy.types.Panel):
	"""Creates a Panel in the scene context of the properties editor"""
	bl_label = "GT Lowpoly tools"
	bl_idname = "SCENE_GT_lowpoly"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "GT"
	#bl_order = -1

	#PROPERTIES
	bpy.types.Scene.scn_targetVCLayer= bpy.props.StringProperty( attr="targetLayer1", name="Target VC Layer", description="Target VC Layer", default="Col" )
	bpy.types.Scene.scn_inputVCLayer1= bpy.props.StringProperty( attr="inputLayer1", name="Input VC Layer", description="Input VC Layer", default="Col" )
	bpy.types.Scene.scn_inputVCLayer2= bpy.props.StringProperty( attr="inputLayer2", name="Input VC Layer", description="Input VC Layer", default="Col" )
	bpy.types.Scene.scn_character_export_path = bpy.props.StringProperty (
		name="Output Path",
		default="",
		description="Define the path where to export or import from",
		subtype='DIR_PATH'
	)
	bpy.types.Scene.scn_noiseDeviance = bpy.props.FloatProperty(name = "Noise Deviance",default=0.2)
	bpy.types.Scene.scn_saturationAmount = bpy.props.FloatProperty(name = "Saturation",default=0.05)
	bpy.types.Scene.scn_lightnessAmount = bpy.props.FloatProperty(name = "Lightness",default=0.05)
	bpy.types.Scene.scn_snap = bpy.props.FloatProperty(name = "Snap",default=0.5)
	
	
	
	def draw(self, context):
		layout = self.layout
		scene = context.scene
		
		box = layout.box()
		box.label(text="Multi Layer Operations")
		row0 = box.row()
		row0.scale_y = 1.0
		row0.prop( scene, "scn_inputVCLayer1", text="InLayer1" )
		row0.prop( scene, "scn_inputVCLayer2", text="InLayer2" )
		row0.prop( scene, "scn_targetVCLayer", text="OutLayer" )
		box.operator("gt.combine_ao")
		
		layout.row().separator()
		#layout.seperator()
		
		box = layout.box()
		box.label(text="Selected Vertex Operations")
		box.operator("gt.set_vertex_color")
		box.operator("gt.multiply_by_color")
		box.operator("gt.set_greyscale")
		
		box.label(text="Advanced")
		row1 = box.row()
		row1.scale_y = 1.0
		row1.prop( scene, "scn_noiseDeviance", text="Deviance" )
		row1.operator("gt.color_noise")
		
		row2 = box.row()
		row2.scale_y = 1.0
		row2.prop( scene, "scn_saturationAmount", text="Amount" )
		row2.operator("gt.saturate")
		row2.operator("gt.desaturate")
		
		row3 = box.row()
		row3.scale_y = 1.0
		row3.prop( scene, "scn_lightnessAmount", text="Amount" )
		row3.operator("gt.multiply_ao")
		
		layout.row().separator()
		#layout.seperator()
		
		box = layout.box()
		box.label(text="Character Export")
		
		row4 = box.row(align=True)
		if context.scene.scn_character_export_path == "":
			row4.alert = True
		row4.prop(scene, "scn_character_export_path", text="Export path")
		if context.scene.scn_character_export_path != "":
			row4 = row4.row(align=True)
			row4.operator("gt.open_folder", text="", icon='FILE_FOLDER')
		#box.prop( scene, "scn_snap", text="Snap" )
		box.operator("gt.export_character")
		box.operator("gt.export_charactermerged")
#-------------------------------------------
# GENERAL FUNCTIONS

def CheckVertexColorLayer(layerName, mesh):
	if not layerName in mesh.vertex_colors:
		mesh.vertex_colors.new(layerName)

#-------------------------------------------
# OPERATORS

def RunExportCharacterMerged(self, context):
	#-----------------------------------------Save
	if bpy.data.is_dirty:
		bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
		
	objs = [obj for obj in bpy.data.objects if obj.type == 'MESH']
	#-----------------------------------------Apply modifiers
	for obj in objs:
		bpy.context.scene.objects.active = obj
		for modifier in obj.modifiers:
			if modifier.type != "ARMATURE":
				bpy.ops.object.modifier_apply(modifier=modifier.name)
	#-----------------------------------------Merge All
	for obj in objs:
		obj.select = True
	for obj in objs:
		if obj.name == "Body":
			bpy.context.scene.objects.active = obj
	bpy.ops.object.join()
	#-----------------------------------------Export
	path_folder = os.path.dirname( bpy.path.abspath( context.scene.scn_character_export_path))
	
	path_fullname = os.path.basename(bpy.data.filepath) # won't work on linux
	path_name, extension = os.path.splitext(path_fullname)
	print("Target Folder: "+path_folder)
	print("Target Name: "+path_name)
	path_full = os.path.join(path_folder, path_name)+".fbx"
	print("Full Path: "+path_full)
	try:
		bpy.ops.export_scene.fbx(
			filepath		=path_full, 
			
			axis_forward	='-Z', 
			axis_up			='Y', 
			object_types={'EMPTY', 'ARMATURE', 'MESH', 'OTHER'},
			
			use_mesh_modifiers=False,
			add_leaf_bones=False,
			bake_anim=False,
			
			apply_scale_options='FBX_SCALE_ALL',
			global_scale =1.00, 
			apply_unit_scale=True,
		
			path_mode='AUTO',
			embed_textures=True, 
			mesh_smooth_type='FACE',
			batch_mode='OFF',
			
			use_custom_props=False,
 			bake_space_transform = True
			)
	except (TypeError, ValueError):
		bpy.ops.export_scene.fbx('INVOKE_DEFAULT')
	#-----------------------------------------Undo
	bpy.ops.wm.open_mainfile(filepath=bpy.data.filepath)

def RunExportCharacter( context):
	#for obj in bpy.data.objects:
	#	if obj.type == 'MESH' : 
	#		bpy.ops.object.modifier_apply(apply_as='DATA', modifier='Mirror')
	#bpy.ops.ed.undo_push()
	path_folder = os.path.dirname( bpy.path.abspath( context.scene.scn_character_export_path))
	#path_name, extension = os.path.splitext(bpy.data.filepath)
	path_fullname = os.path.basename(bpy.data.filepath) # won't work on linux
	path_name, extension = os.path.splitext(path_fullname)
	print("Target Folder: "+path_folder)
	print("Target Name: "+path_name)
	path_full = os.path.join(path_folder, path_name)+".fbx"
	print("Full Path: "+path_full)
	try:
		bpy.ops.export_scene.fbx(
			filepath		=path_full, 
			
			axis_forward	='-Z', 
			axis_up			='Y', 
			object_types={'EMPTY', 'ARMATURE', 'MESH', 'OTHER'},
			
			use_mesh_modifiers=True,
			add_leaf_bones=False,
			bake_anim=False,
			
			apply_scale_options='FBX_SCALE_ALL',
			global_scale =1.00, 
			apply_unit_scale=True,
			
			path_mode='AUTO',
			embed_textures=True, 
			mesh_smooth_type='FACE',
			batch_mode='OFF',
			
			use_custom_props=False,

 			bake_space_transform = True
			)
	except (TypeError, ValueError):
		bpy.ops.export_scene.fbx('INVOKE_DEFAULT')
	#bpy.ops.ed.undo()
#---------------
# Snap
#
def RunSnap(context):

	for nr, obj in enumerate(bpy.context.selected_objects):
		obj.location.x = round(obj.location.x / context.scene.scn_snap) * context.scene.scn_snap
		obj.location.y = round(obj.location.y / context.scene.scn_snap) * context.scene.scn_snap

def RunArrangeToGrid(context):
	offset_y = 1
	offset_z = 1
	row_length = 5

	for nr, obj in enumerate(bpy.context.selected_objects):
		row = nr % row_length
		col = nr // row_length
		obj.location = (col * offset_z+0.5, row * offset_y+0.5, 0)		
#---------------
# Multi Layer
#
def RunCombineAO(context):
	obj = bpy.context.active_object
	mesh = obj.data
	
	# Set mode
	oldMode = bpy.context.object.mode
	if (bpy.context.mode != 'OBJECT'):
		bpy.ops.object.mode_set(mode='OBJECT')
	
	# Check layers exist
	CheckVertexColorLayer(context.scene.scn_inputVCLayer1, mesh)
	CheckVertexColorLayer(context.scene.scn_inputVCLayer2, mesh)
	CheckVertexColorLayer(context.scene.scn_targetVCLayer, mesh)
	
	# Get layers
	inputLayer1 = mesh.vertex_colors[context.scene.scn_inputVCLayer1]
	inputLayer2 = mesh.vertex_colors[context.scene.scn_inputVCLayer2]
	targetLayer = mesh.vertex_colors[context.scene.scn_targetVCLayer]
	color = Color()

	# Perform operation
	i = 0
	for poly in mesh.polygons:
		for loop in poly.loop_indices:
			color.r = inputLayer1.data[i].color.r* inputLayer2.data[i].color.r
			color.g = inputLayer1.data[i].color.g* inputLayer2.data[i].color.g
			color.b = inputLayer1.data[i].color.b* inputLayer2.data[i].color.b
			targetLayer.data[loop].color = color
			i += 1
	
	# Update mesh and revert to old mode
	mesh.update()
	bpy.ops.object.mode_set(mode=oldMode)
	print("Finished CombineAOOperator")
	
#---------------
# Vertex based
#
def RunSetVertexColor(context):
	obj = bpy.context.active_object
	mesh = obj.data
	
	# Set mode
	oldMode = bpy.context.object.mode
	if (bpy.context.mode != 'OBJECT'):
		bpy.ops.object.mode_set(mode='OBJECT')

	# Get Selected layer and color
	col_layer = mesh.vertex_colors.active
	color = bpy.data.brushes["Draw"].color

	# Perform operation
	i = 0
	for poly in mesh.polygons:
		for loop in poly.loop_indices:
			if(mesh.vertices[mesh.loops[loop].vertex_index].select):
				col_layer.data[loop].color = color
			i += 1
	
	# Update mesh and revert to old mode
	mesh.update()
	bpy.ops.object.mode_set(mode=oldMode)
	print("Finished Color Noise")
	
def RunMultiplyByColor(context):
	obj = bpy.context.active_object
	mesh = obj.data

	# Set mode
	oldMode = bpy.context.object.mode
	if (bpy.context.mode != 'OBJECT'):
		bpy.ops.object.mode_set(mode='OBJECT')
	
	# Get selected layer and color
	col_layer = mesh.vertex_colors.active
	color = bpy.data.brushes["Draw"].color

	# Perform operation
	i = 0
	for poly in mesh.polygons:
		for loop in poly.loop_indices:
			if(mesh.vertices[mesh.loops[loop].vertex_index].select):
				clr = col_layer.data[loop].color
				col_layer.data[loop].color = (color.r*clr.r,color.g*clr.g,color.b*clr.b)
			i += 1
			
	# Update mesh and revert to old mode
	mesh.update()
	bpy.ops.object.mode_set(mode=oldMode)
	print("Finished Color Multiply")
	
def RunSetGreyscale(context):
	obj = bpy.context.active_object
	mesh = obj.data

	# Set mode
	oldMode = bpy.context.object.mode
	if (bpy.context.mode != 'OBJECT'):
		bpy.ops.object.mode_set(mode='OBJECT')
	
	# Get selected layer and color
	col_layer = mesh.vertex_colors.active
	color = bpy.data.brushes["Draw"].color

	# Perform operation
	i = 0
	for poly in mesh.polygons:
		for loop in poly.loop_indices:
			if(mesh.vertices[mesh.loops[loop].vertex_index].select):
				clr = col_layer.data[loop].color
				greyscale = clr.r + clr.g + clr.b
				greyscale = greyscale / 3
				col_layer.data[loop].color = (greyscale,greyscale,greyscale)
			i += 1
			
	# Update mesh and revert to old mode
	mesh.update()
	bpy.ops.object.mode_set(mode=oldMode)
	print("Finished Setting Greyscale")
	
def RunSaturate(context, multiplier):
	obj = bpy.context.active_object
	mesh = obj.data
	
	# Set mode
	oldMode = bpy.context.object.mode
	if (bpy.context.mode != 'VERTEX_PAINT'):
		bpy.ops.object.mode_set(mode='VERTEX_PAINT')

	col_layer = mesh.vertex_colors.active

	# Perform operation
	i = 0
	for poly in mesh.polygons:
		for loop in poly.loop_indices:
			if(mesh.vertices[mesh.loops[loop].vertex_index].select):
				clr = col_layer.data[loop].color
				h, s, v = colorsys.rgb_to_hsv(clr.r, clr.g, clr.b)
				s = s + (context.scene.scn_saturationAmount* multiplier)
				r,g,b = colorsys.hsv_to_rgb(h, s, v)
				clr.r = r
				clr.g = g
				clr.b = b
				col_layer.data[loop].color = (clr.r,clr.g,clr.b)
			i += 1
			
	# Update mesh and revert to old mode
	mesh.update()
	bpy.ops.object.mode_set(mode=oldMode)
	print("Finished Saturation")

def RunColorNoise(context):
	obj = bpy.context.active_object
	mesh = obj.data

	# Set mode
	oldMode = bpy.context.object.mode
	if (bpy.context.mode != 'OBJECT'):
		bpy.ops.object.mode_set(mode='OBJECT')
	
	col_layer = mesh.vertex_colors.active
	color = Color()
	
	# Perform operation
	i = 0
	for poly in mesh.polygons:
		for loop in poly.loop_indices:
			if(mesh.vertices[mesh.loops[loop].vertex_index].select):
				color = col_layer.data[loop].color
				h, s, v = colorsys.rgb_to_hsv(color.r, color.g, color.b)
				h += random.uniform(-context.scene.scn_noiseDeviance,context.scene.scn_noiseDeviance)
				s += random.uniform(-context.scene.scn_noiseDeviance,context.scene.scn_noiseDeviance)
				v += random.uniform(-context.scene.scn_noiseDeviance,context.scene.scn_noiseDeviance)
				r,g,b = colorsys.hsv_to_rgb(h, s, v)
				color.r = r
				color.g = g
				color.b = b
				col_layer.data[loop].color = color
			i += 1
	
	# Update mesh and revert to old mode
	mesh.update()
	bpy.ops.object.mode_set(mode=oldMode)
	print("Finished Color Noise")
	
def RunMultiplyAO(context):
	obj = bpy.context.active_object
	mesh = obj.data
	
	# Set mode
	oldMode = bpy.context.object.mode
	if (bpy.context.mode != 'VERTEX_PAINT'):
		bpy.ops.object.mode_set(mode='VERTEX_PAINT')

	col_layer = mesh.vertex_colors.active

	# Perform operation
	i = 0
	for poly in mesh.polygons:
		for loop in poly.loop_indices:
			if(mesh.vertices[mesh.loops[loop].vertex_index].select):
				clr = col_layer.data[loop].color
				h, s, v = colorsys.rgb_to_hsv(clr.r, clr.g, clr.b)
				v = v + (context.scene.scn_lightnessAmount)
				r,g,b = colorsys.hsv_to_rgb(h, s, v)
				clr.r = r
				clr.g = g
				clr.b = b
				col_layer.data[loop].color = (clr.r,clr.g,clr.b)
			i += 1
			
	# Update mesh and revert to old mode
	mesh.update()
	bpy.ops.object.mode_set(mode=oldMode)
	print("Finished Value")
	
def RunOpenFolder(self, path):
	path = os.path.dirname( bpy.path.abspath( path ))
	# Warnings
	if not os.path.exists(path):
		self.report({'ERROR_INVALID_INPUT'}, "Path doesn't exist." )
		return

	# Open Folder
	os.startfile(path)
	print("Open path on system "+path)
	
	
class ExportCharacterMerged(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.export_charactermerged"
	bl_label = "Export Character Merged"
	# bl_options = {'REGISTER', 'UNDO'}
	# Can either use the blender auto undo (above) or manually add point using bpy.ops.ed.undo_push()
	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunExportCharacterMerged(self,context)
		return {'FINISHED'}
	
class OpenFolder(bpy.types.Operator):
	bl_idname = "gt.open_folder"
	bl_label = "Open Folder"
	bl_description = "Open the specified folder"

	@classmethod
	def poll(cls, context):
		if context.scene.scn_character_export_path == "":
			return False

		return True

	def execute(self, context):
		RunOpenFolder(self, context.scene.scn_character_export_path)
		
		return {'FINISHED'}



class ExportCharacter(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.export_character"
	bl_label = "Export Character"
	# bl_options = {'REGISTER', 'UNDO'}
	# Can either use the blender auto undo (above) or manually add point using bpy.ops.ed.undo_push()
	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunExportCharacter(context)
		return {'FINISHED'}
	
	
	
class ArrangeSelectedOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.selected_arrange_to_grid"
	bl_label = "Arrange Selected To Grid"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunArrangeToGrid(context)
		return {'FINISHED'}

	
class SnapOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.selected_snap"
	bl_label = "Snap Selected"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunSnap(context)
		return {'FINISHED'}

	
class CombineAOOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.combine_ao"
	bl_label = "Multiply Layers"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunCombineAO(context)
		return {'FINISHED'}

class MultiplyAOOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.multiply_ao"
	bl_label = "Adjust Lightness of Selected"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunMultiplyAO(context)
		return {'FINISHED'}

class SetVertexColorOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.set_vertex_color"
	bl_label = "Selected to Selected Color"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunSetVertexColor(context)
		return {'FINISHED'}
		
class SetGreyscaleOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.set_greyscale"
	bl_label = "Selected to Greyscale"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunSetGreyscale(context)
		return {'FINISHED'}
		
class MultiplyByColorOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.multiply_by_color"
	bl_label = "Multiply Selected By Current Color"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunMultiplyByColor(context)
		return {'FINISHED'}

class DesaturateOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.desaturate"
	bl_label = "Desaturate"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunSaturate(context, -1)
		return {'FINISHED'}

class SaturateOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.saturate"
	bl_label = "Saturate"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunSaturate(context, 1)
		return {'FINISHED'}
		
class ColorNoiseOperator(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "gt.color_noise"
	bl_label = "Selected: Add Noise"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		RunColorNoise(context)
		return {'FINISHED'} 		

def register():
	bpy.utils.register_class(ExportCharacterMerged)
	bpy.utils.register_class(OpenFolder)
	bpy.utils.register_class(ExportCharacter)
	bpy.utils.register_class(ArrangeSelectedOperator)
	bpy.utils.register_class(SnapOperator)
	bpy.utils.register_class(CombineAOOperator)
	bpy.utils.register_class(MultiplyAOOperator)
	bpy.utils.register_class(ColorNoiseOperator)
	bpy.utils.register_class(SetVertexColorOperator)
	bpy.utils.register_class(SetGreyscaleOperator)
	bpy.utils.register_class(MultiplyByColorOperator)
	bpy.utils.register_class(SaturateOperator)
	bpy.utils.register_class(DesaturateOperator)
	bpy.utils.register_class(LayoutDemoPanel)


def unregister():
	bpy.utils.unregister_class(LayoutDemoPanel)
	bpy.utils.unregister_class(DesaturateOperator)
	bpy.utils.unregister_class(SaturateOperator)
	bpy.utils.unregister_class(MultiplyByColorOperator)
	bpy.utils.unregister_class(SetGreyscaleOperator)
	bpy.utils.unregister_class(SetVertexColorOperator)
	bpy.utils.unregister_class(ColorNoiseOperator)
	bpy.utils.unregister_class(MultiplyAOOperator)
	bpy.utils.unregister_class(CombineAOOperator)
	bpy.utils.unregister_class(SnapOperator)
	bpy.utils.unregister_class(ArrangeSelectedOperator)
	bpy.utils.unregister_class(ExportCharacter)
	bpy.utils.unregister_class(OpenFolder)
	bpy.utils.unregister_class(ExportCharacterMerged)

if __name__ == "__main__":
	register()