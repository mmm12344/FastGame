import pyglet

class InputAxis:
    def __init__(self, positive_direction=[], negative_direction=[], snap=True, sensitivity=1):
        self.positive_direction = positive_direction
        self.negative_direction = negative_direction
        self.snap = snap
        self.sensitivity = sensitivity
        self.value = 0
        
    def update(self, keys, delta_time):
        target = 0
        if any(key in keys for key in self.positive_direction):
            target = 1
        elif any(key in keys for key in self.negative_direction):
            target = -1
            
        if self.snap == True:
            self.value = target
        else:
            self.value += (target - self.value) * self.sensitivity * delta_time

class InputManager:
    def __init__(self):
        self.quit = False
        self.input_axes = {}
        self.pressed_keys = set()
        self._pyglet_window = None
        
    def attach_window(self, window):
        self._pyglet_window = window
        window.push_handlers(self)
        
    def add_axis(self, axis_name, axis_obj):
        self.input_axes[axis_name] = axis_obj
        
    def remove_axis(self, axis_name):
        del self.input_axes[axis_name]
        
    def on_key_press(self, symbol, modifiers):
        key_name = pyglet.window.key.symbol_string(symbol).lower()
        self.pressed_keys.add(key_name)
        
    def on_key_release(self, symbol, modifiers):
        key_name = pyglet.window.key.symbol_string(symbol).lower()
        if key_name in self.pressed_keys:
            self.pressed_keys.remove(key_name)
                    
    def update(self, delta_time):
        # pyglet handles events automatically, so just update axes
        for axis in self.input_axes.values():
            axis.update(self.pressed_keys, delta_time)
