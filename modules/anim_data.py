import bpy
import re
from bpy.types import Panel, Operator, UIList, Menu, PropertyGroup
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, FloatProperty, CollectionProperty, PointerProperty
from bpy.props import FloatVectorProperty

mat_sub_types = (
    ('VECTOR', 'Custom Vector', 'Custom Vector'),
    ('FLOAT', 'Custom Float', 'Custom Float'),
    ('BOOL', 'Custom Bool', 'Custom Bool'),
    ('PATTERN', 'Pattern Index', 'Pattern Index'),
    ('TEXTURE', 'Texture Transform', 'Texture Transform')
)

class SUB_PT_sub_smush_anim_data_master(Panel):
    bl_label = "Ultimate Animation Data"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        return context.object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        arma = obj.data

class SUB_PT_sub_smush_anim_data_vis_tracks(Panel):
    bl_label = "Ultimate Visibility Track Entries"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "SUB_PT_sub_smush_anim_data_master"

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        return context.object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        arma = obj.data
        row = layout.row()
        row.template_list(
            "SUB_UL_vis_track_entries",
            "",
            arma.sub_anim_properties,
            "vis_track_entries",
            arma.sub_anim_properties,
            "active_vis_track_index",
            rows=3,
            maxrows=10,
            )
        col = row.column(align=True)
        col.operator('sub.vis_entry_add', icon='ADD', text="")
        col.operator('sub.vis_entry_remove', icon='REMOVE', text="")
        col.separator()
        col.menu("SUB_MT_vis_entry_context_menu", icon='DOWNARROW_HLT', text="")

class SUB_PT_sub_smush_anim_data_mat_tracks(Panel):
    bl_label = "Ultimate Material Tracks"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "SUB_PT_sub_smush_anim_data_master"

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        return context.object.type == 'ARMATURE'

    def draw(self, context):
        layout = self.layout
        obj = context.object
        arma = obj.data
        col = layout.column()
        row = col.row()
        split = row.split(factor=.4)
        c = split.column()
        c.label(text='Material Names')
        c.template_list(
            "SUB_UL_mat_tracks",
            "",
            arma.sub_anim_properties,
            "mat_tracks",
            arma.sub_anim_properties,
            "active_mat_track_index",
            rows=5,
            maxrows=5,
            )
        split = split.split(factor=.66)
        c = split.column()
        c.label(text='Property Names')
        amti = arma.sub_anim_properties.active_mat_track_index
        if len(arma.sub_anim_properties.mat_tracks) > 0:
            c.template_list(
                "SUB_UL_mat_properties",
                "",
                arma.sub_anim_properties.mat_tracks[amti],
                "properties",
                arma.sub_anim_properties.mat_tracks[amti],
                "active_property_index",
                rows=5,
                maxrows=5,
            )
        else:
            c.enabled = False
        split = split.split()
        c = split.column()
        c.enabled = False
        c.label(text='Property Values')
        if len(arma.sub_anim_properties.mat_tracks) > 0:
            if len(arma.sub_anim_properties.mat_tracks[amti].properties) > 0:
                '''
                After removing the last entry from the list, the 'active' index can remain its previous value
                which is now out of bounds
                '''
                amtpi = arma.sub_anim_properties.mat_tracks[amti].active_property_index
                if amtpi < len(arma.sub_anim_properties.mat_tracks[amti].properties):
                    ap = arma.sub_anim_properties.mat_tracks[amti].properties[amtpi]
                    if ap.sub_type == 'VECTOR':
                        c.prop(ap, "custom_vector", text="", emboss=False)
                    elif ap.sub_type == 'FLOAT':
                        c.prop(ap, "custom_float", text="", emboss=False)
                    elif ap.sub_type == 'BOOL':
                        icon = 'CHECKBOX_HLT' if ap.custom_bool == True else 'CHECKBOX_DEHLT'
                        c.prop(ap, "custom_bool", text="", icon=icon, emboss=False)
                    elif ap.sub_type == 'PATTERN':
                        c.prop(ap, "pattern_index", text="", emboss=False)
                    elif ap.sub_type == 'TEXTURE':
                        c.prop(ap, "texture_transform", text="", emboss=False)
                    c.enabled = True
        # Bottom Row, composed of 3 Sub Rows algined with the above columns
        row = layout.row()
        # Sub Row 1
        split = row.split(factor=.4)
        sr = split.row(align=True)
        sr.operator(SUB_OP_mat_track_add.bl_idname, text='+')
        sr.operator(SUB_OP_mat_track_remove.bl_idname, text='-')
        # Sub Row 2
        split = split.split(factor=.66)
        sr = split.row(align=True)
        sr.operator(SUB_OP_mat_property_add.bl_idname, text='+')
        sr.operator(SUB_OP_mat_property_remove.bl_idname, text='-')
        # Sub 3
        split = split.split()
        sr = split.row(align=True)
        sr.menu('SUB_MT_mat_entry_context_menu', text='Drivers...')      

