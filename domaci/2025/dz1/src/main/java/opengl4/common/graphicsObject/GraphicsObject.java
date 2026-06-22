package opengl4.common.graphicsObject;

import opengl4.common.camera.Camera;
import opengl4.common.glsl.ShaderProgram;
import com.jogamp.opengl.GL4;
import org.joml.Matrix4f;

public abstract class GraphicsObject extends AbstractGraphicsObject {
	private ShaderProgram shaderProgram;
	
	public GraphicsObject ( ShaderProgram shaderProgram, Matrix4f transform ) {
		super ( transform );
		this.shaderProgram = shaderProgram;
	}
	
	public GraphicsObject ( ShaderProgram shaderProgram ) {
		this ( shaderProgram, new Matrix4f ( ) );
	}
	
	protected abstract void initializeInternal ( GL4 gl );
	
	public void initialize ( GL4 gl ) {
		this.shaderProgram.initialize ( gl );
		
		this.initializeInternal ( gl );
	}
	
	protected abstract void renderInternal ( GL4 gl, Matrix4f parentTransform, Camera camera );
	
	@Override
	public void renderImplementation ( GL4 gl, Matrix4f parentTransform, Camera camera ) {
		this.shaderProgram.activate ( gl );
		this.renderInternal ( gl, parentTransform , camera );
		this.shaderProgram.deactivate ( gl );
	}
	
	protected abstract void destroyInternal ( GL4 gl );
	
	public void destroy ( GL4 gl ) {
		this.shaderProgram.destroy ( gl );
		
		this.destroyInternal ( gl );
	}
	
	public void update ( ) { }
}