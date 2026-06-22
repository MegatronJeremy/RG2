package opengl4.common.light;

import com.jogamp.opengl.GL4;
import opengl4.common.camera.Camera;
import opengl4.common.graphicsObject.GraphicsObject;
import org.joml.Matrix4f;
import org.joml.Vector3f;

public class Light extends GraphicsObject {
	private static Matrix4f getTransform ( Vector3f position ) {
		Matrix4f transform = new Matrix4f (
				1, 0, 0, 0,
				0, 1, 0, 0,
				0, 0, 1, 0,
				position.x, position.y, position.z, 1
		);
		
		return transform;
	}
	
	private LightingShaderProgram lightingShaderProgram;
	
	public Light ( LightingShaderProgram lightingShaderProgram, Vector3f position ) {
		super ( lightingShaderProgram, Light.getTransform ( position ) );
		
		this.lightingShaderProgram = lightingShaderProgram;
	}
	
	@Override
	protected void initializeInternal ( GL4 gl ) { }
	
	@Override
	protected void renderInternal ( GL4 gl, Matrix4f parentTransform, Camera camera ) {
		Vector3f lightPosition = new Vector3f (
				parentTransform.m30 ( ),
				parentTransform.m31 ( ),
				parentTransform.m32 ( )
		);
		
		this.lightingShaderProgram.setLightPosition ( gl, lightPosition );
	}
	
	@Override
	protected void destroyInternal ( GL4 gl ) { }
}
