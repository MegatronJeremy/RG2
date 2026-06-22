#version 430

in vec2 fragmentTextureCoordinates;
out vec4 color;

uniform sampler2D textureUnit;

void main ( ) {
    color = texture ( textureUnit, fragmentTextureCoordinates );
}
