#version 430 core

in vec3 fragTexCoord;

uniform samplerCube skyboxMap;

out vec4 outColor;

void main() {
    outColor = texture(skyboxMap, fragTexCoord);
}