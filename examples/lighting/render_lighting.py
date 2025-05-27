import os
import json
import math

from bpyrenderer import SceneManager
from bpyrenderer.engine import init_render_engine
from bpyrenderer.environment import set_env_map, set_background_color, clear_environment
from bpyrenderer.lighting import (
    generate_random_lighting_setup,
    setup_lighting_from_metadata,
    clear_lights
)
from bpyrenderer.render_output import enable_color_output

import bpy

def disable_all_passes():
    """Disable all render passes except color."""
    # Get the active view layer
    view_layer = bpy.context.view_layer
    
    # Disable all passes
    view_layer.use_pass_z = False
    view_layer.use_pass_normal = False
    view_layer.use_pass_diffuse_color = False
    view_layer.use_pass_glossy_color = False
    view_layer.use_pass_transmission_color = False
    
    # Clear all existing output nodes
    scene = bpy.context.scene
    if scene.use_nodes and scene.node_tree:
        scene.node_tree.nodes.clear()

def main():
    # Get the absolute path to the workspace
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Set up paths
    intrinsic_maps_dir = os.path.join(workspace_dir, "outputs/intrinsic_maps")
    output_dir = os.path.join(workspace_dir, "outputs/lighting_renders")
    env_map_path = os.path.join(workspace_dir, "assets/env_textures/brown_photostudio_02_1k.exr")
    scene_blend_path = os.path.join(intrinsic_maps_dir, "scene.blend")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load metadata for saving with lighting info
    with open(os.path.join(intrinsic_maps_dir, "meta.json"), "r") as f:
        meta_info = json.load(f)
    
    # Load the saved scene with all configurations
    bpy.ops.wm.open_mainfile(filepath=scene_blend_path)
    
    # Disable all passes and clear output nodes
    disable_all_passes()

    # Example 1: Generate random setups for each lighting type
    lighting_types = ['studio', 'dramatic', 'natural', 'random', 'env_map']
    
    for lighting_type in lighting_types:
        setup_dir = os.path.join(output_dir, f"{lighting_type}_example")
        os.makedirs(setup_dir, exist_ok=True)
        
        # Clear existing lights and environment
        clear_lights()
        clear_environment()
        
        # Generate random lighting setup for specific type
        lights, lighting_metadata = generate_random_lighting_setup(lighting_type)
        
        # Set environment lighting based on type
        if lighting_type == 'env_map':
            # Pure environment lighting
            set_env_map(
                env_path=env_map_path,
                rotation=(0, 0, 0),
                strength=lighting_metadata['env_map']['strength']
            )
        elif lighting_type in ['natural', 'studio']:
            # Use environment map with reduced strength for ambient light
            set_env_map(
                env_path=env_map_path,
                rotation=(0, 0, 0),
                strength=0.3
            )
        else:
            # Dark background for dramatic and random setups
            set_background_color([0.1, 0.1, 0.1, 1.0], strength=0.1)
        
        # Setup render output
        enable_color_output(
            bpy.context.scene.render.resolution_x, 
            bpy.context.scene.render.resolution_y, 
            setup_dir,
            mode="PNG",
            film_transparent=False
        )
        
        # Single render call for all frames
        scene_manager = SceneManager()
        scene_manager.render()
        
        # Save lighting metadata
        lighting_meta = {
            "width": bpy.context.scene.render.resolution_x,
            "height": bpy.context.scene.render.resolution_y,
            "lighting_setup": lighting_metadata,
            "base_meta": meta_info
        }
        
        with open(os.path.join(setup_dir, "lighting_meta.json"), "w") as f:
            json.dump(lighting_meta, f, indent=4)
        
        # Clean up lights
        clear_lights()
    
    # Example 2: Load and use existing metadata
    metadata_path = os.path.join(output_dir, "studio_example/lighting_meta.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            saved_meta = json.load(f)
        
        setup_dir = os.path.join(output_dir, "metadata_recreation")
        os.makedirs(setup_dir, exist_ok=True)
        
        # Clear existing lights and environment
        clear_lights()
        clear_environment()
        
        # Recreate lighting from saved metadata
        lights = setup_lighting_from_metadata(saved_meta["lighting_setup"])
        
        # Set appropriate environment lighting
        if saved_meta["lighting_setup"]["lighting_type"] == "env_map":
            set_env_map(
                env_path=env_map_path,
                rotation=(0, 0, 0),
                strength=saved_meta["lighting_setup"]["env_map"]["strength"]
            )
        elif saved_meta["lighting_setup"]["lighting_type"] in ["natural", "studio"]:
            set_env_map(
                env_path=env_map_path,
                rotation=(0, 0, 0),
                strength=0.3
            )
        else:
            set_background_color([0.1, 0.1, 0.1, 1.0], strength=0.1)
        
        # Setup render output
        enable_color_output(
            bpy.context.scene.render.resolution_x, 
            bpy.context.scene.render.resolution_y, 
            setup_dir,
            mode="PNG",
            film_transparent=False
        )
        
        # Single render call for all frames
        scene_manager = SceneManager()
        scene_manager.render()
        
        # Save lighting metadata
        with open(os.path.join(setup_dir, "lighting_meta.json"), "w") as f:
            json.dump(saved_meta, f, indent=4)

if __name__ == "__main__":
    main() 