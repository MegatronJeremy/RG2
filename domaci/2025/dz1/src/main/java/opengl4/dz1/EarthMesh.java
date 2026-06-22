package opengl4.dz1;

import com.jogamp.common.nio.Buffers;
import com.jogamp.opengl.GL4;
import opengl4.Utilities;
import opengl4.common.camera.Camera;
import opengl4.common.graphicsObject.GraphicsObject;
import org.joml.Matrix4f;
import org.joml.Vector3f;

import java.nio.FloatBuffer;
import java.nio.IntBuffer;

public class EarthMesh extends GraphicsObject {
    private final float radius;
    private final int resolution;
    private final EarthShaderProgram earthShaderProgram;

    private int vertexArrayObjectId;
    private int positionBufferObjectId;
    private int normalBufferObjectId;
    private int textureCoordinatesBufferObjectId;
    private int tangentBufferObjectId;
    private int elementBufferObjectId;
    private int indexCount;

    private int diffuseTextureId;
    private int specularTextureId;
    private int normalTextureId;

    public EarthMesh(EarthShaderProgram earthShaderProgram, float radius, int resolution) {
        super(earthShaderProgram);

        this.earthShaderProgram = earthShaderProgram;
        this.radius = radius;
        this.resolution = resolution;
    }

    @Override
    protected void initializeInternal(GL4 gl) {
        Utilities.PNG heightMap = Utilities.loadImage(EarthMesh.class, "heightMap.jpg");

        CubeSphereGenerator.MeshData meshData =
                CubeSphereGenerator.generate(this.radius, this.resolution, heightMap, this.radius * 0.01f);

        this.indexCount = meshData.getIndexCount();

        IntBuffer intBuffer = Buffers.newDirectIntBuffer(1);

        gl.glGenVertexArrays(1, intBuffer);
        this.vertexArrayObjectId = intBuffer.get(0);

        gl.glBindVertexArray(this.vertexArrayObjectId);

        FloatBuffer positionBuffer = Buffers.newDirectFloatBuffer(meshData.positions, 0);
        FloatBuffer normalBuffer = Buffers.newDirectFloatBuffer(meshData.normals, 0);
        FloatBuffer textureCoordinatesBuffer = Buffers.newDirectFloatBuffer(meshData.textureCoordinates, 0);
        FloatBuffer tangentBuffer = Buffers.newDirectFloatBuffer(meshData.tangents, 0);
        IntBuffer indexBuffer = Buffers.newDirectIntBuffer(meshData.indices, 0);

        intBuffer.rewind();
        gl.glGenBuffers(1, intBuffer);
        this.positionBufferObjectId = intBuffer.get(0);
        gl.glBindBuffer(GL4.GL_ARRAY_BUFFER, this.positionBufferObjectId);
        gl.glBufferData(
                GL4.GL_ARRAY_BUFFER,
                (long) meshData.positions.length * Float.BYTES,
                positionBuffer,
                GL4.GL_STATIC_DRAW
        );
        gl.glEnableVertexAttribArray(0);
        gl.glVertexAttribPointer(0, 3, GL4.GL_FLOAT, false, 0, 0);

        intBuffer.rewind();
        gl.glGenBuffers(1, intBuffer);
        this.normalBufferObjectId = intBuffer.get(0);
        gl.glBindBuffer(GL4.GL_ARRAY_BUFFER, this.normalBufferObjectId);
        gl.glBufferData(
                GL4.GL_ARRAY_BUFFER,
                (long) meshData.normals.length * Float.BYTES,
                normalBuffer,
                GL4.GL_STATIC_DRAW
        );
        gl.glEnableVertexAttribArray(1);
        gl.glVertexAttribPointer(1, 3, GL4.GL_FLOAT, false, 0, 0);

        intBuffer.rewind();
        gl.glGenBuffers(1, intBuffer);
        this.textureCoordinatesBufferObjectId = intBuffer.get(0);
        gl.glBindBuffer(GL4.GL_ARRAY_BUFFER, this.textureCoordinatesBufferObjectId);
        gl.glBufferData(
                GL4.GL_ARRAY_BUFFER,
                (long) meshData.textureCoordinates.length * Float.BYTES,
                textureCoordinatesBuffer,
                GL4.GL_STATIC_DRAW
        );
        gl.glEnableVertexAttribArray(2);
        gl.glVertexAttribPointer(2, 2, GL4.GL_FLOAT, false, 0, 0);

        intBuffer.rewind();
        gl.glGenBuffers(1, intBuffer);
        this.tangentBufferObjectId = intBuffer.get(0);
        gl.glBindBuffer(GL4.GL_ARRAY_BUFFER, this.tangentBufferObjectId);
        gl.glBufferData(
                GL4.GL_ARRAY_BUFFER,
                (long) meshData.tangents.length * Float.BYTES,
                tangentBuffer,
                GL4.GL_STATIC_DRAW
        );
        gl.glEnableVertexAttribArray(3);
        gl.glVertexAttribPointer(3, 3, GL4.GL_FLOAT, false, 0, 0);

        intBuffer.rewind();
        gl.glGenBuffers(1, intBuffer);
        this.elementBufferObjectId = intBuffer.get(0);
        gl.glBindBuffer(GL4.GL_ELEMENT_ARRAY_BUFFER, this.elementBufferObjectId);
        gl.glBufferData(
                GL4.GL_ELEMENT_ARRAY_BUFFER,
                (long) meshData.indices.length * Integer.BYTES,
                indexBuffer,
                GL4.GL_STATIC_DRAW
        );

        gl.glBindVertexArray(0);
        gl.glBindBuffer(GL4.GL_ARRAY_BUFFER, 0);

        this.diffuseTextureId = this.loadTexture(gl, "earth.jpg");
        this.specularTextureId = this.loadTexture(gl, "specularMap.jpg");
        this.normalTextureId = this.loadTexture(gl, "normalMap.jpg");
    }

