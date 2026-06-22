package opengl4.common.glsl.dummyTextureQuadShaderProgram;

import com.jogamp.opengl.GL4;
import opengl4.Utilities;
import opengl4.common.glsl.ShaderProgram;
import opengl4.common.glsl.shaders.FragmentShader;
import opengl4.common.glsl.shaders.VertexShader;

public class DummyTextureQuadShaderProgram extends ShaderProgram {
	public DummyTextureQuadShaderProgram ( String name, FragmentShader fragmentShader ) {
		super (
			name,
			new VertexShader (
				name + ".vertexShader",
				Utilities.readFile ( DummyTextureQuadShaderProgram.class, "vertexShader.glsl" )
			),
			fragmentShader
		);
	}
	
	public DummyTextureQuadShaderProgram ( String name ) {
		this (
				name,
				new FragmentShader (
						name + ".fragmentShader",
						Utilities.readFile ( DummyTextureQuadShaderProgram.class, "fragmentShader.glsl" )
				)
		);
	}
	public DummyTextureQuadShaderProgram ( ) {
		this ( "DummyQuadShaderProgram" );
	}
	
	public void setTextureUnit ( GL4 gl, int textureUnit ) {
		super.setSamplerUniform ( gl, "textureUnit", textureUnit );
	}
}
