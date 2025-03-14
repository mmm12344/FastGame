from components import Transform, Mesh, Material, ComponentBase
from renderer import Renderer
from mesh_parser import MeshParser

class GameObject:
    def __init__(self, name='empty'):
        self.transform = Transform(game_object=self)
        self.renderer = Renderer(game_object=self)
        
        self._components = {}
        
        self.add_component(self.transform)
        
        self._children = []
        self.input_axes = {} 
        self.delta_time = 0
        self.name = name
        
        self.start()
        
    def add_child(self, game_object):
        if not isinstance(game_object, GameObject):
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
    
    def add_component(self, component_name, component):
        if not isinstance(component, ComponentBase):
            raise TypeError('component must be of type ComponentBase')
        self._components[component_name] = component
    
    def get_component(self, component_name):
        return self._components[component_name]
    
    def remove_component(self, component_name):
        del self._components[component_name]
            
    def start(self):
        return
    
    def update(self):
        return
        
        
class Cuboid(GameObject): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh = Mesh('cuboid', game_object=self)
        self.material = Material(game_object=self)
        
        self.add_component('mesh', self.mesh)
        self.add_component('material', self.material)
        
        
class Plane(GameObject): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh = Mesh('plane', game_object=self)
        self.material = Material(game_object=self)
        
        self.add_component('mesh', self.mesh)
        self.add_component('material', self.material)
        
        
class Sphere(GameObject): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh = Mesh('sphere', game_object=self)
        self.material = Material(game_object=self)
        
        self.add_component('mesh', self.mesh)
        self.add_component('material', self.material)
        
class Cylinder(GameObject): 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh = Mesh('cylinder', game_object=self)
        self.material = Material(game_object=self)
        
        self.add_component('mesh', self.mesh)
        self.add_component('material', self.material)
        
