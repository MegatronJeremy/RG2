#version 430 core

in vec3 fragWorldPosition;
in vec3 fragWorldNormal;
in vec3 fragWorldTangent;
in vec2 fragTexCoord;

uniform vec3 cameraPosition;
uniform vec3 lightPosition;
uniform vec3 lightColor;

uniform sampler2D diffuseMap;
uniform sampler2D specularMap;
uniform sampler2D normalMap;

out vec4 outColor;

void main() {
    vec3 albedo = texture(diffuseMap, fragTexCoord).rgb;
    float specMask = texture(specularMap, fragTexCoord).r;

    vec3 baseNormal = normalize(fragWorldNormal);

    // Build the TBN from the interpolated per-vertex tangent (aligned with the UV
    // mapping) instead of an arbitrary up vector, so the normal map's perturbations
    // line up with the planet's surface (east/north) rather than a random direction.
    vec3 T = normalize(fragWorldTangent - baseNormal * dot(baseNormal, fragWorldTangent));
    vec3 B = cross(baseNormal, T);
    mat3 tbn = mat3(T, B, baseNormal);

    vec3 normalTex = texture(normalMap, fragTexCoord).rgb;
    normalTex = normalTex * 2.0 - 1.0;

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