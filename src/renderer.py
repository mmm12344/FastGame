from game_objects import GameObject
from shader import Shader
from components import Transform, Mesh, Material

class Renderer:
    def __init__(self, shader=Shader('shaders/simple.vert', 'shaders/simple.frag')):
        if type(shader) != Shader:
            raise TypeError('Object must be of type Shader')
        
        self.game_objects = None
        self.shader = shader
        
    def find_components(self, game_object):
        transform = game_object.transform
        mesh = game_object.mesh
        material = game_object.material
        
        if type(transform) != Transform:
            raise TypeError()
        if type(mesh) != Mesh:
            raise TypeError()
        if type(material) != Material:
            raise TypeError()
        
        return transform, mesh, material
    
    def render_objects(self, game_object):
        if type(game_object) != GameObject:
            raise TypeError('Object must be of type GameObject')
        
        transform, mesh, material = self.find_components(game_object)
        
        
        