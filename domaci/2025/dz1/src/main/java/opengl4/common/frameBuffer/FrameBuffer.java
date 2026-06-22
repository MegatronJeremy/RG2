package opengl4.common.frameBuffer;

import com.jogamp.common.nio.Buffers;
import com.jogamp.opengl.GL4;
import org.joml.Vector4f;
import java.nio.IntBuffer;

public class FrameBuffer {
	private int id;
	private int colorBufferId;
	private int depthStencilBufferId;
	
	private int width;
	private int height;
	
	public FrameBuffer ( int width, int height ) {
		this.width = width;
		this.height = height;
	}
	
	public void initialize ( GL4 gl ) {
		IntBuffer intBuffer = IntBuffer.allocate ( 1 );
		gl.glGenFramebuffers ( 1, intBuffer );
		this.id = intBuffer.get ( 0 );
		
		gl.glBindFramebuffer ( GL4.GL_FRAMEBUFFER, this.id );
		
		intBuffer.rewind ( );
		gl.glGenTextures(1, intBuffer );
		this.colorBufferId = intBuffer.get ( 0 );
		
		gl.glBindTexture ( GL4.GL_TEXTURE_2D, this.colorBufferId );
		gl.glTexImage2D (
				GL4.GL_TEXTURE_2D,
				0,
				GL4.GL_RGB,
				this.width,
				this.height,
				0,
				GL4.GL_RGB,
				GL4.GL_UNSIGNED_BYTE,
				null
		);
		
		gl.glTexParameteri ( GL4.GL_TEXTURE_2D, GL4.GL_TEXTURE_MIN_FILTER, GL4.GL_LINEAR );
		gl.glTexParameteri ( GL4.GL_TEXTURE_2D, GL4.GL_TEXTURE_MAG_FILTER, GL4.GL_LINEAR );
		
		gl.glBindTexture ( GL4.GL_TEXTURE_2D, 0 );
		gl.glFramebufferTexture2D (
				GL4.GL_FRAMEBUFFER,
				GL4.GL_COLOR_ATTACHMENT0,
				GL4.GL_TEXTURE_2D,
				this.colorBufferId,
				0
		);
		
		intBuffer.rewind ( );
		gl.glGenRenderbuffers (1, intBuffer );
		this.depthStencilBufferId = intBuffer.get ( 0 );
		
		gl.glBindRenderbuffer ( GL4.GL_RENDERBUFFER, this.depthStencilBufferId );
		gl.glRenderbufferStorage ( GL4.GL_RENDERBUFFER, GL4.GL_DEPTH24_STENCIL8, this.width, this.height );
		gl.glBindRenderbuffer ( GL4.GL_RENDERBUFFER, 0 );
		gl.glFramebufferRenderbuffer ( GL4.GL_FRAMEBUFFER, GL4.GL_DEPTH_STENCIL_ATTACHMENT, GL4.GL_RENDERBUFFER, this.depthStencilBufferId );
		
		if ( gl.glCheckFramebufferStatus ( GL4.GL_FRAMEBUFFER ) != GL4.GL_FRAMEBUFFER_COMPLETE ) {
			System.out.println ( "Frame buffer not complete!" );
		}
		
		gl.glBindFramebuffer ( GL4.GL_FRAMEBUFFER, 0 );
	}
	
	public void destroy ( GL4 gl ) {
		int ids[] = {
				this.depthStencilBufferId,
				this.colorBufferId,
				this.id
		};
		IntBuffer intBuffer = Buffers.newDirectIntBuffer ( ids );
		
		gl.glDeleteRenderbuffers ( 1, intBuffer );
		gl.glDeleteTextures ( 1, intBuffer );
		gl.glDeleteFramebuffers ( 1, intBuffer );
	}
	
	public void clear ( GL4 gl, Vector4f clearColor ) {
		gl.glClearColor ( clearColor.x, clearColor.y, clearColor.z, clearColor.w );
		gl.glClear ( GL4.GL_COLOR_BUFFER_BIT | GL4.GL_DEPTH_BUFFER_BIT | GL4.GL_STENCIL_BUFFER_BIT );
	}
	
	public void bind ( GL4 gl ) {
		gl.glBindFramebuffer ( GL4.GL_FRAMEBUFFER, this.id );
	}
	
	public void unbind ( GL4 gl ) {
		gl.glBindFramebuffer ( GL4.GL_FRAMEBUFFER, 0 );
	}
	
	public void bindColorBufferToTextureUnit ( GL4 gl, int textureUnit ) {
		gl.glActiveTexture ( GL4.GL_TEXTURE0 + textureUnit );
		gl.glBindTexture ( GL4.GL_TEXTURE_2D, this.colorBufferId );
	}
}
