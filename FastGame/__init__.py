from .shader import UniformManager

class InternalData:
    def __init__(self):
        self.window_width = 0
        self.window_height = 0
        self.delta_time = 0
        self.input_manager = None
        self.current_shader = None
        self.current_scene = None
        self.uniform_manager = None
        
internal_data = InternalData()


