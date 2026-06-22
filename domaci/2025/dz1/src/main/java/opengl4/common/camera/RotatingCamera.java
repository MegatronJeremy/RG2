package opengl4.common.camera;

import org.joml.Matrix4f;

public class RotatingCamera extends Camera {
	private static Matrix4f getProjectionMatrix ( float zFar ) {
		return new Matrix4f ( ).perspective ( ( float ) Math.toRadians ( 45.0 ), 1.0f, 0.1f, zFar );
	}
	
	private float z;
	private float xAngle;
	
	public RotatingCamera ( float z, float xAngle, float zFar ) {
		super (
			new Matrix4f ( ),
			RotatingCamera.getProjectionMatrix ( zFar )
		);
		
		this.z      = z;
		this.xAngle = xAngle;
	}
	
	public RotatingCamera ( ) {
		this ( -2.0f, 0, 5.0f );
	}
	
	@Override
	public synchronized void update ( ) {
		double angle = ( System.currentTimeMillis ( ) % 3000 ) * 360.0 / 3000.0;
		super.getView ( ).identity ( )
		    .translate ( 0, 0, this.z )
		    .rotate ( ( float ) Math.toRadians ( this.xAngle ), 1, 0, 0 )
		    .rotate ( ( float ) Math.toRadians ( angle ), 0, 1, 0 );
	}
}
