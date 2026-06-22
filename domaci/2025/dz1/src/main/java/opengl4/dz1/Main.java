package opengl4.dz1;

import com.jogamp.newt.event.WindowAdapter;
import com.jogamp.newt.event.WindowEvent;
import com.jogamp.newt.opengl.GLWindow;
import com.jogamp.opengl.GLCapabilities;
import com.jogamp.opengl.GLProfile;
import com.jogamp.opengl.util.FPSAnimator;
import opengl4.common.camera.UpdatableCamera;
import opengl4.common.glView.MouseKeyGLView;

public class Main {
    private static final int WINDOW_WIDTH = 1000;
    private static final int WINDOW_HEIGHT = 1000;
    private static final int FPS = 60;
    private static final String TITLE = "RG2 DZ1 - Earth";

    private static void createWindow(
            GLCapabilities glCapabilities,
            String title,
            MouseKeyGLView view,
            int width,
            int height,
            int x,
            int y
    ) {
        System.out.println("Creating window...");

        GLWindow window = GLWindow.create(glCapabilities);

        final FPSAnimator fpsAnimator = new FPSAnimator(window, Main.FPS, true);

        window.addWindowListener(new WindowAdapter() {
            @Override
            public void windowDestroyNotify(WindowEvent event) {
                new Thread() {
                    @Override
                    public void run() {
                        fpsAnimator.stop();
                        System.exit(0);
                    }
                }.start();
            }
        });

        window.addGLEventListener(view);
        window.addMouseListener(view);

        window.setSize(width, height);
        window.setPosition(x, y);
        window.setTitle(title);
        window.setVisible(true);
        System.out.println("Window visible set.");

        fpsAnimator.start();
    }

    public static void main(String[] args) {
        GLProfile glProfile = GLProfile.get(GLProfile.GL4);

        System.out.println(glProfile.getGLImplBaseClassName());
        System.out.println(glProfile.getImplName());
        System.out.println(glProfile.getName());
        System.out.println(glProfile.hasGLSL());

        GLCapabilities glCapabilities = new GLCapabilities(glProfile);
        glCapabilities.setAlphaBits(8);
        glCapabilities.setDepthBits(24);

        System.out.println(glCapabilities);

        UpdatableCamera camera = new UpdatableCamera(
                -30.0f,   // distance / position along view axis
                20.0f,    // initial x rotation
                0.0f,     // initial y rotation
                1.0f,     // aspect ratio placeholder
                0.1f,     // near
                1000.0f   // far
        );

        EarthShaderProgram earthShaderProgram = new EarthShaderProgram();
        SkyboxShaderProgram skyboxShaderProgram = new SkyboxShaderProgram();

        Main.createWindow(
                glCapabilities,
                Main.TITLE,
                new EarthView(camera, earthShaderProgram, skyboxShaderProgram),
                Main.WINDOW_WIDTH,
                Main.WINDOW_HEIGHT,
                30,
                100
        );
    }
}