class SUB_OP_mat_track_add(Operator):
    bl_idname = 'sub.mat_track_add'
    bl_label  = 'Add Mat Track'

    def execute(self, context):
        mat_tracks = context.object.data.sub_anim_properties.mat_tracks
        mat_track = mat_tracks.add()
        mat_track.name = 'NewMaterialTrack'
        sap = context.object.data.sub_anim_properties
        sap.active_mat_track_index = sap.mat_tracks.find(mat_track.name)
        return {'FINISHED'}

class SUB_OP_mat_track_remove(Operator):
    bl_idname = 'sub.mat_track_remove'
    bl_label = 'Remove Mat Track'

    @classmethod
    def poll(cls, context):
        sap = context.object.data.sub_anim_properties
        return len(sap.mat_tracks) > 0

    def execute(self, context):
        sap = context.object.data.sub_anim_properties
        amt = sap.mat_tracks[sap.active_mat_track_index]
        # Find matching Fcurve and Remove
        try:
            fcurves = context.object.data.animation_data.action.fcurves
        except AttributeError:
            sap.mat_tracks.remove(sap.active_mat_track_index)
            i = sap.active_mat_track_index
            sap.active_mat_track_index = min(max(0,i-1),len(sap.mat_tracks))
            return {'FINISHED'}
        # Remove fcurves of all properties of this material track
        for fc in fcurves:
            amti = sap.active_mat_track_index
            if fc.data_path.startswith(f"sub_anim_properties.mat_tracks[{amti}]"):
                fcurves.remove(fc)
        # The remaining materials with an index greater than this one must have all thier fcurves adjusted
        fcurves = context.object.data.animation_data.action.fcurves
        for fc in fcurves:
            regex = r"sub_anim_properties\.mat_tracks\[(\d+)\](\.properties\[\d+\]\.\w+)"
            matches = re.match(regex, fc.data_path)
            if matches is None:
                continue
            if len(matches.groups()) < 2:
                continue
            cmti = int(matches.groups()[0])
            suffix = matches.groups()[1]
            amti = sap.active_mat_track_index
            if cmti < amti:
                continue
            new_data_path = f"sub_anim_properties.mat_tracks[{cmti-1}]{suffix}"
            fc.data_path = new_data_path
        # Now actually remove the material track
        sap.mat_tracks.remove(sap.active_mat_track_index)
        i = sap.active_mat_track_index
        sap.active_mat_track_index = min(max(0,i-1),len(sap.mat_tracks))
        # Refresh Material Drivers
        remove_material_drivers(context.object)
        from .import_anim import setup_material_drivers
        setup_material_drivers(context.object)
        return {'FINISHED'}

class SUB_OP_mat_property_add(Operator):
    bl_idname = 'sub.mat_prop_add'
    bl_label = 'Add Material Property'
    bl_property = "sub_type"

    sub_type: bpy.props.EnumProperty(
        name='Mat Track Entry Subtype',
        description='',
        items=mat_sub_types, 
        default='VECTOR',)

    @classmethod
    def poll(cls, context):
        sap = context.object.data.sub_anim_properties
        return len(sap.mat_tracks) > 0

    def execute(self, context):
        sap = context.object.data.sub_anim_properties
        props = sap.mat_tracks[sap.active_mat_track_index].properties
        prop = props.add()
        prop.sub_type = self.sub_type
        if prop.sub_type == 'VECTOR':
            prop.name = f'CustomVectorX'
        elif prop.sub_type == 'FLOAT':
            prop.name = f'CustomFloatX'
        elif prop.sub_type == 'BOOL':
            prop.name = f'CustomBooleanX'
        else:
            prop.name = f'New{prop.sub_type}Property'
        sap.mat_tracks[sap.active_mat_track_index].active_property_index = props.find(prop.name)
        return {'FINISHED'}
    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

