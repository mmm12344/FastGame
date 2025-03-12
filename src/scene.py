from utils import Color
from game_objects import GameObject

class Scene:
    def __init__(self, background_color=Color('f0f0f0')):
        self.background_color = background_color
        self._game_objects = []
        self._lights = []
        self._cameras = []
        
    def add_game_object(self, game_object):
        if type(object) != type(GameObject):
            raise TypeError('Object type must be GameObject')
        if game_object.name in [obj.name for obj in self._game_objects]:
            raise ValueError('Object name is used')
        
        self._game_objects.append(game_object)
        
    def remove_game_object(self, name):
        removed = False
        for obj in self._game_objects:
            if obj.name == name:
                self._game_objects.remove(obj)
                removed = True
        if not removed:
            return False
        return True
        
