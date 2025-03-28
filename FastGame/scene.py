from .utils import Color
from .game_objects import GameObject, ObjectManager, InVisibleGameObject, SkyBox
from . import internal_data


class Scene:
    def __init__(self, name, background_color=Color('f0f0f0')):
        self.name = name
        self.background_color = background_color
        self.objects = ObjectManager()
    
    def render(self):
        
        for game_object in self.objects.get_all(GameObject):
            if hasattr(game_object, 'renderer'):
                game_object.renderer.shader.uniforms.clear()
        
        transparent_objects, opaque_objects = self.objects.get_transparent_opaque_objects(except_class_name=SkyBox)
        invisible_objects = self.objects.get_all(InVisibleGameObject)
        
        transparent_objects = self.objects.sort_backtofront(transparent_objects)
        opaque_objects = self.objects.sort_fronttoback(opaque_objects)
        
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
