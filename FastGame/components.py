import ctypes
import numpy as np
import math
from OpenGL.GL import *
import pyglet

from PIL import Image
from .mesh_parser import MeshParser
from .utils import Color
from .game_objects import GameObject, VisibleGameObject
from pyglm import glm
from .utils import check_gl_error

from . import internal_data
from pytransform3d.rotations import euler_from_matrix
from scipy.spatial.transform import Rotation



class ComponentBase:
    def __init__(self, game_object=None):
        if game_object is not None:
            if not isinstance(game_object, GameObject):
                raise TypeError('Object type must be GameObject')
        self.game_object = game_object
    
    def start(self):
        pass
            
    def update(self):
        pass

        
        
class ComponentManager:
    def __init__(self, game_object):
        if game_object is not None:
            if not isinstance(game_object, GameObject):
                raise TypeError('Object type must be GameObject')
        
        self._components = {}
        self.game_object = game_object
        self.start_lock = False
        
        
    def add(self, component_name, component):
        if not isinstance(component, ComponentBase):
            raise TypeError('component must be of type ComponentBase')
        component.game_object = self.game_object
        self._components[component_name] = component
        if not self.start_lock:
            component.start()
    
    def get(self, component_name : str):
        return self._components.get(component_name)
    
    def get_all(self, component_class=None):
        if component_class is None:
            return self._components.values()
        return [component for component in self._components.values() if isinstance(component, component_class)]
    
    def remove(self, component_name):
        self._components.pop(component_name, None)
        
    def remove_all(self, component_class):
        for key, value in self._components.items():
            if isinstance(value, component_class):
                self._components.pop(key)
    
    
    def update(self):
        for component in self._components.values():
            component.update()
            
    def start(self):
        for component in self._components.values():
            component.start()
        
        
        

class RenderedComponent(ComponentBase):
    def set_uniforms(self):
        return {}
    def setup(self):
        pass
    def post_setup(self):
        pass
    def post_uniforms(self):
        return {}
    

