#version 430 core

layout(location = 0) in vec3 inPosition;

uniform mat4 transform;

out vec3 fragTexCoord;

void main() {
    fragTexCoord = inPosition;

    vec4 position = transform * vec4(inPosition, 1.0);
    gl_Position = position.xyww;
}