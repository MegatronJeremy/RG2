#version 430

float vertices[] = {
    -1.0, -1.0, 0.0,
     1.0, -1.0, 0.0,
     1.0,  1.0, 0.0,
    -1.0,  1.0, 0.0,
};

float textureCoordinates[] = {
    0, 0,
    1, 0,
    1, 1,
    0, 1
};

out vec2 fragmentTextureCoordinates;

void main ( ) {
    int vindex = gl_VertexID * 3;
    int tindex = gl_VertexID * 2;

    fragmentTextureCoordinates = vec2 ( textureCoordinates[tindex], textureCoordinates[tindex + 1] );

    gl_Position = vec4 ( vertices[vindex], vertices[vindex + 1], vertices[vindex + 2], 1.0 );
}