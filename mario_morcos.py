import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

pygame.init()
display = (800, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
gluOrtho2D(0, display[0], 0, display[1])
glClearColor(0.0, 0.0, 0.0, 1.0)

def draw_line(x1, y1, x2, y2, color):
    glBegin(GL_LINES)
    glColor3f(*color)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

def fractal_tree(x, y, angle, length, depth):
    if depth == 0:
        return
    x2 = x + math.cos(math.radians(angle)) * length
    y2 = y + math.sin(math.radians(angle)) * length
    draw_line(x, y, x2, y2, (0.3, 0.8, 0.3))
    fractal_tree(x2, y2, angle - 20, length * 0.7, depth - 1)
    fractal_tree(x2, y2, angle + 20, length * 0.7, depth - 1)
    

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    fractal_tree(400, 150, 90, 80, 7)
    pygame.display.flip()
    pygame.time.wait(30)
pygame.quit()