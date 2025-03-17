from .game_objects import GameObject
from .shader import Shader
from .components import Transform, Mesh, Material, RenderedComponent
from OpenGL.GL import *
import numpy as np
import pygame
import ctypes
from .utils import check_gl_error

class Renderer:
    def __init__(self, game_object, shader):
        if not isinstance(shader, Shader):
            raise TypeError('Object must be of type Shader')
        if not isinstance(game_object, GameObject):
            raise TypeError('Object must be of type GameObject')
        
        self.game_object = game_object
        self.shader = shader
        self.VBO = None
        self.VAO = None
        self.EBO = None
        
        self.VBO_layout = {
            'stride': 8 * ctypes.sizeof(ctypes.c_float),
            'data': [
                {
                    'index': 0,
                    'size': 3,
                    'type': GL_FLOAT,
                    'normalized': GL_FALSE,
                    'offset': 0
                },
                {
                    'index': 1,
                    'size': 2,
                    'type': GL_FLOAT,
                    'normalized': GL_FALSE,
                    'offset': 3 * ctypes.sizeof(ctypes.c_float)
                },
                {
                    'index': 2,
                    'size': 3,
                    'type': GL_FLOAT,
                    'normalized': GL_FALSE,
                    'offset': 5 * ctypes.sizeof(ctypes.c_float)
                }
            ]
        }
        
        self._index_size = 0
        self._intialized = False
        
        
        self.shader.bind()
        
        
    def get_rendered_components(self, game_object):
        rendered_components = []
        for component in game_object.components:
            if isinstance(component, RenderedComponent):
                rendered_components.append(component)
        return rendered_components
    
    def render(self):
        if not self._intialized:
            if hasattr(self.game_object, 'mesh'):
                self.generate_buffers()
                self.load_buffers()
            self._intialized = True
            
            
        rendered_components = self.get_rendered_components(self.game_object)
        
        for component in rendered_components:
            component.setup()
            uniforms = component.set_uniforms()
            if uniforms:
                self.set_uniforms(uniforms)
                
        if hasattr(self.game_object, 'mesh'):
            print(self.game_object)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)
            glBindVertexArray(self.VAO) 
            glDrawElements(GL_TRIANGLES, self._index_size, GL_UNSIGNED_INT, None)
            pygame.display.flip()
    
    def load_buffers(self):
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        rendered_components = self.get_rendered_components(self.game_object)
        for component in rendered_components:
            buffers = component.set_buffers()
            if buffers:
                self.set_buffers(buffers)

        
        
    def generate_buffers(self):
        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)
        
    def set_VBO(self, vertices):
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    def set_EBO(self, indices):
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
     
        
    def set_buffers(self, buffers):
        if 'VBO' in buffers:
            self.set_VBO(buffers['VBO'])
            self.set_VBO_layout()
        if 'EBO' in buffers:
            self.set_EBO(buffers['EBO'])
            self._index_size = buffers['EBO'].size
    
        
    def set_uniforms(self, uniforms):
        for uniform, value in uniforms.items():
            self.shader.set_uniform(uniform, value)
            
    def set_VBO_layout(self):
        stride = self.VBO_layout['stride']
        data = self.VBO_layout['data']
        for i in data:
            glVertexAttribPointer(i['index'], i['size'], i['type'], i['normalized'], stride, ctypes.c_void_p(i['offset'] ))
            glEnableVertexAttribArray(i['index'])
            
            
    def __del__(self):
        if self.VBO:
            glDeleteBuffers(1, np.array([self.VBO], dtype=np.uint32))
        if self.EBO:
            glDeleteBuffers(1, np.array([self.EBO], dtype=np.uint32))
        if self.VAO:
            glDeleteVertexArrays(1, np.array([self.VAO], dtype=np.uint32))
            
        self.shader.delete()

