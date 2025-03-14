import ctypes
import numpy as np
import math
from OpenGL.GL import *
from PIL import Image
from mesh_parser import MeshParser
from utils import Color
from game_objects import GameObject

class ComponentBase:
    def __init__(self, game_obj):
        if not isinstance(game_obj, GameObject):
            raise TypeError('Object type must be GameObject')
        self.game_obj = game_obj

class RenderedComponent(ComponentBase):
    def set_uniforms(self):
        return {}
    def set_buffers(self):
        return {}
    def setup(self):
        pass

class Transform(RenderedComponent):
    def __init__(self, position={'x': 0, 'y': 0, 'z': 0},
                 rotation={'x': 0, 'y': 0, 'z': 0},
                 scale={'x': 1, 'y': 1, 'z': 1}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.position = position
        self.rotation = rotation
        self.scale = scale
        
    def _create_translation_matrix(self, tx, ty, tz):
        return np.array([[1, 0, 0, tx],
                         [0, 1, 0, ty],
                         [0, 0, 1, tz],
                         [0, 0, 0, 1]], dtype=np.float32)
        
    def _create_rotation_matrix(self, rx, ry, rz):
        cosx, sinx = math.cos(rx), math.sin(rx)
        rotx = np.array([[1, 0, 0, 0],
                         [0, cosx, -sinx, 0],
                         [0, sinx, cosx, 0],
                         [0, 0, 0, 1]], dtype=np.float32)
        cosy, siny = math.cos(ry), math.sin(ry)
        roty = np.array([[cosy, 0, siny, 0],
                         [0, 1, 0, 0],
                         [-siny, 0, cosy, 0],
                         [0, 0, 0, 1]], dtype=np.float32)
        cosz, sinz = math.cos(rz), math.sin(rz)
        rotz = np.array([[cosz, -sinz, 0, 0],
                         [sinz, cosz, 0, 0],
                         [0, 0, 1, 0],
                         [0, 0, 0, 1]], dtype=np.float32)
        return rotx @ roty @ rotz
    
    def _create_scale_matrix(self, sx, sy, sz):
        return np.array([[sx, 0, 0, 0],
                         [0, sy, 0, 0],
                         [0, 0, sz, 0],
                         [0, 0, 0, 1]], dtype=np.float32)
        
    def _compute_model_matrix(self):
        translation = self._create_translation_matrix(self.position['x'], self.position['y'], self.position['z'])
        rotation = self._create_rotation_matrix(self.rotation['x'], self.rotation['y'], self.rotation['z'])
        scale = self._create_scale_matrix(self.scale['x'], self.scale['y'], self.scale['z'])
        return translation @ rotation @ scale
    
    def translate(self, x=0, y=0, z=0):
        self.position['x'] += x
        self.position['y'] += y
        self.position['z'] += z
        
    def rotate(self, x=0, y=0, z=0):
        self.rotation['x'] += x
        self.rotation['y'] += y
        self.rotation['z'] += z
        
    def set_uniforms(self):
        model_matrix = self._compute_model_matrix()
        return {"model": model_matrix}
    


class Mesh(RenderedComponent):
    def __init__(self, mesh=MeshParser('meshes/cuboid'), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mesh = None
        self.mesh = mesh
        
    @property
    def mesh(self):
        return self._mesh
    
    @mesh.setter
    def mesh(self, value):
        if not isinstance(value, MeshParser):
            raise TypeError("mesh type must be MeshParser")
        self._mesh = value
        
    def set_buffers(self):
        return {
            'VBO': self.mesh.vertices,
            'EBO': self.mesh.indices
        }




class Material(RenderedComponent):
    def __init__(self, color=Color("808080"), alpha=1.0,
                 ambient_light=1, diffuse_reflection=1,
                 specular_reflection=1, wireframe=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color = None
        self.color = color
        self.alpha = alpha
        self.ambient_light = ambient_light
        self.diffuse_reflection = diffuse_reflection
        self.specular_reflection = specular_reflection
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
            'vertex_color': [*self.color, self.alpha],
            'ambient_light': self.ambient_light,
            'diffuse_reflection': self.diffuse_reflection,
            'specular_reflection': self.specular_reflection
        }
        
    def setup(self):
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
            


    def setup(self):
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
        
    def set_uniforms(self):
        return {
            'texture_id': self.texture_id,
            'texture_wrapping': self.texture_wrapping,
            'texture_filtering': self.texture_filtering
        }
        
class LightSource(RenderedComponent):
    def __init__(self, light_type='point', color=Color("FFFFFF"), position={'x': 0, 'y': 0, 'z': 0}, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if light_type not in ['point', 'directional', 'spot']:
            raise ValueError("Light type must be one of: ['point', 'directional', 'spot']")
        self.light_type = light_type
        self.color = color
        self.position = position
        
    def set_uniforms(self):
        return {
            'light_type': self.light_type,
            'light_color': [*self.color, 1.0],
            'light_position': [self.position['x'], self.position['y'], self.position['z']]
        }
