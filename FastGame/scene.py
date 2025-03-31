from .utils import Color
from .game_objects import GameObject, ObjectManager, InVisibleGameObject, SkyBox, Light, SpotLight, DirectionalLight
from . import internal_data
from .shader import Shader
from .shadow_mapper import ShadowMapper
from . import uniform_manager


class Scene:
    def __init__(self, name, shader, depth_shader):
        if not isinstance(name, str):
            raise TypeError('Name must be a string')
        if not isinstance(shader, Shader):
            raise TypeError('Shader must be of type Shader')
        self.name = name
        self.shader = shader
        self.depth_shader = depth_shader
        self.shadow_mapper = ShadowMapper()
        self.objects = ObjectManager()
    
    def render(self):
        
        uniform_manager.clear()
        
        transparent_objects, opaque_objects = self.objects.get_transparent_opaque_objects(except_class_name=SkyBox)
        invisible_objects = self.objects.get_all(InVisibleGameObject)
        
        transparent_objects = self.objects.sort_backtofront(transparent_objects)
        opaque_objects = self.objects.sort_fronttoback(opaque_objects)
        
        lights = self.objects.get_all(DirectionalLight)
        
        self.depth_shader.bind()
        self.shadow_mapper.bind_depth_map()
        self.shadow_mapper.render(lights, opaque_objects)
        self.shadow_mapper.unbind_depth_map()
        
        self.shader.bind()
        
        self.shadow_mapper.set_depth_texture(0)
        
        for game_object in invisible_objects:
            if hasattr(game_object, 'renderer'):
                game_object.render()

        for game_object in opaque_objects:
            if hasattr(game_object, 'renderer'):
                game_object.render()
                
        skybox = self.objects.get_all(SkyBox)
        if len(skybox) > 0:
            skybox[0].render()
            
        for game_object in transparent_objects:
            if hasattr(game_object, 'renderer'):
                game_object.render()
                
        
        
            
        
    
    def start(self):
        pass
        
            
    def update(self):
        self.objects.update()
