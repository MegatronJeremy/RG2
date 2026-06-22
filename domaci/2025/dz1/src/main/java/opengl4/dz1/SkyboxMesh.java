package opengl4.dz1;

import com.jogamp.common.nio.Buffers;
import com.jogamp.opengl.GL4;
import opengl4.Utilities;
import opengl4.common.camera.Camera;
import opengl4.common.graphicsObject.GraphicsObject;
import org.joml.Matrix4f;

import java.nio.FloatBuffer;
import java.nio.IntBuffer;

public class SkyboxMesh extends GraphicsObject {
    private final SkyboxShaderProgram skyboxShaderProgram;

    private int vertexArrayObjectId;
    private int positionBufferObjectId;
    private int cubemapTextureId;

    public SkyboxMesh(SkyboxShaderProgram skyboxShaderProgram) {
        super(skyboxShaderProgram);
        this.skyboxShaderProgram = skyboxShaderProgram;
    }

    @Override
    protected void initializeInternal(GL4 gl) {
        float[] positions = {
                // back
                -1.0f, 1.0f, -1.0f,
                -1.0f, -1.0f, -1.0f,
                1.0f, -1.0f, -1.0f,
                1.0f, -1.0f, -1.0f,
                1.0f, 1.0f, -1.0f,
                -1.0f, 1.0f, -1.0f,

                // left
                -1.0f, -1.0f, 1.0f,
                -1.0f, -1.0f, -1.0f,
                -1.0f, 1.0f, -1.0f,
                -1.0f, 1.0f, -1.0f,
                -1.0f, 1.0f, 1.0f,
                -1.0f, -1.0f, 1.0f,

                // right
                1.0f, -1.0f, -1.0f,
                1.0f, -1.0f, 1.0f,
                1.0f, 1.0f, 1.0f,
                1.0f, 1.0f, 1.0f,
                1.0f, 1.0f, -1.0f,
                1.0f, -1.0f, -1.0f,

                // front
                -1.0f, -1.0f, 1.0f,
                -1.0f, 1.0f, 1.0f,
                1.0f, 1.0f, 1.0f,
                1.0f, 1.0f, 1.0f,
                1.0f, -1.0f, 1.0f,
                -1.0f, -1.0f, 1.0f,

                // top
                -1.0f, 1.0f, -1.0f,
                1.0f, 1.0f, -1.0f,
                1.0f, 1.0f, 1.0f,
                1.0f, 1.0f, 1.0f,
                -1.0f, 1.0f, 1.0f,
                -1.0f, 1.0f, -1.0f,

                // bottom
                -1.0f, -1.0f, -1.0f,
                -1.0f, -1.0f, 1.0f,
                1.0f, -1.0f, -1.0f,
                1.0f, -1.0f, -1.0f,
                -1.0f, -1.0f, 1.0f,
                1.0f, -1.0f, 1.0f
        };

        IntBuffer intBuffer = Buffers.newDirectIntBuffer(1);

        gl.glGenVertexArrays(1, intBuffer);
        this.vertexArrayObjectId = intBuffer.get(0);

        gl.glBindVertexArray(this.vertexArrayObjectId);

        FloatBuffer positionBuffer = Buffers.newDirectFloatBuffer(positions);

        intBuffer.rewind();
        gl.glGenBuffers(1, intBuffer);
        this.positionBufferObjectId = intBuffer.get(0);

        gl.glBindBuffer(GL4.GL_ARRAY_BUFFER, this.positionBufferObjectId);
        gl.glBufferData(
                GL4.GL_ARRAY_BUFFER,
                (long) positions.length * Float.BYTES,
                positionBuffer,
                GL4.GL_STATIC_DRAW
        );

        gl.glEnableVertexAttribArray(0);
        gl.glVertexAttribPointer(0, 3, GL4.GL_FLOAT, false, 0, 0);

        gl.glBindVertexArray(0);
        gl.glBindBuffer(GL4.GL_ARRAY_BUFFER, 0);

        this.cubemapTextureId = loadCubemap(
                gl,
                "skybox/browncloud_rt.jpg", // +X
                "skybox/browncloud_lf.jpg", // -X
                "skybox/browncloud_up.jpg", // +Y
                "skybox/browncloud_dn.jpg", // -Y
                "skybox/browncloud_bk.jpg", // +Z
                "skybox/browncloud_ft.jpg"  // -Z
        );
    }

