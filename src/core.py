from .game_objects import GameObject
from .components import *
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import time, sys
from .input_manager import Input
from .scene import Scene


class Game:
    def __init__(self, scene, input_manager=Input(), options={
        'display': (800, 600),
        'show_title_bar': True,
        'title': 'FAST GAME',
        'fps': 30
    }):
        if not isinstance(scene, Scene):
            raise TypeError('Scene must be of type Scene')
        if not isinstance(input_manager, Input):
            raise TypeError('Input manager must be of type Input')
        if not isinstance(options, dict):
            raise TypeError('Options must be of type dict')
        self.scene = scene
        self.options = options
        self.running = False
        self._clock = None
        self.input_manager = input_manager
        
        self.display = options['display']
        self.show_title_bar = options['show_title_bar']
        self.title = options['title']
        self.fps = options['fps']
        
        
        self.internal_data = {
            'delta_time': 0,
            'window_width': self.display[0],
            'window_height': self.display[1],
        }
        
        
        
        
        self.init_pygame()
        self.init_opengl()
        self.init_input_manager()
            
    def init_pygame(self):
        pygame.init()
        if self.show_title_bar:
            display_flags = pygame.DOUBLEBUF | pygame.OPENGL
        else:
            display_flags = pygame.NOFRAME | pygame.OPENGL | pygame.DOUBLEBUF
    
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        # pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1) 
        # pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        # pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE, 24)
        self.screen = pygame.display.set_mode(self.display, display_flags)
        pygame.display.set_caption(self.title)     
        self.clock = pygame.time.Clock()
        
    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LESS)
        glDepthRange(0.0, 1.0)
        glViewport(0, 0, self.display[0], self.display[1])
        
    def init_scene(self):
        for object in self.scene.game_objects:
            object.input_axes = self.input_manager.input_axes
            object.internal_data = self.internal_data
            
    def init_input_manager(self):
        self.input_manager.internal_data = self.internal_data
            

    def update_internal_data(self):
        self.internal_data['delta_time'] = self.clock.tick(self.fps) / 1000
        self.internal_data['window_width'] = self.display[0]
        self.internal_data['window_height'] = self.display[1]        
        
        
    def update(self):
        self.input_manager.update()
        self.update_internal_data()
        self.scene.update()
            
    def render(self):
        self.scene.render()
        
    def run(self):
        self.running = True
        self.init_scene()
        
        while self.running:
            if self.input_manager.quit:
                pygame.quit()
                sys.exit()
                
            self.update()
            self.render()
            
            
            