import pygame

class InputAxisBase:
    def __init__(self, positive_direction=[], negative_direction=[], snap=False, sensitivity=0.5):
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
        
        
        
        
            

class Input:
    def __init__(self, input_axes = {}):
        self.quit = False
        self.input_axes = input_axes
        
    def add_axis(self, axis_name, axis_obj):
        self.input_axes[axis_name] = axis_obj
        
    def remove_axis(self, axis_name):
        del self.input_axes[axis_name]
        
    def update(self, delta_time):
        pressed_keys = set()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
                return
            elif event.type == pygame.KEYDOWN:
                pressed_keys.add(pygame.key.name(event.key))
            elif event.type == pygame.KEYUP:
                key_name = pygame.key.name(event.key)
                if key_name in pressed_keys:
                    pressed_keys.remove(key_name)
                    
        for axis in self.input_axes.values():
            axis.update(pressed_keys, delta_time)
                