    @Override
    protected void renderInternal(GL4 gl, Matrix4f parentTransform, Camera camera) {
        gl.glDepthFunc(GL4.GL_LEQUAL);

        Matrix4f view = new Matrix4f(camera.getView());
        view.m30(0.0f);
        view.m31(0.0f);
        view.m32(0.0f);

        Matrix4f transform = new Matrix4f(camera.getProjection()).mul(view);

        this.skyboxShaderProgram.setTransformUniform(gl, transform);

        gl.glActiveTexture(GL4.GL_TEXTURE0);
        gl.glBindTexture(GL4.GL_TEXTURE_CUBE_MAP, this.cubemapTextureId);
        this.skyboxShaderProgram.setSkyboxMap(gl, 0);

        gl.glBindVertexArray(this.vertexArrayObjectId);
        gl.glDrawArrays(GL4.GL_TRIANGLES, 0, 36);
        gl.glBindVertexArray(0);

        gl.glBindTexture(GL4.GL_TEXTURE_CUBE_MAP, 0);
        gl.glDepthFunc(GL4.GL_LESS);
    }

    @Override
    protected void destroyInternal(GL4 gl) {
        IntBuffer buffer = Buffers.newDirectIntBuffer(1);
        buffer.put(this.positionBufferObjectId);
        buffer.rewind();
        gl.glDeleteBuffers(1, buffer);

        buffer = Buffers.newDirectIntBuffer(1);
        buffer.put(this.vertexArrayObjectId);
        buffer.rewind();
        gl.glDeleteVertexArrays(1, buffer);

        buffer = Buffers.newDirectIntBuffer(1);
        buffer.put(this.cubemapTextureId);
        buffer.rewind();
        gl.glDeleteTextures(1, buffer);
    }

    private int loadCubemap(
            GL4 gl,
            String right,
            String left,
            String top,
            String bottom,
            String front,
            String back
    ) {
        String[] faces = {right, left, top, bottom, front, back};

        IntBuffer textureIdBuffer = Buffers.newDirectIntBuffer(1);
        gl.glGenTextures(1, textureIdBuffer);
        int textureId = textureIdBuffer.get(0);

        gl.glBindTexture(GL4.GL_TEXTURE_CUBE_MAP, textureId);

        for (int i = 0; i < faces.length; i++) {
            int rotate90Steps = 0;

            if (i == 2) { // top
                rotate90Steps = 3; // 270 degrees
            }

            if (i == 3) { // bottom
                rotate90Steps = 1;  // 90 degrees
            }


            Utilities.PNG image = Utilities.loadImage(
                    SkyboxMesh.class,
                    faces[i],
                    false,
                    rotate90Steps
            );

            gl.glTexImage2D(
                    GL4.GL_TEXTURE_CUBE_MAP_POSITIVE_X + i,
                    0,
                    GL4.GL_RGBA8,
                    image.getWidth(),
                    image.getHeight(),
                    0,
                    GL4.GL_RGBA,
                    GL4.GL_UNSIGNED_BYTE,
                    image.getData()
            );
        }

        gl.glEnable(GL4.GL_TEXTURE_CUBE_MAP_SEAMLESS);

        gl.glTexParameteri(GL4.GL_TEXTURE_CUBE_MAP, GL4.GL_TEXTURE_MIN_FILTER, GL4.GL_LINEAR);
        gl.glTexParameteri(GL4.GL_TEXTURE_CUBE_MAP, GL4.GL_TEXTURE_MAG_FILTER, GL4.GL_LINEAR);
        gl.glTexParameteri(GL4.GL_TEXTURE_CUBE_MAP, GL4.GL_TEXTURE_WRAP_S, GL4.GL_CLAMP_TO_EDGE);
        gl.glTexParameteri(GL4.GL_TEXTURE_CUBE_MAP, GL4.GL_TEXTURE_WRAP_T, GL4.GL_CLAMP_TO_EDGE);
        gl.glTexParameteri(GL4.GL_TEXTURE_CUBE_MAP, GL4.GL_TEXTURE_WRAP_R, GL4.GL_CLAMP_TO_EDGE);

        gl.glBindTexture(GL4.GL_TEXTURE_CUBE_MAP, 0);

        return textureId;
    }
}