class SUB_OP_mat_property_remove(Operator):
    bl_idname = 'sub.mat_prop_remove'
    bl_label = 'Remove Material Property'

    @classmethod
    def poll(cls, context):
        sap = context.object.data.sub_anim_properties
        if len(sap.mat_tracks) > 0:
            active_track = sap.mat_tracks[sap.active_mat_track_index]
            if len(active_track.properties) > 0:
                return True
        return False

    def execute(self, context):
        sap = context.object.data.sub_anim_properties
        amt = sap.mat_tracks[sap.active_mat_track_index]  
        try:
            fcurves = context.object.data.animation_data.action.fcurves
        except AttributeError:
            amt.properties.remove(amt.active_property_index)
            i = amt.active_property_index
            amt.active_property_index = min(max(0,i-1), len(amt.properties)-1)
            return {'FINISHED'}
        # Remove matching fcurve
        for fc in fcurves:
            amti = sap.active_mat_track_index
            api = sap.mat_tracks[amti].active_property_index
            if fc.data_path.startswith(f"sub_anim_properties.mat_tracks[{amti}].properties[{api}]"):
                fcurves.remove(fc)
        # The material's remaining properties' fcurves with indexes greater to this one must be decremented
        fcurves = context.object.data.animation_data.action.fcurves

        for fc in fcurves:    
            regex = r"sub_anim_properties\.mat_tracks\[(\d+)\]\.properties\[(\d+)\](\.\w+)"
            matches = re.match(regex, fc.data_path)
            if matches is None:
                continue
            if len(matches.groups()) < 3:
                continue
            cmti = int(matches.groups()[0])
            cpi = int(matches.groups()[1])
            suffix = matches.groups()[2]
            amti = sap.active_mat_track_index
            api = sap.mat_tracks[amti].active_property_index
            if cmti != amti or cpi <= api:
                continue
            new_data_path = f"sub_anim_properties.mat_tracks[{cmti}].properties[{cpi-1}]{suffix}"
            fc.data_path = new_data_path 
        # Now actually remove the property
        amt.properties.remove(amt.active_property_index)
        i = amt.active_property_index
        amt.active_property_index = min(max(0,i-1), len(amt.properties)-1)
        # Refresh Material Drivers
        remove_material_drivers(context.object)
        from .import_anim import setup_material_drivers
        setup_material_drivers(context.object)
        return {'FINISHED'}

class SUB_OP_vis_entry_add(Operator):
    bl_idname = 'sub.vis_entry_add'
    bl_label = 'Add Vis Track Entry'

    def execute(self, context):
        entries = context.object.data.sub_anim_properties.vis_track_entries
        entry = entries.add()
        entry.name = 'NewVisTrackEntry'
        entry.value = True
        sap = context.object.data.sub_anim_properties
        sap.active_vis_track_index = entries.find(entry.name)
        return {'FINISHED'} 

