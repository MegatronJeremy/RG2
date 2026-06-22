#version 430

out vec4 color;

in vec2 fragmentTextureCoordinate;

uniform sampler2D textureUnit;

void main ( ) {
    color = texture ( textureUnit, fragmentTextureCoordinate );
}
