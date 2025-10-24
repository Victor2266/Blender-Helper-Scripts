# This Script generates a bone chain for hair curves or any curve
# 1. Convert Hair Curve to Mesh
# 2. Select two edges that run from root to tip on opposite sides of mesh
# 3. Duplicate and separate by selection
# 4. Edit new mesh, bridge edge loops and then do a loop cut through the middle
# 5. Invert selection and delete every vertex that is not in the middle
# 6. Convert this "center line" into a curve
# 7. Edit the curve and delete verticies near the root anb throughout to simplify the bone chain
# 8. Select the curve and run this script to generate bone chain
# I target under 5-7 bones per strand and less than 30 strands for long waist length hair.
# Bones near hair roots can be deleted because the hair roots can be weight painted to head bone.

# --- SCRIPT SETTINGS ---
# If your bones point TOWARDS the scalp, change this to True.
# This will reverse the bone direction without affecting your hair's style.
REVERSE_BONE_DIRECTION = False
# -----------------------


# Python Script: Create Bones From Selected Curves (v3 - With Direction Control)
import bpy

def create_armature_from_curve(curve_obj):
    """Creates a single bone chain armature from a single curve object."""
    
    armature_data = bpy.data.armatures.new(name=f"{curve_obj.name}_Armature")
    armature_obj = bpy.data.objects.new(armature_data.name, armature_data)
    bpy.context.collection.objects.link(armature_obj)
    
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    for spline in curve_obj.data.splines:
        points = []
        if spline.type == 'BEZIER':
            points = spline.bezier_points
        elif spline.type in ['POLY', 'NURBS']:
            points = spline.points

        if not points:
            continue

        prev_bone = None
        
        # --- LOGIC FOR BONE DIRECTION ---
        if not REVERSE_BONE_DIRECTION:
            # --- Standard Direction: Scalp to Tip ---
            for i in range(len(points) - 1):
                bone = armature_data.edit_bones.new(name=f"HairBone_{i}")
                
                p1_co = points[i].co
                p2_co = points[i+1].co
                
                bone.head = (curve_obj.matrix_world @ p1_co).xyz
                bone.tail = (curve_obj.matrix_world @ p2_co).xyz
                
                if prev_bone:
                    bone.parent = prev_bone
                prev_bone = bone
        else:
            # --- Reversed Direction: Tip to Scalp ---
            # We iterate backwards along the curve's points
            # This makes "HairBone_0" the bone at the tip
            for i in range(len(points) - 1, 0, -1):
                bone = armature_data.edit_bones.new(name=f"HairBone_{len(points) - 1 - i}")

                p1_co = points[i].co      # Point closer to the tip
                p2_co = points[i-1].co    # Point closer to the scalp

                # Head of the bone is at the tip, tail is towards the scalp
                bone.head = (curve_obj.matrix_world @ p1_co).xyz
                bone.tail = (curve_obj.matrix_world @ p2_co).xyz

                # --- THIS IS THE FIX ---
                # The current bone (closer to scalp) becomes the child of the
                # previous bone (closer to tip), making HairBone_0 the root.
                if prev_bone:
                    bone.parent = prev_bone # <-- Was: prev_bone.parent = bone
                prev_bone = bone

    bpy.ops.object.mode_set(mode='OBJECT')
    return armature_obj

# --- Main part of the script ---
selected_curves = [obj for obj in bpy.context.selected_objects if obj.type == 'CURVE']

if not selected_curves:
    bpy.context.window_manager.popup_menu(
        lambda self, context: self.layout.label(text="No curve objects selected."),
        title="Error", icon='ERROR'
    )
else:
    bpy.ops.object.select_all(action='DESELECT')
    
    all_new_armatures = []
    for curve in selected_curves:
        new_arm = create_armature_from_curve(curve)
        all_new_armatures.append(new_arm)
        print(f"Created armature for {curve.name}")

    for arm in all_new_armatures:
        arm.select_set(True)
    if all_new_armatures:
        bpy.context.view_layer.objects.active = all_new_armatures[0]

print("Script finished. Newly created armatures are selected.")