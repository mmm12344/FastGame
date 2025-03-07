import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
import copy as cpy


# assignment Computer Graphics
# Author: Mario Morcos
# ID: 211004852


class ArtLine:
    def __init__(self,  start=0, colors_in_rgb=[]):
        self.coord_colors = []
        self.start = start
        if len(colors_in_rgb) != 0:
            self.add_colors(colors_in_rgb)
        
    def add_offset(self, offset):
        for coord_color in self.coord_colors:
            coord_color[0][1] += offset
            
    def add_color(self, color_in_rgb):
        if len(self.coord_colors) != 0:
            self.coord_colors.append([[0, self.coord_colors[-1][0][1]-1], color_in_rgb])
        else:
            self.coord_colors.append([[0, self.start], color_in_rgb])
            
    def add_colors(self, colors_in_rgb):
        for color in colors_in_rgb:
            self.add_color(color)
            
    def draw(self, point_size):
        i = 0
        for coord_color in self.coord_colors:
            glPointSize(point_size)
            glColor3f(*coord_color[1])
            glBegin(GL_POINTS)
            glVertex2f(*coord_color[0])
            glEnd()
            i += 1
        
    def copy(self):
        return cpy.deepcopy(self)
            

class SymetricPixelArt:
    def __init__(self, art_lines):
        self.art_lines_right_half = art_lines
        self.art_lines_left_half = []
        
        self.add_x_coords()
        self.mirror_art()
        
    def add_x_coords(self):
        i = 0
        for art_line in self.art_lines_right_half:
            for coord_color in art_line.coord_colors:
                coord_color[0][0] = i
            i += 1
    
    def mirror_art(self):
        for art_line in reversed(self.art_lines_right_half):
            art_line_left = art_line.copy()
            for coord_color in art_line_left.coord_colors:
                coord_color[0][0] = -coord_color[0][0]
            self.art_lines_left_half.append(art_line_left)
            
    def add_offset(self, offset):
        for art_line in self.art_lines_left_half:
            art_line.add_offset(offset)
        for art_line in self.art_lines_right_half:
            art_line.add_offset(offset)
            
    def draw(self, point_size):
        for art_line in self.art_lines_left_half:
            art_line.draw(point_size)
        for art_line in self.art_lines_right_half:
            art_line.draw(point_size)

def main():
    b = [0.12, 0.12, 0.12]
    r = [0.68, 0.2, 0.2]
    w = [0.767, 0.776, 0.76]
    y = [0.835, 0.627, 0.49]
    
    line1_arr = [b,r,w,w,b,b,b,y,y,y,y,y,b,b,y,b]
    line2_arr = [b,r,r,w,b,b,b,w,b,b,y,y,b,b,y,b]
    line3_arr = [b,r,r,b,b,b,w,w,w,y,b,b,b,y,b]
    line4_arr = [b,r,r,r,b,b,b,y,y,y,b,b,y,b]
    line5_arr = [b,r,r,r,b,b,y,y,b,y,y,b]
    line6_arr = [b,r,r,r,r,b,b,b,b,b]
    line7_arr = [b,b,b,b,b,y,y,b]
    line8_arr = [b,b]
    
    line1 = ArtLine(0, line1_arr)
    line2 = ArtLine(0, line2_arr)
    line3 = ArtLine(-1, line3_arr)
    line4 = ArtLine(-1, line4_arr)
    line5 = ArtLine(-2, line5_arr)
    line6 = ArtLine(-3, line6_arr)
    line7 = ArtLine(-4, line7_arr)
    line8 = ArtLine(-9, line8_arr)
    
    lines = [line1, line2, line3, line4, line5, line6, line7, line8]
    
    mario_pixel_art = SymetricPixelArt(lines)
    mario_pixel_art.add_offset(8)
    
    pg.init()
    display = (500, 500)
    pg.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluOrtho2D(-10, 10, -10, 10)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return
        glClear(GL_COLOR_BUFFER_BIT)
        
        mario_pixel_art.draw(25)
        
        pg.display.flip()
        pg.time.wait(10)

if __name__ == '__main__':
    main()
