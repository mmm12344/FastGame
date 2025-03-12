from components import Transform, Mesh, Material


class GameObject:
    def __init__(self, name='empty'):
        self.transform = Transform(game_object=self)
        self.mesh = Mesh(type='empty', game_obj=self)
        
        self._children = []
        self.input_axes = {} 
        self.delta_time = 0
        self.name = name
        
    def add_child(self, game_object):
        if type(object) != type(GameObject):
            raise TypeError('Object type must be GameObject')
        if game_object.name == self.name or game_object.name in [ obj.name for obj in self._children]:
            raise ValueError('Object name is used')
        self._children.append(game_object)
        
    def remove_child(self, name):
        removed = False
        for obj in self._children:
            if obj.name == name:
                self._children.remove(obj)
                removed = True
        if not removed:
            return False
        return True
    
    def start(self):
        return
    
    def update(self):
        return
        
        
class Cuboid(GameObject): 
    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.mesh = Mesh('cuboid', game_object=self)
        
        
class Plane(GameObject): 
    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.mesh = Mesh('plane', game_object=self)
        
        
class Sphere(GameObject): 
    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.mesh = Mesh('sphere', game_object=self)
        
class Cylinder(GameObject): 
    def __init__(self, *args, **kwargs):
        super.__init__(*args, **kwargs)
        self.mesh = Mesh('cylinder', game_object=self)
        
