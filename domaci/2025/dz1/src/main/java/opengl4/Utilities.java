package opengl4;

import de.matthiasmann.twl.utils.PNGDecoder;
import org.joml.Vector3f;

import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;

public class Utilities {
    public static String readFile(Class scope, String filename) {
        String returnString = null;

        try (InputStream inputStream = scope.getResourceAsStream(filename)) {
            returnString = new String(inputStream.readAllBytes());
        } catch (IOException | NullPointerException exception) {
            exception.printStackTrace();
        }

        return returnString;
    }

    public static PNG loadPNG(Class scope, String filename) {
        PNG result = null;

        try (
                InputStream in = scope.getResourceAsStream(filename)
        ) {
            PNGDecoder decoder = new PNGDecoder(in);

            int width = decoder.getWidth();
            int height = decoder.getHeight();
            ByteBuffer data = ByteBuffer.allocateDirect(4 * width * height);

            decoder.decode(data, width * 4, PNGDecoder.Format.RGBA);

            data.flip();

            result = new PNG(width, height, data);
        } catch (IOException e) {
            e.printStackTrace();
        }

        return result;
    }

    public static PNG loadImage(Class scope, String filename, boolean flipVertically, int rotate90Steps) {
        try (InputStream in = scope.getResourceAsStream(filename)) {
            if (in == null) {
                throw new RuntimeException("Resource not found: " + filename);
            }

            java.awt.image.BufferedImage image = javax.imageio.ImageIO.read(in);
            if (image == null) {
                throw new RuntimeException("Unsupported image format: " + filename);
            }

            int normalizedSteps = ((rotate90Steps % 4) + 4) % 4;

            for (int i = 0; i < normalizedSteps; i++) {
                image = rotate90CW(image);
            }

            int width = image.getWidth();
            int height = image.getHeight();

            ByteBuffer data = ByteBuffer.allocateDirect(4 * width * height);

            for (int y = 0; y < height; y++) {
                int srcY = flipVertically ? (height - 1 - y) : y;

                for (int x = 0; x < width; x++) {
                    int argb = image.getRGB(x, srcY);

                    byte a = (byte) ((argb >> 24) & 0xFF);
                    byte r = (byte) ((argb >> 16) & 0xFF);
                    byte g = (byte) ((argb >> 8) & 0xFF);
                    byte b = (byte) (argb & 0xFF);

                    data.put(r).put(g).put(b).put(a);
                }
            }

            data.flip();
            return new PNG(width, height, data);
        } catch (IOException e) {
            throw new RuntimeException("Failed to load image: " + filename, e);
        }
    }

    private static java.awt.image.BufferedImage rotate90CW(java.awt.image.BufferedImage src) {
        int srcWidth = src.getWidth();
        int srcHeight = src.getHeight();

        java.awt.image.BufferedImage dst =
                new java.awt.image.BufferedImage(
                        srcHeight,
                        srcWidth,
                        java.awt.image.BufferedImage.TYPE_INT_ARGB
                );

        for (int y = 0; y < srcHeight; y++) {
            for (int x = 0; x < srcWidth; x++) {
                dst.setRGB(srcHeight - 1 - y, x, src.getRGB(x, y));
            }
        }

        return dst;
    }

    public static PNG loadImage(Class scope, String filename) {
        return loadImage(scope, filename, false, 0);
    }

    public static PNG loadImage(Class scope, String filename, boolean flipVertically) {
        return loadImage(scope, filename, flipVertically, 0);
    }

    private static Vector3f makeVector(float[] vertices, int index0, int index1) {
        float x = vertices[index1] - vertices[index0];
        float y = vertices[index1 + 1] - vertices[index0 + 1];
        float z = vertices[index1 + 2] - vertices[index0 + 2];

        return new Vector3f(x, y, z);
    }

    public static float[] computeNormals(float[] vertices) {
        float[] normals = new float[vertices.length];

        for (int i = 0; i < (vertices.length / 9); ++i) {
            int index0 = i * 9;
            int index1 = i * 9 + 3;
            int index2 = i * 9 + 6;

            Vector3f vector0 = Utilities.makeVector(vertices, index0, index1);
            Vector3f vector1 = Utilities.makeVector(vertices, index0, index2);

            Vector3f normal = vector0.cross(vector1);

            for (int j = 0; j < 3; ++j) {
                normals[i * 9 + j * 3] = normal.x;
                normals[i * 9 + j * 3 + 1] = normal.y;
                normals[i * 9 + j * 3 + 2] = normal.z;
            }
        }

        return normals;
    }

    public static class PNG {
        private final int width;
        private final int height;
        private final ByteBuffer data;

        public PNG(int width, int height, ByteBuffer data) {
            this.width = width;
            this.height = height;
            this.data = data;
        }

        public int getWidth() {
            return width;
        }

        public int getHeight() {
            return height;
        }

        public ByteBuffer getData() {
            return data;
        }
    }
}
