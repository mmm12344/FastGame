from mesh_parser import MeshParser
from utils import Color


class ComponentBase:
    def __init__(self, game_obj):
        if type(game_obj) != GameObject:
            raise TypeError('Object type must be GameObject')
        self.game_obj = game_obj

class Transform(ComponentBase):
    def __init__(self, position={'x':0, 'y':0, 'z':0}, rotation={'x':0, 'y':0, 'z':0}, scale={'x':1, 'y':1, 'z':1}, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.position = position
        self.rotation = rotation
        self.scale = scale
        
    def translate(self, x=0, y=0, z=0):
        self.position['x'] += x
        self.position['y'] += y
        self.position['z'] += z
        
    def rotate(self, x=0, y=0, z=0):
        self.rotation['x'] += x
        self.rotation['y'] += y
        self.rotation['z'] += z
        


class Mesh(ComponentBase):
    def __init__(self, type='empty', *args, **kwargs):
        super.__init__(*args, **kwargs)
        self._mesh_parser = MeshParser()
        self.set_type(type)
        
    def set_type(self, type = 'empty'):
        if type not in ['cuboid', 'plane', 'sphere', 'cylinder', 'empty']:
            raise ValueError('Mesh Type not defined')
        self._mesh_parser.load('/meshes/{type}.obj')
    
    def load_mesh_obj(self, filename):
        self._mesh_parser.load(filename)
    
    
        

class Material(ComponentBase):
    def __init__(self, color=Color("808080"), alpha=1.0, ambient_light=1, diffuse_reflection=1, specular_reflection=1, smooth=False, wireframe=False, *args, **kwargs):
        super.__init__(*args, **kwargs)
        
        self._color = None
        self.color = color
        self.alpha = alpha
        self.ambient_light = ambient_light
        self.diffuse_reflection = diffuse_reflection
        self.specular_reflection = specular_reflection
        self.smooth = smooth
        self.wireframe = wireframe
        
    @property
    def color(self):
        return self._color
    
    @color.setter
    def color(self, value):
        if type(value) != Color:
            raise TypeError()
        self._color = value
        
        
      
        
class Texture(ComponentBase):
    def __init__(self, texture_path=None, texture_wrapping='repeat', texture_filtering='linear', *args, **kwargs):
        super.__init__(*args, **kwargs)
        
        if texture_wrapping not in ['repeat', 'mirrored_repeat', 'clamp_to_edge', 'clamp_to_border']:
            raise ValueError("Texture wrapping must be one of the following: ['repeat', 'mirrored_repeat', 'clamp_to_edge', 'clamp_to_border']")
        if texture_filtering not in ['linear', 'nearest']:
            raise ValueError("Texture filtering must be one of the following: ['linear', 'nearest']")
        
        self._texture_path = texture_path
        self._texture_wrapping = texture_wrapping
        self._texture_filtering = texture_filtering
        self._texture_bytes = None
        self.load_texture()
        
    @property
    def texture_path(self):
        return self._texture_path       
    
    @texture_path.setter
    def texture_path(self, value):
        self.texture_path = value
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
        with open(self.texture_path, 'rb') as f:
            self.texture_bytes = f.read()
            
    
    
from game_objects import GameObject