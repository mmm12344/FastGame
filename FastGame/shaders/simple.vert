#version 330 core
layout(location = 0) in vec3 a_vertex_position;
layout(location = 1) in vec2 a_texture_coordinate;
layout(location = 2) in vec3 a_vertex_normal;



uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

uniform vec2 texture_repeat;

uniform bool use_skybox=false;

out vec2 tex_coord;
out vec3 frag_normal;
out vec3 frag_position;


void main(){
    vec4 world_pos = model * vec4(a_vertex_position, 1.0);
    frag_position = world_pos.xyz;
    
    gl_Position = projection * view * world_pos;
    
    tex_coord = vec2(a_texture_coordinate[0] * texture_repeat[0], a_texture_coordinate[1] * texture_repeat[1]);
    frag_normal = mat3(transpose(inverse(model))) * a_vertex_normal;
}
