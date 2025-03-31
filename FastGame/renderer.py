from .game_objects import GameObject, VisibleGameObject, SkyBox
from .shader import Shader
from .components import Transform, Mesh, Material, RenderedComponent
from OpenGL.GL import *
import numpy as np
import pygame
import ctypes
from . import uniform_manager




class Renderer:
    def __init__(self, game_object):
        # if not isinstance(shader, Shader):
        #     raise TypeError('Object must be of type Shader')
        if not isinstance(game_object, GameObject):
            raise TypeError('Object must be of type GameObject')
        
        self.game_object = game_object
        # self.shader = shader
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
        
        self._rendered_components = []
        self._mesh_component = None
        
        self._index_size = 0
        
        
    def setup(self):
        # self.shader.bind()
        self.get_rendered_components()
        if isinstance(self.game_object, VisibleGameObject):
            self.generate_buffers()
            self.load_buffers()
        
    def get_rendered_components(self):
        self._rendered_components = self.game_object.components.get_all(RenderedComponent)
        
        if isinstance(self.game_object, VisibleGameObject):
            self._mesh_component = self.game_object.components.get_all(Mesh)[0]

        return self._rendered_components
    
    def render(self):
        
        for component in self._rendered_components:
            component.update()
            uniforms = component.set_uniforms()
            if uniforms:
                self.set_uniforms(uniforms)
        
        if isinstance(self.game_object, VisibleGameObject):
            glBindVertexArray(self.VAO)
            glDrawElements(GL_TRIANGLES, self._index_size, GL_UNSIGNED_INT, None)
            glBindVertexArray(0)
        
        for component in self._rendered_components:
            component.post_setup()
            uniforms = component.post_uniforms()
            if uniforms:
                self.set_uniforms(uniforms) 
        
    
    def load_buffers(self):
        glBindVertexArray(self.VAO)
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        buffers = self._mesh_component.set_buffers()
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
        self.set_VBO(buffers['VBO'])
        self.set_VBO_layout(self.VBO_layout)
        self.set_EBO(buffers['EBO'])
        self._index_size = len(buffers['EBO'])
    
        
    def set_uniforms(self, uniforms):
        for uniform, value in uniforms.items():
            uniform_manager.set(uniform, value)
            
    def set_VBO_layout(self, VBO_layout):
        stride = VBO_layout['stride']
        data = VBO_layout['data']
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
            

