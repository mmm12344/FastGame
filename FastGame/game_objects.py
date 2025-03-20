
class GameObject:
    def __init__(self, name, shader):
        
        if not isinstance(shader, Shader):
            raise TypeError('Object must be of type Shader')
        
        self.name = name
        self.transform = Transform(game_object=self)

        self._children = []
        
        self.renderer = Renderer(game_object=self, shader=shader)
        
        self.components = ComponentManager(game_object=self)
        self.components.add('transform', self.transform)


    def add_child(self, game_object):
        if not isinstance(game_object, GameObject):
            raise TypeError('Object type must be GameObject')
        if game_object.name == self.name or game_object.name in [obj.name for obj in self._children]:
            raise ValueError('Object name is used')
        self._children.append(game_object)

    def remove_child(self, name):
        for obj in self._children:
            if obj.name == name:
                self._children.remove(obj)
                return True
        return False

    def start(self):
        self.renderer.setup()

    def update(self):
        self.components.update()
        for child in self._children:
            child.update()

    def render(self):
        self.renderer.render()
        

class ObjectManager:
    def __init__(self):
        self._objects = {}
        self._camera = None
        
    def add(self, game_object):
        if not isinstance(game_object, GameObject):
            raise TypeError('Object type must be GameObject')
        if game_object.name in self._objects:
            raise ValueError('Object name is used')
        if isinstance(game_object, Camera):
            if len(self.get_all(Camera)) > 0:
                raise ValueError('Only one camera is allowed')
            self._camera = game_object
        self._objects[game_object.name] = game_object
        game_object.start()
        
    def update(self):
        for game_object in self._objects.values():
            game_object.update()
        
    def get(self, name):
        return self._objects.get(name)
    
    def get_all(self, class_name=None):
        if class_name is None:
            return self._objects.values()
        return [obj for obj in self._objects.values() if isinstance(obj, class_name)]
    
    def remove(self, name):
        self._objects.pop(name, None)
        
    def remove_all(self, class_name):
        for key, value in self._objects.items():
            if isinstance(value, class_name):
                self._objects.pop(key)
                
    def sort_backtofront(self, game_objects):
        if self._camera is None:
            raise ValueError('Camera is not found')
        length = len(game_objects)
        for i in range(length):  
            distance1 = game_objects[i].transform.get_distance_from(*self._camera.transform.position.values())
            for j in range(i+1, length):
                distance2=  game_objects[i].transform.get_distance_from(*self._camera.transform.position.values())
                if distance1 > distance2:
                    game_objects[i], game_objects[j] = game_objects[j], game_objects[i]
        return game_objects
    
    def sort_fronttoback(self, game_objects):
        if self._camera is None:
            raise ValueError('Camera is not found')
        length = len(game_objects)
        for i in range(length):  
            distance1 = game_objects[i].transform.get_distance_from(*self._camera.transform.position.values())
            for j in range(i+1, length):
                distance2=  game_objects[i].transform.get_distance_from(*self._camera.transform.position.values())
                if distance1 < distance2:
                    game_objects[i], game_objects[j] = game_objects[j], game_objects[i]
        return game_objects
    
    def get_transparent_opaque_objects(self):
        transparent = []
        opaque = []
        for game_object in self.get_all(VisibleGameObject):
            if game_object.material.alpha < 1:
                transparent.append(game_object)
            else:
                opaque.append(game_object)
        return transparent, opaque
    
        
        
class VisibleGameObject(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transform = Transform(game_object=self)
        self.mesh = Mesh(game_object=self)
        self.material = Material(game_object=self)


        self.components.add('transform', self.transform)
        self.components.add('mesh', self.mesh)
        self.components.add('material', self.material)

        
class InVisibleGameObject(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        

class Cuboid(VisibleGameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh.mesh = MeshParser('meshes/cuboid.obj')
        


class Plane(VisibleGameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh.mesh = MeshParser('meshes/plane.obj')
       


class Sphere(VisibleGameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh.mesh = MeshParser('meshes/sphere.obj')
       


class Cylinder(VisibleGameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh.mesh  =  MeshParser('meshes/cylinder.obj')
      


class Light(InVisibleGameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transform = LightTransform(game_object=self)
        self.light_source = LightSource(game_object=self)

        self.components.add('transform', self.transform)
        self.components.add('light_source', self.light_source)

        


class Camera(InVisibleGameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transform = CameraTransform(game_object=self)
        self.lens = CameraLens(game_object=self)

        self.components.add('transform', self.transform)
        self.components.add('lens', self.lens)

        
        
        
        
  
from .components import *
from .renderer import Renderer
from .mesh_parser import MeshParser
from .shader import Shader