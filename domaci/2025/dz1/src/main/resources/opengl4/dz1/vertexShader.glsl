#version 430 core

layout(location = 0) in vec3 inPosition;
layout(location = 1) in vec3 inNormal;
layout(location = 2) in vec2 inTexCoord;

uniform mat4 transform;
uniform mat4 model;

out vec3 fragWorldPosition;
out vec3 fragWorldNormal;
out vec2 fragTexCoord;

void main() {
    vec4 worldPosition = model * vec4(inPosition, 1.0);

    fragWorldPosition = worldPosition.xyz;
    fragWorldNormal = normalize(mat3(transpose(inverse(model))) * inNormal);
    fragTexCoord = inTexCoord;

    gl_Position = transform * vec4(inPosition, 1.0);
}