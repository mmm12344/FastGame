from mesh_parser import MeshParser


class ComponentBase:
    def __init__(self, obj):
        if type(obj) != type(EmptyObject):
            raise TypeError('Object type must be or inheret from EmptyObject')
        self.obj = obj

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
        


class MeshShape(ComponentBase):
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
    def __init__(self, ambient_color_rgba=(69, 69, 69, 1), primary_color_rgba=(138, 138, 138, 1), highlights_color_rgba=(219, 219, 219, 1), smothiness=0.3, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.set_ambient_color(ambient_color_rgba)
        self.set_primary_color(primary_color_rgba)
        self.set_highlights_color(highlights_color_rgba)
        self.set_smothiness(smothiness)
        
    def _normalize_rgba_values(self, color):
        return (color[0]/255, color[1]/255, color[2]/255, color[3])
    
    def _denormalize_rgba_values(self, color):
        return (color[0]*255, color[1]*255, color[2]*255, color[3])
    
    def set_ambient_color(self, color_in_rgba):
        self._ambient_color_rgba = self._normalize_rgba_values(color_in_rgba)
        
    def get_ambient_color(self):
        return self._denormalize_rgba_values(self._ambient_color_rgba)
    
    def set_primary_color(self, color_in_rgba):
        self._primary_color_rgba = self._normalize_rgba_values(color_in_rgba)
        
    def get_primary_color(self):
        return self._denormalize_rgba_values(self._primary_color_rgba)
    
    def set_highlights_color(self, color_in_rgba):
        self._highlight_color_rgba = self._normalize_rgba_values(self._highlight_color_rgba)
        
    def get_highlights_color(self):
        return self._denormalize_rgba_values(self._highlight_color_rgba)
    
    def set_smothiness(self, value):
        self._smothiness = value * 128
    
    def get_smothiness(self):
        return self._smothiness / 128
    
    
from base_objects import EmptyObject