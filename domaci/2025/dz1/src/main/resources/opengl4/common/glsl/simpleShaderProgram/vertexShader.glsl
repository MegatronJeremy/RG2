#version 430

layout ( location = 0 ) in vec3 vertex;
layout ( location = 1 ) in vec3 color;

out vec4 fragmentColor;

uniform mat4 transform;

void main ( ) {
    gl_Position = transform * vec4 ( vertex, 1.0 );
    fragmentColor = vec4 ( color, 1 );
}
