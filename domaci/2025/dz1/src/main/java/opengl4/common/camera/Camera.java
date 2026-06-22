package opengl4.common.camera;

import org.joml.Matrix3f;
import org.joml.Matrix4f;
import org.joml.Vector3f;

public abstract class Camera {
	private Matrix4f view;
	private Matrix4f projection;
	
	protected Camera ( Matrix4f view, Matrix4f projection ) {
		this.view       = view;
		this.projection = projection;
	}
	
	public Matrix4f getView ( ) {
		return this.view;
	}
	
	public Matrix4f getProjection ( ) {
		return this.projection;
	}
	
	public synchronized Matrix4f getViewProjection ( ) {
		return new Matrix4f ( ).mul ( this.projection ).mul ( this.view );
	}
	
	public synchronized Vector3f getWorldPosition ( ) {
		Vector3f position = new Vector3f ( -this.view.m30 ( ), -this.view.m31 ( ), -this.view.m32 ( ) );
		Matrix3f transform = new Matrix3f ( );
		
		this.view.get3x3 ( transform );
		transform.transpose ( );
		
		transform.transform ( position );
		
		return position;
	}
	
	public void update ( ) { }
}