    @Override
    protected void renderInternal(GL4 gl, Matrix4f parentTransform, Camera camera) {
        gl.glBindVertexArray(this.vertexArrayObjectId);

        Matrix4f viewProjection = camera.getViewProjection();
        Matrix4f transform = new Matrix4f(viewProjection).mul(parentTransform);

        this.earthShaderProgram.setTransformUniform(gl, transform);
        this.earthShaderProgram.setModelUniform(gl, parentTransform);

        Vector3f cameraPosition = camera.getWorldPosition();
        this.earthShaderProgram.setCameraPosition(gl, cameraPosition);

        this.earthShaderProgram.setLightPosition(gl, new Vector3f(50.0f, 20.0f, 50.0f));
        this.earthShaderProgram.setLightColor(gl, new Vector3f(1.0f, 1.0f, 1.0f));

        gl.glActiveTexture(GL4.GL_TEXTURE0);
        gl.glBindTexture(GL4.GL_TEXTURE_2D, this.diffuseTextureId);
        this.earthShaderProgram.setDiffuseMap(gl, 0);

        gl.glActiveTexture(GL4.GL_TEXTURE1);
        gl.glBindTexture(GL4.GL_TEXTURE_2D, this.specularTextureId);
        this.earthShaderProgram.setSpecularMap(gl, 1);

        gl.glActiveTexture(GL4.GL_TEXTURE2);
        gl.glBindTexture(GL4.GL_TEXTURE_2D, this.normalTextureId);
        this.earthShaderProgram.setNormalMap(gl, 2);

        gl.glDrawElements(GL4.GL_TRIANGLES, this.indexCount, GL4.GL_UNSIGNED_INT, 0);

        gl.glActiveTexture(GL4.GL_TEXTURE2);
        gl.glBindTexture(GL4.GL_TEXTURE_2D, 0);

        gl.glActiveTexture(GL4.GL_TEXTURE1);
        gl.glBindTexture(GL4.GL_TEXTURE_2D, 0);

        gl.glActiveTexture(GL4.GL_TEXTURE0);
        gl.glBindTexture(GL4.GL_TEXTURE_2D, 0);

        gl.glBindVertexArray(0);
    }

    @Override
    protected void destroyInternal(GL4 gl) {
        IntBuffer buffer = Buffers.newDirectIntBuffer(5);
        buffer.put(this.positionBufferObjectId);
        buffer.put(this.normalBufferObjectId);
        buffer.put(this.textureCoordinatesBufferObjectId);
        buffer.put(this.tangentBufferObjectId);
        buffer.put(this.elementBufferObjectId);
        buffer.rewind();
        gl.glDeleteBuffers(5, buffer);

        IntBuffer vaoBuffer = Buffers.newDirectIntBuffer(1);
        vaoBuffer.put(this.vertexArrayObjectId);
        vaoBuffer.rewind();
        gl.glDeleteVertexArrays(1, vaoBuffer);

        IntBuffer textureBuffer = Buffers.newDirectIntBuffer(3);
        textureBuffer.put(this.diffuseTextureId);
        textureBuffer.put(this.specularTextureId);
        textureBuffer.put(this.normalTextureId);
        textureBuffer.rewind();
        gl.glDeleteTextures(3, textureBuffer);
    }

    private int loadTexture(GL4 gl, String fileName) {
        Utilities.PNG png = Utilities.loadImage(EarthMesh.class, fileName);

        IntBuffer textureIdBuffer = Buffers.newDirectIntBuffer(1);
        gl.glGenTextures(1, textureIdBuffer);
        int textureId = textureIdBuffer.get(0);

        gl.glBindTexture(GL4.GL_TEXTURE_2D, textureId);

        gl.glTexImage2D(
                GL4.GL_TEXTURE_2D,
                0,
                GL4.GL_RGBA8,
                png.getWidth(),
                png.getHeight(),
                0,
                GL4.GL_RGBA,
                GL4.GL_UNSIGNED_BYTE,
                png.getData()
        );

        gl.glGenerateMipmap(GL4.GL_TEXTURE_2D);

        gl.glTexParameteri(GL4.GL_TEXTURE_2D, GL4.GL_TEXTURE_WRAP_S, GL4.GL_REPEAT);
        gl.glTexParameteri(GL4.GL_TEXTURE_2D, GL4.GL_TEXTURE_WRAP_T, GL4.GL_REPEAT);

        gl.glTexParameteri(GL4.GL_TEXTURE_2D, GL4.GL_TEXTURE_MIN_FILTER, GL4.GL_LINEAR_MIPMAP_LINEAR);
        gl.glTexParameteri(GL4.GL_TEXTURE_2D, GL4.GL_TEXTURE_MAG_FILTER, GL4.GL_LINEAR);

        gl.glBindTexture(GL4.GL_TEXTURE_2D, 0);

        return textureId;
    }
}