package opengl4.common.glsl.shaders;

import com.jogamp.opengl.GL4;
import opengl4.common.glsl.Shader;

public class ComputeShader extends Shader {
	public ComputeShader ( String shaderName, String[] shaderSource ) {
		super ( shaderName, GL4.GL_COMPUTE_SHADER, shaderSource );
	}
	
	public ComputeShader ( String shaderName, String shaderSource ) {
		super ( shaderName, GL4.GL_COMPUTE_SHADER, shaderSource );
	}
}
