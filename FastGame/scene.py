from .utils import Color
from .game_objects import GameObject, ObjectManager, InVisibleGameObject, SkyBox, Light, SpotLight, DirectionalLight
from . import internal_data
from .shader import Shader
from .shadow_mapper import ShadowMapper
from . import internal_data


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
        self.objects.start_lock = True
    
    def render(self):
        
        transparent_objects, opaque_objects = self.objects.get_transparent_opaque_objects(except_class_name=SkyBox)
        invisible_objects = self.objects.get_all(InVisibleGameObject)
        
        transparent_objects = self.objects.sort_backtofront(transparent_objects)
        opaque_objects = self.objects.sort_fronttoback(opaque_objects)
        
        
        # lights = self.objects.get_all(Light)
        
        # self.depth_shader.bind()
        # self.shadow_mapper.bind_depth_map()
        # self.shadow_mapper.render(lights, opaque_objects)
        # self.shadow_mapper.unbind_depth_map()
        
        # internal_data.uniform_manager.clear()
        
        self.shader.bind()
        
        # self.shadow_mapper.set_depth_texture(2)
        
        # print(invisible_objects)
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
                
        
        internal_data.uniform_manager.clear()
                
    
    def start(self):
        self.shader.compile()
        self.depth_shader.compile()
        self.shadow_mapper.generate_depth_map()
        self.objects.start_lock = False
        self.shader.bind()
        self.objects.start()
        
            
    def update(self):
        self.objects.update()
