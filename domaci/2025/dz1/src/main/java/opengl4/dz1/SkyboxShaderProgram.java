package opengl4.dz1;

import com.jogamp.opengl.GL4;
import opengl4.Utilities;
import opengl4.common.glsl.ShaderProgram;
import opengl4.common.glsl.shaders.FragmentShader;
import opengl4.common.glsl.shaders.VertexShader;
import org.joml.Matrix4f;

public class SkyboxShaderProgram extends ShaderProgram {
    public SkyboxShaderProgram(String name) {
        super(
                name,
                new VertexShader(
                        name + ".vertexShader",
                        Utilities.readFile(SkyboxShaderProgram.class, "skyboxVertexShader.glsl")
                ),
                new FragmentShader(
                        name + ".fragmentShader",
                        Utilities.readFile(SkyboxShaderProgram.class, "skyboxFragmentShader.glsl")
                )
        );
    }

    public SkyboxShaderProgram() {
        this("SkyboxShaderProgram");
    }

    public void setTransformUniform(GL4 gl, Matrix4f transform) {
        int location = super.getUniformLocation("transform");

        float[] data = new float[16];
        transform.get(data);

        gl.glUniformMatrix4fv(location, 1, false, data, 0);
    }

    public void setSkyboxMap(GL4 gl, int textureUnit) {
        super.setSamplerUniform(gl, "skyboxMap", textureUnit);
    }
}