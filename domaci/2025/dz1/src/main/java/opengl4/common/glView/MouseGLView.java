package opengl4.common.glView;

import com.jogamp.newt.event.MouseEvent;
import com.jogamp.newt.event.MouseListener;
import opengl4.common.scene.Scene;
import org.joml.Vector4f;

public abstract class MouseGLView extends GLView implements MouseListener {
	public MouseGLView ( Scene scene ) {
		super ( scene );
	}
	
	public MouseGLView ( Scene scene, Vector4f clearColor ) {
		super ( scene, clearColor );
	}
	
	@Override
	public void mouseClicked ( MouseEvent e ) { }
	
	@Override
	public void mouseEntered ( MouseEvent e ) { }
	
	@Override
	public void mouseExited ( MouseEvent e ) { }
	
	@Override
	public void mousePressed ( MouseEvent e ) { }
	
	@Override
	public void mouseReleased ( MouseEvent e ) { }
	
	@Override
	public void mouseMoved ( MouseEvent e ) { }
	
	@Override
	public void mouseDragged ( MouseEvent e ) { }
	
	@Override
	public void mouseWheelMoved ( MouseEvent e ) { }
}
