import bpy
import re
from bpy.types import Scene, Object, Armature, PropertyGroup
from bpy.props import IntProperty, StringProperty, EnumProperty, BoolProperty, FloatProperty, CollectionProperty, PointerProperty
from bpy.props import FloatVectorProperty
from .panels import exo_skel, io_matl, import_anim
from . import panels
def register():
    Scene.smash_armature = PointerProperty(
        name='Smash Armature',
        description='Select the Smash armature',
        type=Object,
        poll=exo_skel.poll_armatures,
        #update=?
    )

    Scene.other_armature = PointerProperty(
        name='Other Armature',
        description='Select the Other armature',
        type=Object,
        poll=exo_skel.poll_other_armatures,
        #update=?
    )

    Scene.bone_list = CollectionProperty(
        type=exo_skel.BoneListItem
    )

    Scene.saved_bone_list = CollectionProperty(
        type=exo_skel.BoneListItem
    )

    Scene.bone_list_index = IntProperty(
        name="Index for the exo bone list",
        default=0
    )

    Scene.pairable_bone_list = CollectionProperty(
        type=exo_skel.PairableBoneListItem
    )

    Scene.armature_prefix = StringProperty(
        name="Prefix",
        description="The Prefix that will be added to the bones in the 'Other' armature. Must begin with H_ or else it wont work!",
        default="H_Exo_"
    )

    Scene.ssbh_lib_json_path = StringProperty(
        name='ssbh_lib_json path',
        description='The Path to the ssbh_lib_json.exe file',
        default='',
    )
    

    Scene.numatb_file_path = StringProperty(
        name='.numatb file path',
        description='The Path to the model.numatb file',
        default='',
    )

    Scene.sub_model_numshb_file_name = StringProperty(
        name='.numshb file path',
        description='The Path to the model.numshb file',
        default='',
    )

    Scene.sub_model_nusktb_file_name = StringProperty(
        name='.nusktb file path',
        description='The Path to the model.nusktb file',
        default='',
    )

    Scene.sub_model_numdlb_file_name = StringProperty(
        name='.numdlb file path',
        description='The Path to the model.numdlb file',
        default='',
    )

    Scene.sub_model_numatb_file_name = StringProperty(
        name='.numatb file path',
        description='The Path to the model.numatb file',
        default='',
    )

    Scene.sub_model_nuhlpb_file_name = StringProperty(
        name='.nuhlpb file path',
        description='The Path to the model.nuhlpb file',
        default='',
    )

    Scene.sub_model_folder_path = StringProperty(
        name='Model folder path',
        description='The path to the model folder',
        default='',
    )

    Scene.io_matl_armature = PointerProperty(
        name='Armature',
        description='Select the Armature',
        type=Object,
        poll=exo_skel.poll_armatures,
    )

    Scene.sub_model_export_armature = PointerProperty(
        name='Armature',
        description='Select the Armature',
        type=Object,
        poll=exo_skel.poll_armatures,
    )

    Scene.sub_vanilla_nusktb = StringProperty(
        name='Vanilla .NUSKTB file path',
        description='The path to the vanilla nusktb file',
        default='',
    )

    Scene.sub_merge_same_name_meshes = BoolProperty(
        name='merge_same_name_meshes',
        description='Wether to merge same name meshes',
        default=True,
    )

    Scene.sub_anim_armature = PointerProperty(
        name='Armature',
        description='Select the Armature',
        type=Object,
        poll=exo_skel.poll_armatures,
    )
    
    Scene.sub_anim_camera = PointerProperty(
        name='Camera',
        description='Select the Camera',
        type=Object,
        poll=import_anim.poll_cameras,
    )

    Armature.sub_anim_properties = PointerProperty(
        type=SubAnimProperties
    )
    
    Scene.sub_scene_properties = PointerProperty(
        type=SubSceneProperties
    )

class SubSceneProperties(PropertyGroup):
    mat_reimport_arma: PointerProperty(
        name='Armature',
        description='Select the Armature',
        type=Object,
        poll=exo_skel.poll_armatures,
    )

class VisTrackEntry(PropertyGroup):
    name: StringProperty(name="Vis Name", default="Unknown")
    value: BoolProperty(name="Visible", default=False)
    deleted: BoolProperty(name="Deleted", default=False)

def mat_track_prop_name_update(self, context):
    sap = context.object.data.sub_anim_properties
    found = False
    current_mat_track_index = None
    current_property_index = None
    for mat_track_index, mat_track in enumerate(sap.mat_tracks):
        for property_index, property in enumerate(mat_track.properties):
            if property.as_pointer() == self.as_pointer():
                current_mat_track_index = mat_track_index
                current_property_index = property_index
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

class MatTrackProperty(PropertyGroup):
    name: StringProperty(
        name="Property Name",
        default="Unknown",
        update=mat_track_prop_name_update,)
    sub_type: EnumProperty(
        name='Mat Track Entry Subtype',
        description='CustomVector or CustomFloat or CustomBool',
        items=panels.anim_properties.mat_sub_types, 
        default='VECTOR',)
    deleted: BoolProperty(name="Deleted", default=False)
    custom_vector: FloatVectorProperty(name='Custom Vector', size=4)
    custom_bool: BoolProperty(name='Custom Bool')
    custom_float: FloatProperty(name='Custom Float')
    pattern_index: IntProperty(name='Pattern Index', subtype='UNSIGNED')
    texture_transform: FloatVectorProperty(name='Texture Transform', size=5)

class MatTrack(PropertyGroup):
    name: StringProperty(name="Material Name", default="Unknown")
    properties: CollectionProperty(type=MatTrackProperty)
    deleted: BoolProperty(name="Deleted", default=False)
    active_property_index: IntProperty(name='Active Mat Property Index', default=0)

class SubAnimProperties(PropertyGroup):
    vis_track_entries: CollectionProperty(type=VisTrackEntry)
    active_vis_track_index: IntProperty(name='Active Vis Track Index', default=0)
    mat_tracks: CollectionProperty(type=MatTrack)
    active_mat_track_index: IntProperty(name='Active Mat Track Index', default=0)

