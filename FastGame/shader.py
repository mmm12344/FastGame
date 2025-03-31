from OpenGL.GL import *
import numpy as np  
import os
import regex as re


class UniformManager:
    def __init__(self):
        self._list_key_indexes = {}
    
        
    def set(self, uniform:str, value):
        if '[n]' in uniform:
            if uniform.replace('[n]', '') not in self._list_key_indexes:
                index = 0
            else:
                index = self._list_key_indexes[uniform.replace('[n]', '')]
            self._list_key_indexes[uniform.replace('[n]', '')] = index + 1
            uniform = uniform.replace('[n]', f'[{index}]')
            
        else:
            if type(value) == str:
                matched = re.match("num\((.+)\)", value)
                if matched:
                    # print(self._list_key_indexes)
                    value = self._list_key_indexes[matched.group(1)]
            
        self.set_directly(uniform, value)
            
    def set_directly(self, uniform_name, value):
        from . import internal_data
        location = glGetUniformLocation(internal_data.current_shader.program_id, uniform_name)
        if isinstance(value, int):
            glUniform1i(location, value)
        elif isinstance(value, float):
            glUniform1f(location, value)
        elif isinstance(value, bool):
            glUniform1i(location, int(value))
        elif isinstance(value, np.ndarray):
            if value.ndim == 2:
                if value.shape == (2, 2):
                    glUniformMatrix2fv(location, 1, GL_TRUE, value)
                elif value.shape == (3, 3):
                    glUniformMatrix3fv(location, 1, GL_TRUE, value)
                elif value.shape == (4, 4):
                    glUniformMatrix4fv(location, 1, GL_TRUE, value)
                else:
                    raise ValueError("Unsupported matrix shape: " + str(value.shape))
            elif value.ndim == 1:
                if value.shape[0] == 2:
                    glUniform2f(location, *value)
                elif value.shape[0] == 3:
                    glUniform3f(location, *value)
                elif value.shape[0] == 4:
                    glUniform4f(location, *value)
                else:
                    raise ValueError("Unsupported vector length: " + str(value.shape[0]))
            else:
                raise ValueError("Unsupported numpy array dimension: " + str(value.ndim))
        elif isinstance(value, (list, tuple)):
            arr = np.array(value)
            if arr.ndim == 1:
                if arr.shape[0] == 2:
                    glUniform2f(location, *arr)
                elif arr.shape[0] == 3:
                    glUniform3f(location, *arr)
                elif arr.shape[0] == 4:
                    glUniform4f(location, *arr)
                else:
                    raise ValueError("Unsupported vector length: " + str(arr.shape[0]))
            elif arr.ndim == 2:
                if arr.shape == (2, 2):
                    glUniformMatrix2fv(location, 1, GL_FALSE, arr)
                elif arr.shape == (3, 3):
                    glUniformMatrix3fv(location, 1, GL_FALSE, arr)
                elif arr.shape == (4, 4):
                    glUniformMatrix4fv(location, 1, GL_FALSE, arr)
                else:
                    raise ValueError("Unsupported matrix shape: " + str(arr.shape))
        else:
            raise TypeError("Unsupported uniform type: " + str(type(value)))
            
    def clear(self):
        self._list_key_indexes.clear()
            
    def __del__(self):
        self.clear()



class Shader:
    def __init__(self, vertex_shader_path, fragment_shader_path):
        self.vertex_shader_path = os.path.join(os.path.dirname(__file__), vertex_shader_path)
        self.fragement_shader_path = os.path.join(os.path.dirname(__file__), fragment_shader_path)
        self.vertex_shader_source = ''
        self.fragement_shader_source = ''
        self.program_id = None
        self.compile()
        # self.uniforms = UniformManager(self.program_id)
        
    def get_attribute_location(self, attribute_name):
        return glGetAttribLocation(self.program_id, attribute_name)

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
        from . import internal_data
        glUseProgram(self.program_id)
        internal_data.current_shader = self
        
    def unbind(self):
        glUseProgram(0)
    
    def delete(self):
        glDeleteProgram(self.program_id)
        
    
