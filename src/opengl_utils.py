from OpenGL import GL





class OpenGLUtils:
    
    def intialize_shader(shader_code, shader_type):
        extension = '#extension GL_ARB_shading_language_420pack: require\n'
        shader_code = '#version 130 \n' + extension + shader_code
        
        shader_ref = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader_ref, shader_code)
        
        GL.glCompileShader(shader_ref)
        
        compile_success = GL.glGetShaderiv(shader_ref, GL.GL_COMPILE_STATUS)
        if not compile_success:
            error_message = GL.glGetShaderInfoLog(shader_ref)
            GL.glDeleteShader(shader_ref)
            error_message = '\n' + error_message.decode('utf-8')
            raise Exception(error_message)
        
        return shader_ref
    
    def intialize_program(vertex_shader_code, fragment_shader_code):
        vertex_shader_ref = OpenGLUtils.intialize_shader(vertex_shader_code, GL.GL_VERTEX_SHADER)
        fragment_shader_ref = OpenGLUtils.intialize_shader(fragment_shader_code, GL.GL_FRAGMENT_SHADER)
        
        program_ref = GL.glCreateProgram()
        
        GL.glAttachShader(program_ref, vertex_shader_ref)
        GL.glAttachShader(program_ref, fragment_shader_ref)
        
        GL.glLinkProgram(program_ref)
        
        link_success = GL.glGetProgramiv(program_ref, GL.GL_LINK_STATUS)
        if not link_success:
            error_message = GL.glGetProgramInfoLog(program_ref)
            GL.glDeleteProgram(program_ref)
            error_message = '\n' + error_message.decode('utf-8')
            raise Exception(error_message)
        
        return program_ref
        