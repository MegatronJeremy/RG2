#version 430

layout ( location = 0 ) in vec3 vertex;
layout ( location = 1 ) in vec2 textureCordinate;

out vec2 fragmentTextureCoordinate;

uniform mat4 transform;

void main() {
    fragmentTextureCoordinate = textureCordinate;

    gl_Position = transform * vec4 ( vertex, 1.0 );
}
