from OpenGL.GL import *
from .shader import Shader
from .game_objects import GameObject
from .components import Transform, Mesh, LightSourceShadow
from . import internal_data
from .utils import check_gl_error



class ShadowMapper:
    def __init__(self):
        
        self.depth_map_fbo = None
        self.depth_map = None
        
        self._shadow_width = 2048
        self._shadow_height = 2048
        
        self._shadow_bias = 0.005
        # self.generate_depth_map()
    
    def generate_depth_map(self):
        if self.depth_map:
            glDeleteTextures([self.depth_map])
        if self.depth_map_fbo:
            glDeleteFramebuffers([self.depth_map_fbo])

        self.depth_map_fbo = glGenFramebuffers(1)
        
        self.depth_map = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_map)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, self._shadow_width, self._shadow_height, 0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        borderColor = [ 1.0, 1.0, 1.0, 1.0 ]
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, borderColor)


        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_map_fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depth_map, 0)

        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        
        
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(f"Framebuffer incomplete: {hex(status)}")
        
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        # glBindTexture(GL_TEXTURE_2D, 0)
        
    def bind_depth_map(self):
        glViewport(0, 0, self._shadow_width, self._shadow_height)
        glBindFramebuffer(GL_FRAMEBUFFER, self.depth_map_fbo)
        glClear(GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glCullFace(GL_FRONT)
        
    def unbind_depth_map(self):
        glViewport(0, 0, internal_data.window_width, internal_data.window_height)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glCullFace(GL_BACK)
        # glDepthFunc(GL_GREATER)
        
    def render(self, lights, game_objects):
        for light in lights:
            shadow_component = light.components.get_all(LightSourceShadow)
            transform = light.components.get_all(Transform)[0]
            if len(shadow_component) == 0:
                pass
            light.renderer.set_component_uniforms(shadow_component[0])
            light.renderer.set_component_uniforms(transform)
            for game_object in game_objects:
                transform = game_object.components.get_all(Transform)[0]
                game_object.renderer.set_component_uniforms(transform)
                game_object.renderer.render_directly()
        
    def set_depth_texture(self, texture_unit=0):
        # print(self.depth_map)
        glActiveTexture(GL_TEXTURE0 + texture_unit)
        glBindTexture(GL_TEXTURE_2D, self.depth_map)
        internal_data.uniform_manager.set("shadow_map", texture_unit)
        
        
 
        