class SUB_OP_vis_entry_remove(Operator):
    bl_idname = 'sub.vis_entry_remove'
    bl_label = 'Remove Vis Track Entry'

    @classmethod
    def poll(cls, context):
        sap = context.object.data.sub_anim_properties
        return len(sap.vis_track_entries) > 0

    def execute(self, context):
        sap = context.object.data.sub_anim_properties
        # Find matching Fcurve and Remove
        try:
            fcurves = context.object.data.animation_data.action.fcurves
        except AttributeError:
            sap.vis_track_entries.remove(sap.active_vis_track_index)
            i = sap.active_vis_track_index
            sap.active_vis_track_index = min(max(0,i-1),len(sap.vis_track_entries))
            return {'FINISHED'}
        for fc in fcurves:
            avti = sap.active_vis_track_index
            if fc.data_path.startswith(f"sub_anim_properties.vis_track_entries[{avti}]"):
                fcurves.remove(fc)
        fcurves = context.object.data.animation_data.action.fcurves
        for fc in fcurves:
            regex = r"sub_anim_properties\.vis_track_entries\[(\d+)\]\.value"
            matches = re.match(regex, fc.data_path)
            if matches is None:
                continue
            cvtei = int(matches.groups()[0])
            avtei = sap.active_vis_track_index
            if cvtei < avtei:
                continue
            new_data_path = f'sub_anim_properties.vis_track_entries[{cvtei-1}].value'
            fc.data_path = new_data_path
        sap.vis_track_entries.remove(sap.active_vis_track_index)
        i = sap.active_vis_track_index
        sap.active_vis_track_index = min(max(0, i-1), len(sap.vis_track_entries))

        remove_visibility_drivers(context)
        from .import_anim import setup_visibility_drivers
        setup_visibility_drivers(context.object)        
        return {'FINISHED'} 

class SUB_OP_vis_drivers_refresh(Operator):
    bl_idname = 'sub.vis_drivers_refresh'
    bl_label = 'Refresh Visibility Drivers'

    def execute(self, context):
        from .import_anim import setup_visibility_drivers
        setup_visibility_drivers(context.object)
        return {'FINISHED'} 

class SUB_OP_vis_drivers_remove(Operator):
    bl_idname = 'sub.vis_drivers_remove'
    bl_label = 'Remove Visibility Drivers'

    def execute(self, context):
        remove_visibility_drivers(context)
        return {'FINISHED'}

class SUB_OP_auto_fill_vis_entries(Operator):
    bl_idname = 'sub.auto_fill_vis_entries'
    bl_label = 'Auto Fill Vis Entries'

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        return context.object.type == 'ARMATURE'

    def execute(self, context):
        arma: bpy.types.Object = context.object
        mesh_names = {child.name for child in arma.children if child.type == 'MESH'}
        vis_names: set[str] = set()
        for name in mesh_names:
            regex = r"(.*)\_VIS\_.*"
            match = re.match(regex, name)
            if match:
                vis_names.add(match.groups()[0])
        sap: SubAnimProperties = arma.data.sub_anim_properties
        for vis_name in vis_names:
            if vis_name not in sap.vis_track_entries:
                new_entry: VisTrackEntry = sap.vis_track_entries.add()
                new_entry.name = vis_name
                new_entry.value = True
        return {'FINISHED'}

class SUB_OP_set_all_vis_entries_false(Operator):
    bl_idname = 'sub.set_all_vis_entries_false'
    bl_label = 'Set All Vis Entries False'

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        return context.object.type == 'ARMATURE'
    
    def execute(self, context):
        for vis_entry in context.object.data.sub_anim_properties.vis_track_entries:
            vis_entry.value = False
        return {'FINISHED'}

class SUB_OP_set_all_vis_entries_true(Operator):
    bl_idname = 'sub.set_all_vis_entries_true'
    bl_label = 'Set All Vis Entries True'

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        return context.object.type == 'ARMATURE'
    
    def execute(self, context):
        for vis_entry in context.object.data.sub_anim_properties.vis_track_entries:
            vis_entry.value = True
        return {'FINISHED'}

class SUB_OP_insert_all_vis_entry_keyframes(Operator):
    bl_idname = 'sub.insert_all_vis_entry_keyframes'
    bl_label = 'Insert All Vis Entry Keyframes'

    @classmethod
    def poll(cls, context):
        if not context.object:
            return False
        return context.object.type == 'ARMATURE'
    
    def execute(self, context):
        arma: bpy.types.Object = context.object
        sap: SubAnimProperties = arma.data.sub_anim_properties
        for index, vis_entry in enumerate(sap.vis_track_entries):
            arma.data.keyframe_insert(data_path=f'sub_anim_properties.vis_track_entries[{index}].value', group='Visibility', options={'INSERTKEY_NEEDED'})
        return {'FINISHED'}

def remove_visibility_drivers(context):
    arma = context.object
    mesh_children = [child for child in arma.children if child.type == 'MESH']
    for m in mesh_children:
        if not m.animation_data:
            continue
        drivers = m.animation_data.drivers
        for d in drivers:
            if any(d.data_path == s for s in ['hide_viewport', 'hide_render']):
                drivers.remove(d)

