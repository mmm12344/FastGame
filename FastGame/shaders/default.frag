#version 330 core

in vec2 tex_coord;
in vec3 frag_normal;
in vec3 frag_position;
in vec3 skyboxTexCoords;

out vec4 FragColor;

struct Material {
    vec4 vertex_color;
    float ambient_light;
    float diffuse_reflection;
    float specular_reflection;
    float shininess;
};

struct DirLight {
    vec3 direction;
    vec3 color;
};

struct PointLight {
    vec3 position;
    vec3 color;
    float constant;
    float linear;
    float quadratic;
};

struct SpotLight {
    vec3 position;
    vec3 direction;
    vec3 color;
    float constant;
    float linear;
    float quadratic;
    float cutOff;
    float outerCutOff;
};

const int POINT_LIGHT_MAX_NUM = 50;
const int SPOT_LIGHT_MAX_NUM = 50;
const int DIRECTIONAL_LIGHT_MAX_NUM = 1;

uniform int directional_light_num;
uniform int point_light_num;
uniform int spot_light_num;

uniform DirLight directional_light[DIRECTIONAL_LIGHT_MAX_NUM];
uniform PointLight point_light[POINT_LIGHT_MAX_NUM];
uniform SpotLight spot_light[SPOT_LIGHT_MAX_NUM];

uniform Material material;
uniform vec3 view_position;
uniform sampler2D diffuse_texture;
uniform bool use_texture;

uniform bool use_skybox;
uniform samplerCube skybox;


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


vec3 CalcDirectionalLight(DirLight light, vec3 normal, vec3 viewDir) {
    vec3 lightDir = normalize(-light.direction);
    vec3 ambient = CalcAmbient(light.color, material.ambient_light);
    vec3 diffuse = CalcDiffuse(normal, lightDir, light.color, material.diffuse_reflection);
    vec3 specular = CalcSpecular(normal, lightDir, viewDir, light.color, material.specular_reflection, material.shininess);
    
    return ambient + diffuse + specular;
}


vec3 CalcPointLight(PointLight light, vec3 normal, vec3 viewDir) {
    vec3 lightDir = normalize(light.position - frag_position);
    float distance = length(light.position - frag_position);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));
    
    vec3 ambient = CalcAmbient(light.color, material.ambient_light) * attenuation;
    vec3 diffuse = CalcDiffuse(normal, lightDir, light.color, material.diffuse_reflection) * attenuation;
    vec3 specular = CalcSpecular(normal, lightDir, viewDir, light.color, material.specular_reflection, material.shininess) * attenuation;
    
    return ambient + diffuse + specular;
}


vec3 CalcSpotLight(SpotLight light, vec3 normal, vec3 viewDir) {
    vec3 lightDir = normalize(light.position - frag_position);
    float theta = dot(lightDir, normalize(-light.direction));
    float epsilon = light.cutOff - light.outerCutOff;
    float intensity = clamp((theta - light.outerCutOff) / epsilon, 0.0, 1.0);
    
    float distance = length(light.position - frag_position);
    float attenuation = 1.0 / (light.constant + light.linear * distance + light.quadratic * (distance * distance));
    
    vec3 ambient = CalcAmbient(light.color, material.ambient_light) * attenuation;
    vec3 diffuse = CalcDiffuse(normal, lightDir, light.color, material.diffuse_reflection) * intensity * attenuation;
    vec3 specular = CalcSpecular(normal, lightDir, viewDir, light.color, material.specular_reflection, material.shininess) * intensity * attenuation;
    
    return ambient + diffuse + specular;
}


void main() {

    if (use_skybox) {
        FragColor = texture(skybox, skyboxTexCoords);
    } else {
        vec3 norm = normalize(frag_normal);
        vec3 viewDir = normalize(view_position - frag_position);
        vec3 lighting = vec3(0.0);
        
        for (int i = 0; i < directional_light_num; i++) {
            lighting += CalcDirectionalLight(directional_light[i], norm, viewDir);
        }
        
        for (int i = 0; i < point_light_num; i++) {
            lighting += CalcPointLight(point_light[i], norm, viewDir);
        }
        
        for (int i = 0; i < spot_light_num; i++) {
            lighting += CalcSpotLight(spot_light[i], norm, viewDir);
        }
        
        vec3 baseColor = use_texture ? texture(diffuse_texture, tex_coord).rgb : material.vertex_color.rgb;
        vec4 frag_color = vec4(baseColor * lighting, material.vertex_color.a);
        float gamma = 1.2;
        FragColor = vec4(pow(frag_color.rgb, vec3(1.0 / gamma)), frag_color.a);
    }
}
