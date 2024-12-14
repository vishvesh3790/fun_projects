import bpy
import bmesh
import math
import random
from mathutils import Vector, Matrix

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

def create_bird():
    # Create the bird's body (UV sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(0, 0, 0))
    bird = bpy.context.active_object
    bird.name = 'Bird'
    
    # Add materials to bird
    bird_material = bpy.data.materials.new(name="BirdMaterial")
    bird_material.use_nodes = True
    nodes = bird_material.node_tree.nodes
    nodes["Principled BSDF"].inputs[0].default_value = (1.0, 1.0, 0.0, 1)  # Yellow color
    bird.data.materials.append(bird_material)
    
    # Add wings (flattened spheres)
    for side in [-1, 1]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(side * 0.3, 0, 0))
        wing = bpy.context.active_object
        wing.scale = (0.2, 0.4, 0.1)
        wing.rotation_euler = (0, math.radians(30), 0)
        wing.parent = bird
        wing.data.materials.append(bird_material)
    
    return bird

def create_pipe(location, height=4):
    # Create pipe body
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=height, location=location)
    pipe = bpy.context.active_object
    pipe.name = 'Pipe'
    
    # Add pipe material
    pipe_material = bpy.data.materials.new(name="PipeMaterial")
    pipe_material.use_nodes = True
    nodes = pipe_material.node_tree.nodes
    nodes["Principled BSDF"].inputs[0].default_value = (0.0, 0.8, 0.0, 1)  # Green color
    pipe.data.materials.append(pipe_material)
    
    # Add pipe cap
    bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=0.2, 
                                      location=(location[0], location[1], location[2] + height/2))
    cap = bpy.context.active_object
    cap.parent = pipe
    cap.data.materials.append(pipe_material)
    
    return pipe

def create_environment():
    # Create ground plane
    bpy.ops.mesh.primitive_plane_add(size=100, location=(0, 0, -5))
    ground = bpy.context.active_object
    ground.name = 'Ground'
    
    # Add ground material
    ground_material = bpy.data.materials.new(name="GroundMaterial")
    ground_material.use_nodes = True
    nodes = ground_material.node_tree.nodes
    nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.8, 0.2, 1)  # Grass green
    ground.data.materials.append(ground_material)
    
    # Create sky (large sphere)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=50, location=(0, 0, 0))
    sky = bpy.context.active_object
    sky.name = 'Sky'
    sky.scale = (1, 1, 0.5)  # Flatten the sky sphere
    
    # Add sky material
    sky_material = bpy.data.materials.new(name="SkyMaterial")
    sky_material.use_nodes = True
    nodes = sky_material.node_tree.nodes
    nodes["Principled BSDF"].inputs[0].default_value = (0.5, 0.7, 1.0, 1)  # Sky blue
    sky.data.materials.append(sky_material)
    
    # Flip normals of sky sphere to see it from inside
    bpy.context.view_layer.objects.active = sky
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.flip_normals()
    bpy.ops.object.mode_set(mode='OBJECT')

def create_pipe_pair(z_pos):
    gap_size = 3  # Space between pipes
    pipe_height = 6
    y_pos = random.uniform(-2, 2)  # Random height variation
    
    # Create bottom pipe
    bottom_pipe = create_pipe((0, z_pos, y_pos - gap_size/2 - pipe_height/2), pipe_height)
    
    # Create top pipe (inverted)
    top_pipe = create_pipe((0, z_pos, y_pos + gap_size/2 + pipe_height/2), pipe_height)
    top_pipe.rotation_euler = (math.radians(180), 0, 0)
    
    return bottom_pipe, top_pipe

def setup_camera():
    # Create and position camera
    bpy.ops.object.camera_add(location=(5, 0, 0))
    camera = bpy.context.active_object
    camera.name = 'GameCamera'
    camera.rotation_euler = (math.radians(90), 0, math.radians(90))
    
    # Make this the active camera
    bpy.context.scene.camera = camera
    
    # Add track to constraint to follow bird
    bird = bpy.data.objects['Bird']
    constraint = camera.constraints.new(type='TRACK_TO')
    constraint.target = bird
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'

def setup_lighting():
    # Create sun light
    bpy.ops.object.light_add(type='SUN', location=(10, 0, 10))
    sun = bpy.context.active_object
    sun.data.energy = 5
    
    # Create ambient light
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
    ambient = bpy.context.active_object
    ambient.data.energy = 3
    ambient.scale = (10, 10, 10)

def setup_game():
    # Create all game elements
    bird = create_bird()
    create_environment()
    
    # Create initial set of pipes
    for z_pos in range(5, 26, 5):  # Create 5 pairs of pipes
        create_pipe_pair(z_pos)
    
    setup_camera()
    setup_lighting()
    
    # Set render engine to Cycles for better quality
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.samples = 128  # Adjust samples for better performance
    
    # Set world background color
    world = bpy.context.scene.world
    if not world:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes["Background"]
    bg_node.inputs[0].default_value = (0.5, 0.7, 1.0, 1)  # Sky blue

# Run the setup
setup_game()

# Save the .blend file
bpy.ops.wm.save_as_mainfile(filepath="/home/vishveshs/project_trial_llm0/trial_proj/flappy_bird_3d.blend")
