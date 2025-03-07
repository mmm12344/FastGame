from base_objects import EmptyObject
from components import *
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import time, sys
from input_manager import Input


class Renderer:
    
    def render_cuboid(obj):
        base_vertices = [
            [1, 1, -1],  [1, -1, -1],  [-1, -1, -1],  [-1, 1, -1],  
            [1, 1, 1],  [1, -1, 1],  [-1, -1, 1],  [-1, 1, 1]  
        ]
        faces = [
            (0, 1, 2, 3),
            (4, 5, 6, 7),
            (0, 1, 5, 4),
            (2, 3, 7, 6),
            (0, 3, 7, 4),
            (1, 2, 6, 5)
        ]
        for vertix in base_vertices:
            vertix = vertix * list(obj.transform.get_position().values())

            
        
            
    def render_obj(obj):
        if type(obj) != type(EmptyObject):
            raise TypeError('Object type must be or inheret from EmptyObject')
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        if obj.mesh_shape.get_type() == 'cuboid':
            Renderer.render_cuboid(obj)
            
        
        
            





class Game:
    def __init__(self, input_manager=Input(),options={
        'display': (800, 600),
        'show_title_bar': True,
        'title': 'FAST GAME',
        'fps' : 60
    }):
        self.options = options
        self._objects = []
        self.running = False
        self._clock = None
        self.input_manager = input_manager
        
        self.display = options['display']
        self.show_title_bar = options['show_title_bar']
        self.title = options['title']
        self.fps = options['fps']
        
    def add_object(self, obj):
        if type(obj) != type(EmptyObject):
            raise TypeError('Object type must be or inheret from EmptyObject')
        self._objects.append(object)
        
    def set_objects(self, lst):
        for obj in lst:
            self.add_object(obj)
            
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
        glTranslatef(0.0, 0.0, -5)
        glEnable(GL_DEPTH_TEST)
        
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
            