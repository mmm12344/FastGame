#version 330 core
layout(location = 0) in vec3 a_vertex_position;
layout(location = 1) in vec2 a_texture_coordinate;
layout(location = 2) in vec3 a_vertex_normal;

uniform mat4 model;
uniform mat4 lightSpaceMatrix;


void main()
{
    gl_position = lightSpaceMatrix * model * vec4(a_vertex_position, 1.0);
}