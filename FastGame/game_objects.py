class GameObject:
    def __init__(self, name):
        
        self.name = name
        self.transform = Transform(game_object=self)

        self.parent = None
        
        self.objects = ObjectManager(parent=self)
        
        self.renderer = Renderer(game_object=self)
        
        self.components = ComponentManager(game_object=self)
        self.components.start_lock = True
        self.components.add('transform', self.transform)
        
    def start(self):
        self.components.start_lock = False
        self.components.start()
        self.objects.start()
        self.renderer.setup()

    def update(self):
        self.components.update()
        self.objects.update()

    def render(self):
        self.renderer.render()
        

class ObjectManager:
    def __init__(self, parent=None):
        self._objects = []
        self.parent = parent
        self.start_lock = False
        
    def add(self, game_object):
        if not isinstance(game_object, GameObject):
            raise TypeError('Object type must be GameObject')
        if self.get(game_object.name) is not None:
            raise ValueError('Object name is used')
        if isinstance(game_object, Camera):
            if len(self.get_all(Camera)) > 0:
                raise ValueError('Only one camera is allowed')
            self._camera = game_object

        self._objects.append(game_object)
        if self.parent is not None:
            game_object.parent = self.parent
        if not self.start_lock:
            game_object.start()
        
    def update(self):
        for game_object in self._objects:
            game_object.update()
            
    def start(self):
        for game_object in self._objects:
            game_object.start()
        
    def get(self, name):
        for obj in self._objects:
            if obj.name == name:
                return obj
            if obj.objects.get(name) is not None:
                return obj
    
    def get_all(self, class_name=None, except_class_name=None):
        if class_name is None:
            return self._objects
        game_objects = []
        for obj in self._objects:
            if isinstance(obj, class_name):
                if except_class_name is not None:
                    if not isinstance(obj, except_class_name):
                        game_objects.append(obj)
                else:
                    game_objects.append(obj)
            game_objects.extend(obj.objects.get_all(class_name, except_class_name))
        return game_objects
    
    def remove(self, name):
        self._objects.pop(name, None)
        
    def remove_all(self, class_name):
        for obj in self._objects:
            if isinstance(obj, class_name):
                self._objects.pop(obj)
                
    def sort_backtofront(self, game_objects):
        camera = self.get_all(Camera)[0]
        length = len(game_objects)
        for i in range(length):  
            distance1 = game_objects[i].transform.get_distance_from(camera.transform.get_position())
            for j in range(i+1, length):
                distance2=  game_objects[i].transform.get_distance_from(camera.transform.get_position())
                if distance1 > distance2:
                    game_objects[i], game_objects[j] = game_objects[j], game_objects[i]
        return game_objects
    
    def sort_fronttoback(self, game_objects):
        camera = self.get_all(Camera)[0]
        length = len(game_objects)
        for i in range(length):  
            distance1 = game_objects[i].transform.get_distance_from(camera.transform.get_position())
            for j in range(i+1, length):
                distance2=  game_objects[i].transform.get_distance_from(camera.transform.get_position())
                if distance1 < distance2:
                    game_objects[i], game_objects[j] = game_objects[j], game_objects[i]
        return game_objects
    
    def get_transparent_opaque_objects(self, except_class_name=None):
        transparent = []
        opaque = []
        for game_object in self.get_all(VisibleGameObject, except_class_name):
            if game_object.material.alpha < 1:
                transparent.append(game_object)
            else:
                opaque.append(game_object)
        return transparent, opaque
 
    
        
        
class VisibleGameObject(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh = Mesh(game_object=self)
        self.material = Material(game_object=self)
        self.texture = Texture(game_object=self)

        self.components.add('mesh', self.mesh)
        self.components.add('material', self.material)
        self.components.add('texture', self.texture)

        
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


class SkyBox(VisibleGameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.texture  =  SkyBoxTexture(game_object=self)
        self.mesh.mesh = MeshParser('meshes/cuboid.obj')
        
        self.components.add('texture', self.texture)
        
        
class FootballGoal(VisibleGameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh.mesh  =  MeshParser('meshes/football_goal.obj')
      

class Light(InVisibleGameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DirectionalLight(Light):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.transform = DirectionalLightTransform(game_object=self)
        self.light_source = DirectionalLightSource(game_object=self)
        self.shadows = LightSourceShadow(game_object=self, perspective=False)

        self.components.add('transform', self.transform)
        self.components.add('light_source', self.light_source)
        self.components.add('shadows', self.shadows)


class PointLight(Light):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.transform = PointLightTransform(game_object=self)
        self.light_source = PointLightSource(game_object=self)

        self.components.add('transform', self.transform)
        self.components.add('light_source', self.light_source)
        
        
class SpotLight(Light):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.transform = SpotLightTransform(game_object=self)
        self.light_source = SpotLightSource(game_object=self)
        self.shadows = LightSourceShadow(game_object=self, perspective=True)

        self.components.add('transform', self.transform)
        self.components.add('light_source', self.light_source)
        self.components.add('shadows', self.shadows)
        

class Camera(InVisibleGameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.transform = CameraTransform(game_object=self)
        self.lens = CameraLens(game_object=self)

        self.components.add('transform', self.transform)
        self.components.add('lens', self.lens)


class Text(GameObject):
    def __init__(self, name, text='', x=10, y=10, font_size=24, color=None, anchor_x='left', anchor_y='top'):
        super().__init__(name)
        from .components import TextDisplay, Color
        if color is None:
            color = Color('#FFFFFF')
        text_display = TextDisplay(
            text=text,
            x=x,
            y=y,
            font_size=font_size,
            color=color,
            anchor_x=anchor_x,
            anchor_y=anchor_y
        )
        self.components.add('text_display', text_display)

  
from .components import *
from .renderer import Renderer
from .mesh_parser import MeshParser
from .shader import Shader