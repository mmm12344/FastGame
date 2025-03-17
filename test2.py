from src.shader import Shader
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader




def create_shader_program():
    vertex_shader = """
    #version 330 core
    layout (location = 0) in vec3 aPos;
    void main()
    {
        gl_Position = vec4(aPos, 1.0);
    }
    """
    
    fragment_shader = """
    #version 330 core
    out vec4 FragColor;
    void main()
    {
        FragColor = vec4(1.0, 0.5, 0.2, 1.0);
    }
    """
    
    shader_program = compileProgram(
        compileShader(vertex_shader, GL_VERTEX_SHADER),
        compileShader(fragment_shader, GL_FRAGMENT_SHADER)
    )
    return shader_program


def initialize_data():
    # shader = Shader('shaders/simple.vert', 'shaders/simple.frag')

    # shader.bind()

    vertex_data = np.array([
        0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
        0.5, -0.5, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0,
        -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 1.0,
        -0.5, 0.5, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0
    ], dtype=np.float32)

    index_data = np.array([
        0, 1, 3,
        1, 2, 3
    ], dtype=np.uint32)

    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    VBO_layout = {
                'stride': 8 * ctypes.sizeof(ctypes.c_float),
                'data': [
                    {
                        'index': 0,
                        'size': 3,
                        'type': GL_FLOAT,
                        'normalized': GL_FALSE,
                        'offset': 0
                    },
                    {
                        'index': 1,
                        'size': 2,
                        'type': GL_FLOAT,
                        'normalized': GL_FALSE,
                        'offset': 3 * ctypes.sizeof(ctypes.c_float)
                    },
                    {
                        'index': 2,
                        'size': 3,
                        'type': GL_FLOAT,
                        'normalized': GL_FALSE,
                        'offset': 5 * ctypes.sizeof(ctypes.c_float)
                    }
                ]
            }
    stride = VBO_layout['stride']
    for i in VBO_layout['data']:
        glVertexAttribPointer(i['index'], i['size'], i['type'], i['normalized'], stride, ctypes.c_void_p(i['offset'] ))
        glEnableVertexAttribArray(i['index'])

    EBO = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

  


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    
    glEnable(GL_DEPTH_TEST)
    
    # Set OpenGL Core Profile
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
    pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
    
    shader_program = create_shader_program()
    
    glUseProgram(shader_program)
    
    initialize_data()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)
        
        pygame.display.flip()
        pygame.time.wait(10)
    
    pygame.quit()

if __name__ == "__main__":
    main()
