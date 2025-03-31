import ctypes
import numpy as np
import math
from OpenGL.GL import *

from PIL import Image
from .mesh_parser import MeshParser
from .utils import Color
from .game_objects import GameObject
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
        
        
    def add(self, component_name, component):
        if not isinstance(component, ComponentBase):
            raise TypeError('component must be of type ComponentBase')
        component.game_object = self.game_object
        component.start()
        self._components[component_name] = component
    
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
        if self.game_object.parent is None:
            return self.get_model_matrix()
        else:
            parent_model = self.game_object.parent.transform.get_global_model_matrix()
            return parent_model * self.get_model_matrix()
        
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
        self._translate_model_matrix(vec3 - self._position)
        self._position = vec3
        

    def get_rotation(self):
        return self._rotation

    def set_rotation(self, quat: glm.quat):
        self._rotate_model_matrix(glm.normalize(quat) * glm.inverse(self._rotation))
        self._rotation = glm.normalize(quat)
        
    def set_rotation_euler(self, vec3 : glm.vec3):
        rad = glm.radians(vec3)
        quat = glm.quat(rad)
        self.set_rotation(quat)
    
    def get_scale(self):
        return self._scale

    def set_scale(self, vec3: glm.vec3):
        self._scale_model_matrix(vec3)
        self._scale = vec3

    def translate(self, vec3: glm.vec3):
        self._position += vec3
        self._translate_model_matrix(vec3)

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
        
    def _scale_model_matrix(self, vec3: glm.vec3):
        scale = glm.scale(glm.mat4(1.0), vec3)
        self._model = self._model * scale

    def get_distance_from(self, vec3: glm.vec3):
        return glm.distance(self._position, vec3)

    def look_at(self, target: glm.vec3, up: glm.vec3):
        position = self.get_global_position()
        direction = glm.normalize(target - position)
        rot = glm.quatLookAt(direction, up)
        self.set_rotation(rot)

    def set_uniforms(self):
        model = self.get_global_model_matrix()
        return {"model": np.array(model, dtype=np.float32)}

    
    
class DirectionalLightTransform(Transform):
    def set_uniforms(self):
        return {
            'ligh_view': np.array(list(self.get_global_view_matrix()), dtype=np.float32)
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
            'ligh_view': np.array(list(self.get_global_view_matrix()), dtype=np.float32)
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
        
    def update(self):
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
        
    def update(self):
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
            
    def update(self):
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
        self.direction = {'x': 0, 'y': -1, 'z': 0}
        if color is None:
           self.color = Color('#FFFFFF')
        else: 
            self.color = color
        
    def set_uniforms(self):
        return {
            'directional_light[n].direction': np.array(list(self.direction.values()), dtype=np.float32),
            'directional_light[n].color': np.array(self.color.color_in_rgb, dtype=np.float32),
            'directional_light_num': 'num(point_light.color)',
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
        self.direction = {'x': 0, 'y': -1, 'z': 0}
        self.constant = constant
        self.linear = linear
        self.quadratic = quadratic
        self.cutoff = cutoff
        self.outer_cutoff = outer_cutoff
        
    def set_uniforms(self):
        return {
            'use_spot_light': True,
            'spot_light[n].color': np.array(self.color.color_in_rgb, dtype=np.float32),
            'spot_light[n].direction': np.array(list(self.direction.values()), dtype=np.float32),
            'spot_light[n].constant': float(self.constant),
            'spot_light[n].linear': float(self.linear),
            'spot_light[n].quadratic': float(self.quadratic),
            'spot_light[n].cutOff': math.cos(math.radians(self.cutoff)),
            'spot_light[n].outerCutOff': math.cos(math.radians(self.outer_cutoff)),
            'spot_light_num': 'num(spot_light.color)',
        }
        
        
class LightSourceShadow(RenderedComponent):
    def __init__(self, FOV=45, near=0.1, far=100, orthographic_scale=100, perspective=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FOV = FOV
        self.near = near
        self.far = far
        self.orthographic_scale = orthographic_scale
        self.perspective = perspective
        
    def compute_perspective_projection_matrix(self):
        aspect_ratio = internal_data.window_width / internal_data.window_height
        return np.array(glm.perspective(glm.radians(self.FOV), aspect_ratio, self.near, self.far), dtype=np.float32)
    
    def compute_orthographic_projection_matrix(self):
        scale = 100
        left = -internal_data.window_width / scale
        right = internal_data.window_width / scale
        top = internal_data.window_height / scale
        bottom = -internal_data.window_height / scale
        return np.array(glm.ortho(left, right, bottom, top, self.near, self.far), dtype=np.float32)
    
    def set_uniforms(self):
        projection = self.compute_perspective_projection_matrix() if self.perspective else self.compute_orthographic_projection_matrix()
        return {
            'light_projection': projection
        }
    
    
    
        
class CameraLens(RenderedComponent):
    def __init__(self, FOV=45, near=0.1, far=100, orthographic_scale=100, perspective=True,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FOV = FOV
        self.near = near
        self.far = far
        self.orthographic_scale = orthographic_scale
        self.perspective = perspective
        
    def compute_perspective_projection_matrix(self):
        aspect_ratio = internal_data.window_width / internal_data.window_height
        return np.array(glm.perspective(glm.radians(self.FOV), aspect_ratio, self.near, self.far), dtype=np.float32)
    
    def compute_orthographic_projection_matrix(self):
        left = -internal_data.window_width / self.orthographic_scale
        right = internal_data.window_width / self.orthographic_scale
        top = internal_data.window_height / self.orthographic_scale
        bottom = -internal_data.window_height / self.orthographic_scale
        return np.array(glm.ortho(left, right, bottom, top, self.near, self.far), dtype=np.float32)     
        
    def set_uniforms(self):
        projection = self.compute_perspective_projection_matrix() if self.perspective else self.compute_orthographic_projection_matrix()
        return {
            'projection': projection,
            'perspective_projection': self.perspective,
        }
                
        
        
class SkyBoxTexture(RenderedComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._texture_id = None
        self.active = False
        
    def load_texture(self, texture_paths):
        if len(texture_paths) != 6:
            raise ValueError("Skybox texture must have 6 faces")
        image_data = []
        images = []
        for texture_path in texture_paths:
            image = Image.open(texture_path)
            images.append(image.transpose(Image.FLIP_TOP_BOTTOM))
            image_data.append(np.array(image.convert("RGB"), dtype=np.uint8))
        
        
        self._texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_CUBE_MAP, self._texture_id)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        i = 0
        for image, data in zip(images, image_data):
            if image.width != images[0].width or image.height != images[0].height:
                raise ValueError("All skybox faces must have the same dimensions")
            glTexImage2D(GL_TEXTURE_CUBE_MAP_POSITIVE_X + i, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, data)
            i += 1
            
        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)
        
        self.active = True
        
    def update(self):
        if self.active:
            glDepthFunc(GL_LEQUAL)
            # glDisable(GL_CULL_FACE)
            glCullFace(GL_BACK)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_CUBE_MAP, self._texture_id)
            
    def post_setup(self):
        glDepthFunc(GL_LESS)
        # glEnable(GL_CULL_FACE)
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
    
    
