package opengl4.dz1;

import com.jogamp.newt.event.MouseEvent;
import opengl4.common.camera.UpdatableCamera;
import opengl4.common.glView.MouseKeyGLView;
import opengl4.common.scene.Scene;

public class EditorCameraView extends MouseKeyGLView {
    private final UpdatableCamera camera;
    private final float rotateSpeedDegPerPixel = 0.25f;
    private final float zoomStepPerWheelTick = 0.35f;

    private int lastX;
    private int lastY;
    private boolean dragging = false;

    public EditorCameraView(Scene scene, UpdatableCamera camera) {
        super(scene);
        this.camera = camera;
    }

    @Override
    public void mousePressed(MouseEvent e) {
        if (e.getButton() == MouseEvent.BUTTON1) {
            dragging = true;
            lastX = e.getX();
            lastY = e.getY();
        }
    }

    @Override
    public void mouseReleased(MouseEvent e) {
        if (e.getButton() == MouseEvent.BUTTON1) {
            dragging = false;
        }
    }

    @Override
    public void mouseDragged(MouseEvent e) {
        if (!dragging) return;

        int x = e.getX();
        int y = e.getY();
        int dx = x - lastX;
        int dy = y - lastY;

        camera.yRotate(-dx * rotateSpeedDegPerPixel);
        camera.xRotate(dy * rotateSpeedDegPerPixel);

        lastX = x;
        lastY = y;
    }

    @Override
    public void mouseWheelMoved(MouseEvent e) {
        float wheel = e.getRotation()[1];
        camera.move(-wheel * zoomStepPerWheelTick);
    }
}