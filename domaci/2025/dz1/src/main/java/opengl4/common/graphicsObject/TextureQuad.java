package opengl4.common.graphicsObject;

import com.jogamp.common.nio.Buffers;
import com.jogamp.opengl.GL4;
import opengl4.common.camera.Camera;
import opengl4.common.glsl.simpleTextureShaderProgram.SimpleTextureShaderProgram;
import org.joml.Matrix4f;

import java.nio.FloatBuffer;
import java.nio.IntBuffer;

public class TextureQuad extends GraphicsObject {
	private int vertexArrayObjectId;
	private int vertexBufferObjectId;
	private int textureCoordinateBufferObjectId;
	
	private float width;
	private float height;
	
    private SimpleTextureShaderProgram simpleTextureShaderProgram;
    
	public TextureQuad ( SimpleTextureShaderProgram simpleTextureShaderProgram, Matrix4f transform, float width, float height ) {
        super ( simpleTextureShaderProgram, transform );
        
		this.width      = width;
		this.height     = height;
        
        this.simpleTextureShaderProgram = simpleTextureShaderProgram;
	}
	
	public TextureQuad ( SimpleTextureShaderProgram simpleTextureShaderProgram, float width, float height ) {
		this ( simpleTextureShaderProgram, new Matrix4f ( ), width, height );
	}
	
	@Override
	protected void initializeInternal ( GL4 gl ) {
		IntBuffer intBuffer = IntBuffer.allocate ( 1 );
		gl.glGenVertexArrays ( 1, intBuffer );
		this.vertexArrayObjectId = intBuffer.get ( 0 );
		
		gl.glBindVertexArray ( this.vertexArrayObjectId );
		
		
		float vertices[] = {
			-0.5f * this.width, -0.5f * this.height, 0.0f,
			 0.5f * this.width, -0.5f * this.height, 0.0f,
			 0.5f * this.width,  0.5f * this.height, 0.0f,
			-0.5f * this.width,  0.5f * this.height, 0.0f,
		};
		
		float textureCoordinates[] = {
				0.0f, 0.0f,
				1.0f, 0.0f,
				1.0f, 1.0f,
				0.0f, 1.0f,
		};
		
		FloatBuffer vertexBuffer             = Buffers.newDirectFloatBuffer ( vertices, 0 );
		FloatBuffer textureCoordinatesBuffer = Buffers.newDirectFloatBuffer ( textureCoordinates, 0 );
		
		intBuffer.rewind ( );
		gl.glGenBuffers ( 1, intBuffer );
		this.vertexBufferObjectId = intBuffer.get ( 0 );
		gl.glBindBuffer ( GL4.GL_ARRAY_BUFFER, this.vertexBufferObjectId );
		gl.glBufferData ( GL4.GL_ARRAY_BUFFER, vertices.length * Float.BYTES, vertexBuffer, GL4.GL_STATIC_DRAW );
		gl.glEnableVertexAttribArray ( 0 );
		gl.glVertexAttribPointer ( 0, 3, GL4.GL_FLOAT, false, 0, 0 );
		
		intBuffer.rewind ( );
		gl.glGenBuffers ( 1, intBuffer );
		this.textureCoordinateBufferObjectId = intBuffer.get ( 0 );
		gl.glBindBuffer ( GL4.GL_ARRAY_BUFFER, this.textureCoordinateBufferObjectId );
		gl.glBufferData ( GL4.GL_ARRAY_BUFFER, textureCoordinates.length * Float.BYTES, textureCoordinatesBuffer, GL4.GL_STATIC_DRAW );
		gl.glEnableVertexAttribArray ( 1 );
		gl.glVertexAttribPointer ( 1, 2, GL4.GL_FLOAT, false, 0, 0 );
	}
    
    @Override
    protected void renderInternal ( GL4 gl, Matrix4f parentTransform, Camera camera ) {
        gl.glBindVertexArray ( this.vertexArrayObjectId );
		
		Matrix4f transform = new Matrix4f ( ).mul ( camera.getViewProjection ( ) ).mul ( parentTransform );
		
		this.simpleTextureShaderProgram.setTransform ( gl, transform );
        
        gl.glDrawArrays ( GL4.GL_QUADS, 0, 4 );
		
        gl.glBindVertexArray ( 0 );
    }
    
    
    @Override
	protected void destroyInternal ( GL4 gl ) {
		IntBuffer buffer = Buffers.newDirectIntBuffer ( 2 );
		buffer.put ( this.vertexBufferObjectId );
		buffer.put ( this.textureCoordinateBufferObjectId );
		buffer.rewind ( );
		gl.glDeleteBuffers ( 2, buffer );
		
		buffer.rewind ( );
		buffer.put ( this.vertexArrayObjectId );
		buffer.rewind ( );
		gl.glDeleteVertexArrays ( 1, buffer );
	}
	
}
