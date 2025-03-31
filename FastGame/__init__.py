from .shader import UniformManager

class InternalData:
    def __init__(self):
        self.window_width = 0
        self.window_height = 0
        self.delta_time = 0
        self.input_manager = None
        self.current_shader = None
        
        
internal_data = InternalData()
uniform_manager = UniformManager()


