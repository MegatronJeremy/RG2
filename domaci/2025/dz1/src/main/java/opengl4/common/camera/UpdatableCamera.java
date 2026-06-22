package opengl4.common.camera;

import org.joml.Matrix4f;
import org.joml.Vector3f;

public class UpdatableCamera extends Camera {
    private final Vector3f target = new Vector3f(0.0f, 0.0f, 0.0f);
    private final Vector3f up = new Vector3f(0.0f, 1.0f, 0.0f);
    private float distance;
    private float xAngle;
    private float yAngle;

    public UpdatableCamera(float z, float xAngle, float yAngle, float aspect, float zNear, float zFar) {
        super(
                new Matrix4f(),
                UpdatableCamera.getProjectionMatrix(aspect, zNear, zFar)
        );

        this.distance = Math.abs(z);
        this.xAngle = xAngle;
        this.yAngle = yAngle;

        this.updateView();
    }

    private static Matrix4f getProjectionMatrix(float aspect, float zNear, float zFar) {
        return new Matrix4f().perspective((float) Math.toRadians(45.0), aspect, zNear, zFar);
    }

    private static float clamp(float value, float min, float max) {
        return Math.max(min, Math.min(max, value));
    }

    private void updateView() {
        this.xAngle = clamp(this.xAngle, -89.0f, 89.0f);
        this.distance = clamp(this.distance, 2.0f, 200.0f);

        float pitchRad = (float) Math.toRadians(this.xAngle);
        float yawRad = (float) Math.toRadians(this.yAngle);

        float x = this.distance * (float) (Math.cos(pitchRad) * Math.sin(yawRad));
        float y = this.distance * (float) Math.sin(pitchRad);
        float z = this.distance * (float) (Math.cos(pitchRad) * Math.cos(yawRad));

        Vector3f eye = new Vector3f(x, y, z);

        super.getView().identity().lookAt(eye, this.target, this.up);
    }

    public void move(float zStep) {
        this.distance += zStep;
        this.updateView();
    }

    public void yRotate(float yAngleStep) {
        this.yAngle += yAngleStep;
        this.updateView();
    }

    public void xRotate(float xAngleStep) {
        this.xAngle += xAngleStep;
        this.updateView();
    }
}