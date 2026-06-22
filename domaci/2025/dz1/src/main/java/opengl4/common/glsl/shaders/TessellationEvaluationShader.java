package opengl4.common.glsl.shaders;

import com.jogamp.opengl.GL4;
import opengl4.common.glsl.Shader;

public class TessellationEvaluationShader extends Shader {
	public TessellationEvaluationShader ( String shaderName, String[] shaderSource ) {
		super ( shaderName, GL4.GL_TESS_EVALUATION_SHADER, shaderSource );
	}
	
	public TessellationEvaluationShader ( String shaderName, String shaderSource ) {
		super ( shaderName, GL4.GL_TESS_EVALUATION_SHADER, shaderSource );
	}
}
