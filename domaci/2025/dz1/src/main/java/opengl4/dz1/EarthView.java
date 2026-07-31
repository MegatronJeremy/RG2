package opengl4.dz1;

import com.jogamp.opengl.GL4;
import com.jogamp.opengl.GLAutoDrawable;
import opengl4.common.camera.UpdatableCamera;
import opengl4.common.scene.Scene;

public class EarthView extends EditorCameraView {
    private final UpdatableCamera camera;

    public EarthView(UpdatableCamera camera, EarthShaderProgram earthShaderProgram, SkyboxShaderProgram skyboxShaderProgram) {
        super(createScene(camera, earthShaderProgram, skyboxShaderProgram), camera);
        this.camera = camera;
    }

    private static Scene createScene(UpdatableCamera camera, EarthShaderProgram earthShaderProgram, SkyboxShaderProgram skyboxShaderProgram) {
        EarthMesh earthMesh = new EarthMesh(earthShaderProgram, 10.0f, 64);
        SkyboxMesh skyboxMesh = new SkyboxMesh(skyboxShaderProgram);

        return new Scene(
                camera,
                earthMesh,
                skyboxMesh
        );
    }

    @Override
    public void init(GLAutoDrawable drawable) {
        super.init(drawable);

        GL4 gl = drawable.getGL().getGL4();

        gl.glEnable(GL4.GL_DEPTH_TEST);
        gl.glDisable(GL4.GL_CULL_FACE);
    }

    @Override
    public void render(GLAutoDrawable drawable) {
        super.render(drawable);
    }

    // The framework's GLView.reshape() is a no-op, so on window resize the GL
    // viewport stayed at its initial size and the fixed aspect=1 projection
    // stretched the scene. Update both here: match the viewport to the drawable
    // and rebuild the projection for the new aspect ratio.
    @Override
    public void reshape(GLAutoDrawable drawable, int x, int y, int width, int height) {
        GL4 gl = drawable.getGL().getGL4();
        gl.glViewport(0, 0, width, height);

        float aspect = height == 0 ? 1.0f : (float) width / (float) height;
        this.camera.setAspect(aspect);
    }
}