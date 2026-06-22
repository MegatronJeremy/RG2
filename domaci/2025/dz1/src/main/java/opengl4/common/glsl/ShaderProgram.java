package opengl4.common.glsl;

import com.jogamp.opengl.GL4;
import org.joml.Vector4f;

import java.nio.ByteBuffer;
import java.util.*;

public class ShaderProgram {
	public enum Status {
		PROGRAM_NOT_COMPLETE,
		PROGRAM_COMPLETE,
		ACTIVE,
		INACTIVE
	}
	
	private String                      name;
	private Dictionary<String, Integer> uniformLocations;
	private List<String>                uniforms;
	private List<Shader>                shaders;
	private int                         id;
	private StringBuilder               buildLog;
	private Status                      programStatus;
	
	public ShaderProgram ( String name, Shader... shaders ) {
		this.name             = name;
		this.programStatus    = Status.PROGRAM_NOT_COMPLETE;
		this.uniformLocations = new Hashtable<> ( );
		this.uniforms         = new ArrayList<> ( );
		this.shaders          = new ArrayList<> ( );
		
		this.shaders.addAll ( Arrays.asList ( shaders ) );
	}

	public void initialize ( GL4 gl ) {
		if ( !Status.PROGRAM_NOT_COMPLETE.equals ( this.programStatus ) ) {
			return;
		}
		
		if ( this.id == 0 ) {
			this.id = gl.glCreateProgram ( );
		}
		
		this.programStatus = Status.PROGRAM_NOT_COMPLETE;
		
		this.buildLog = new StringBuilder ( );
		this.buildLog.append ( String.format ( "Shader program %s build log:\n", this.name ) );
		
		boolean allSuccessful = true;
		
		for ( Shader shader : this.shaders ) {
			List<String> uniforms = shader.initialize ( gl );
			
			if ( !Shader.Status.COMPILED_SUCCESS.equals ( shader.getCompilationStatus ( ) ) ) {
				allSuccessful = false;
			} else {
				this.uniforms.addAll ( uniforms );
			}
			
			this.buildLog.append ( shader.getCompilationLog ( ) );
		}
		
		if ( !allSuccessful ) {
			this.buildLog.append ( String.format ( "Shader program %s not created", this.name ) );
			gl.glDeleteProgram ( this.id );
			System.out.println ( this.buildLog.toString ( ) );
			return;
		}
		
		for ( Shader shader : this.shaders ) {
			gl.glAttachShader ( this.id, shader.getShaderID ( ) );
		}
		
		gl.glLinkProgram ( this.id );
		
		int[] params = new int[1];
		
		gl.glGetProgramiv ( this.id, GL4.GL_LINK_STATUS, params, 0 );
		
		this.buildLog.append ( String.format ( "Program %s link status: ", this.name ) );
		
		if ( params[0] == GL4.GL_TRUE ) {
			this.buildLog.append ( "Success" );
			this.programStatus = Status.PROGRAM_COMPLETE;
		} else {
			this.buildLog.append ( "Failure" );
		}
		
		this.buildLog.append ( System.lineSeparator ( ) );
		
		if ( Status.PROGRAM_COMPLETE.equals ( this.programStatus ) ) {
			for ( String uniform : this.uniforms ) {
				int location = gl.glGetUniformLocation ( this.id, uniform );
				if ( location > -1 ) {
					this.uniformLocations.put ( uniform, location );
				} else {
					this.buildLog.append ( String.format ( "Shader program %s: uniform %s not found", this.name, uniform ) );
				}
			}
		}
		
		gl.glGetProgramiv ( this.id, GL4.GL_INFO_LOG_LENGTH, params, 0 );
		int        infoLogLength = params[0];
		ByteBuffer infoLog       = ByteBuffer.allocate ( infoLogLength );
		gl.glGetProgramInfoLog ( this.id, infoLogLength, null, infoLog );
		this.buildLog.append ( new String ( infoLog.array ( ) ) ).append ( System.lineSeparator ( ) );
		
		System.out.println ( this.buildLog );
	}
	
	public void destroy ( GL4 gl ) {
		if ( this.id != 0 ) {
			this.shaders.forEach ( shader -> shader.destroy ( gl ) );
			gl.glDeleteProgram ( this.id );
			this.id = 0;
		}
	}
	
	public void activate ( GL4 gl ) {
		if ( !Status.ACTIVE.equals ( this.programStatus ) ) {
			gl.glUseProgram ( this.id );
			this.programStatus = Status.ACTIVE;
		}
	}
	
	public void deactivate ( GL4 gl ) {
		if ( !Status.INACTIVE.equals ( this.programStatus ) ) {
			gl.glUseProgram ( 0 );
			this.programStatus = Status.INACTIVE;
		}
	}
	
	public int getUniformLocation ( String name ) {
		return this.uniformLocations.get ( name );
	}
	
	protected void setSamplerUniform ( GL4 gl, String name, int textureUnit ) {
		int location = this.getUniformLocation ( name );
		
		gl.glProgramUniform1i ( this.id, location, textureUnit );
	}
	
	protected void setVector4fUniform ( GL4 gl, String name, Vector4f vector4f ) {
		int location = this.getUniformLocation ( name );
		
		gl.glProgramUniform4f ( this.id, location, vector4f.x, vector4f.y, vector4f.z, vector4f.w );
	}
}
