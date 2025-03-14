from game_objects import GameObject
from shader import Shader
from components import Transform, Mesh, Material, RenderedComponent
from OpenGL.GL import *
import numpy as np

class Renderer:
    def __init__(self, game_object, shader=Shader('shaders/simple.vert', 'shaders/simple.frag')):
        if not isinstance(shader, Shader):
            raise TypeError('Object must be of type Shader')
        if not isinstance(game_object, GameObject):
            raise TypeError('Object must be of type GameObject')
        
        self.game_object = game_object
        self.shader = shader
        self.VBO = None
        self.VAO = None
        self.EBO = None
        
        self.initialize_buffers()
        
    def get_rendered_components(self, game_object):
        rendered_components = []
        for component in game_object._components:
            if isinstance(component, RenderedComponent):
                rendered_components.append(component)
        return rendered_components
    
    def render(self):
        self.shader.bind()
        glBindVertexArray(self.VAO)
        
        rendered_components = self.get_rendered_components(self.game_object)
        for component in rendered_components:
            component.setup()
            buffers = component.set_buffers()
            if buffers:
                self.set_buffers(buffers)
            uniforms = component.set_uniforms()
            if uniforms:
                self.set_uniforms(uniforms)
            
            glDrawElements(GL_TRIANGLES, component.mesh.index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        self.shader.unbind()
    
    def initialize_buffers(self):
        self.VAO = glGenVertexArrays(1)
        glBindVertexArray(self.VAO)
    
        self.VBO = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        
        self.EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        
    def set_VBO(self, vertices):
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
    
    def set_EBO(self, indices):
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        glBindVertexArray(0)
        
    def set_buffers(self, buffers):
        if 'VBO' in buffers:
            self.set_VBO(buffers['VBO'])
        if 'EBO' in buffers:
            self.set_EBO(buffers['EBO'])
        
    def set_uniforms(self, uniforms):
        for uniform, value in uniforms.items():
            self.shader.set_uniform(uniform, value)
            
    def __del__(self):
        if self.VBO:
            glDeleteBuffers(1, [self.VBO])
        if self.EBO:
            glDeleteBuffers(1, [self.EBO])
        if self.VAO:
            glDeleteVertexArrays(1, [self.VAO])
