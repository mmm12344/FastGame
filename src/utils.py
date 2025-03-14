


class Color:
    def __init__(self, color_in_hex=None, color_in_rgb=None):
        if color_in_hex != None:
            self.color_in_hex = color_in_hex
        elif color_in_rgb != None:
            self.color_in_rgb = color_in_rgb
    
    @property
    def color_in_hex(self):
        return self._color_in_hex
    
    @color_in_hex.setter
    def color_in_hex(self, value):
        self._color_in_hex = value
        self._color_in_rgb = self.hex_to_rgb(value)
        
    @property
    def color_in_rgb(self):
        return self._color_in_rgb
    
    @color_in_rgb.setter
    def color_in_rgb(self, value):
        self._color_in_rgb = self.normalize_rgb(value)
        self._color_in_hex = self.rgb_to_hex(value)
        
    def normalize_rgb(self, rgb):
        return (rgb[0]/255, rgb[1]/255, rgb[2]/255)
        
    def hex_to_rgb(self, hex):
        return self.normalize_rgb(tuple(int(hex[i:i+2], 16) / 255 for i in (0, 2, 4)))
    
    def rgb_to_hex(rgb):
        return "{:02X}{:02X}{:02X}".format(*rgb)
    
    def __str__(self):
        return self.color_in_rgb