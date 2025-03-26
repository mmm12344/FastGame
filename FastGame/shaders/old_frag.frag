#version 330 core

in vec3 frag_normal;
in vec3 frag_position;

out vec4 FragColor;

struct Material {
    vec4 vertex_color;
    float ambient_light;
    float diffuse_reflection;
    float specular_reflection;
    float shininess;
};

struct Light {
    vec3 position;
    vec3 color;
};

uniform Material material;
uniform Light light;
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
    vec3 norm = normalize(frag_normal);
    
    vec3 lightDir = normalize(light.position - frag_position);
    
    vec3 ambient = CalcAmbient(light.color, material.ambient_light);
    vec3 diffuse = CalcDiffuse(norm, lightDir, light.color, material.diffuse_reflection);
    
    vec3 viewDir = normalize(view_position - frag_position);
    vec3 specular = CalcSpecular(norm, lightDir, viewDir, light.color, material.specular_reflection, material.shininess);
    
    vec3 lighting = ambient + diffuse + specular;

    vec3 baseColor = material.vertex_color.rgb;
    
    FragColor = vec4(baseColor * lighting, material.vertex_color.a);
}
