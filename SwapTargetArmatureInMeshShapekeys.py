import bpy
# This script batch changes the prop field in the drivers for an mesh's shape keys
# Used for when I need to copy and paste a mesh from an older version of the file that has a bunch of drivers

# --- Configuration ---
# The name of the incorrect ARMATURE DATA that is currently linked in the driver.
# This is NOT an object name. It's the name you see in the green triangle data properties.
incorrect_armature_data_name = "Genesis 8.1 Female.002"

# The name of the correct ARMATURE OBJECT in the scene.
# This is the object you click on in the Outliner.
# The script will check that it exists and that it's armature exists
correct_target_object_name = "Genesis 8.1 Female"

# These are the strings in the data_path string that the script will swap
string_to_find_in_path = incorrect_armature_data_name
string_to_replace_in_path = "Genesis 8.1 Female.001"
# --- End of Configuration ---


# Get the currently selected object in the viewport
active_obj = bpy.context.active_object

# Find the armature object in the scene
target_armature_obj = bpy.data.objects.get(correct_target_object_name)

# Counter for tracking how many modifications were made
mods_made_count = 0

# --- Verification Checks ---
if not active_obj:
    print("Error: Please select a mesh object first.")
elif not target_armature_obj:
    print(f"Error: Cannot find the target armature object named '{correct_target_object_name}'.")
elif target_armature_obj.type != 'ARMATURE':
    print(f"Error: The target object '{correct_target_object_name}' is not an Armature.")
elif not (active_obj.type == 'MESH' and active_obj.data and active_obj.data.shape_keys):
    print("Error: The selected object is not a mesh or has no shape keys.")
elif not active_obj.data.shape_keys.animation_data:
    print("No drivers found on the shape keys of the selected object.")
else:
    print(f"Processing shape key drivers for: '{active_obj.name}'...")
    print(f"Will retarget drivers to Armature Data: '{target_armature_obj.data.name}'")
    
    # Get the animation data from the shape keys
    shape_keys_anim_data = active_obj.data.shape_keys.animation_data

    # Iterate through all fcurves that are drivers
    for fcurve in shape_keys_anim_data.drivers:
        driver = fcurve.driver
        
        # A driver can have multiple variables, so loop through them
        for var in driver.variables:
            
            # A variable can have multiple targets, loop through them (usually just one)
            for target in var.targets:
                
                # --- Task 1: Check and correct the target ID (the data-block) ---
                # Check if the target.id exists and is an Armature data-block
                # THIS IS THE FIX: Use isinstance() to correctly check the data-block type.
                if target.id and isinstance(target.id, bpy.types.Armature):
                    
                    # Now, check if this armature data has the incorrect name
                    if target.id.name == incorrect_armature_data_name:
                        print(f"- Correcting target ID: FROM '{target.id.name}' TO '{target_armature_obj.data.name}'")
                        
                        # Assign the correct armature data-block
                        target.id = target_armature_obj.data
                        mods_made_count += 1

                # --- Task 2: Check and correct the data_path string ---
                # This often needs to be fixed as well.
                if string_to_find_in_path in target.data_path:
                    old_path = target.data_path
                    # Perform the replacement
                    target.data_path = target.data_path.replace(string_to_find_in_path, string_to_replace_in_path)
                    print(f"- Updated data_path: FROM '{old_path}' TO '{target.data_path}'")
                    mods_made_count += 1


    if mods_made_count > 0:
        print(f"\nFinished. A total of {mods_made_count} modifications were made.")
    else:
        print("\nFinished. No drivers needed modification.")