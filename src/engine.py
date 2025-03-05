from base_objects import EmptyObject
from components import *
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import numpy as np
import time

class Game:
    def __init__(self, options={
        'display': (800, 600),
        
    }):
        self.options = options
        self._objects = []
        
    def add_object(self, obj):
        if type(object) != type(EmptyObject):
            raise TypeError('Object type must be or inheret from EmptyObject')
        self._objects.append(object)
        
    def set_objects(self, lst):
        for obj in lst:
            self.add_object(obj)
            
    def init_pygame(self):
        pygame.init()
        pygame.display.set_mode(self.options['display'], DOUBLEBUF | OPENGL)
        
    def init_opengl(self):
        display = self.options['display']
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, -5)
        glEnable(GL_DEPTH_TEST)
            
    def run(self):
        self.init_pygame()
        self.init_opengl()
        
        curr_time = time.time()
        while True:
            for obj in self._objects:
                pass