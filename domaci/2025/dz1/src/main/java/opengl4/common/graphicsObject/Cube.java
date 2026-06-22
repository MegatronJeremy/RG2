package opengl4.common.graphicsObject;

import com.jogamp.common.nio.Buffers;
import com.jogamp.opengl.GL4;
import opengl4.common.camera.Camera;
import opengl4.common.glsl.simpleShaderProgram.SimpleShaderProgram;
import org.joml.Matrix4f;

import java.nio.FloatBuffer;
import java.nio.IntBuffer;

public class Cube extends GraphicsObject {
	private int vertexArrayObjectId;
	private int vertexBufferObjectId;
	private int colorBufferObjectId;
	private int elementBufferObjectId;
	
	private SimpleShaderProgram simpleShaderProgram;
	
	private float length;
	
	public Cube ( SimpleShaderProgram simpleShaderProgram, Matrix4f transform, float length ) {
		super ( simpleShaderProgram, transform );
		
		this.simpleShaderProgram = simpleShaderProgram;
		
		this.length = length;
	}
	
	@Override
	protected void initializeInternal ( GL4 gl ) {
		IntBuffer intBuffer = IntBuffer.allocate ( 1 );
		gl.glGenVertexArrays ( 1, intBuffer );
		this.vertexArrayObjectId = intBuffer.get ( 0 );
		
		gl.glBindVertexArray ( this.vertexArrayObjectId );
		
		float vertices[] = {
			-0.5f * this.length, -0.5f * this.length, -0.5f * this.length,
			 0.5f * this.length, -0.5f * this.length, -0.5f * this.length,
			 0.5f * this.length,  0.5f * this.length, -0.5f * this.length,
			-0.5f * this.length,  0.5f * this.length, -0.5f * this.length,
			-0.5f * this.length, -0.5f * this.length,  0.5f * this.length,
			 0.5f * this.length, -0.5f * this.length,  0.5f * this.length,
			 0.5f * this.length,  0.5f * this.length,  0.5f * this.length,
			-0.5f * this.length,  0.5f * this.length,  0.5f * this.length,
		};
		
		float colors[] = {
				1.0f, 1.0f, 1.0f,
				0.0f, 0.0f, 1.0f,
				0.0f, 1.0f, 0.0f,
				0.0f, 1.0f, 1.0f,
				1.0f, 0.0f, 0.0f,
				1.0f, 0.0f, 1.0f,
				1.0f, 1.0f, 0.0f,
				1.0f, 1.0f, 1.0f,
		};
		
		int indices[] = {
			0, 1, 2, 3,
			0, 4, 5, 1,
			4, 0, 3, 7,
			3, 2, 6, 7,
			1, 5, 6, 2,
			5, 4, 7, 6,
		};
		
		FloatBuffer verticesBuffer = Buffers.newDirectFloatBuffer ( vertices, 0 );
		FloatBuffer colorsBuffer    = Buffers.newDirectFloatBuffer ( colors, 0 );
		IntBuffer indicesBuffer = Buffers.newDirectIntBuffer ( indices, 0 );
		
		intBuffer.rewind ( );
		gl.glGenBuffers ( 1, intBuffer );
		this.vertexBufferObjectId = intBuffer.get ( 0 );
		gl.glBindBuffer ( GL4.GL_ARRAY_BUFFER, this.vertexBufferObjectId );
		gl.glBufferData ( GL4.GL_ARRAY_BUFFER, vertices.length * Float.BYTES, verticesBuffer, GL4.GL_STATIC_DRAW );
		gl.glEnableVertexAttribArray ( 0 );
		gl.glVertexAttribPointer ( 0, 3, GL4.GL_FLOAT, false, 0, 0 );
		
		intBuffer.rewind ( );
		gl.glGenBuffers ( 1, intBuffer );
		this.colorBufferObjectId = intBuffer.get ( 0 );
		gl.glBindBuffer ( GL4.GL_ARRAY_BUFFER, this.colorBufferObjectId );
		gl.glBufferData ( GL4.GL_ARRAY_BUFFER, colors.length * Float.BYTES, colorsBuffer, GL4.GL_STATIC_DRAW );
		gl.glEnableVertexAttribArray ( 1 );
		gl.glVertexAttribPointer ( 1, 3, GL4.GL_FLOAT, false, 0, 0 );
		
		intBuffer.rewind ( );
		gl.glGenBuffers ( 1, intBuffer );
		this.elementBufferObjectId = intBuffer.get ( 0 );
		gl.glBindBuffer ( GL4.GL_ELEMENT_ARRAY_BUFFER, this.elementBufferObjectId );
		gl.glBufferData ( GL4.GL_ELEMENT_ARRAY_BUFFER, indices.length * Float.BYTES, indicesBuffer, GL4.GL_STATIC_DRAW );
	}
	
	@Override
	protected void renderInternal ( GL4 gl, Matrix4f parentTransform, Camera camera ) {
		gl.glBindVertexArray ( this.vertexArrayObjectId );
		
		Matrix4f transform = new Matrix4f ( ).mul ( camera.getViewProjection ( ) ).mul ( parentTransform );
		
		this.simpleShaderProgram.setTransformUniform ( gl, transform );
		
		gl.glDrawElements ( GL4.GL_QUADS, 24, GL4.GL_UNSIGNED_INT, 0 );
		
		gl.glBindVertexArray ( 0 );
	}
	
	@Override
	protected void destroyInternal ( GL4 gl ) {
		IntBuffer buffer = Buffers.newDirectIntBuffer ( 3 );
		buffer.put ( this.vertexBufferObjectId );
		buffer.put ( this.colorBufferObjectId );
		buffer.put ( this.elementBufferObjectId );
		buffer.rewind ( );
		gl.glDeleteBuffers ( 3, buffer );
		
		buffer.rewind ( );
		buffer.put ( this.vertexArrayObjectId );
		buffer.rewind ( );
		gl.glDeleteVertexArrays ( 1, buffer );
	}
}
