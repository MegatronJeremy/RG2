package opengl4.common.glsl.shaders;

import com.jogamp.opengl.GL4;
import opengl4.common.glsl.Shader;

public class GeometryShader extends Shader {
	public GeometryShader ( String shaderName, String[] shaderSource ) {
		super ( shaderName, GL4.GL_GEOMETRY_SHADER, shaderSource );
	}
	
	public GeometryShader ( String shaderName, String shaderSource ) {
		super ( shaderName, GL4.GL_GEOMETRY_SHADER, shaderSource );
	}
}
