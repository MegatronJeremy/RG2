#version 430 core

in vec3 fragWorldPosition;
in vec3 fragWorldNormal;
in vec2 fragTexCoord;

uniform vec3 cameraPosition;
uniform vec3 lightPosition;
uniform vec3 lightColor;

uniform sampler2D diffuseMap;
uniform sampler2D specularMap;
uniform sampler2D normalMap;

out vec4 outColor;

mat3 buildTBN(vec3 N) {
    vec3 up = abs(N.y) < 0.999 ? vec3(0.0, 1.0, 0.0) : vec3(1.0, 0.0, 0.0);
    vec3 T = normalize(cross(up, N));
    vec3 B = normalize(cross(N, T));
    return mat3(T, B, N);
}

void main() {
    vec3 albedo = texture(diffuseMap, fragTexCoord).rgb;
    float specMask = texture(specularMap, fragTexCoord).r;

    vec3 baseNormal = normalize(fragWorldNormal);

    vec3 normalTex = texture(normalMap, fragTexCoord).rgb;
    normalTex = normalTex * 2.0 - 1.0;

    mat3 tbn = buildTBN(baseNormal);
    vec3 N = normalize(tbn * normalTex);

    vec3 L = normalize(lightPosition - fragWorldPosition);
    vec3 V = normalize(cameraPosition - fragWorldPosition);
    vec3 R = reflect(-L, N);

    float ambientStrength = 0.15;
    float diffuseStrength = max(dot(N, L), 0.0);
    float shininess = 64.0;
    float specularStrength = 0.8;

    vec3 ambient = ambientStrength * albedo;
    vec3 diffuse = diffuseStrength * albedo * lightColor;

    float specularFactor = pow(max(dot(V, R), 0.0), shininess);
    vec3 specular = specularStrength * specMask * specularFactor * lightColor;

    vec3 color = ambient + diffuse + specular;
    outColor = vec4(color, 1.0);
}