def remove_material_drivers(arma:bpy.types.Object):
    mesh_children = [child for child in arma.children if child.type == 'MESH']
    materials = {material_slot.material for mesh in mesh_children for material_slot in mesh.material_slots}
    for material in materials:
        for node in material.node_tree.nodes:
            for input in node.inputs:
                if hasattr(input, 'default_value'):
                    input.driver_remove('default_value')

class SUB_OP_mat_drivers_refresh(Operator):
    bl_idname = 'sub.mat_drivers_refresh'
    bl_label = 'Refresh Material Drivers'   

    def execute(self, context):
        remove_material_drivers(context.object)
        from .import_anim import setup_material_drivers
        setup_material_drivers(context.object)
        return {'FINISHED'}  

class SUB_OP_mat_drivers_remove(Operator):
    bl_idname = 'sub.mat_drivers_remove'
    bl_label = 'Remove Material Drivers'

    def execute(self, context):
        remove_material_drivers(context.object)
        return {'FINISHED'}  

class SUB_MT_vis_entry_context_menu(Menu):
    bl_label = "Vis Entry Specials"

    def draw(self, context):
        layout = self.layout
        layout.operator('sub.vis_drivers_refresh', icon='FILE_REFRESH', text='Refresh Visibility Drivers')
        layout.operator('sub.vis_drivers_remove', icon='X', text='Remove Visibility Drivers')
        layout.separator()
        layout.operator('sub.auto_fill_vis_entries', icon='SHADERFX', text='Autofill Visibility Entries')
        layout.operator('sub.insert_all_vis_entry_keyframes', icon='KEY_HLT', text='Insert Keyframes for All Entries')
        layout.separator()
        layout.operator('sub.set_all_vis_entries_false', icon='HIDE_ON', text='Set All Entries Off')
        layout.operator('sub.set_all_vis_entries_true', icon='HIDE_OFF', text='Set All Entries On')
        
class SUB_MT_mat_entry_context_menu(Menu):
    bl_label = "Mat Entry Specials"

    def draw(self, context):
        layout = self.layout
        layout.operator(SUB_OP_mat_drivers_refresh.bl_idname, icon='FILE_REFRESH', text='Refresh Material Drivers')
        layout.operator(SUB_OP_mat_drivers_remove.bl_idname, icon='X', text='Remove Material Drivers')

class SUB_UL_vis_track_entries(UIList):
    def draw_item(self, _context, layout, _data, item, icon, active_data, _active_propname, index):
        # assert(isinstance(item, bpy.types.ShapeKey))
        obj = active_data
        # key = data
        entry = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            split = layout.split(factor=0.66, align=False)
            split.prop(entry, "name", text="", emboss=False, icon='HIDE_OFF')
            row = split.row(align=True)
            row.emboss = 'NONE_OR_STATUS'
            row.label(text="")
            icon = 'CHECKBOX_HLT' if entry.value == True else 'CHECKBOX_DEHLT'
            row.prop(entry, "value", text="", icon=icon, emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class SUB_UL_mat_tracks(UIList):
    def draw_item(self, _context, layout, _data, item, icon, active_data, _active_propname, index):
        obj = active_data
        entry = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(entry, "name", text="", emboss=False, icon='MATERIAL')
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class SUB_UL_mat_properties(UIList):
    def draw_item(self, _context, layout, _data, item, icon, active_data, _active_propname, index):
        obj = active_data
        entry = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            row.prop(entry, "name", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)

class SUB_UL_mat_property_values(UIList):
    def draw_item(self, _context, layout, _data, item, icon, active_data, _active_propname, index):
        obj = active_data
        entry = item
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            row = layout.row()
            if entry.sub_type == 'VECTOR':
                row.prop(entry, "custom_vector", text="", emboss=False)
            elif entry.sub_type == 'FLOAT':
                row.prop(entry, "custom_float", text="", emboss=False)
            elif entry.sub_type == 'BOOL':
                row.prop(entry, "custom_bool", text="", emboss=False)
            elif entry.sub_type == 'PATTERN':
                row.prop(entry, "pattern_index", text="", emboss=False)
            elif entry.sub_type == 'TEXTURE':
                row.prop(entry, "texture_transform", text="", emboss=False)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)        




