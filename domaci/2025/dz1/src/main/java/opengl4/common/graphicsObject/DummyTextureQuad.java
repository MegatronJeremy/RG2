package opengl4.common.graphicsObject;

import com.jogamp.opengl.GL4;
import opengl4.common.camera.Camera;
import opengl4.common.glsl.dummyTextureQuadShaderProgram.DummyTextureQuadShaderProgram;
import org.joml.Matrix4f;

public class DummyTextureQuad extends GraphicsObject {
	
	private DummyTextureQuadShaderProgram dummyTextureQuadShaderProgram;
	private int                           textureUnit;
	
	public DummyTextureQuad ( DummyTextureQuadShaderProgram dummyTextureQuadShaderProgram, int textureUnit ) {
		super ( dummyTextureQuadShaderProgram );
		
		this.dummyTextureQuadShaderProgram = dummyTextureQuadShaderProgram;
		
		this.textureUnit = textureUnit;
	}
	
	public DummyTextureQuad ( int textureUnit ) {
		this ( new DummyTextureQuadShaderProgram ( ), textureUnit );
	}
	
	@Override protected void initializeInternal ( GL4 gl ) { }
	
	@Override protected void renderInternal ( GL4 gl, Matrix4f parentTransform, Camera camera ) {
		this.dummyTextureQuadShaderProgram.setTextureUnit ( gl, this.textureUnit );
		gl.glDrawArrays ( GL4.GL_QUADS, 0, 4 );
	}
	
	@Override protected void destroyInternal ( GL4 gl ) { }
}
