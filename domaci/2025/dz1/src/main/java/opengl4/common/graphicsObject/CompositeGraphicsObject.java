package opengl4.common.graphicsObject;

import com.jogamp.opengl.GL4;
import opengl4.common.camera.Camera;
import org.joml.Matrix4f;

public class CompositeGraphicsObject extends AbstractGraphicsObject {
	
	private AbstractGraphicsObject abstractGraphicsObjects[];
	
	public CompositeGraphicsObject ( Matrix4f transform, AbstractGraphicsObject ...graphicsObjects ) {
		super ( transform );
		
		this.abstractGraphicsObjects = new AbstractGraphicsObject[graphicsObjects.length];
		for ( int i = 0; i < this.abstractGraphicsObjects.length; ++i ) {
			this.abstractGraphicsObjects[i] = graphicsObjects[i];
		}
	}
	
	public CompositeGraphicsObject ( AbstractGraphicsObject ...graphicsObjects ) {
		this ( new Matrix4f ( ), graphicsObjects );
	}
	
	@Override
	public void initialize ( GL4 gl ) {
		for ( AbstractGraphicsObject graphicsObject : this.abstractGraphicsObjects ) {
			graphicsObject.initialize ( gl );
		}
	}
	
	@Override
	public void renderImplementation ( GL4 gl, Matrix4f parentTransform, Camera camera ) {
		for ( AbstractGraphicsObject graphicsObject : this.abstractGraphicsObjects ) {
			graphicsObject.render ( gl, parentTransform, camera );
		}
	}
	
	@Override
	public void destroy ( GL4 gl ) {
		for ( AbstractGraphicsObject graphicsObject : this.abstractGraphicsObjects ) {
			graphicsObject.destroy ( gl );
		}
	}
	
	@Override
	public void update ( ) {
		for ( AbstractGraphicsObject graphicsObject : this.abstractGraphicsObjects ) {
			graphicsObject.update ( );
		}
	}
}
