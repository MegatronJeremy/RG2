package opengl4.common.texture;

import com.jogamp.opengl.GL4;
import opengl4.Utilities;

import java.nio.IntBuffer;

public class CubeMap {
	private int id;
	
	public CubeMap ( GL4 gl, Class scope, String right, String left, String top, String bottom, String back, String front ) {
		IntBuffer intBuffer = IntBuffer.allocate ( 1 );
		gl.glGenTextures ( 1, intBuffer );
		this.id = intBuffer.get ( 0 );
		
		gl.glBindTexture ( GL4.GL_TEXTURE_CUBE_MAP, this.id );
		
		String faces[] = {
				right,
				left,
				top,
				bottom,
				back,
				front
		};
		
		for ( int i = 0; i < faces.length; ++i ) {
			Utilities.PNG png = Utilities.loadPNG ( scope, faces[i] );
			gl.glTexImage2D (
					GL4.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
					0,
					GL4.GL_RGB,
					png.getWidth ( ),
					png.getHeight ( ),
					0,
					GL4.GL_RGBA,
					GL4.GL_UNSIGNED_BYTE,
					png.getData ( )
			);
		}
		
		gl.glTexParameteri ( GL4.GL_TEXTURE_CUBE_MAP, GL4.GL_TEXTURE_MIN_FILTER, GL4.GL_LINEAR );
		gl.glTexParameteri ( GL4.GL_TEXTURE_CUBE_MAP, GL4.GL_TEXTURE_MAG_FILTER, GL4.GL_LINEAR );
		gl.glTexParameteri ( GL4.GL_TEXTURE_CUBE_MAP, GL4.GL_TEXTURE_WRAP_S, GL4.GL_CLAMP_TO_EDGE );
		gl.glTexParameteri ( GL4.GL_TEXTURE_CUBE_MAP, GL4.GL_TEXTURE_WRAP_T, GL4.GL_CLAMP_TO_EDGE );
		gl.glTexParameteri ( GL4.GL_TEXTURE_CUBE_MAP, GL4.GL_TEXTURE_WRAP_R, GL4.GL_CLAMP_TO_EDGE );
	}
	
	public CubeMap bind ( GL4 gl, int textureUnit ) {
		gl.glActiveTexture ( GL4.GL_TEXTURE0 + textureUnit );
		gl.glBindTexture ( GL4.GL_TEXTURE_CUBE_MAP, this.id );
		return this;
	}
	
	public CubeMap bind ( GL4 gl ) {
		return this.bind ( gl, 0 );
	}
	
	public CubeMap setParameter ( GL4 gl, int parameterName, int parameterValue ) {
		gl.glTexParameteri ( GL4.GL_TEXTURE_CUBE_MAP, parameterName, parameterValue );
		return this;
	}
	
	public void destroy ( GL4 gl ) {
		IntBuffer intBuffer = IntBuffer.allocate ( 1 );
		intBuffer.put ( this.id );
		intBuffer.rewind ( );
		gl.glDeleteTextures ( 1, intBuffer );
	}
}
