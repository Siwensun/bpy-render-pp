import os
import json

from bpyrenderer import SceneManager
from bpyrenderer.camera import add_camera
from bpyrenderer.camera.layout import get_camera_positions_on_sphere
from bpyrenderer.objects import add_floor_plane
from bpyrenderer.materials import ensure_pbr_materials
from bpyrenderer.engine import init_render_engine
from bpyrenderer.environment import set_background_color
from bpyrenderer.importer import load_file
from bpyrenderer.render_output import (
    enable_albedo_output,
    enable_normals_output,
    enable_depth_output,
    enable_pbr_output,
)
from bpyrenderer.utils import convert_normal_to_webp, convert_depth_to_webp

import bpy

def main():
    # Get the absolute path to the workspace
    workspace_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Set up paths
    output_dir = os.path.join(workspace_dir, "outputs/intrinsic_maps")
    model_path = os.path.join(workspace_dir, "assets/models/reflective_cone_collars.glb")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize engine and scene
    init_render_engine("CYCLES", render_samples=128)
    scene_manager = SceneManager()
    scene_manager.clear(reset_keyframes=True)
    
    # Set frame range explicitly
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = 1
    
    # Configure Cycles for better quality
    bpy.context.scene.cycles.denoiser = 'OPTIX'
    bpy.context.scene.cycles.device = 'GPU'
    
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
    
    # Setup camera positions
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

    # Set black background for material maps
    set_background_color([0.0, 0.0, 0.0, 1.0])
    
    # Add all cameras first
    cameras = []
    for i, camera_mat in enumerate(cam_mats):
        camera = add_camera(camera_mat, add_frame=i < len(cam_mats) - 1)
        cameras.append(camera)
    
    # Setup render outputs for material properties
    enable_albedo_output(output_dir)  # Pure diffuse color
    enable_normals_output(output_dir)
    enable_depth_output(output_dir)
    enable_pbr_output(output_dir, "Roughness", file_prefix="roughness_")
    enable_pbr_output(output_dir, "Metallic", file_prefix="metallic_")
    
    # Single render call for all frames
    scene_manager.render()
    
    # Convert normal maps to WEBP format
    for file in os.listdir(output_dir):
        if file.startswith("normal_") and file.endswith(".exr"):
            filepath = os.path.join(output_dir, file)
            render_filepath = filepath.replace("normal_", "render_").replace(
                ".exr", ".webp"
            )
            convert_normal_to_webp(
                filepath,
                filepath.replace(".exr", ".webp"),
                render_filepath,
            )
            os.remove(filepath)
    
    # Convert depth maps to WEBP format
    depth_files = [f for f in os.listdir(output_dir) if f.startswith("depth_") and f.endswith(".exr")]
    if depth_files:
        src_files = [os.path.join(output_dir, f) for f in depth_files]
        dst_files = [f.replace(".exr", ".webp") for f in src_files]
        min_depth, scale = convert_depth_to_webp(src_files, dst_files)
    
    # Save metadata
    meta_info = {
        "width": width,
        "height": height,
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
    
    with open(os.path.join(output_dir, "meta.json"), "w") as f:
        json.dump(meta_info, f, indent=4)
    
    # Save the scene with all objects and cameras
    blend_file = os.path.join(output_dir, "scene.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    
    # Clean up cameras
    for camera in cameras:
        try:
            if camera.name in bpy.data.objects:
                bpy.data.objects.remove(camera, do_unlink=True)
        except ReferenceError:
            continue  # Skip if camera was already removed

if __name__ == "__main__":
    main() 