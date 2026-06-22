package opengl4.common.graphicsObject;

import com.jogamp.opengl.GL4;
import opengl4.common.camera.Camera;
import opengl4.common.texture.Texture;
import org.joml.Matrix4f;

public class TextureCompositeGraphicsObject extends CompositeGraphicsObject {
	
	private String textureName;
	private Class scope;
	private Texture texture;
	
	public TextureCompositeGraphicsObject ( String textureName, Class scope, AbstractGraphicsObject...graphicsObjects ) {
		super ( graphicsObjects );
		
		this.textureName = textureName;
		
		this.scope = scope;
	}
	
	@Override public void initialize ( GL4 gl ) {
		super.initialize ( gl );
		
		this.texture = new Texture (
			gl,
			this.scope,
			this.textureName,
			GL4.GL_RGBA,
			GL4.GL_RGBA,
			GL4.GL_UNSIGNED_BYTE,
			true
		);
	}
	
	@Override public void renderImplementation ( GL4 gl, Matrix4f parentTransform, Camera camera ) {
		gl.glActiveTexture ( GL4.GL_TEXTURE0 );
		this.texture.bind ( gl, 0 );
		
		super.renderImplementation ( gl, parentTransform, camera );
	}
}
