


class GameObject:
    def __init__(self, name):
        self.name = name
        self.transform = Transform(game_object=self)

        self._components = {}
        self.add_component('transform', self.transform)

        self._children = []
        self.input_axes = {}
        self.internal_data = {}
        
        
        
        self.renderer = Renderer(game_object=self, shader=Shader('shaders/simple.vert', 'shaders/simple.frag'))

    @property
    def delta_time(self):
        return self.internal_data.get('delta_time', 0)

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

    def add_component(self, component_name, component):
        if not isinstance(component, ComponentBase):
            raise TypeError('component must be of type ComponentBase')
        self._components[component_name] = component

    def get_component(self, component_name):
        return self._components.get(component_name)

    @property
    def components(self):
        return self._components.values()

    def remove_component(self, component_name):
        self._components.pop(component_name, None)

    def start(self):
        pass

    def update(self):
        pass

    def render(self):
        self.renderer.render()


class Cuboid(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh = Mesh(mesh=MeshParser('meshes/cuboid.obj'), game_object=self)
        self.material = Material(game_object=self)

        self.add_component('mesh', self.mesh)
        self.add_component('material', self.material)

        self.start()


class Plane(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh = Mesh(MeshParser('meshes/plane.obj'), game_object=self)
        self.material = Material(game_object=self)

        self.add_component('mesh', self.mesh)
        self.add_component('material', self.material)

        self.start()


class Sphere(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh = Mesh(MeshParser('meshes/sphere.obj'), game_object=self)
        self.material = Material(game_object=self)

        self.add_component('mesh', self.mesh)
        self.add_component('material', self.material)

        self.start()


class Cylinder(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mesh = Mesh(MeshParser('meshes/cylinder.obj'), game_object=self)
        self.material = Material(game_object=self)

        self.add_component('mesh', self.mesh)
        self.add_component('material', self.material)

        self.start()


class Light(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_component('transform')
        self.transform = LightTransform(game_object=self)
        self.light_source = LightSource(game_object=self)

        self.add_component('transform', self.transform)
        self.add_component('light_source', self.light_source)

        self.start()


class Camera(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_component('transform')
        self.transform = CameraTransform(game_object=self)
        self.lens = CameraLens(game_object=self)

        self.add_component('transform', self.transform)
        self.add_component('lens', self.lens)

        self.start()
        
        
        
        
from .components import Transform, Mesh, Material, ComponentBase, LightTransform, CameraTransform, CameraLens, LightSource
from .renderer import Renderer
from .mesh_parser import MeshParser
from .shader import Shader