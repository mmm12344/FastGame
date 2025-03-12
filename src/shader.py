from OpenGL.GL import *

class Shader:
    def __init__(self, vertex_shader_path, fragement_shader_path):
        self.vertex_shader_path = vertex_shader_path
        self.fragement_shader_path = fragement_shader_path
        self.vertex_shader_source = ''
        self.fragement_shader_source = ''
        self.program_id = None
        
    def set_uniform(self, uniform_name, value):
        if type(value) == int:
            glUniform1i(glGetUniformLocation(self.program_id, uniform_name), value)
        elif type(value) == float:
            glUniform1f(glGetUniformLocation(self.program_id, uniform_name), value)
        elif type(value) == bool:
            glUniform1i(glGetUniformLocation(self.program_id, uniform_name), int(value))

    def read_shader(self, path):
        with open(path, 'r') as f:
            return f.read()
    
    def read_vertex_shader(self):
        self.vertex_shader_source = self.read_shader(self.vertex_shader_path)
        
    def read_fragement_shader(self):
        self.fragement_shader_source = self.read_shader(self.fragement_shader_path)
        
    def compile_shader(self, source, shader_type):
        shader_id = glCreateShader(shader_type)
        glShaderSource(shader_id, source)
        glCompileShader(shader_id)
        
        compile_status = glGetShaderiv(shader_id, GL_COMPILE_STATUS)
        if not compile_status:
            info_log = glGetShaderInfoLog(shader_id)
            shader_type_str = "vertex" if shader_type == GL_VERTEX_SHADER else "fragment"
            print(f"ERROR: {shader_type_str} shader compilation failed:\n{info_log.decode()}")
        return shader_id
    
    def compile(self):
        self.read_vertex_shader()
        self.read_fragement_shader()
        
        vertex_shader = self.compile_shader(self.vertex_shader_source, GL_VERTEX_SHADER)
        fragment_shader = self.compile_shader(self.fragement_shader_source, GL_FRAGMENT_SHADER)
        
        self.program_id = glCreateProgram()
        glAttachShader(self.program_id, vertex_shader)
        glAttachShader(self.program_id, fragment_shader)
        glLinkProgram(self.program_id)
        
        link_status = glGetProgramiv(self.program_id, GL_LINK_STATUS)
        if not link_status:
            info_log = glGetProgramInfoLog(self.program_id)
            print(f"ERROR: Shader program linking failed:\n{info_log.decode()}")
        
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)
    
    def bind(self):
        glUseProgram(self.program_id)
        
    def unbind(self):
        glUseProgram(0)
    
    def delete(self):
        glDeleteProgram(self.program_id)
