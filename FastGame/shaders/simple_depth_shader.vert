#version 330 core
layout(location = 0) in vec3 a_vertex_position;
layout(location = 1) in vec2 a_texture_coordinate;
layout(location = 2) in vec3 a_vertex_normal;

uniform mat4 model;
uniform mat4 light_projection;
uniform mat4 light_view;



void main()
{
    gl_Position = light_projection * light_view * model * vec4(a_vertex_position, 1.0);
        // gl_Position = vec4(a_vertex_position, 1.0);
}