import os
import math
import bpy
from mathutils import Vector, Euler
from typing import List, Tuple, Optional


def set_env_map(
    env_path: str,
    rotation: Tuple[float, float, float] = (0, 0, 0),
    strength: float = 1.0
):
    """Set environment map with rotation and strength control.
    
    Args:
        env_path: Path to the environment map image
        rotation: (x, y, z) rotation in radians
        strength: Strength of environment lighting
        background_alpha: Alpha value for background (0-1)
    """
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"Environment map not found: {env_path}")

    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    world.node_tree.nodes.clear()

    # Create and setup nodes
    tex_coord = world.node_tree.nodes.new(type="ShaderNodeTexCoord")
    mapping = world.node_tree.nodes.new(type="ShaderNodeMapping")
    mapping.inputs["Rotation"].default_value = rotation
    
    env_texture = world.node_tree.nodes.new(type="ShaderNodeTexEnvironment")
    background = world.node_tree.nodes.new(type="ShaderNodeBackground")
    background.inputs["Strength"].default_value = strength
    
    output = world.node_tree.nodes.new(type="ShaderNodeOutputWorld")

    # Link nodes
    links = world.node_tree.links
    links.new(tex_coord.outputs["Generated"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], env_texture.inputs["Vector"])
    links.new(env_texture.outputs["Color"], background.inputs["Color"])
    links.new(background.outputs["Background"], output.inputs["Surface"])

    # Load environment texture
    bpy.ops.image.open(filepath=env_path)
    env_texture.image = bpy.data.images.get(os.path.basename(env_path))


def set_background_color(rgba: List = [1.0, 1.0, 1.0, 1.0], strength: float = 1.0):
    """Set background color with strength control.
    
    Args:
        rgba: RGBA color values (0-1)
        strength: Light emission strength
    """
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    world.use_nodes = True
    world.node_tree.nodes.clear()

    # Create nodes
    background = world.node_tree.nodes.new(type="ShaderNodeBackground")
    background.inputs["Color"].default_value = rgba
    background.inputs["Strength"].default_value = strength
    
    output = world.node_tree.nodes.new(type="ShaderNodeOutputWorld")
    
    # Link nodes
    world.node_tree.links.new(background.outputs["Background"], output.inputs["Surface"])


def clear_environment():
    """Clear all environment lighting.
    
    This function:
    1. Removes any existing environment texture
    2. Creates a new empty world node tree
    3. Sets up a black background with zero strength (no light contribution)
    """
    # Ensure world exists
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    
    # Reset to empty node tree
    world.use_nodes = True
    world.node_tree.nodes.clear()
    
    # Add background node with black color (no light)
    background = world.node_tree.nodes.new('ShaderNodeBackground')
    background.inputs['Color'].default_value = (0, 0, 0, 1)
    background.inputs['Strength'].default_value = 0
    
    output = world.node_tree.nodes.new('ShaderNodeOutputWorld')
    world.node_tree.links.new(background.outputs['Background'], output.inputs['Surface'])

