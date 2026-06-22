package opengl4.common.light;

import org.joml.Vector3f;

public class RotatingLight extends Light {
    public RotatingLight ( LightingShaderProgram lightingShaderProgram, Vector3f position ) {
        super ( lightingShaderProgram, position );
    }
    
    @Override
    public void update ( ) {
        double angle = ( System.currentTimeMillis ( ) % 5000 ) * 360.0 / 5000.0;
    
        float x = ( float ) ( 5 * Math.cos ( Math.toRadians ( angle ) ) );
        float z = ( float ) ( 5 * Math.sin ( Math.toRadians ( angle ) ) );
        
        super.getTransform ( ).m30 ( x );
        super.getTransform ( ).m32 ( z );
    }
}
