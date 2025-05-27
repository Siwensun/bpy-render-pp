"""Utility functions for creating and managing 3D objects and materials."""

import bpy
from typing import Tuple, Optional, Union, Dict
from .materials import create_material

def add_floor_plane(
    size: float = 10.0,
    location: Tuple[float, float, float] = (0, 0, -1),
    material_props: Optional[Dict] = None
) -> bpy.types.Object:
    """Add a floor plane to the scene with specified material properties.
    
    Args:
        size: Size of the plane
        location: (x, y, z) location
        material_props: Optional dictionary of material properties:
            {
                'base_color': (r, g, b, a),
                'metallic': float,
                'roughness': float,
                'use_principled': bool
            }
    
    Returns:
        The created plane object
    """
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    plane = bpy.context.active_object
    
    # Use default material properties if none provided
    if material_props is None:
        material_props = {
            'base_color': (0.8, 0.8, 0.8, 1.0),
            'metallic': 0.1,
            'roughness': 0.7,
            'use_principled': True
        }
    
    mat = create_material(
        name="Floor_Material",
        **material_props
    )
    plane.data.materials.append(mat)
    
    return plane
