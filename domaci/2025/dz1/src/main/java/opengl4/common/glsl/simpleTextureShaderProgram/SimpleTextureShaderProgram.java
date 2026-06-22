package opengl4.common.glsl.simpleTextureShaderProgram;

import com.jogamp.opengl.GL4;
import opengl4.Utilities;
import opengl4.common.glsl.ShaderProgram;
import opengl4.common.glsl.shaders.FragmentShader;
import opengl4.common.glsl.shaders.VertexShader;
import org.joml.Matrix4f;

public class SimpleTextureShaderProgram extends ShaderProgram {
	public SimpleTextureShaderProgram ( String name ) {
		super (
			name,
			new VertexShader (
				name + ".vertexShader",
				Utilities.readFile ( SimpleTextureShaderProgram.class, "vertexShader.glsl" )
			),
			new FragmentShader (
					name + ".fragmentShader",
					Utilities.readFile ( SimpleTextureShaderProgram.class, "fragmentShader.glsl" )
			)
		);
	}
	
	public SimpleTextureShaderProgram ( ) {
		this ( "SimpleTextureShaderProgram" );
	}
	
	public void setTransform ( GL4 gl, Matrix4f transform ) {
		int location = super.getUniformLocation ( "transform" );
		
		float data[] = new float[16];
		transform.get ( data );
		
		gl.glUniformMatrix4fv ( location, 1, false, data, 0 );
	}
	
	public void setTextureUnit ( GL4 gl, int textureUnit ) {
		super.setSamplerUniform ( gl, "textureUnit", textureUnit );
	}
}
