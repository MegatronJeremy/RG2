package opengl4.common.glsl;


import com.jogamp.opengl.GL;
import com.jogamp.opengl.GL4;

import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public abstract class Shader {
    
    public enum Status {
        INITIALIZED,
        COMPILED_FAILURE,
        COMPILED_SUCCESS,
        CANNOT_CREATE_OBJECT
    }
	
	private int            id;
	private String         name;
	private int            type;
	private String[]       sources;
	private StringBuffer   compilationLog;
	private Status         compilationStatus;
	private List<String> uniforms;
    
    protected Shader ( String shaderName, int shaderType, String[] shaderSource ) {
		this.name = shaderName;
		this.type = shaderType;
		this.sources = shaderSource;
		this.compilationStatus = Status.INITIALIZED;
		this.compilationLog    = new StringBuffer ( );
	}
	
	protected Shader ( String shaderName, int shaderType, String shaderSource ) {
		this ( shaderName, shaderType, new String[] { shaderSource } );
	}
	
	public String getCompilationLog ( ) {
		return this.compilationLog.toString ( );
	}
	
	public int getShaderID ( ) {
		return this.id;
	}
	
	public Status getCompilationStatus ( ) {
		return this.compilationStatus;
	}
	
	public List<String> initialize ( GL4 gl ) {
		if ( !Status.INITIALIZED.equals ( this.compilationStatus ) ) {
			return this.uniforms;
		}
		
		this.compilationLog = new StringBuffer ( );
		
		if ( this.id == 0 ) {
			this.id = gl.glCreateShader ( this.type );
			
			int error = gl.glGetError ( );
			if ( error != GL.GL_NO_ERROR ) {
				String message = String.format ( "Cannot create shader %s, error: %d", this.name, error );
				this.compilationLog.append ( message );
				this.compilationStatus = Status.CANNOT_CREATE_OBJECT;
				return this.uniforms;
			}
		}
		
		gl.glShaderSource ( this.id, this.sources.length, this.sources, null );
		gl.glCompileShader ( this.id );
		
		int[] parameter = new int[1];
		
		gl.glGetShaderiv ( this.id, GL4.GL_COMPILE_STATUS, parameter, 0 );
		
		if ( parameter[0] == gl.GL_TRUE ) {
			String message = String.format ( "Shader %s compiled successfully", this.name );
			this.compilationLog.append ( message );
			this.compilationStatus = Status.COMPILED_SUCCESS;
		} else {
			String message = String.format ( "Shader %s compilation error: %d", this.name, parameter[0] );
			this.compilationLog.append ( message );
			this.compilationStatus = Status.COMPILED_FAILURE;
		}
		
		this.compilationLog.append ( System.lineSeparator ( ) );
		
		gl.glGetShaderiv ( this.id, GL4.GL_INFO_LOG_LENGTH, parameter, 0 );
		
		int infoLogLength = parameter[0];
		
		ByteBuffer shaderInfoLog = ByteBuffer.allocate ( infoLogLength );
		gl.glGetShaderInfoLog ( this.id, infoLogLength, null, shaderInfoLog );
		this.compilationLog.append ( new String ( shaderInfoLog.array ( ) ) ).append ( System.lineSeparator ( ) );
		
		this.uniforms = new ArrayList<String> ( );
		for ( int i = 0; i < this.sources.length; ++i ) {
			String  regex   = "uniform\\s+\\w+\\s+([a-zA-Z0-9_]+)";
			Pattern pattern = Pattern.compile ( regex );
			Matcher matcher = pattern.matcher ( this.sources[i] );
			
			matcher.results ( ).forEach (
					matchResult -> this.uniforms.add ( matchResult.group ( 1 ) )
			);
		}
		
		return this.uniforms;
	}
	
	public void destroy ( GL4 gl ) {
		gl.glDeleteShader ( this.id );
		this.id = 0;
		this.compilationStatus = Status.INITIALIZED;
	}
}
