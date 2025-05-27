import os
import random
import json
import numpy as np
from mathutils import Vector, Euler

from bpyrenderer import SceneManager
from bpyrenderer.camera import add_camera
from bpyrenderer.camera.layout import get_camera_positions_on_sphere
from bpyrenderer.objects import add_floor_plane
from bpyrenderer.materials import ensure_pbr_materials
from bpyrenderer.engine import init_render_engine
from bpyrenderer.environment import set_env_map, set_background_color
from bpyrenderer.importer import load_file
from bpyrenderer.render_output import (
    enable_color_output,
    enable_depth_output,
    enable_albedo_output,
    enable_normals_output,
)
from bpyrenderer.utils import convert_normal_to_webp

import bpy


def add_point_light(location, energy=1000, color=(1, 1, 1), size=0.1):
    """Add a point light to the scene."""
    light_data = bpy.data.lights.new(name="point_light", type='POINT')
    light_data.energy = energy
    light_data.color = color
    light_data.shadow_soft_size = size  # Controls shadow softness
    
    light_obj = bpy.data.objects.new(name="Point_Light", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = location
    return light_obj

def setup_random_lighting(num_lights=3):
    """Set up random point lights in the scene."""
    lights = []
    for i in range(num_lights):
        # Random position in a sphere
        theta = random.uniform(0, 2 * np.pi)
        phi = random.uniform(0, np.pi)
        r = random.uniform(2, 4)
        
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        # Random color temperature (warm to cool)
        temp = random.uniform(2700, 6500)
        color = blackbody_to_rgb(temp)
        
        energy = random.uniform(500, 2000)
        light = add_point_light((x, y, z), energy, color)
        lights.append(light)
    return lights

def blackbody_to_rgb(temperature):
    """Approximate RGB color from color temperature."""
    # Simple approximation
    if temperature <= 4000:
        r = 1.0
        g = 0.7 + 0.3 * (temperature - 2700) / 1300
        b = 0.4 + 0.6 * (temperature - 2700) / 1300
    else:
        r = 1.0
        g = 1.0
        b = 0.8 + 0.2 * (temperature - 4000) / 2500
    return (r, g, b)

def main():
    # Get the absolute path to the workspace
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Set up paths
    output_dir = os.path.join(workspace_dir, "outputs/advanced_render")
    model_path = os.path.join(workspace_dir, "assets/models/reflective_cone_collars.glb")
    env_map_path = os.path.join(workspace_dir, "assets/env_textures/brown_photostudio_02_1k.exr")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Available environment maps
    env_maps = [env_map_path]
    
    # Initialize engine and scene
    init_render_engine("CYCLES", render_samples=128)  # Use Cycles for better shadows
    scene_manager = SceneManager()
    scene_manager.clear(reset_keyframes=True)
    
    # Set frame range explicitly
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 1
    
    # Configure Cycles for better quality
    bpy.context.scene.cycles.denoiser = 'OPTIX'  # GPU denoising
    bpy.context.scene.cycles.device = 'GPU'
    # bpy.context.scene.cycles.adaptive_threshold = 0.01
    # bpy.context.scene.cycles.caustics_reflective = True
    
    # Import model and prepare materials
    load_file(model_path)
    scene_manager.smooth()
    scene_manager.clear_normal_map()
    scene_manager.set_material_transparency(False)
    scene_manager.set_materials_opaque()  # Important for normal maps
    scene_manager.normalize_scene(1.0)

    # Ensure all materials use Principled BSDF
    ensure_pbr_materials()
    
    # Get the scene bounding box to place floor right below objects
    bbox_min, bbox_max = scene_manager.get_scene_bbox()
    floor_z = bbox_min.z - 0.01  # Place slightly below the lowest point
    
    # Add floor plane with custom material properties
    floor = add_floor_plane(
        size=10.0,
        location=(0, 0, floor_z),
        material_props={
            'base_color': (0.8, 0.8, 0.8, 1.0),
            'metallic': 0.1,
            'roughness': 0.7,
            'use_principled': True
        }
    )
    
    # Setup random camera positions
    cam_pos, cam_mats, elevations, azimuths = get_camera_positions_on_sphere(
        center=(0, 0, 0),
        radius=2.0,
        elevations=[15, 45],
        num_camera_per_layer=2
    )
    
    # Render settings
    width, height = 1024, 1024
    bpy.context.scene.render.resolution_x = width
    bpy.context.scene.render.resolution_y = height

    # Iterate through different lighting setups
    # lighting_setups = ['env_map', 'single_point', 'multi_point']
    lighting_setups = ['env_map']
    
    for setup in lighting_setups:
        setup_dir = os.path.join(output_dir, setup)
        os.makedirs(setup_dir, exist_ok=True)
        
        # Clear existing lights
        for obj in bpy.data.objects:
            if obj.type == 'LIGHT':
                bpy.data.objects.remove(obj, do_unlink=True)
        
        # Setup lighting
        if setup == 'env_map':
            env_map = random.choice(env_maps)
            set_env_map(env_map)
        else:
            set_background_color([0.0, 0.0, 0.0, 1.0])
            if setup == 'single_point':
                add_point_light((2, 2, 3), 1500)
            else:  # multi_point
                setup_random_lighting(3)
        
        # Add all cameras first
        cameras = []
        for i, camera_mat in enumerate(cam_mats):
            camera = add_camera(camera_mat, add_frame=i < len(cam_mats) - 1)
            cameras.append(camera)
        
        # Setup render outputs
        enable_color_output(width, height, setup_dir, mode="PNG", film_transparent=False)
        enable_depth_output(setup_dir)
        enable_normals_output(setup_dir)
        enable_albedo_output(setup_dir)  # Pure diffuse color
        
        # Single render call for all frames
        scene_manager.render()
        
        # Convert normal maps to WEBP format
        for file in os.listdir(setup_dir):
            if file.startswith("normal_") and file.endswith(".exr"):
                filepath = os.path.join(setup_dir, file)
                render_filepath = filepath.replace("normal_", "render_").replace(
                    ".exr", ".webp"
                )
                convert_normal_to_webp(
                    filepath,
                    filepath.replace(".exr", ".webp"),
                    render_filepath,
                )
                os.remove(filepath)
        
        # Save metadata
        meta_info = {
            "width": width,
            "height": height,
            "lighting_setup": setup,
            "cameras": []
        }
        for i, (camera, pos) in enumerate(zip(cameras, cam_pos)):
            meta_info["cameras"].append({
                "index": f"{i:04d}",
                "position": list(pos),
                "elevation": elevations[i],
                "azimuth": azimuths[i],
                "transform_matrix": [list(row) for row in cam_mats[i]]
            })
        
        with open(os.path.join(setup_dir, "meta.json"), "w") as f:
            json.dump(meta_info, f, indent=4)
        
        # Clean up cameras
        for camera in cameras:
            try:
                if camera.name in bpy.data.objects:
                    bpy.data.objects.remove(camera, do_unlink=True)
            except ReferenceError:
                continue  # Skip if camera was already removed

if __name__ == "__main__":
    main() 