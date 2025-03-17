#version 330 core

in vec2 texture_coordinate;
in vec3 frag_normal;
in vec3 frag_position;

out vec4 FragColor;

struct Material {
    vec4 vertex_color;
    float ambient_light;
    float diffuse_reflection;
    float specular_reflection;
};

struct Light {
    vec3 position;
    vec3 color;
};

uniform Material material;
uniform Light light;
uniform sampler2D u_texture;
uniform vec3 view_position;

vec3 CalcAmbient(vec3 lightColor, float ambientIntensity) {
    return ambientIntensity * lightColor;
}

vec3 CalcDiffuse(vec3 normal, vec3 lightDir, vec3 lightColor, float diffuseCoeff) {
    float diff = max(dot(normal, lightDir), 0.0);
    return diffuseCoeff * diff * lightColor;
}

vec3 CalcSpecular(vec3 normal, vec3 lightDir, vec3 viewDir, vec3 lightColor, float specularCoeff, float shininess) {
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    return specularCoeff * spec * lightColor;
}

void main() {
    vec4 texColor = texture(u_texture, texture_coordinate);
    vec3 norm = normalize(frag_normal);
    vec3 lightDir = normalize(light.position - frag_position);
    
    vec3 ambient = CalcAmbient(light.color, material.ambient_light);
    vec3 diffuse = CalcDiffuse(norm, lightDir, light.color, material.diffuse_reflection);
    
    vec3 viewDir = normalize(view_position - frag_position);
    vec3 specular = CalcSpecular(norm, lightDir, viewDir, light.color, material.specular_reflection, 32.0);
    
    vec3 lighting = ambient + diffuse + specular;
    // vec3 baseColor = texColor.rgb * material.vertex_color.rgb;
    vec3 baseColor = texColor.rgb * material.vertex_color.rgb;
    // FragColor = vec4(baseColor * lighting, texColor.a * material.vertex_color.a);
    FragColor = vec4(1.0, 1.0, 1.0, 1.0); 
    // FragColor = vec4(material.vertex_color.rgb, 1.0) ;
}
