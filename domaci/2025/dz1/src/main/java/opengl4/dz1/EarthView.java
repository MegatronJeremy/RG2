package opengl4.dz1;

import com.jogamp.opengl.GL4;
import com.jogamp.opengl.GLAutoDrawable;
import opengl4.common.camera.UpdatableCamera;
import opengl4.common.scene.Scene;

public class EarthView extends EditorCameraView {
    public EarthView(UpdatableCamera camera, EarthShaderProgram earthShaderProgram, SkyboxShaderProgram skyboxShaderProgram) {
        super(createScene(camera, earthShaderProgram, skyboxShaderProgram), camera);
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
}