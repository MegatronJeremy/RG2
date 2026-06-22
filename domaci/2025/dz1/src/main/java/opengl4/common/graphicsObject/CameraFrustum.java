package opengl4.common.graphicsObject;

import com.jogamp.common.nio.Buffers;
import com.jogamp.opengl.GL4;
import opengl4.common.camera.Camera;
import opengl4.common.glsl.simpleShaderProgram.SimpleShaderProgram;
import org.joml.Matrix4f;

import java.nio.FloatBuffer;
import java.nio.IntBuffer;

public class CameraFrustum extends GraphicsObject {
	private int vertexArrayObjectId;
	private int vertexBufferObjectId;
    private int colorBufferObjectId;
	private int elementBufferObjectId;

    private SimpleShaderProgram simpleShaderProgram;
	
	private Camera myCamera;
 
	public CameraFrustum ( SimpleShaderProgram simpleShaderProgram, Camera myCamera ) {
        super ( simpleShaderProgram );
        
        this.simpleShaderProgram = simpleShaderProgram;
		
        this.myCamera = myCamera;
	}
	
	public CameraFrustum ( Camera camera ) {
		this ( new SimpleShaderProgram ( ), camera );
	}
	
	@Override
	protected void initializeInternal ( GL4 gl ) {
		IntBuffer intBuffer = IntBuffer.allocate ( 1 );
		gl.glGenVertexArrays ( 1, intBuffer );
        this.vertexArrayObjectId = intBuffer.get ( 0 );
		
		gl.glBindVertexArray ( this.vertexArrayObjectId );
		
		float vertices[] = {
			-1.0f, -1.0f, -1.0f,
			-1.0f, -1.0f,  1.0f,
			 1.0f, -1.0f,  1.0f,
			 1.0f, -1.0f, -1.0f,
			-1.0f,  1.0f, -1.0f,
			-1.0f,  1.0f,  1.0f,
			 1.0f,  1.0f,  1.0f,
			 1.0f,  1.0f, -1.0f
		};
        
        float colors[] = {
            1.0f, 1.0f, 1.0f,
            1.0f, 1.0f, 1.0f,
            1.0f, 1.0f, 1.0f,
            1.0f, 1.0f, 1.0f,
            1.0f, 1.0f, 1.0f,
            1.0f, 1.0f, 1.0f,
            1.0f, 1.0f, 1.0f,
            1.0f, 1.0f, 1.0f
        };
		
		int indices[] = {
            0, 1,
            1, 2,
            2, 3,
            3, 0,
            4, 5,
            5, 6,
            6, 7,
            7, 4,
            0, 4,
            1, 5,
            2, 6,
            3, 7
        };
		
		FloatBuffer vertexBuffer  = Buffers.newDirectFloatBuffer ( vertices, 0 );
		FloatBuffer colorBuffer   = Buffers.newDirectFloatBuffer ( colors, 0 );
		IntBuffer   indicesBuffer = Buffers.newDirectIntBuffer ( indices, 0 );
		
		intBuffer.rewind ( );
		gl.glGenBuffers ( 1, intBuffer );
        this.vertexBufferObjectId = intBuffer.get ( 0 );
		gl.glBindBuffer ( GL4.GL_ARRAY_BUFFER, this.vertexBufferObjectId );
		gl.glBufferData ( GL4.GL_ARRAY_BUFFER, vertices.length * Float.BYTES, vertexBuffer, GL4.GL_STATIC_DRAW );
		gl.glEnableVertexAttribArray ( 0 );
		gl.glVertexAttribPointer ( 0, 3, GL4.GL_FLOAT, false, 0, 0 );
        
        intBuffer.rewind ( );
        gl.glGenBuffers ( 1, intBuffer );
        this.colorBufferObjectId = intBuffer.get ( 0 );
        gl.glBindBuffer ( GL4.GL_ARRAY_BUFFER, this.colorBufferObjectId );
        gl.glBufferData ( GL4.GL_ARRAY_BUFFER, colors.length * Float.BYTES, colorBuffer, GL4.GL_STATIC_DRAW );
        gl.glEnableVertexAttribArray ( 1 );
        gl.glVertexAttribPointer ( 1, 3, GL4.GL_FLOAT, false, 0, 0 );
		
		intBuffer.rewind ( );
		gl.glGenBuffers ( 1, intBuffer );
        this.elementBufferObjectId = intBuffer.get ( 0 );
		gl.glBindBuffer ( GL4.GL_ELEMENT_ARRAY_BUFFER, this.elementBufferObjectId );
		gl.glBufferData ( GL4.GL_ELEMENT_ARRAY_BUFFER, indices.length * Integer.BYTES, indicesBuffer, GL4.GL_STATIC_DRAW );
		
		gl.glBindVertexArray ( 0 );
	}
	
	@Override
	protected void renderInternal ( GL4 gl, Matrix4f parentTransform, Camera camera ) {
		gl.glBindVertexArray ( this.vertexArrayObjectId );
		
		Matrix4f inverseTransform = this.myCamera.getViewProjection ( ).invert ( );
		Matrix4f viewProjection = camera.getViewProjection ( );
		Matrix4f transform = new Matrix4f ( ).mul ( viewProjection )
		                                     .mul ( parentTransform )
		                                     .mul ( inverseTransform );
		
		this.simpleShaderProgram.setTransformUniform ( gl, transform );
		
		gl.glDrawElements ( GL4.GL_LINES, 24, GL4.GL_UNSIGNED_INT, 0 );
		
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
