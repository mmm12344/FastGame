


class ComponentBase:
    def __init__(self, obj):
        if type(obj) != type(EmptyObject):
            raise TypeError('Object type must be or inheret from EmptyObject')
        self.obj = obj

class Transform(ComponentBase):
    def __init__(self, position={'x':0, 'y':0, 'z':0}, rotation={'x':0, 'y':0, 'z':0}, scale={'x':1, 'y':1, 'z':1}, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self._position = position
        self._rotation = rotation
        self._scale = scale
        
    def set_position(self, x=None, y=None, z=None):
        x = x if x != None else self.position['x']
        y = y if y != None else self.position['y']
        z = z if z != None else self.position['z']
        self.position = {'x':x, 'y':y, 'z':z}
    
    def set_rotation(self, x=None, y=None, z=None):
        x = x if x != None else self.position['x']
        y = y if y != None else self.position['y']
        z = z if z != None else self.position['z']
        self.position = {'x':x, 'y':y, 'z':z}
        
    def set_scale(self, x=None, y=None, z=None):
        x = x if x != None else self.position['x']
        y = y if y != None else self.position['y']
        z = z if z != None else self.position['z']
        self.position = {'x':x, 'y':y, 'z':z}
        


class MeshShape(ComponentBase):
    def __init__(self, type='cuboid', *args, **kwargs):
        super.__init__(*args, **kwargs)
        self._type = ''
        self.set_type(type)
        
    def set_type(self, type = 'cuboid'):
        if type not in ['cuboid', 'plane', 'sphere', 'cylinder']:
            raise ValueError('Mesh Type not defined')
        self._type = type
        

class Material(ComponentBase):
    def __init__(self, from_img=False, img_src=None, color_in_hex='#ffff', *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.from_img = from_img
        self.img_src = img_src
        self.color_in_hex = color_in_hex
        
        
if __name__ == '__main__':
    t = Transform()
    
    t.set_position(0, 0)
    
    
from base_objects import EmptyObject