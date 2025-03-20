import ctypes
import numpy as np
import math
from OpenGL.GL import *

from PIL import Image
from .mesh_parser import MeshParser
from .utils import Color
from .game_objects import GameObject
from pyglm import glm

from . import internal_data




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
    

class Transform(RenderedComponent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = {'x': 0, 'y': 0, 'z': 0}
        self.rotation = {'x': 0, 'y': 0, 'z': 0}
        self.scale = {'x': 1, 'y': 1, 'z': 1}
        
        self._model = glm.mat4(1.0)
        
    
    def translate(self, x=0, y=0, z=0):
        self.position['x'] += x
        self.position['y'] += y
        self.position['z'] += z
        
        translation = glm.mat4(1.0)
        translation = glm.translate(translation, glm.vec3(x, y, z))
        
        self._model = translation * self._model
        
    def rotate(self, x=0, y=0, z=0):
        self.rotation['x'] += x
        self.rotation['y'] += y
        self.rotation['z'] += z
        
        rotation = glm.mat4(1.0)
        rotation = glm.rotate(rotation, glm.radians(x), glm.vec3(1, 0, 0))
        rotation = glm.rotate(rotation, glm.radians(y), glm.vec3(0, 1, 0))
        rotation = glm.rotate(rotation, glm.radians(z), glm.vec3(0, 0, 1))
        
        self._model = rotation * self._model
        
    def get_distance_from(self, x=0, y=0, z=0):
        return glm.distance(glm.vec3(self.position['x'], self.position['y'], self.position['z']), glm.vec3(x, y, z))
        
    def set_uniforms(self):
        return {"model": np.array(self._model, dtype=np.float32)}
    
    
class LightTransform(Transform):
    def set_uniforms(self):
        return {
            'light.position': np.array([self.position['x'], 
                                        self.position['y'], 
                                        self.position['z']], dtype=np.float32)
        }
        
        

        
class CameraTransform(Transform):
    def set_uniforms(self):
        view_position = [self.position['x'], self.position['y'], self.position['z']]
        return {"view": np.array(self._model, dtype=np.float32),
                "view_position": np.array(view_position, dtype=np.float32)}
        

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
        return {
            'VBO': self.mesh.vertices.flatten(),
            'EBO': self.mesh.indices.flatten()
        }




class Material(RenderedComponent):
    def __init__(self, color=Color("C0C0C0"), alpha=1.0,
                 ambient_light=0.3, diffuse_reflection=0.7,
                 specular_reflection=1, shininess = 100, wireframe=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color = None
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




class Texture(RenderedComponent):
    def __init__(self, texture_path=None, texture_wrapping='repeat',
                 texture_filtering='linear', *args, **kwargs):
        super().__init__(*args, **kwargs)
        if texture_wrapping not in ['repeat', 'mirrored_repeat', 'clamp_to_edge', 'clamp_to_border']:
            raise ValueError("Texture wrapping must be one of: ['repeat', 'mirrored_repeat', 'clamp_to_edge', 'clamp_to_border']")
        if texture_filtering not in ['linear', 'nearest']:
            raise ValueError("Texture filtering must be one of: ['linear', 'nearest']")
        if not texture_path:
            raise ValueError("Texture path must be set")
        self._texture_path = texture_path
        self._texture_wrapping = texture_wrapping
        self._texture_filtering = texture_filtering
        self._image_data = None
        self._image = None
        self._texture_id = None
        self.load_texture()
        
    @property
    def texture_path(self):
        return self._texture_path
    @texture_path.setter
    def texture_path(self, value):
        self._texture_path = value
        self.load_texture()
    @property
    def texture_wrapping(self):
        return self._texture_wrapping
    @texture_wrapping.setter
    def texture_wrapping(self, value):
        self._texture_wrapping = value
    @property
    def texture_filtering(self):
        return self._texture_filtering
    @texture_filtering.setter
    def texture_filtering(self, value):
        self._texture_filtering = value
        
        
    def load_texture(self):
        image = Image.open(self.texture_path)
        self._image = image.transpose(Image.FLIP_TOP_BOTTOM)
        self._image_data = np.array(image.convert("RGBA"), dtype=np.uint8)
            


    def update(self):
        self._texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._texture_id)
        
        wrap_modes = {'repeat': GL_REPEAT, 'mirrored_repeat': GL_MIRRORED_REPEAT, 'clamp_to_edge': GL_CLAMP_TO_EDGE, 'clamp_to_border': GL_CLAMP_TO_BORDER}
        filter_modes = {'linear': GL_LINEAR, 'nearest': GL_NEAREST}
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap_modes[self.texture_wrapping])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap_modes[self.texture_wrapping])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, filter_modes[self.texture_filtering])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, filter_modes[self.texture_filtering])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self._image.width, self._image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.image_data)
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        
    # def set_uniforms(self):
        
class LightSource(RenderedComponent):
    def __init__(self, light_type='point', color=Color("FFFFFF"), *args, **kwargs):
        super().__init__(*args, **kwargs)
        if light_type not in ['point', 'directional', 'spot']:
            raise ValueError("Light type must be one of: ['point', 'directional', 'spot']")
        
        self.light_type = light_type
        self.color = color
        
    def set_uniforms(self):
        return {
            'light.color': [*self.color.color_in_rgb],
        }
        
class CameraLens(RenderedComponent):
    def __init__(self, FOV=45, near=0.1, far=100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FOV = FOV
        self.near = near
        self.far = far
        
    def compute_perspective_projection_matrix(self):
        aspect_ratio = internal_data.window_width / internal_data.window_height
        return np.array(glm.perspective(glm.radians(self.FOV), aspect_ratio, self.near, self.far), dtype=np.float32)
           
        
    def set_uniforms(self):
        return {
            'projection': self.compute_perspective_projection_matrix()
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
    
    
