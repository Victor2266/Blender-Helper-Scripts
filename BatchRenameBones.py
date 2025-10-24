# Python Script: Batch Rename Bones
# This script goes through each armature and appends the bone name after the armature name
# This gets rid of duplicate bone names in the armatures so you can join them after weight painting without issue
# Used for weight painting hair strands separately then joining them together

# Select all armature objects you want to process and run.

import bpy

# Get all selected objects
selected_objects = bpy.context.selected_objects

for obj in selected_objects:
    # Make sure the object is an armature and is the active one
    if obj.type == 'ARMATURE':
        bpy.context.view_layer.objects.active = obj
        
        # Switch to Edit Mode to rename bones
        bpy.ops.object.mode_set(mode='EDIT')
        
        armature = obj.data
        
        # Loop through every bone in the armature
        for bone in armature.edit_bones:
            # Construct the new name: ObjectName.BoneName
            new_name = f"{obj.name}.{bone.name}"
            
            print(f"Renaming '{bone.name}' to '{new_name}'")
            
            # Apply the new name
            bone.name = new_name
            
        # Switch back to Object Mode
        bpy.ops.object.mode_set(mode='OBJECT')

print("Batch renaming complete.")