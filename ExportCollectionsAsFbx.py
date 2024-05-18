bl_info = {
    "name": "Export Collections as FBX",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
import os


class ExportCollectionsAsFBXOperator(bpy.types.Operator):
    bl_idname = "export_collections.fbx"
    bl_label = "Export Collections as FBX"
    bl_description = "Export all collections as FBX with the name of the collection"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        export_path = bpy.path.abspath("//")

        # Function to add objects to the active view layer
        def add_objects_to_view_layer(collection):
            view_layer = bpy.context.view_layer
            layer_collection = view_layer.layer_collection

            # Ensure the collection is in the view layer
            def recursive_layer_collection(layer_coll, coll_name):
                if layer_coll.name == coll_name:
                    return layer_coll
                for layer in layer_coll.children:
                    found = recursive_layer_collection(layer, coll_name)
                    if found:
                        return found
                return None

            target_layer_coll = recursive_layer_collection(
                layer_collection, collection.name
            )

            if target_layer_coll:
                target_layer_coll.exclude = False
                target_layer_coll.hide_viewport = False
                target_layer_coll.holdout = False
                target_layer_coll.indirect_only = False

        # Function to export collection as FBX
        def export_collection_as_fbx(collection):
            # Deselect all objects
            bpy.ops.object.select_all(action="DESELECT")

            # Add objects to the active view layer
            add_objects_to_view_layer(collection)

            # Select objects in the collection
            for obj in collection.objects:
                if (
                    obj.visible_get() and obj.hide_render is False
                ):  # Check if object is render visible
                    obj.select_set(True)

            # Set the collection as active
            if collection.objects:
                bpy.context.view_layer.objects.active = next(
                    (obj for obj in collection.objects if obj.select_get()), None
                )

            # Define the file path for the FBX export
            fbx_file_path = os.path.join(export_path, collection.name + ".fbx")

            # Export selected objects as FBX
            bpy.ops.export_scene.fbx(
                filepath=fbx_file_path,
                use_selection=True,
                global_scale=1.0,
                apply_unit_scale=True,
                bake_space_transform=False,
                object_types={"MESH", "ARMATURE"},
                use_mesh_modifiers=True,
                use_mesh_modifiers_render=True,
                mesh_smooth_type="OFF",
                use_armature_deform_only=True,
                add_leaf_bones=False,
                primary_bone_axis="Y",
                secondary_bone_axis="X",
                use_metadata=True,
            )

        # Store the initial exclusion state of collections
        initial_exclusion = {
            col.name: (
                bpy.context.view_layer.layer_collection.children[col.name].exclude
                if col.name in bpy.context.view_layer.layer_collection.children
                else None
            )
            for col in bpy.data.collections
        }

        # Loop through all collections and export them as FBX
        for collection in bpy.data.collections:
            if collection.objects:
                # Enable collection in view layer
                layer_collection = bpy.context.view_layer.layer_collection.children.get(
                    collection.name
                )
                if layer_collection:
                    layer_collection.exclude = False
                export_collection_as_fbx(collection)

        # Restore initial exclusion state for collections
        for collection in bpy.data.collections:
            initial_exclusion_state = initial_exclusion.get(collection.name)
            if initial_exclusion_state is not None:
                bpy.context.view_layer.layer_collection.children[
                    collection.name
                ].exclude = initial_exclusion_state

        self.report({"INFO"}, "Export completed.")
        return {"FINISHED"}


def menu_func_export(self, context):
    self.layout.operator(ExportCollectionsAsFBXOperator.bl_idname)


addon_keymaps = []


def register():
    bpy.utils.register_class(ExportCollectionsAsFBXOperator)
    bpy.types.VIEW3D_MT_object.append(menu_func_export)

    # Handle the keymap
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="Object Mode", space_type="EMPTY")
    kmi = km.keymap_items.new(
        ExportCollectionsAsFBXOperator.bl_idname, "E", "PRESS", ctrl=True
    )
    addon_keymaps.append((km, kmi))


def unregister():
    bpy.types.VIEW3D_MT_object.remove(menu_func_export)
    bpy.utils.unregister_class(ExportCollectionsAsFBXOperator)

    # Handle the keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()
