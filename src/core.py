from game_objects import EmptyObject
from components import *
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import time, sys
from input_manager import Input



class Game:
    def __init__(self, input_manager=Input(),options={
        'display': (800, 600),
        'show_title_bar': True,
        'title': 'FAST GAME',
        'fps' : 60
    }):
        self.options = options
        self.running = False
        self._clock = None
        self.input_manager = input_manager
        
        self.display = options['display']
        self.show_title_bar = options['show_title_bar']
        self.title = options['title']
        self.fps = options['fps']
            
    def init_pygame(self):
        pygame.init()
        if self.show_title_bar:
            display_flags = pygame.DOUBLEBUF | pygame.OPENGL
        else:
            display_flags =  pygame.NOFRAME | pygame.OPENGL | pygame.DOUBLEBUF
        pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1) 
        pygame.display.gl_set_attribute( pygame.GL_MULTISAMPLESAMPLES, 4)
        pygame.display.gl_set_attribute( pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        self.screen = pygame.display.set_mode( self.display, display_flags )
        pygame.display.set_caption(self.title)     
        self.running = True
        self.clock = pygame.time.Clock()
        
    def init_opengl(self):
        gluPerspective(45, (self.display[0] / self.display[1]), 0.1, 50.0)
        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LESS)
        glDepthRange(0.0, 1.0)
        
    def init_objects(self):
        for object in self._objects:
            object.input_axes = self.input_manager.input_axes
            object.start()
            
    def update(self):
        delta_time = self.clock.tick(self.options['fps']) / 1000
        self.input_manager.update(delta_time)
        
        for object in self._objects:
            object.delta_time = delta_time
            object.update()
            
    def run(self):
        self.init_pygame()
        self.init_opengl()
        self.init_objects()
        
        while True:
    
            if self.input_manager.quit == True:
                pygame.quit()
                sys.exit()
                
            self.update()
            