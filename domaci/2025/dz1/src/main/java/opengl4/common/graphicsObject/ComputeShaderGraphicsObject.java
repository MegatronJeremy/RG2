package opengl4.common.graphicsObject;

import com.jogamp.opengl.GL4;
import opengl4.common.camera.Camera;
import opengl4.common.glsl.ShaderProgram;
import org.joml.Matrix4f;

public abstract class ComputeShaderGraphicsObject extends GraphicsObject {
	private int workGroupX;
	private int workGroupY;
	private int workGroupZ;
	
	public ComputeShaderGraphicsObject ( ShaderProgram shaderProgram, int workGroupX, int workGroupY, int workGroupZ ) {
		super ( shaderProgram );
		
		this.workGroupX = workGroupX;
		this.workGroupY = workGroupY;
		this.workGroupZ = workGroupZ;
	}
	
	@Override protected void renderInternal ( GL4 gl, Matrix4f parentTransform, Camera camera ) {
		gl.glDispatchCompute ( this.workGroupX, this.workGroupY, this.workGroupZ );
		gl.glMemoryBarrier ( GL4.GL_SHADER_IMAGE_ACCESS_BARRIER_BIT );
	}
}
