import pyglet
from pyglet import gl
import numpy as np
import sys, time
from . import internal_data
from .scene import Scene
from .input_manager import InputManager
from .shader import UniformManager

class Game:
    def __init__(self, input_manager=None, options=None, multi_windows=None):
        if input_manager is None:
            input_manager = InputManager()
        if options is None:
            options = {
                'display': (800, 600),
                'show_title_bar': True,
                'title': 'FAST GAME',
                'fps': 30
            }
        if not isinstance(input_manager, InputManager):
            raise TypeError('Input manager must be of type Input')
        if not isinstance(options, dict):
            raise TypeError('Options must be of type dict')
        self._scene = None
        self.options = options
        self.running = False
        self.input_manager = input_manager
        self.display = options['display']
        self.show_title_bar = options['show_title_bar']
        self.title = options['title']
        self.fps = options['fps']
        self.window = None
        self.clock = pyglet.clock.Clock()
        self.multi_windows = multi_windows if multi_windows is not None else []
        if not self.multi_windows:
            self.init_pyglet()
            self.input_manager.attach_window(self.window)
            self.init_opengl()
            self.init_internal_data()
        
            
        else:
            self.windows = []
            for win_opts in self.multi_windows:
                win_input = win_opts.get('input_manager', InputManager())
                win_options = win_opts.get('options', options)
                scene_factory = win_opts.get('scene_factory', None)
                config = gl.Config(double_buffer=True, depth_size=24, sample_buffers=1, samples=4, major_version=3, minor_version=3)
                win_window = pyglet.window.Window(
                    width=win_options['display'][0],
                    height=win_options['display'][1],
                    caption=win_options['title'],
                    config=config,
                    resizable=False,
                    visible=True
                )
                win_window.set_vsync(True)
                win_input.attach_window(win_window)
         
                internal_data.window_width = win_options['display'][0]
                internal_data.window_height = win_options['display'][1]
            
             
                self.init_opengl()
        
                win_window.switch_to()
                
                if scene_factory:
                    win_scene = scene_factory()
                else:
                    win_scene = win_opts.get('scene', None)
                if win_scene is not None:
                    win_scene.start()
              
                win_uniform_manager = UniformManager()
                self.windows.append({'window': win_window, 'input_manager': win_input, 'scene': win_scene, 'options': win_options, 'uniform_manager': win_uniform_manager})

    @property
    def scene(self):
        return self._scene
    @scene.setter
    def scene(self, value):
        if not isinstance(value, Scene):
            raise TypeError('Scene must be of type Scene')
        self._scene = value
        self.init_scene()

    def init_pyglet(self):
        config = gl.Config(double_buffer=True, depth_size=24, sample_buffers=1, samples=4, major_version=3, minor_version=3)
        self.window = pyglet.window.Window(
            width=self.display[0],
            height=self.display[1],
            caption=self.title,
            config=config,
            resizable=False,
            visible=True
        )
        self.window.set_vsync(True)
        @self.window.event
        def on_close():
            self.running = False
            self.window.close()
            sys.exit()

    def init_opengl(self):
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glCullFace(gl.GL_FRONT)
        gl.glFrontFace(gl.GL_CW)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glDepthMask(gl.GL_TRUE)
        gl.glDepthFunc(gl.GL_LESS)
        gl.glDepthRange(0.0, 1.0)
        gl.glViewport(0, 0, self.display[0], self.display[1])

    def init_scene(self):
        self.scene.start()
        internal_data.current_scene = self.scene

    def init_internal_data(self):
        internal_data.delta_time = 0
        internal_data.window_width = self.display[0]
        internal_data.window_height = self.display[1]
        internal_data.input_manager = self.input_manager
        internal_data.current_scene = self.scene
        internal_data.uniform_manager = UniformManager()

    def update_internal_data(self, dt):
        internal_data.delta_time = dt
        internal_data.window_width = self.display[0]
        internal_data.window_height = self.display[1]

    def update(self, dt):
        self.update_internal_data(dt)
        self.input_manager.update(dt)
        self.scene.update()

    def render(self):
        self.scene.render()

    def run(self):
        if not self.multi_windows:
            self.running = True
            last_time = time.time()
            def update_frame(dt):
                if not self.running:
                    pyglet.app.exit()
                    return
                now = time.time()
                delta = now - update_frame.last_time
                update_frame.last_time = now
                self.update(delta)
                gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
                self.render()
            update_frame.last_time = time.time()
            pyglet.clock.schedule_interval(update_frame, 1.0 / self.fps)
            pyglet.app.run()
        else:
            self.running = True
            last_times = [time.time() for _ in self.windows]
            def make_update_frame(idx):
                def update_frame(dt):
                    if not self.running:
                        pyglet.app.exit()
                        return
                    now = time.time()
                    delta = now - last_times[idx]
                    last_times[idx] = now
                    win = self.windows[idx]
              
                    win['window'].switch_to()

                    internal_data.current_scene = win['scene']
                    internal_data.input_manager = win['input_manager']
                    internal_data.delta_time = delta
    
                    internal_data.uniform_manager = win.get('uniform_manager', None)
                    win['input_manager'].update(delta)
                    if win['scene']:
                        win['scene'].update()
                    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
                    if win['scene']:
                        win['scene'].render()
                return update_frame
            for idx, win in enumerate(self.windows):
                pyglet.clock.schedule_interval(make_update_frame(idx), 1.0 / win['options']['fps'])
            pyglet.app.run()
