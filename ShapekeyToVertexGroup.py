# Usage: Select a shape key and run the script, it will move the vertices affected by the shapekey into a vertex group
# You can then go into edit mode and select the verticies in the vertex group to view them

import bpy

import numpy as np

# Ensure an active mesh object

obj = bpy.context.object

if obj and obj.type == 'MESH' and obj.data.shape_keys and obj.active_shape_key:

    basis = obj.data.shape_keys.key_blocks[0]  # Basis shape key

    shape_key = obj.active_shape_key  # Selected shape key

    if shape_key == basis:
        print("Please select a shape key other than the Basis.")
    else:
        # Convert shape key data to NumPy arrays (for fast processing)
        basis_coords = np.array([v.co[:] for v in basis.data])
        shape_coords = np.array([v.co[:] for v in shape_key.data])

        # Compute absolute difference between shape key and basis
        displacement = np.linalg.norm(shape_coords - basis_coords, axis=1)

        # Define threshold for real movement (ignore floating-point noise)
        threshold = 1e-4  # 0.0001

        # Get indices of affected vertices (convert to Python list of ints)
        affected_indices = np.where(displacement > threshold)[0].tolist()

        if affected_indices:
            # Create or get the vertex group
            vg_name = "Shape Key Selection"
            if vg_name in obj.vertex_groups:
                vg = obj.vertex_groups[vg_name]
                # **Remove all existing vertices from the group**
                for v in obj.data.vertices:
                    vg.remove([v.index])
            else:
                vg = obj.vertex_groups.new(name=vg_name)

            # Assign affected vertices to the vertex group
            vg.add(affected_indices, 1.0, 'REPLACE')
            print(f"Assigned {len(affected_indices)} vertices to '{vg_name}' vertex group.")
        else:
            print("No affected vertices found.")
else:
    print("No valid shape keys found.")
