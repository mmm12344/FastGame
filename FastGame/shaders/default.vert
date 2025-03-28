#version 330 core
layout(location = 0) in vec3 a_vertex_position;
layout(location = 1) in vec2 a_texture_coordinate;
layout(location = 2) in vec3 a_vertex_normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform vec2 texture_repeat;
uniform bool use_skybox;

out vec2 tex_coord;
out vec3 frag_normal;
out vec3 frag_position;
out vec3 skyboxTexCoords;

void main() {
    if (use_skybox) {
        mat4 view_no_translation = mat4(mat3(view));
        vec4 skybox_pos = projection * view_no_translation * vec4(a_vertex_position, 1.0);
        gl_Position = skybox_pos.xyww;
        skyboxTexCoords = a_vertex_position;
    } else {
        vec4 world_pos = model * vec4(a_vertex_position, 1.0);
        frag_position = world_pos.xyz;
        gl_Position = projection * view * world_pos;
        tex_coord = a_texture_coordinate * texture_repeat;
        frag_normal = mat3(transpose(inverse(model))) * a_vertex_normal;
    }
}
