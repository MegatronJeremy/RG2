package opengl4.common.texture;

import com.jogamp.opengl.GL4;
import opengl4.Utilities;
import java.nio.IntBuffer;

public class Texture {
	private int id;
	
	public Texture ( GL4 gl, Class scope, String textureFilePath, int internalFormat, int format, int type, boolean generateMipmap ) {
		Utilities.PNG png = Utilities.loadPNG ( scope, textureFilePath );
		
		IntBuffer intBuffer = IntBuffer.allocate ( 1 );
		gl.glGenTextures ( 1, intBuffer );
		this.id = intBuffer.get ( 0 );
		
		gl.glBindTexture ( GL4.GL_TEXTURE_2D, this.id );
		
		gl.glTexImage2D (
				GL4.GL_TEXTURE_2D,
				0,
				internalFormat,
				png.getWidth ( ),
				png.getHeight ( ),
				0,
				format,
				type,
				png.getData ( )
		);
		
		if ( generateMipmap ) {
			gl.glGenerateMipmap ( GL4.GL_TEXTURE_2D );
		}
	}
	
	public Texture ( GL4 gl, Class scope, String textureFilePath, boolean generateMipmap ) {
		this ( gl, scope, textureFilePath, GL4.GL_RGB, GL4.GL_RGBA, GL4.GL_UNSIGNED_BYTE, generateMipmap );
	}
	
	public Texture bind ( GL4 gl, int textureUnit ) {
		gl.glActiveTexture ( GL4.GL_TEXTURE0 + textureUnit );
		gl.glBindTexture ( GL4.GL_TEXTURE_2D, this.id );
		return this;
	}
	
	public Texture bind ( GL4 gl ) {
		return this.bind ( gl, 0 );
	}
	
	public Texture setParameter ( GL4 gl, int parameterName, int parameterValue ) {
		gl.glTexParameteri ( GL4.GL_TEXTURE_2D, parameterName, parameterValue );
		return this;
	}
	
	public void destroy ( GL4 gl ) {
		IntBuffer intBuffer = IntBuffer.allocate ( 1 );
		intBuffer.put ( this.id );
		intBuffer.rewind ( );
		gl.glDeleteTextures ( 1, intBuffer );
	}
}