class Transform(RenderedComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._position = glm.vec3(0, 0, 0)
        self._rotation = glm.quat(1, 0, 0, 0)
        self._scale = glm.vec3(0, 0, 0)
        self._model = glm.mat4(1.0)
        self.set_position(glm.vec3(0, 0, 0))
        self.set_rotation(glm.quat(1, 0, 0, 0))
        self.set_scale(glm.vec3(1, 1, 1))

    def get_global_model_matrix(self):
        scale = glm.scale(glm.mat4(1.0), self.get_scale())
        if self.game_object.parent is None:
            return self.get_model_matrix() * scale
        else:
            parent_model = self.game_object.parent.transform.get_global_model_matrix()
            return parent_model * self.get_model_matrix() * scale
        
    def get_global_view_matrix(self):
        model = self.get_global_model_matrix()
        return glm.inverse(model)
    
    def get_global_position(self):
        if self.game_object.parent is None:
            return self.get_position()
        else:
            parent_pos = self.game_object.parent.transform.get_global_position()
            return parent_pos + self.get_position()
    
    def get_global_rotation(self):
        if self.game_object.parent is None:
            return self.get_rotation()
        else:
            parent_rotation = self.game_object.parent.transform.get_global_rotation()
            return glm.normalize(parent_rotation * self.get_rotation())
        
    def get_model_matrix(self):
        return self._model

    def get_position(self):
        return self._position

    def set_position(self, vec3: glm.vec3):
        scale = self.get_scale()
        position = vec3 #* glm.vec3(1/scale.x if scale.x != 0 else 1, 1/scale.y if scale.y != 0 else 1, 1/scale.z if scale.z != 0 else 1)
        # print(position)
        self._translate_model_matrix(position - self._position)
        self._position = glm.vec3(self.get_model_matrix()[3])
        

    def get_rotation(self):
        return self._rotation

    def set_rotation(self, quat: glm.quat):
        self._rotate_model_matrix(glm.inverse(self._rotation) * glm.normalize(quat))
        self._rotation = glm.normalize(quat)
        
    def set_rotation_euler(self, vec3 : glm.vec3):
        rad = glm.radians(vec3)
        quat = glm.quat(rad)
        self.set_rotation(quat)
    
    def get_scale(self):
        return self._scale

    def set_scale(self, vec3: glm.vec3):
        # self._scale_model_matrix(vec3)
        self._scale = vec3

    def translate(self, vec3: glm.vec3):
        scale = self.get_scale()
        position = vec3 #* glm.vec3(1/scale.x if scale.x != 0 else 1, 1/scale.y if scale.y != 0 else 1, 1/scale.z if scale.z != 0 else 1)
        self._translate_model_matrix(position)
        self._position = glm.vec3(self.get_model_matrix()[3])
        
    def rotate(self, quat: glm.quat):
        self._rotation = glm.normalize(self._rotation * glm.normalize(quat))
        self._rotate_model_matrix(quat)
        
    def rotate_euler(self, vec3 : glm.vec3):
        rad = glm.radians(vec3)
        quat = glm.quat(rad)
        self.rotate(quat)
        
    def _rotate_model_matrix(self, quat: glm.quat):
        rotation = glm.mat4_cast(quat)
        self._model = self._model * rotation
        
    def _translate_model_matrix(self, vec3: glm.vec3):
        translation = glm.translate(glm.mat4(1.0), vec3)
        self._model = self._model * translation
        

    def get_distance_from(self, vec3: glm.vec3):
        return glm.distance(self._position, vec3)

    def look_at(self, target: glm.vec3, up: glm.vec3):
        position = self.get_global_position()
        direction = glm.normalize(target - position)
        desired_global_rot = glm.quatLookAt(direction, up)
        
        if self.game_object.parent is not None:
            parent_global_rot = self.game_object.parent.transform.get_global_rotation()
            desired_local_rot = glm.inverse(parent_global_rot) * desired_global_rot
        else:
            desired_local_rot = desired_global_rot
        
        self.set_rotation(desired_local_rot)

    def set_uniforms(self):
        model = self.get_global_model_matrix()
        return {"model": np.array(model, dtype=np.float32)}

    
    
class DirectionalLightTransform(Transform):
    def set_uniforms(self):
        # print(self.get_global_view_matrix())
        # self.look_at(glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
        return {
            'directional_light[n].direction': np.array(glm.normalize(self.get_rotation() * glm.vec3(0,0,-1)), dtype=np.float32),
            'light_view': np.array(self.get_global_view_matrix(), dtype=np.float32)
       
        }
        
class PointLightTransform(Transform):
    def set_uniforms(self):
        return {
            'point_light[n].position': np.array(list(self.get_global_position()), dtype=np.float32)
        }
        
class SpotLightTransform(Transform):
    def set_uniforms(self):
        return {
            'spot_light[n].position': np.array(list(self.get_global_position()), dtype=np.float32),
            'spot_light[n].direction': np.array(glm.normalize(self.get_rotation() * glm.vec3(0,0,-1)), dtype=np.float32),
            'light_view': np.array(self.get_global_view_matrix(), dtype=np.float32)
        }
        
        

        
class CameraTransform(Transform):   
    def set_uniforms(self):
        return {"view": np.array(self.get_global_view_matrix(), dtype=np.float32),
                "view_position": np.array(list(self.get_global_position()), dtype=np.float32)}
        

class Mesh(RenderedComponent):
    def __init__(self, mesh=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mesh = None
        self.mesh = mesh
        
    @property
    def mesh(self):
        return self._mesh
    
    @mesh.setter
    def mesh(self, value):
        if value is None:
            return
        if not isinstance(value, MeshParser):
            raise TypeError("mesh type must be MeshParser")
        self._mesh = value
        
    def set_buffers(self):
        # print(self.game_object, self.mesh.vertices)
        return {
            'VBO': self.mesh.vertices.flatten(),
            'EBO': self.mesh.indices.flatten()
        }
        
    def setup(self):
        if self._mesh.is_3d:
            glEnable(GL_CULL_FACE)
            glCullFace(GL_FRONT)
        else:
            glDisable(GL_CULL_FACE)




class Material(RenderedComponent):
    def __init__(self, color=None, alpha=1.0,
                 ambient_light=0.1, diffuse_reflection=0.7,
                 specular_reflection=0, shininess = 32, wireframe=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color = None
        if color is None:
           self.color = Color('#C0C0C0')
        else: 
            self.color = color
        self.alpha = alpha
        self.ambient_light = ambient_light
        self.diffuse_reflection = diffuse_reflection
        self.specular_reflection = specular_reflection
        self.shininess = shininess
        self.wireframe = wireframe
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        if not isinstance(value, Color):
            raise TypeError("Color must be an instance of Color")
        self._color = value
        
    def set_uniforms(self):
        return {
            'material.vertex_color': [*self.color.color_in_rgb, self.alpha],
            'material.ambient_light': float(self.ambient_light),
            'material.diffuse_reflection': float(self.diffuse_reflection),
            'material.specular_reflection': float(self.specular_reflection),
            'material.shininess': float(self.shininess)
        }
        
    def setup(self):
        if self.wireframe:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
        if self.alpha < 1:
            glEnable(GL_BLEND)
            glDepthMask(GL_FALSE)
        else:
            glDisable(GL_BLEND)
            glDepthMask(GL_TRUE)




class Texture(RenderedComponent):
    def __init__(self, repeat_x = 1, repeat_y = 1, *args, **kwargs):
        super().__init__(*args, **kwargs)
 
        self.repeat_x = repeat_x
        self.repeat_y = repeat_y
        self._image_data = None
        self._image = None
        self._texture_id = None
        self.active = False
        
    @property
    def texture_wrapping(self):
        return self._texture_wrapping
    @texture_wrapping.setter
    def texture_wrapping(self, value):
        self._texture_wrapping = value

        
        
    def load_texture(self, texture_path):
        image = Image.open(texture_path)
        self._image = image.transpose(Image.FLIP_TOP_BOTTOM)
        self._image_data = np.array(image.convert("RGBA"), dtype=np.uint8)
        
    def start(self):

        if self._image:
            self._texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self._texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self._image.width, self._image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, self._image_data)
            glGenerateMipmap(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)
            self.active = True
            
    def setup(self):
        if self.active:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self._texture_id)
            
    def post_setup(self):
        glBindTexture(GL_TEXTURE_2D, 0)
        pass
        
        
    def set_uniforms(self):
        if self.active:
            return {
                'texture_repeat': np.array([self.repeat_x, self.repeat_y], dtype=np.float32),
                'use_texture': True,
                'diffuse_texture': 0
            }
        else:
            return {
                'use_texture': False
            }
        
        
class DirectionalLightSource(RenderedComponent):
    def __init__(self, color=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if color is None:
           self.color = Color('#FFFFFF')
        else: 
            self.color = color
        
    def set_uniforms(self):
        return {
            'directional_light[n].color': np.array(self.color.color_in_rgb, dtype=np.float32),
            'directional_light_num': 'num(directional_light.color)',
        }
        
class PointLightSource(RenderedComponent):
    def __init__(self, color=None, constant=0, linear=0, quadratic=0.05,*args, **kwargs):
        super().__init__(*args, **kwargs)
        if color is None:
           self.color = Color('#FFFFFF')
        else: 
            self.color = color
        self.constant = constant
        self.linear = linear
        self.quadratic =  quadratic
        
    def set_uniforms(self):
        return {
            'use_point_light': True,
            'point_light[n].color': np.array(self.color.color_in_rgb, dtype=np.float32),
            'point_light[n].constant': float(self.constant),
            'point_light[n].linear': float(self.linear),
            'point_light[n].quadratic': float(self.quadratic),
            'point_light_num': 'num(point_light.color)',
        }
        
        
class SpotLightSource(RenderedComponent):
    def __init__(self, color=None, constant=0, linear=0, quadratic=0.05, cutoff=30, outer_cutoff=35, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if color is None:
           self.color = Color('#FFFFFF')
        else: 
            self.color = color
        self.constant = constant
        self.linear = linear
        self.quadratic = quadratic
        self.cutoff = cutoff
        self.outer_cutoff = outer_cutoff
        
    def set_uniforms(self):
        return {
            'use_spot_light': True,
            'spot_light[n].color': np.array(self.color.color_in_rgb, dtype=np.float32),
            'spot_light[n].constant': float(self.constant),
            'spot_light[n].linear': float(self.linear),
            'spot_light[n].quadratic': float(self.quadratic),
            'spot_light[n].cutOff': math.cos(math.radians(self.cutoff)),
            'spot_light[n].outerCutOff': math.cos(math.radians(self.outer_cutoff)),
            'spot_light_num': 'num(spot_light.color)',
        }
        
        
class LightSourceShadow(RenderedComponent):
    def __init__(self, FOV=45, near=0.1, far=1000, orthographic_size=50, perspective=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FOV = FOV
        self.near = near
        self.far = far
        self.orthographic_size = orthographic_size
        self.perspective = perspective
    
    @property 
    def aspect_ratio(self):
        return internal_data.window_width / internal_data.window_height
        
    def compute_perspective_projection_matrix(self):
        return np.array(glm.perspective(glm.radians(self.FOV), self.aspect_ratio, self.near, self.far), dtype=np.float32)
    
    def compute_orthographic_projection_matrix(self):
        left = -self.orthographic_size 
        right = self.orthographic_size 
        top = self.orthographic_size
        bottom = -self.orthographic_size
        return np.array(glm.ortho(left, right, bottom, top, self.near, self.far), dtype=np.float32)
        
    def get_projection_matrix(self):
        if self.perspective:
            return self.compute_perspective_projection_matrix()
        return self.compute_orthographic_projection_matrix()
    
    def set_uniforms(self):
        # print(self.get_projection_matrix())
        return {
            'light_projection': self.get_projection_matrix()
        }
    
    
    
        
class CameraLens(RenderedComponent):
    def __init__(self, FOV=45, near=0.1, far=1000, orthographic_size=10, perspective=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FOV = FOV
        self.near = near
        self.far = far
        self.orthographic_size = orthographic_size
        self.perspective = perspective
    
    @property 
    def aspect_ratio(self):
        return internal_data.window_width / internal_data.window_height
        
    def compute_perspective_projection_matrix(self):
        return np.array(glm.perspective(glm.radians(self.FOV), self.aspect_ratio, self.near, self.far), dtype=np.float32)
    
    def compute_orthographic_projection_matrix(self):
        left = -self.orthographic_size * self.aspect_ratio
        right = self.orthographic_size * self.aspect_ratio
        top = self.orthographic_size
        bottom = -self.orthographic_size
        return np.array(glm.ortho(left, right, bottom, top, self.near, self.far), dtype=np.float32)
        
    def get_projection_matrix(self):
        if self.perspective:
            return self.compute_perspective_projection_matrix()
        return self.compute_orthographic_projection_matrix()  
        
    def set_uniforms(self):
        return {
            'projection': self.get_projection_matrix(),
            'perspective_projection': self.perspective,
        }
                
        
        
class SkyBoxTexture(RenderedComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._texture_id = None
        self.active = False
        self.image_data = None
        self.images = None
        
    def load_texture(self, texture_paths):
        if len(texture_paths) != 6:
            raise ValueError("Skybox texture must have 6 faces")
        self.image_data = []
        self.images = []
        for texture_path in texture_paths:
            image = Image.open(texture_path)
            self.images.append(image.transpose(Image.FLIP_TOP_BOTTOM))
            self.image_data.append(np.array(image.convert("RGB"), dtype=np.uint8))
        
    def start(self):
        self._texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self._texture_id)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        i = 0
        for image, data in zip(self.images, self.image_data):
            if image.width != self.images[0].width or image.height != self.images[0].height:
                raise ValueError("All skybox faces must have the same dimensions")
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
            i += 1
            
        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)
        self.active = True
        
    def setup(self):
        if self.active:
            glDepthFunc(GL_LEQUAL)
            glCullFace(GL_BACK)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_CUBE_MAP, self._texture_id)
            
    def post_setup(self):
        glDepthFunc(GL_LESS)
        glCullFace(GL_FRONT)
        
    def post_uniforms(self):
        return {
            'use_skybox': False
        }
        
        
    def set_uniforms(self):
        if self.active:
            return {
                'skybox': 1,
                'use_skybox': True
            }
        else:
            return {
                'use_skybox': False
            }
            



class Script(ComponentBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def delta_time(self):
        return internal_data.delta_time
    
    @property
    def input_axes(self):
        return internal_data.input_manager.input_axes
        
        
        
    def update(self):
        pass
    def start(self):
        pass


class BoxCollider(ComponentBase):
    def __init__(self, size=None, on_trigger=None, is_trigger=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.size = size if size is not None else [1.0, 1.0, 1.0]
        self.on_trigger = on_trigger  
        self._last_colliding = set()
        self.is_trigger = is_trigger

    def get_bounds(self):
        
        pos = self.game_object.transform.get_global_position()
        scale = self.game_object.transform.get_scale()
       
        half_size = [s * sc * 0.5 for s, sc in zip(self.size, [scale.x, scale.y, scale.z])]

        # scale_vec = [abs(scale.x) if scale.x != 0 else 1, abs(scale.y) if scale.y != 0 else 1, abs(scale.z) if scale.z != 0 else 1]
        # half_size = [abs(s) * sc * 0.5 for s, sc in zip(self.size, scale_vec)]
        min_bound = [pos.x - half_size[0], pos.y - half_size[1], pos.z - half_size[2]]
        max_bound = [pos.x + half_size[0], pos.y + half_size[1], pos.z + half_size[2]]
        return min_bound, max_bound

    def check_collision(self, other):
        min_a, max_a = self.get_bounds()
        min_b, max_b = other.get_bounds()
        return all(max_a[i] >= min_b[i] and min_a[i] <= max_b[i] for i in range(3))

    def update(self):
       
        all_objects = internal_data.current_scene.objects.get_all(VisibleGameObject)
        other_colliders = []
        for game_object in all_objects:
            collider = game_object.components.get('collider')
            if collider:
                other_colliders.append(collider)
       
        for other in other_colliders:
            if other is self:
                continue
            if self.check_collision(other):
                if other not in self._last_colliding:
                    self._last_colliding.add(other)
                   
                    if callable(self.on_trigger):
                        # print(f"Trigger: {self.game_object.name} collided with {other.game_object.name}")
                        print(self.get_bounds())
                        print(other.get_bounds())
                        self.on_trigger(self, other)
            else:
                if other in self._last_colliding:
                    self._last_colliding.remove(other)

class RigidBody(ComponentBase):
    def __init__(self,
                 mass: float = 1.0,
                 use_gravity: bool = True,
                 gravity: np.ndarray = np.array([0, -9.81, 0]),
                 friction: float = 0.1,
                 bounciness: float = 0.2,
                 linear_damping: float = 0.01,
                 angular_damping: float = 0.01,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.mass = mass
        self.use_gravity = use_gravity
        self.gravity = np.array(gravity, dtype=np.float32)
        self.velocity = np.zeros(3, dtype=np.float32)
        self.acceleration = np.zeros(3, dtype=np.float32)
        self.friction = np.clip(friction, 0.0, 1.0)
        self.bounciness = np.clip(bounciness, 0.0, 1.0)
        self.linear_damping = linear_damping
        self.angular_damping = angular_damping

    def apply_force(self, force: np.ndarray) -> None:
        self.acceleration += np.array(force, dtype=np.float32) / self.mass
        # print(self.acceleration)

    def start(self):
        pass

    def update(self):
        dt = getattr(self, 'delta_time', 1.0 / 60.0)
        epsilon = 1e-4
        self.velocity += self.acceleration * dt
        self.velocity *= (1.0 - self.linear_damping * dt)
        if hasattr(self.game_object, 'transform'):
            pos = self.game_object.transform.get_position()
            current = np.array([pos.x, pos.y, pos.z], dtype=np.float32)
            collider = self.game_object.components.get('collider')
            all_objects = internal_data.current_scene.objects.get_all(VisibleGameObject)
            other_colliders = [obj.components.get('collider') for obj in all_objects if obj.components.get('collider') is not collider]
            new_pos = current + self.velocity * dt
            hit = None
            hit_t = 1.0
            hit_normal = None
            for other in other_colliders:
                if isinstance(collider, BoxCollider) and isinstance(other, BoxCollider):
                    
                    if collider.is_trigger or other.is_trigger:
                        if collider.check_collision(other):
                            if callable(collider.on_trigger):
                                collider.on_trigger(collider, other)
                        continue
                    temp_collider = collider
                    temp_collider.game_object.transform.set_position(glm.vec3(*new_pos))
                    if temp_collider.check_collision(other):
                        hit = other
                        hit_t = 1.0
                        min_a, max_a = collider.get_bounds()
                        min_b, max_b = other.get_bounds()
                        overlap = [min(max_a[i], max_b[i]) - max(min_a[i], min_b[i]) for i in range(3)]
                        axis = int(np.argmin(np.abs(overlap)))
                        hit_normal = np.zeros(3)
                        hit_normal[axis] = 1.0 if current[axis] > (min_b[axis] + max_b[axis]) / 2 else -1.0
                       
                        other_rb = None
                        if hasattr(other, 'game_object') and hasattr(other.game_object, 'components'):
                            other_rb = other.game_object.components.get('rigidbody')
                        if other_rb is not None:
                            v1 = self.velocity
                            v2 = other_rb.velocity
                            m1 = self.mass
                            m2 = other_rb.mass
                            rel_vel = np.dot(v1 - v2, hit_normal)
                            if rel_vel < 0:  
                                impulse = (-(1 + self.bounciness) * rel_vel) / (1/m1 + 1/m2)
                                impulse_vec = impulse * hit_normal
                                self.velocity += (impulse_vec / m1)
                                other_rb.velocity -= (impulse_vec / m2)
            if hit is not None:
                contact = current + (new_pos - current) * hit_t
                v = self.velocity
                if np.dot(v, hit_normal) < 0:
                    v_reflect = v - 2 * np.dot(v, hit_normal) * hit_normal
                else:
                    v_reflect = v
                self.velocity = v_reflect * self.bounciness
                if abs(hit_normal[1]) > 0.5:
                    self.velocity[0] *= (1.0 - self.friction)
                    self.velocity[2] *= (1.0 - self.friction)
                    normal_vel = np.dot(self.velocity, hit_normal)
                    if abs(normal_vel) < epsilon:
                        self.velocity -= normal_vel * hit_normal
                        self.velocity[1] = 0
                        contact[1] = max(contact[1], current[1]) if hit_normal[1] > 0 else min(contact[1], current[1])
                        min_b, max_b = hit.get_bounds()
                        closest = np.maximum(min_b, np.minimum(contact, max_b))
                        contact = closest
                self.game_object.transform.set_position(glm.vec3(*contact))
                if np.all(np.abs(self.velocity) < epsilon) and np.all(np.abs(self.acceleration) < epsilon):
                    self.velocity[:] = 0
                    self.acceleration[:] = 0
                    return
            else:
                self.game_object.transform.set_position(glm.vec3(*new_pos))
        self.acceleration.fill(0.0)

class TextDisplay(ComponentBase):
    def __init__(self, text='', x=10, y=10, font_size=24, color=Color('#FFFFFF'), anchor_x='left', anchor_y='top', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.x = x
        self.y = y
        self.font_size = font_size
        self.color = color if isinstance(color, Color) else Color(color)
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.label = None

    def start(self):
        rgba = tuple(int(c * 255) for c in self.color.color_in_rgb) + (255,)
        self.label = pyglet.text.Label(
            self.text,
            font_name='Arial',
            font_size=self.font_size,
            x=self.x,
            y=self.y,
            anchor_x=self.anchor_x,
            anchor_y=self.anchor_y,
            color=rgba
        )

    def update(self):
        if self.label:
            self.label.text = self.text
            rgba = tuple(int(c * 255) for c in self.color.color_in_rgb) + (255,)
            self.label.color = rgba
            self.label.draw()
