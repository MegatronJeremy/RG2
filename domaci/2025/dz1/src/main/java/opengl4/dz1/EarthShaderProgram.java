package opengl4.dz1;

import com.jogamp.opengl.GL4;
import opengl4.Utilities;
import opengl4.common.glsl.ShaderProgram;
import opengl4.common.glsl.shaders.FragmentShader;
import opengl4.common.glsl.shaders.VertexShader;
import org.joml.Matrix4f;
import org.joml.Vector3f;

public class EarthShaderProgram extends ShaderProgram {
    public EarthShaderProgram(String name) {
        super(
                name,
                new VertexShader(
                        name + ".vertexShader",
                        Utilities.readFile(EarthShaderProgram.class, "vertexShader.glsl")
                ),
                new FragmentShader(
                        name + ".fragmentShader",
                        Utilities.readFile(EarthShaderProgram.class, "fragmentShader.glsl")
                )
        );
    }

    public EarthShaderProgram() {
        this("EarthShaderProgram");
    }

    public void setTransformUniform(GL4 gl, Matrix4f transform) {
        int location = super.getUniformLocation("transform");

        float[] data = new float[16];
        transform.get(data);

        gl.glUniformMatrix4fv(location, 1, false, data, 0);
    }

    public void setModelUniform(GL4 gl, Matrix4f model) {
        int location = super.getUniformLocation("model");

        float[] data = new float[16];
        model.get(data);

        gl.glUniformMatrix4fv(location, 1, false, data, 0);
    }

    public void setCameraPosition(GL4 gl, Vector3f cameraPosition) {
        int location = super.getUniformLocation("cameraPosition");
        gl.glUniform3f(location, cameraPosition.x, cameraPosition.y, cameraPosition.z);
    }

    public void setLightPosition(GL4 gl, Vector3f lightPosition) {
        int location = super.getUniformLocation("lightPosition");
        gl.glUniform3f(location, lightPosition.x, lightPosition.y, lightPosition.z);
    }

    public void setLightColor(GL4 gl, Vector3f lightColor) {
        int location = super.getUniformLocation("lightColor");
        gl.glUniform3f(location, lightColor.x, lightColor.y, lightColor.z);
    }

    public void setDiffuseMap(GL4 gl, int textureUnit) {
        super.setSamplerUniform(gl, "diffuseMap", textureUnit);
    }

    public void setSpecularMap(GL4 gl, int textureUnit) {
        super.setSamplerUniform(gl, "specularMap", textureUnit);
    }

    public void setNormalMap(GL4 gl, int textureUnit) {
        super.setSamplerUniform(gl, "normalMap", textureUnit);
    }
}