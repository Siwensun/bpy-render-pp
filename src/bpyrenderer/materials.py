import bpy
from typing import Tuple, Optional


def create_material(
    name: str,
    base_color: Tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0),
    metallic: float = 0.0,
    roughness: float = 0.5,
    use_principled: bool = True
) -> bpy.types.Material:
    """Create a new material with specified properties.
    
    Args:
        name: Name of the material
        base_color: RGBA color tuple
        metallic: Metallic value (0-1)
        roughness: Roughness value (0-1)
        use_principled: Whether to use Principled BSDF (True) or Diffuse BSDF (False)
    
    Returns:
        The created material
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    if use_principled:
        shader = nodes.new('ShaderNodeBsdfPrincipled')
        shader.inputs['Base Color'].default_value = base_color
        shader.inputs['Metallic'].default_value = metallic
        shader.inputs['Roughness'].default_value = roughness
    else:
        shader = nodes.new('ShaderNodeBsdfDiffuse')
        shader.inputs['Color'].default_value = base_color
    
    output = nodes.new('ShaderNodeOutputMaterial')
    mat.node_tree.links.new(shader.outputs[0], output.inputs['Surface'])
    
    return mat

def convert_to_principled_bsdf(
    material: bpy.types.Material,
    base_color: Optional[Tuple[float, float, float, float]] = None,
    metallic: Optional[float] = None,
    roughness: Optional[float] = None
) -> None:
    """Convert any material to use Principled BSDF.
    
    Args:
        material: The material to convert
        base_color: Optional RGBA color to set
        metallic: Optional metallic value to set
        roughness: Optional roughness value to set
    """
    if not material.use_nodes:
        material.use_nodes = True
    
    nodes = material.node_tree.nodes
    old_nodes = [n for n in nodes if n.type != 'OUTPUT_MATERIAL']
    for node in old_nodes:
        nodes.remove(node)
    
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    
    # Keep existing values if not specified
    if base_color is not None:
        principled.inputs['Base Color'].default_value = base_color
    if metallic is not None:
        principled.inputs['Metallic'].default_value = metallic
    if roughness is not None:
        principled.inputs['Roughness'].default_value = roughness
    
    # Find or create output node
    output = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None)
    if not output:
        output = nodes.new('ShaderNodeOutputMaterial')
    
    material.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])

def ensure_pbr_materials(scene: Optional[bpy.types.Scene] = None) -> None:
    """Ensure all materials in the scene use Principled BSDF.
    
    Args:
        scene: Optional scene to process (uses current scene if None)
    """
    if scene is None:
        scene = bpy.context.scene
    
    for material in bpy.data.materials:
        if not material.use_nodes or 'Principled BSDF' not in material.node_tree.nodes:
            convert_to_principled_bsdf(material)