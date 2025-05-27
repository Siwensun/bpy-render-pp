# bpy-renderer

A go-to library for rendering 3D scenes and animations. Whether you're looking for a simple rendering script for making demos or producing multi-view image dataset for training, bpy-renderer is a modular toolbox that supports both.

Bpy-renderer offers two core components:

* Core package for setting engines, cameras, environments, models, scenes, rendering outputs, and lighting.
* [Example scripts](./examples/) for various functions.

## Features

- **Comprehensive Lighting System**
  - Support for multiple light types (point, area, sun)
  - Studio lighting setups
  - Random lighting generation with metadata
  - Environment map lighting
  - Fine-grained lighting control
- **Material and Environment Control**
  - Material property rendering
  - Environment setup and control
  - Scene normalization
- **Flexible Rendering Options**
  - Multi-view rendering
  - Animation support
  - Intrinsic image decomposition
  - Depth and normal maps

## Demos

**3D Object**

https://github.com/user-attachments/assets/6e5a5767-0323-40aa-95a7-f1ab465976d6

**3D Scene**

https://github.com/user-attachments/assets/d68cf607-3769-487d-9cc7-9c8da311abb6

**3D Animation**

https://github.com/user-attachments/assets/2c7e356c-be30-4d73-bce8-2d9a9965a482

https://github.com/user-attachments/assets/bda030ee-9144-4cb4-bab0-0fb2082180b8

## Installation

We recommend installing bpy-renderer in **Python-3.10**.

```Bash
git clone https://github.com/huanngzh/bpy-renderer.git
pip install -e ./bpy-renderer
```

## Quick Start

Coming soon! For now, please check our example scripts in the [examples](./examples/) directory.

## Example Scripts

| Category | Script | Task |
| - | - | - |
| **Lighting** | [lighting/render_lighting.py](examples/lighting/render_lighting.py) | Basic lighting setup and rendering |
| | [lighting/render_intrinsic_maps.py](examples/lighting/render_intrinsic_maps.py) | Render material properties (albedo, roughness, metallic) |
| **Object** | [object/render_6ortho.py](examples/object/render_6ortho.py) | Render 6 ortho views with rgb, depth, normals |
| | [object/render_360video.py](examples/object/render_360video.py) | Render 360 degree video |
| **Scene** | [scene/render_360video.py](examples/scene/render_360video.py) | Render 360 degree video from a scene |
| | [scene/render_360video_decomp.py](examples/scene/render_360video_decomp.py) | Render 360 degree "semantic-field-like" video from a scene |
| **Animation** | [animation/render_animation_video.py](examples/animation/render_animation_video.py) | Render a single-view video from an animation |
| | [animation/render_animation_union.py](examples/animation/render_animation_union.py) | Render single-view rgb, depth, normal video from an animation |

## Core Modules

The library is organized into several core modules:

- **lighting.py**: Comprehensive lighting system with support for various light types and setups
- **environment.py**: Environment and scene setup utilities
- **materials.py**: Material property handling and rendering
- **objects.py**: Object manipulation and setup
- **render_output.py**: Output configuration and rendering utilities
- **utils.py**: Common utility functions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
