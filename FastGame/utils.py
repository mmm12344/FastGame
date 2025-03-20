from OpenGL.GL import *
from OpenGL.GLU import *

class Color:
    def __init__(self, color_in_hex=None, color_in_rgb=None):
        if color_in_hex is not None:
            self.color_in_hex = color_in_hex
        elif color_in_rgb is not None:
            self.color_in_rgb = color_in_rgb
        else:
            self.color_in_rgb = (255, 255, 255)
    
    @property
    def color_in_hex(self):
        return self._color_in_hex
    
    @color_in_hex.setter
    def color_in_hex(self, value):
        if value.startswith('#'):
            value = value[1:]
        self._color_in_hex = value.upper()
        self._color_in_rgb = self.hex_to_rgb(self._color_in_hex)
        
    @property
    def color_in_rgb(self):
        return self._color_in_rgb
    
    @color_in_rgb.setter
    def color_in_rgb(self, value):
        self._color_in_rgb = self.normalize_rgb(value)
        self._color_in_hex = self.rgb_to_hex(self._color_in_rgb)
        
    def normalize_rgb(self, rgb):
        if max(rgb) > 1:
            return (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
        return rgb
        
    def hex_to_rgb(self, hex_value):
        return tuple(int(hex_value[i:i+2], 16) / 255.0 for i in (0, 2, 4))
    
    def rgb_to_hex(self, rgb):
        return "{:02X}{:02X}{:02X}".format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    
    def __str__(self):
        return "Color(rgb: {}, hex: {})".format(self.color_in_rgb, self.color_in_hex)

    
    
def check_gl_error():
    error = glGetError()
    while error != GL_NO_ERROR:
        print("OpenGL Error:", gluErrorString(error).decode('utf-8'))
        error = glGetError()