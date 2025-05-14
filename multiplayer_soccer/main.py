from FastGame.game_objects import Cuboid, Camera, Plane, Sphere, Cylinder, DirectionalLight, PointLight, SpotLight, SkyBox, GameObject, VisibleGameObject, FootballGoal, Text
from FastGame.components import Script, RigidBody, BoxCollider
from FastGame.scene import Scene
from FastGame.core import Game
from FastGame.shader import Shader
from FastGame.input_manager import InputManager, InputAxis
from FastGame.utils import Color 
from pyglm.glm import vec3, quat
import numpy as np
import time

player1_vertical = InputAxis(['d'], ['a'])
player1_horizontal = InputAxis(['w'], ['s'])
player2_vertical = InputAxis(['left'], ['right'])
player2_horizontal = InputAxis(['down'], ['up'])

class RoadColorController(Script):
    def generate_color_gradient(self, start_color: Color, end_color: Color, steps: int):
        gradient = []    
        start_rgb = np.array(start_color.color_in_rgb, dtype=np.float32)
        end_rgb   = np.array(end_color.color_in_rgb,   dtype=np.float32)
        
        for t in np.linspace(0, 1, steps):
            rgb = (1 - t) * start_rgb + t * end_rgb
            gradient.append(Color(color_in_rgb=rgb))
        
        return gradient
    
    
    def start(self):
        tmp = self.generate_color_gradient(Color('#FFB347'), Color('#FF6961'), 40)
        tmp += self.generate_color_gradient(Color('#FF6961'), Color('#6A5ACD'), 40)
        tmp += self.generate_color_gradient(Color('#6A5ACD'), Color('#00CED1'), 40)
        tmp += self.generate_color_gradient(Color('#00CED1'), Color('#7FFF00'), 40)
        tmp += self.generate_color_gradient(Color('#7FFF00'), Color('#FFD700'), 40)
        
        self.colors = []
        for color in tmp:
            self.colors.append(color)
        tmp.reverse()
        for color in tmp:
            self.colors.append(color)
            
        self.current_color = 0
        self.time_passed = 0
        
    def update(self):
        self.time_passed += self.delta_time
        # print(self.time_passed)
        if self.time_passed >= 0.05:
            if self.current_color >= len(self.colors):
                self.current_color = 0
            # print(self.game_object.name)
            self.game_object.material.color = self.colors[self.current_color]
            self.current_color += 1
            self.time_passed = 0



