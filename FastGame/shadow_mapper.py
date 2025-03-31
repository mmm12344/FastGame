from OpenGL.GL import *
from .shader import Shader
from .game_objects import GameObject
from . import internal_data



class ShadowMapper:
    def __init__(self, shader):
        if not isinstance(shader, Shader):
            raise TypeError('Object must be of type Shader')
        
        self.depth_map_fbo = None
        self.depth_map = None
        
        self._shadow_width = 1024
        self._shadow_height = 1024
        
        self._shadow_bias = 0.005
        
    def generate_depth_map(self):
        self.depth_map_fbo = glGenFramebuffers(1)
        
        self.depth_map = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_map)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, self._shadow_width, self._shadow_height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_map_fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depth_map, 0)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("Framebuffer not complete")
        
    def bind_depth_map(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_map_fbo)
        glViewport(0, 0, self._shadow_width, self._shadow_height)
        glClear(GL_DEPTH_BUFFER_BIT)
        
    def unbind_depth_map(self):
        glViewport(0, 0, internal_data.window_width, internal_data.window_height)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
 
        