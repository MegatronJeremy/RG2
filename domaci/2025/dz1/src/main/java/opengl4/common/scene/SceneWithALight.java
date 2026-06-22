package opengl4.common.scene;

import opengl4.common.camera.Camera;
import opengl4.common.graphicsObject.AbstractGraphicsObject;
import opengl4.common.light.Light;

public class SceneWithALight extends Scene {
	private static AbstractGraphicsObject[] concatenate ( AbstractGraphicsObject item, AbstractGraphicsObject ...collection ) {
		AbstractGraphicsObject newCollection[] = new AbstractGraphicsObject[collection.length + 1];
		newCollection[0] = item;
		for ( int i = 0; i < collection.length; ++i ) {
			newCollection[i + 1] = collection[i];
		}
		return newCollection;
	}
	
	
	public SceneWithALight ( Camera camera, Light light, AbstractGraphicsObject ...graphicsObjects ) {
		super ( camera, SceneWithALight.concatenate ( light, graphicsObjects ) );
	}
}
