import random
import numpy as np
import bpy
import math
from mathutils import Vector, Euler
from typing import Tuple, Literal, Optional, Union, Dict, List

def add_point_light(location, energy=1000, color=(1, 1, 1), size=0.1):
    """Add a point light to the scene.
    
    Args:
        location (tuple): (x, y, z) coordinates for light position
        energy (float): Light intensity/strength
        color (tuple): RGB color values (0-1)
        size (float): Light size, affects shadow softness
        
    Returns:
        bpy.types.Object: The created light object
    """
    light_data = bpy.data.lights.new(name="point_light", type='POINT')
    light_data.energy = energy
    light_data.color = color
    light_data.shadow_soft_size = size  # Controls shadow softness
    
    light_obj = bpy.data.objects.new(name="Point_Light", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = location
    return light_obj

def add_area_light(
    location: Tuple[float, float, float],
    rotation: Tuple[float, float, float] = (0, 0, 0),
    energy: float = 1000,
    color: Tuple[float, float, float] = (1, 1, 1),
    size: Tuple[float, float] = (1, 1),
    shape: Literal['SQUARE', 'RECTANGLE', 'DISK', 'ELLIPSE'] = 'RECTANGLE'
) -> bpy.types.Object:
    """Add an area light to the scene.
    
    Args:
        location: (x, y, z) coordinates for light position
        rotation: (x, y, z) rotation in radians
        energy: Light intensity/strength
        color: RGB color values (0-1)
        size: (width, height) for the area light
        shape: Shape of the area light
        
    Returns:
        The created light object
    """
    light_data = bpy.data.lights.new(name="area_light", type='AREA')
    light_data.energy = energy
    light_data.color = color
    light_data.shape = shape
    light_data.size = size[0]
    if shape in ['RECTANGLE', 'ELLIPSE']:
        light_data.size_y = size[1]
    
    light_obj = bpy.data.objects.new(name="Area_Light", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location = location
    light_obj.rotation_euler = Euler(rotation)
    return light_obj

def add_sun_light(
    rotation: Tuple[float, float, float],
    energy: float = 1.0,
    color: Tuple[float, float, float] = (1, 1, 1),
    angle: float = 0.526  # Default 30 degrees
) -> bpy.types.Object:
    """Add a sun light to the scene.
    
    Args:
        rotation: (x, y, z) rotation in radians
        energy: Light intensity/strength
        color: RGB color values (0-1)
        angle: Angle of the sun in radians (controls shadow softness)
        
    Returns:
        The created light object
    """
    light_data = bpy.data.lights.new(name="sun_light", type='SUN')
    light_data.energy = energy
    light_data.color = color
    light_data.angle = angle
    
    light_obj = bpy.data.objects.new(name="Sun_Light", object_data=light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.rotation_euler = Euler(rotation)
    return light_obj

def setup_random_lighting(num_lights=3, min_radius=2, max_radius=4, min_energy=500, max_energy=2000):
    """Set up random point lights in the scene.
    
    Args:
        num_lights (int): Number of lights to create
        min_radius (float): Minimum distance from origin
        max_radius (float): Maximum distance from origin
        min_energy (float): Minimum light intensity
        max_energy (float): Maximum light intensity
        
    Returns:
        list: List of created light objects
    """
    lights = []
    for i in range(num_lights):
        # Random position in a sphere
        theta = random.uniform(0, 2 * np.pi)
        phi = random.uniform(0, np.pi)
        r = random.uniform(min_radius, max_radius)
        
        x = r * np.sin(phi) * np.cos(theta)
        y = r * np.sin(phi) * np.sin(theta)
        z = r * np.cos(phi)
        
        energy = random.uniform(min_energy, max_energy)
        light = add_point_light((x, y, z), energy)
        lights.append(light)
    return lights

def setup_studio_lighting(
    key_light_energy: float = 1000,
    fill_light_energy: float = 400,
    back_light_energy: float = 600,
    key_light_color: Tuple[float, float, float] = (1, 1, 1),
    fill_light_color: Tuple[float, float, float] = (0.9, 0.9, 1),
    back_light_color: Tuple[float, float, float] = (1, 1, 0.9)
) -> list:
    """Set up a three-point lighting setup commonly used in studios.
    
    Args:
        key_light_energy: Main light intensity
        fill_light_energy: Fill light intensity
        back_light_energy: Back light intensity
        key_light_color: Main light color
        fill_light_color: Fill light color
        back_light_color: Back light color
        
    Returns:
        List of created light objects
    """
    # Key light (main light)
    key_light = add_area_light(
        location=(4, -4, 4),
        rotation=(math.radians(45), math.radians(0), math.radians(45)),
        energy=key_light_energy,
        color=key_light_color,
        size=(2, 1)
    )
    
    # Fill light (softer, less intense)
    fill_light = add_area_light(
        location=(-4, -4, 2),
        rotation=(math.radians(30), math.radians(0), math.radians(-45)),
        energy=fill_light_energy,
        color=fill_light_color,
        size=(3, 2)
    )
    
    # Back light (rim light)
    back_light = add_area_light(
        location=(0, 4, 3),
        rotation=(math.radians(-45), math.radians(0), math.radians(0)),
        energy=back_light_energy,
        color=back_light_color,
        size=(2, 0.5)
    )
    
    return [key_light, fill_light, back_light]

def blackbody_to_rgb(temperature):
    """Convert color temperature to RGB values.
    
    Args:
        temperature (float): Color temperature in Kelvin
        
    Returns:
        tuple: RGB color values (0-1)
    """
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

def clear_lights():
    """Remove all lights from the scene."""
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj, do_unlink=True)

def generate_random_lighting_setup(lighting_type: Optional[str] = None) -> Tuple[List[bpy.types.Object], Dict]:
    """Generate a random lighting setup and return its metadata.
    
    Args:
        lighting_type: Optional specific lighting type to use. If None, randomly chosen.
                      Valid types: 'studio', 'dramatic', 'natural', 'random', 'env_map'
    
    Returns:
        Tuple[List[bpy.types.Object], Dict]: List of created lights and metadata dictionary
    """
    # Available lighting types and their probabilities
    lighting_types = {
        'studio': 0.25,     # Professional studio lighting
        'dramatic': 0.2,    # Dramatic lighting with strong contrast
        'natural': 0.25,    # Natural lighting with sun and fill
        'random': 0.15,     # Random point lights
        'env_map': 0.15     # Pure environment map lighting
    }
    
    if lighting_type is not None:
        if lighting_type not in lighting_types:
            raise ValueError(f"Invalid lighting type: {lighting_type}. Must be one of {list(lighting_types.keys())}")
    else:
        # Select lighting type based on probabilities
        lighting_type = random.choices(
            list(lighting_types.keys()),
            weights=list(lighting_types.values())
        )[0]
    
    # Random color temperature ranges for different lighting scenarios
    color_temps = {
        'warm': (2700, 3500),    # Warm, tungsten-like lighting
        'neutral': (4000, 5500),  # Natural daylight
        'cool': (6000, 7500)      # Cool, bluish lighting
    }
    
    lights = []
    metadata = {
        "lighting_type": lighting_type,
        "lights": []
    }
    
    if lighting_type == 'env_map':
        # Pure environment lighting - no additional lights
        metadata["env_map"] = {
            "strength": random.uniform(0.8, 1.5)  # Random environment strength
        }
        return lights, metadata
    
    elif lighting_type == 'studio':
        # Generate random studio lighting parameters
        key_energy = random.uniform(800, 1500)
        fill_energy = random.uniform(200, 600)
        back_energy = random.uniform(400, 800)
        
        # Randomize color temperatures
        key_temp = random.uniform(*color_temps['neutral'])
        fill_temp = random.uniform(*color_temps['cool'])  # Slightly cooler fill light
        back_temp = random.uniform(*color_temps['warm'])  # Warmer rim light
        
        lights = setup_studio_lighting(
            key_light_energy=key_energy,
            fill_light_energy=fill_energy,
            back_light_energy=back_energy,
            key_light_color=blackbody_to_rgb(key_temp),
            fill_light_color=blackbody_to_rgb(fill_temp),
            back_light_color=blackbody_to_rgb(back_temp)
        )
        
        metadata["lights"] = [
            {
                "type": "area",
                "role": "key",
                "energy": key_energy,
                "color_temperature": key_temp,
                "position": [4, -4, 4],
                "rotation": [math.radians(45), 0, math.radians(45)],
                "size": [2, 1]
            },
            {
                "type": "area",
                "role": "fill",
                "energy": fill_energy,
                "color_temperature": fill_temp,
                "position": [-4, -4, 2],
                "rotation": [math.radians(30), 0, math.radians(-45)],
                "size": [3, 2]
            },
            {
                "type": "area",
                "role": "back",
                "energy": back_energy,
                "color_temperature": back_temp,
                "position": [0, 4, 3],
                "rotation": [math.radians(-45), 0, 0],
                "size": [2, 0.5]
            }
        ]
    
    elif lighting_type == 'dramatic':
        # Generate dramatic lighting with 1-2 strong lights
        num_lights = random.randint(1, 2)
        for i in range(num_lights):
            # Random position on a sphere
            theta = random.uniform(0, 2 * np.pi)
            phi = random.uniform(0, np.pi / 2)  # Keep lights above horizon
            r = random.uniform(2, 4)
            
            pos = (
                r * np.sin(phi) * np.cos(theta),
                r * np.sin(phi) * np.sin(theta),
                r * np.cos(phi)
            )
            
            # Random rotation pointing at center
            rot = (
                math.atan2(-pos[2], math.sqrt(pos[0]**2 + pos[1]**2)),
                0,
                math.atan2(pos[1], pos[0]) + math.pi
            )
            
            # High energy for dramatic effect
            energy = random.uniform(1000, 2000)
            temp = random.uniform(*color_temps['warm'])
            size = [random.uniform(0.5, 2), random.uniform(0.5, 2)]
            
            light = add_area_light(
                location=pos,
                rotation=rot,
                energy=energy,
                color=blackbody_to_rgb(temp),
                size=size,
                shape='RECTANGLE'
            )
            lights.append(light)
            
            metadata["lights"].append({
                "type": "area",
                "role": f"dramatic_{i+1}",
                "energy": energy,
                "color_temperature": temp,
                "position": list(pos),
                "rotation": list(rot),
                "size": size
            })
    
    elif lighting_type == 'natural':
        # Sun light with fill
        sun_rot = (
            math.radians(random.uniform(-60, -30)),  # Sun elevation
            math.radians(random.uniform(0, 360)),    # Sun rotation
            0
        )
        sun_energy = random.uniform(2, 5)
        sun_angle = math.radians(random.uniform(0.5, 5))  # Sun size
        sun_temp = random.uniform(*color_temps['neutral'])
        
        sun = add_sun_light(
            rotation=sun_rot,
            energy=sun_energy,
            color=blackbody_to_rgb(sun_temp),
            angle=sun_angle
        )
        lights.append(sun)
        
        # Add fill light
        fill_pos = (
            random.uniform(-3, 3),
            random.uniform(-3, 3),
            random.uniform(1, 3)
        )
        fill_energy = random.uniform(200, 400)
        fill_temp = random.uniform(*color_temps['cool'])
        fill_size = [random.uniform(1, 3), random.uniform(1, 3)]
        
        fill = add_area_light(
            location=fill_pos,
            energy=fill_energy,
            color=blackbody_to_rgb(fill_temp),
            size=fill_size
        )
        lights.append(fill)
        
        metadata["lights"] = [
            {
                "type": "sun",
                "role": "main",
                "energy": sun_energy,
                "color_temperature": sun_temp,
                "rotation": list(sun_rot),
                "angle": sun_angle
            },
            {
                "type": "area",
                "role": "fill",
                "energy": fill_energy,
                "color_temperature": fill_temp,
                "position": list(fill_pos),
                "size": fill_size
            }
        ]
    
    else:  # random point lights
        num_lights = random.randint(2, 5)
        min_radius = 2
        max_radius = 4
        min_energy = 300
        max_energy = 800
        
        lights = []
        metadata["lights"] = []
        
        for i in range(num_lights):
            # Random position in a sphere
            theta = random.uniform(0, 2 * np.pi)
            phi = random.uniform(0, np.pi)
            r = random.uniform(min_radius, max_radius)
            
            pos = (
                r * np.sin(phi) * np.cos(theta),
                r * np.sin(phi) * np.sin(theta),
                r * np.cos(phi)
            )
            
            energy = random.uniform(min_energy, max_energy)
            temp = random.uniform(*color_temps['neutral'])  # Store the temperature
            color = blackbody_to_rgb(temp)
            
            light = add_point_light(
                location=pos,
                energy=energy,
                color=color,
                size=0.1
            )
            lights.append(light)
            
            metadata["lights"].append({
                "type": "point",
                "role": f"random_{i+1}",
                "energy": energy,
                "color_temperature": temp,  # Store temperature in metadata
                "color": list(color),       # Store actual color too
                "position": list(pos),
                "size": 0.1
            })
    
    return lights, metadata

def setup_lighting_from_metadata(metadata: Dict) -> List[bpy.types.Object]:
    """Set up lighting based on provided metadata.
    
    Args:
        metadata: Dictionary containing lighting setup information
                 Must include 'lighting_type' and appropriate parameters
    
    Returns:
        List[bpy.types.Object]: List of created light objects
        
    Raises:
        ValueError: If metadata is missing required fields or has invalid values
        KeyError: If required metadata fields are missing
    """
    # Validate lighting_type
    lighting_type = metadata.get('lighting_type')
    if lighting_type is None:
        raise ValueError("Metadata must include 'lighting_type'")
    
    valid_types = ['env_map', 'studio', 'dramatic', 'natural', 'random']
    if lighting_type not in valid_types:
        raise ValueError(f"Invalid lighting_type: {lighting_type}. Must be one of {valid_types}")
    
    lights = []
    
    if lighting_type == 'env_map':
        # Pure environment lighting - no lights to create
        return lights
    
    # For all other types, validate lights array exists
    if 'lights' not in metadata:
        raise KeyError(f"Metadata for {lighting_type} lighting must include 'lights' array")
    
    if lighting_type == 'studio':
        # Create studio lights from metadata
        for light_info in metadata['lights']:
            if 'role' not in light_info:
                raise KeyError("Studio light metadata must include 'role'")
            if light_info['role'] in ['key', 'fill', 'back']:
                light = add_area_light(
                    location=tuple(light_info['position']),
                    rotation=tuple(light_info['rotation']),
                    energy=light_info['energy'],
                    color=blackbody_to_rgb(light_info['color_temperature']),
                    size=tuple(light_info['size'])
                )
                lights.append(light)
    
    elif lighting_type == 'dramatic':
        # Create dramatic lights from metadata
        for light_info in metadata['lights']:
            if 'type' not in light_info:
                raise KeyError("Dramatic light metadata must include 'type'")
            if light_info['type'] == 'area':
                light = add_area_light(
                    location=tuple(light_info['position']),
                    rotation=tuple(light_info['rotation']),
                    energy=light_info['energy'],
                    color=blackbody_to_rgb(light_info['color_temperature']),
                    size=tuple(light_info['size']),
                    shape='RECTANGLE'
                )
                lights.append(light)
    
    elif lighting_type == 'natural':
        # Create natural lighting from metadata
        for light_info in metadata['lights']:
            if 'type' not in light_info:
                raise KeyError("Natural light metadata must include 'type'")
            if light_info['type'] == 'sun':
                light = add_sun_light(
                    rotation=tuple(light_info['rotation']),
                    energy=light_info['energy'],
                    color=blackbody_to_rgb(light_info['color_temperature']),
                    angle=light_info['angle']
                )
                lights.append(light)
            elif light_info['type'] == 'area':
                light = add_area_light(
                    location=tuple(light_info['position']),
                    energy=light_info['energy'],
                    color=blackbody_to_rgb(light_info['color_temperature']),
                    size=tuple(light_info['size'])
                )
                lights.append(light)
    
    else:  # random point lights
        for light_info in metadata['lights']:
            if 'type' not in light_info:
                raise KeyError("Random light metadata must include 'type'")
            if light_info['type'] == 'point':
                # Use stored color directly instead of regenerating from temperature
                light = add_point_light(
                    location=tuple(light_info['position']),
                    energy=light_info['energy'],
                    color=tuple(light_info['color']),  # Use stored color
                    size=light_info['size']
                )
                lights.append(light)
    
    return lights 