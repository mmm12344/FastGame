
#version 330 core


in vec2 texture_coordinate;
in vec3 frag_normal;
in vec3 frag_position;


out vec4 final_color;


uniform vec4 vertex_color;
uniform float ambient_light;
uniform float diffuse_reflection;
uniform float specular_reflection;
uniform sampler2D u_texture;
uniform vec3 lightPosition;
uniform vec3 lightColor;
uniform vec3 viewPosition;


void main(){
    vec4 texColor = texture(u_texture, texture_coordinate);
    vec3 norm = normalize(frag_normal);
    vec3 lightDir = normalize(lightPosition - frag_position);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 ambient = ambient_light * lightColor;
    vec3 diffuse = diffuse_reflection * diff * lightColor;
    vec3 viewDir = normalize(viewPosition - frag_position);
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32.0);
    vec3 specular = specular_reflection * spec * lightColor;
    vec3 lighting = ambient + diffuse + specular;
    vec3 baseColor = texColor.rgb * vertex_color.rgb;
    final_color = vec4(baseColor * lighting, texColor.a * vertex_color.a);
}
