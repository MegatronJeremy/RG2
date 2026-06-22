package opengl4.common.graphicsObject;

import com.jogamp.common.nio.Buffers;
import com.jogamp.opengl.GL4;
import opengl4.common.camera.Camera;
import opengl4.common.glsl.simpleShaderProgram.SimpleShaderProgram;
import org.joml.Matrix4f;

import java.nio.FloatBuffer;
import java.nio.IntBuffer;

public class Tetrahedron extends GraphicsObject {
	private int vertexArrayObjectId;
	private int vertexBufferObjectId;
	private int colorBufferObjectId;
	private int elementBufferObjectId;
	
	private float width;
	private float depth;
	private float height;
	
    private SimpleShaderProgram simpleShaderProgram;
    
	public Tetrahedron ( SimpleShaderProgram simpleShaderProgram, float width, float depth, float height ) {
        super ( simpleShaderProgram );
        
	    this.width  = width;
	    this.depth  = depth;
	    this.height = height;
        
        this.simpleShaderProgram = simpleShaderProgram;
	}
	
	public Tetrahedron ( float width, float depth, float height ) {
		this ( new SimpleShaderProgram ( ), width, depth, height );
	}
	
	@Override
	protected void initializeInternal ( GL4 gl ) {
		IntBuffer intBuffer = IntBuffer.allocate ( 1 );
		gl.glGenVertexArrays ( 1, intBuffer );
		this.vertexArrayObjectId = intBuffer.get ( 0 );
		
		gl.glBindVertexArray ( this.vertexArrayObjectId );
		
		float vertices[] = {
			-0.5f * this.width, -0.5f * this.height,  0.5f * this.depth,
			 0.5f * this.width, -0.5f * this.height,  0.5f * this.depth,
			 0.0f * this.width,  0.5f * this.height,  0.0f * this.depth,
			 0.0f * this.width,  0.0f * this.height, -0.5f * this.depth
		};
		
		float colors[] = {
            1.0f, 0.0f, 0.0f,
            0.0f, 1.0f, 0.0f,
            0.0f, 0.0f, 1.0f,
            1.0f, 1.0f, 0.0f
        };
		
		int indices[] = {
            0, 1, 2,
            1, 3, 2,
            3, 0, 2,
            0, 3, 1
        };
		
		FloatBuffer vertexBuffer      = Buffers.newDirectFloatBuffer ( vertices, 0 );
		FloatBuffer vertexColorBuffer = Buffers.newDirectFloatBuffer ( colors, 0 );
		IntBuffer   vertexIndexBuffer = Buffers.newDirectIntBuffer ( indices, 0 );
		
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
		gl.glBufferData ( GL4.GL_ARRAY_BUFFER, colors.length * Float.BYTES, vertexColorBuffer, GL4.GL_STATIC_DRAW );
		gl.glEnableVertexAttribArray ( 1 );
		gl.glVertexAttribPointer ( 1, 3, GL4.GL_FLOAT, false, 0, 0 );
		
		intBuffer.rewind ( );
		gl.glGenBuffers ( 1, intBuffer );
		this.elementBufferObjectId = intBuffer.get ( 0 );
		gl.glBindBuffer ( GL4.GL_ELEMENT_ARRAY_BUFFER, this.elementBufferObjectId );
		gl.glBufferData ( GL4.GL_ELEMENT_ARRAY_BUFFER, indices.length * Integer.BYTES, vertexIndexBuffer, GL4.GL_STATIC_DRAW );
	}
    
    @Override
    protected void renderInternal ( GL4 gl, Matrix4f parentTransform, Camera camera ) {
        gl.glBindVertexArray ( this.vertexArrayObjectId );
		
		Matrix4f viewProjection = camera.getViewProjection ( );
		Matrix4f transform = new Matrix4f ( ).mul ( viewProjection ).mul ( parentTransform );
        
        this.simpleShaderProgram.setTransformUniform ( gl, transform );
        
        gl.glDrawElements ( GL4.GL_TRIANGLES, 12, GL4.GL_UNSIGNED_INT, 0 );
        
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
