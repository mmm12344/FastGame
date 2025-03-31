from .game_objects import GameObject
from .components import *
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import time, sys
from . import internal_data


class Game:
    def __init__(self, input_manager=None, options=None):
        if input_manager is None:
            input_manager = InputManager()
            
        if options is None:
            options = {
                'display': (800, 600),
                'show_title_bar': True,
                'title': 'FAST GAME',
                'fps': 30
            }
            
        if not isinstance(input_manager, InputManager):
            raise TypeError('Input manager must be of type Input')
        if not isinstance(options, dict):
            raise TypeError('Options must be of type dict')
        
        
        self._scene = None
        self.options = options
        self.running = False
        self._clock = None
        self.input_manager = input_manager
        
        self.display = options['display']
        self.show_title_bar = options['show_title_bar']
        self.title = options['title']
        self.fps = options['fps']
        
        
        self.init_pygame()
        self.init_opengl()
        self.init_internal_data()

    @property
    def scene(self):
        return self._scene
    
    @scene.setter
    def scene(self, value):
        if not isinstance(value, Scene):
            raise TypeError('Scene must be of type Scene')
        self._scene = value
        self.init_scene()
            
    def init_pygame(self):
        pygame.init()
        if self.show_title_bar:
            display_flags = pygame.DOUBLEBUF | pygame.OPENGL
        else:
            display_flags = pygame.NOFRAME | pygame.OPENGL | pygame.DOUBLEBUF
    
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1) 
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        self.screen = pygame.display.set_mode(self.display, display_flags, vsync=1)
        pygame.display.set_caption(self.title)     
        self.clock = pygame.time.Clock()
        
    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        glCullFace(GL_FRONT) 
        glFrontFace(GL_CW)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LESS)
        glDepthRange(0.0, 1.0)
        glViewport(0, 0, self.display[0], self.display[1])
        
    def init_scene(self):
        self.scene.start()
            
    def init_internal_data(self):
        internal_data.delta_time = 0
        internal_data.window_width = self.display[0]
        internal_data.window_height = self.display[1]
        internal_data.input_manager = self.input_manager

    def update_internal_data(self):
        internal_data.delta_time = self.clock.tick(self.fps) / 1000
        internal_data.window_width = self.display[0]
        internal_data.window_height = self.display[1]        
        
        
    def update(self):
        self.update_internal_data()
        self.input_manager.update(internal_data.delta_time)
        self.scene.update()
            
    def render(self):
        self.scene.render()
        
    def run(self):
        self.running = True
        # self.init_scene()
        while self.running:
            if self.input_manager.quit:
                pygame.quit()
                sys.exit()
                
            self.update()
            
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.render()
            pygame.display.flip()
            
            
            
from .scene import Scene
from .input_manager import InputManager
            