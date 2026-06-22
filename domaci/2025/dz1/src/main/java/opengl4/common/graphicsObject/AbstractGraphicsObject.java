package opengl4.common.graphicsObject;

import com.jogamp.opengl.GL4;
import opengl4.common.camera.Camera;
import org.joml.Matrix4f;

public abstract  class AbstractGraphicsObject {
	private Matrix4f transform;
	
	public AbstractGraphicsObject ( Matrix4f transform ) {
		this.transform = transform;
	}
	
	public abstract void initialize ( GL4 gl );
	
	public abstract void renderImplementation ( GL4 gl, Matrix4f parentTransform, Camera camera );
	
	public void render ( GL4 gl, Matrix4f parentTransform, Camera camera ) {
		Matrix4f transform = new Matrix4f ( ).mul ( parentTransform ).mul ( this.transform );
		this.renderImplementation ( gl, transform, camera );
	}
	
	public abstract void destroy ( GL4 gl );
	
	public abstract void update ( );
	
	public Matrix4f getTransform ( ) {
		return this.transform;
	}
}
