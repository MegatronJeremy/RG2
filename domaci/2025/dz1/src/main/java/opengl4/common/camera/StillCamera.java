package opengl4.common.camera;

import org.joml.Matrix4f;

public class StillCamera extends Camera {
	private static Matrix4f getProjectionMatrix ( ) {
		return new Matrix4f ( ).perspective ( ( float ) Math.toRadians ( 45.0 ), 1.0f, 0.1f, 100.0f );
	}
	
	private static Matrix4f getViewMatrix ( float zInitial, float xAngleInitial, float yAngleInitial ) {
		return new Matrix4f ( ).translate ( 0, 0, zInitial )
		    .rotate ( ( float ) Math.toRadians ( xAngleInitial ), 1, 0, 0 )
		    .rotate ( ( float ) Math.toRadians ( yAngleInitial ), 0, 1, 0 );
	}
	
	public StillCamera ( float zInitial, float xAngleInitial, float yAngleInitial ) {
		super (
			StillCamera.getViewMatrix ( zInitial, xAngleInitial, yAngleInitial ),
			StillCamera.getProjectionMatrix ( )
		);
	}
	
	public StillCamera ( float zInitial ) {
		this ( zInitial, 30, 45 );
	}
	
	public StillCamera ( ) {
		this ( -10.0f, 30, 45 );
	}
}
