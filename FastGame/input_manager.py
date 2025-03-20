import pygame

class InputAxis:
    def __init__(self, positive_direction=[], negative_direction=[], snap=False, sensitivity=0.7):
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
        
    def add_axis(self, axis_name, axis_obj):
        self.input_axes[axis_name] = axis_obj
        
    def remove_axis(self, axis_name):
        del self.input_axes[axis_name]
        
    def update(self, delta_time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
                return
            elif event.type == pygame.KEYDOWN:
                self.pressed_keys.add(pygame.key.name(event.key))
            elif event.type == pygame.KEYUP:
                key_name = pygame.key.name(event.key)
                if key_name in self.pressed_keys:
                    self.pressed_keys.remove(key_name)
                    
        for axis in self.input_axes.values():
            axis.update(self.pressed_keys, delta_time)
                