class PlayerController(Script):
    def __init__(self, horizontal_axis, vertical_axis, speed=4000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizontal_axis = horizontal_axis
        self.vertical_axis = vertical_axis
        self.speed = speed
        self.rigidbody = None
        self.brake_factor = 0.8
        
        
    def start(self):
        self.rigidbody = self.game_object.components.get('rigidbody')
        
    def update(self):
        h = self.input_axes.get(self.horizontal_axis)
        v = self.input_axes.get(self.vertical_axis)
        
        
        if self.rigidbody and h is not None and v is not None:
            move = np.array([
                h.value * self.speed,
                0,
                v.value * self.speed
            ], dtype=np.float32)
            if np.linalg.norm(move) > 0.01:
                self.rigidbody.apply_force(move)
            else:
                self.rigidbody.velocity *= self.brake_factor
            pos = self.game_object.transform.get_position()
            
            self.game_object.transform.set_position(vec3(pos.x, 1, pos.z))

player1 = None
player2 = None
ball = None
player1_score_count = 0
player2_score_count = 0
WIN_SCORE = 10

shared_player1 = Cuboid('player1')
shared_player1.components.add('rigidbody', RigidBody(friction=0.1, bounciness=0.1, linear_damping=0.001, gravity=np.array([0,0,0]), mass=25))
shared_player1.components.add('collider', BoxCollider(size=[2,2,2]))
shared_player1.transform.set_scale(vec3(3,1,3))
shared_player1.transform.set_position(vec3(-30, 1, 0))
shared_player1.material.color = Color('#FF4B2B')
shared_player1.components.add('controller', PlayerController('player1_horizontal', 'player1_vertical'))

shared_player2 = Cuboid('player2')
shared_player2.components.add('rigidbody', RigidBody(friction=0.1, bounciness=0.1, linear_damping=0.001, gravity=np.array([0,0,0]), mass=25))
shared_player2.components.add('collider', BoxCollider(size=[2,2,2]))
shared_player2.transform.set_scale(vec3(3,1,3))
shared_player2.transform.set_position(vec3(30, 1, 0))
shared_player2.material.color = Color('#1E90FF')
shared_player2.components.add('controller', PlayerController('player2_horizontal', 'player2_vertical'))

shared_ball = Cuboid('ball')
shared_ball.components.add('rigidbody', RigidBody(friction=0, bounciness=0.99, linear_damping=0.001, gravity=np.array([0,0,0])))
shared_ball.components.add('collider', BoxCollider(size=[2,2,2]))
shared_ball.transform.translate(vec3(0, 1, 0))
shared_ball.material.alpha = 1
shared_ball.material.ambient_light = 0.25
shared_ball.material.diffuse_reflection = 0.8
shared_ball.material.specular_reflection = 1.0
shared_ball.material.shininess = 64
shared_ball.material.color = Color('#FFD700')

def create_scene(win_score_callback, player1, player2, ball, camera=None):
    shader = Shader('shaders/default.vert', 'shaders/default.frag')
    depth_shader = Shader('shaders/simple_depth_shader.vert', 'shaders/simple_depth_shader.frag')
    
    
    scene = Scene('scene', shader, depth_shader)
    wall_height = 1
    wall_thickness = 0.5
    road_y = 0
    road_width = 40
    road_depth = 20
    goal_gap = 8
    road = Plane('road')
    road.components.add('collider', BoxCollider(size=[2, 1, 2]))
    road.transform.translate(vec3(0, -1, 0))
    road.transform.set_scale(vec3(40,1,20))
    road.transform.rotate_euler(vec3(0, 0, 0))
    # road.texture.load_texture('wood.jpeg')
    road.components.add('road_color_controller', RoadColorController())
    road.material.ambient_light = 0.22
    road.material.diffuse_reflection = 0.8
    road.material.specular_reflection = 0.8
    road.material.shininess = 60
    scene.objects.add(road)
    
    
    dir_light = DirectionalLight('light2')
    dir_light.transform.rotate_euler(vec3(-90, 0, 0))
    dir_light.transform.translate(vec3(0,0,100))
    dir_light.light_source.color = Color('#FFFACD')
    scene.objects.add(dir_light)
    
    
    num_spots = 4
    road_length = 60
    for i in range(num_spots):
        x = -30 + i * (road_length / (num_spots - 1))
        spot = SpotLight(f'road_spot_{i}')
        spot.transform.set_position(vec3(x, 12, 0))
        spot.transform.rotate_euler(vec3(-90, 0, 0))
        spot.light_source.color = Color('#FFFACD')
        spot.light_source.quadratic = 0.01
        spot.light_source.linear = 0.01
        spot.light_source.constant = 0.7
        spot.light_source.cutoff = 30
        spot.light_source.outer_cutoff = 60
        scene.objects.add(spot)
    
    
    skybox = SkyBox('skybox')
    skybox.texture.load_texture([
        'skybox_textures/right.jpg',
        'skybox_textures/left.jpg',
        'skybox_textures/top.jpg',
        'skybox_textures/bottom.jpg',
        'skybox_textures/front.jpg',
        'skybox_textures/back.jpg',
    ])
    scene.objects.add(skybox)
    
    
    left_wall_top = Cuboid('left_wall_top')
    left_wall_top.transform.set_scale(vec3(wall_thickness, wall_height, (road_depth - goal_gap) / 2))
    left_wall_top.transform.set_position(vec3(-road_width, road_y + wall_height/2, (road_depth + goal_gap) / 2))
    left_wall_top.material.color = Color('#8B5CF6')
    left_wall_top.components.add('collider', BoxCollider(size=[2,2,2]))
    scene.objects.add(left_wall_top)
    
    
    left_wall_bottom = Cuboid('left_wall_bottom')
    left_wall_bottom.transform.set_scale(vec3(wall_thickness, wall_height, (road_depth - goal_gap) / 2))
    left_wall_bottom.transform.set_position(vec3(-road_width, road_y + wall_height/2, -(road_depth + goal_gap) / 2))
    left_wall_bottom.material.color = Color('#8B5CF6')
    left_wall_bottom.components.add('collider', BoxCollider(size=[2,2,2]))
    scene.objects.add(left_wall_bottom)
    
    
    right_wall_top = Cuboid('right_wall_top')
    right_wall_top.transform.set_scale(vec3(wall_thickness, wall_height, (road_depth - goal_gap) / 2))
    right_wall_top.transform.set_position(vec3(road_width, road_y + wall_height/2, (road_depth + goal_gap) / 2))
    right_wall_top.material.color = Color('#8B5CF6')
    right_wall_top.components.add('collider', BoxCollider(size=[2,2,2]))
    scene.objects.add(right_wall_top)
    
    
    right_wall_bottom = Cuboid('right_wall_bottom')
    right_wall_bottom.transform.set_scale(vec3(wall_thickness, wall_height, (road_depth - goal_gap) / 2))
    right_wall_bottom.transform.set_position(vec3(road_width, road_y + wall_height/2, -(road_depth + goal_gap) / 2))
    right_wall_bottom.material.color = Color('#8B5CF6')
    right_wall_bottom.components.add('collider', BoxCollider(size=[2,2,2]))
    scene.objects.add(right_wall_bottom)
    
    
    top_wall = Cuboid('top_wall')
    top_wall.transform.set_scale(vec3(road_width, wall_height, wall_thickness))
    top_wall.transform.set_position(vec3(0, road_y + wall_height/2, road_depth))
    top_wall.material.color = Color('#F59E42')
    top_wall.components.add('collider', BoxCollider(size=[2,2,2]))
    scene.objects.add(top_wall)
    
    
    bottom_wall = Cuboid('bottom_wall')
    bottom_wall.transform.set_scale(vec3(road_width, wall_height, wall_thickness))
    bottom_wall.transform.set_position(vec3(0, road_y + wall_height/2, -road_depth))
    bottom_wall.material.color = Color('#F59E42')
    bottom_wall.components.add('collider', BoxCollider(size=[2,2,2]))
    scene.objects.add(bottom_wall)
    
    scene.objects.add(player1)
    scene.objects.add(player2)
    scene.objects.add(ball)
    
    goal1 = FootballGoal('goal1')
    goal1.transform.set_scale(vec3(0.03, 0.04, 0.04))
    goal1.transform.set_position(vec3(40, 0, 7))
    goal1.transform.rotate_euler(vec3(0, 90, 0))
    goal1.material.ambient_light = 0.22
    goal1.material.diffuse_reflection = 0.7
    goal1.material.specular_reflection = 0.9
    goal1.material.shininess = 80
    goal1.material.color = Color('#00CFFF')
    scene.objects.add(goal1)
    
    goal2 = FootballGoal('goal2')
    goal2.transform.set_scale(vec3(0.03, 0.04, 0.04))
    goal2.transform.set_position(vec3(-40, 0, -7))
    goal2.transform.rotate_euler(vec3(0, -90, 0))
    goal2.material.ambient_light = 0.22
    goal2.material.diffuse_reflection = 0.7
    goal2.material.specular_reflection = 0.9
    goal2.material.shininess = 80
    goal2.material.color = Color('#FF4B2B')
    scene.objects.add(goal2)
    
    
    def reset_positions():
        player1.transform.set_position(vec3(-30, 1, 0))
        player1.components.get('rigidbody').velocity[:] = 0
        player2.transform.set_position(vec3(30, 1, 0))
        player2.components.get('rigidbody').velocity[:] = 0
        ball.transform.set_position(vec3(0, 1, 0))
        ball.components.get('rigidbody').velocity[:] = 0
    
    player1_score_count = {'count': 0}
    player2_score_count = {'count': 0}
    
    WIN_SCORE = 10
    
    def player1_score(self, other):
        if hasattr(other, 'game_object') and getattr(other.game_object, 'name', None) == 'ball':
            player1_score_count['count'] += 1
            print(f'Player 1 scores! Score: {player1_score_count["count"]}')
            reset_positions()
            if player1_score_count['count'] >= WIN_SCORE:
                print('Player 1 wins!')
                win_score_callback(1)
    
    def player2_score(self, other):
        if hasattr(other, 'game_object') and getattr(other.game_object, 'name', None) == 'ball':
            player2_score_count['count'] += 1
            print(f'Player 2 scores! Score: {player2_score_count["count"]}')
            reset_positions()
            if player2_score_count['count'] >= WIN_SCORE:
                print('Player 2 wins!')
                win_score_callback(2)
    
    
    goal1_trigger = GameObject('goal1_trigger')
    goal1_trigger.transform.set_position(vec3(42, 1, 0))
    goal1_trigger.transform.set_scale(vec3(1,1,10))
    goal1_trigger.components.add('collider', BoxCollider(size=[2,2,2], is_trigger=True, on_trigger=player2_score))
    scene.objects.add(goal1_trigger)
    
    goal2_trigger = GameObject('goal2_trigger')
    goal2_trigger.transform.set_position(vec3(-42, 1, 0))
    goal2_trigger.transform.set_scale(vec3(1,1,10))
    goal2_trigger.components.add('collider', BoxCollider(size=[2,2,2], is_trigger=True, on_trigger=player1_score))
    scene.objects.add(goal2_trigger)
    
    
    if camera is not None:
        scene.objects.add(camera)
    else:
        camera = Camera('camera')
        camera.transform.translate(vec3(0, 50, 35))
        camera.lens.FOV = 60
        camera.lens.perspective = True
        camera.transform.look_at(ball.transform.get_global_position(), vec3(0,1,0))
        scene.objects.add(camera)
    return {'scene': scene, 'player1': player1, 'player2': player2, 'ball': ball, 'camera': camera}

def win_score_callback(winner):
    print(f'Player {winner} wins!')
    import sys; sys.exit(0)

class Camera1Controller(Script):
    def start(self):
        self.player = shared_player1
    def update(self):
        self.game_object.transform.look_at(self.player.transform.get_global_position(), vec3(0,1,0))
        self.game_object.transform.rotate_euler(vec3(10, 0, 0))

class Camera2Controller(Script):
    def start(self):
        self.player = shared_player2
    def update(self):
        self.game_object.transform.look_at(self.player.transform.get_global_position(), vec3(0,1,0))
        self.game_object.transform.rotate_euler(vec3(10, 0, 0))

camera1 = Camera('camera')
camera1.transform.translate(vec3(-50, 20, 0))
camera1.lens.FOV = 60
camera1.lens.perspective = True
camera1.components.add('cam_controller', Camera1Controller())

camera2 = Camera('camera')
camera2.transform.translate(vec3(50, 20, 0))
camera2.lens.FOV = 60
camera2.lens.perspective = True
camera2.components.add('cam_controller', Camera2Controller())

scene1_objs = create_scene(win_score_callback, shared_player1, shared_player2, shared_ball, camera=camera1)
scene2_objs = create_scene(win_score_callback, shared_player1, shared_player2, shared_ball, camera=camera2)
scene1 = scene1_objs['scene']
scene2 = scene2_objs['scene']

input1 = InputManager()
input1.add_axis('player1_horizontal', player1_horizontal)
input1.add_axis('player1_vertical', player1_vertical)
input1.add_axis('player2_horizontal', player2_horizontal)
input1.add_axis('player2_vertical', player2_vertical)

input2 = InputManager()
input2.add_axis('player1_horizontal', player1_horizontal)
input2.add_axis('player1_vertical', player1_vertical)
input2.add_axis('player2_horizontal', player2_horizontal)
input2.add_axis('player2_vertical', player2_vertical)

options1 = {'display': (900, 533), 'show_title_bar': True, 'title': 'Player 1','fps': 60}
options2 = {'display': (900, 533), 'show_title_bar': True, 'title': 'Player 2','fps': 60}

multi_windows = [
    {'scene': scene1, 'input_manager': input1, 'options': options1},
    {'scene': scene2, 'input_manager': input2, 'options': options2},
]

game = Game(multi_windows=multi_windows)


def main():
    game.run()




