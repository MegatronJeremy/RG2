package opengl4.common.glView;

import com.jogamp.newt.event.KeyEvent;
import com.jogamp.newt.event.KeyListener;
import opengl4.common.scene.Scene;
import org.joml.Vector4f;

public abstract class KeyGLView extends GLView implements KeyListener {
	public KeyGLView ( Scene scene ) {
		super ( scene );
	}
	
	public KeyGLView ( Scene scene, Vector4f clearColor ) {
		super ( scene, clearColor );
	}
	
	@Override
	public void keyPressed ( KeyEvent event ) { }
	
	@Override
	public void keyReleased ( KeyEvent event ) { }
}