def vis_track_name_update(self, context):
    sap = context.object.data.sub_anim_properties
    dupe = None
    for vt in sap.vis_track_entries:
        if vt.as_pointer() == self.as_pointer():
            continue
        if vt.name == self.name:
            dupe = vt
            break  
    if dupe is None:
        return
    regex = r"(\w+\.)(\d+)"
    matches = re.match(regex, self.name)
    if matches is None:
        self.name = self.name + '.001'
    else:
        base_name = matches.groups()[0]
        number = int(matches.groups()[1])
        self.name = f'{base_name}{number+1:003d}' 



def mat_track_prop_name_update(self, context):
    sap = context.object.data.sub_anim_properties
    found = False
    current_mat_track_index = None
    for mat_track_index, mat_track in enumerate(sap.mat_tracks):
        for property in mat_track.properties:
            if property.as_pointer() == self.as_pointer():
                current_mat_track_index = mat_track_index
                found = True
                break
        if found:
            break
    current_mat_track = sap.mat_tracks[current_mat_track_index]
    # There should be at most only one duplicate
    dupe = None
    for p in current_mat_track.properties:
        if p.as_pointer() == self.as_pointer():
            continue
        if p.name == self.name:
            dupe = p
            break
    # No duplicate found, name can remain as is
    if dupe is None:
        return
    # Regex match the name, see if it already has like '.001'
    # if it doesnt then add the '.001', otherwise increment the number
    regex = r"(\w+\.)(\d+)"
    matches = re.match(regex, self.name)
    if matches is None:
        self.name = self.name + '.001'
    else:
        base_name = matches.groups()[0]
        number = int(matches.groups()[1])
        self.name = f'{base_name}{number+1:003d}'

def mat_track_name_update(self, context):
    sap = context.object.data.sub_anim_properties
    dupe = None
    for mt in sap.mat_tracks:
        if mt.as_pointer() == self.as_pointer():
            continue
        if mt.name == self.name:
            dupe = mt
            break  
    if dupe is None:
        return
    regex = r"(\w+\.)(\d+)"
    matches = re.match(regex, self.name)
    if matches is None:
        self.name = self.name + '.001'
    else:
        base_name = matches.groups()[0]
        number = int(matches.groups()[1])
        self.name = f'{base_name}{number+1:003d}' 

def dummy_update(self, context):
    '''
    This is needed to force blender to update the driver values when updating via a modal.
    '''
    pass

class VisTrackEntry(PropertyGroup):
    name: StringProperty(
        name="Vis Name",
        default="Unknown",
        update=vis_track_name_update,)
    value: BoolProperty(name="Visible", default=False, update=dummy_update)

class MatTrackProperty(PropertyGroup):
    name: StringProperty(
        name="Property Name",
        default="Unknown",
        update=mat_track_prop_name_update,)
    sub_type: EnumProperty(
        name='Mat Track Entry Subtype',
        description='CustomVector or CustomFloat or CustomBool',
        items=mat_sub_types, 
        default='VECTOR',)
    custom_vector: FloatVectorProperty(name='Custom Vector', size=4, update=dummy_update)
    custom_bool: BoolProperty(name='Custom Bool')
    custom_float: FloatProperty(name='Custom Float')
    pattern_index: IntProperty(name='Pattern Index', subtype='UNSIGNED')
    texture_transform: FloatVectorProperty(name='Texture Transform', size=5)

class MatTrack(PropertyGroup):
    name: StringProperty(
        name="Material Name",
        default="Unknown",
        update=mat_track_name_update,)
    properties: CollectionProperty(type=MatTrackProperty)
    active_property_index: IntProperty(name='Active Mat Property Index', default=0)

class SubAnimProperties(PropertyGroup):
    vis_track_entries: CollectionProperty(type=VisTrackEntry)
    active_vis_track_index: IntProperty(name='Active Vis Track Index', default=0)
    mat_tracks: CollectionProperty(type=MatTrack)
    active_mat_track_index: IntProperty(name='Active Mat Track Index', default=0)
