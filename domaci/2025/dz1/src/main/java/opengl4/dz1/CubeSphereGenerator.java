package opengl4.dz1;

import opengl4.Utilities;
import org.joml.Vector3f;

import java.util.Arrays;

public final class CubeSphereGenerator {
    private CubeSphereGenerator() {
    }

    private static MeshData splitTriangleUVSeams(
            float[] positions,
            float[] normals,
            float[] textureCoordinates,
            int[] indices
    ) {
        java.util.ArrayList<Float> newPositions = new java.util.ArrayList<>();
        java.util.ArrayList<Float> newNormals = new java.util.ArrayList<>();
        java.util.ArrayList<Float> newTexCoords = new java.util.ArrayList<>();

        for (float v : positions) {
            newPositions.add(v);
        }
        for (float v : normals) {
            newNormals.add(v);
        }
        for (float v : textureCoordinates) {
            newTexCoords.add(v);
        }

        int[] newIndices = indices.clone();

        for (int i = 0; i < newIndices.length; i += 3) {
            int i0 = newIndices[i];
            int i1 = newIndices[i + 1];
            int i2 = newIndices[i + 2];

            float u0 = newTexCoords.get(i0 * 2);
            float u1 = newTexCoords.get(i1 * 2);
            float u2 = newTexCoords.get(i2 * 2);

            float minU = Math.min(u0, Math.min(u1, u2));
            float maxU = Math.max(u0, Math.max(u1, u2));

            if (maxU - minU > 0.5f) {
                if (u0 < 0.5f) {
                    newIndices[i] = duplicateVertexWithShift(i0, newPositions, newNormals, newTexCoords, 1.0f);
                }
                if (u1 < 0.5f) {
                    newIndices[i + 1] = duplicateVertexWithShift(i1, newPositions, newNormals, newTexCoords, 1.0f);
                }
                if (u2 < 0.5f) {
                    newIndices[i + 2] = duplicateVertexWithShift(i2, newPositions, newNormals, newTexCoords, 1.0f);
                }
            }
        }

        return new MeshData(
                toFloatArray(newPositions),
                toFloatArray(newNormals),
                toFloatArray(newTexCoords),
                newIndices
        );
    }

    private static int duplicateVertexWithShift(
            int originalIndex,
            java.util.ArrayList<Float> positions,
            java.util.ArrayList<Float> normals,
            java.util.ArrayList<Float> texCoords,
            float uShift
    ) {
        int p = originalIndex * 3;
        int t = originalIndex * 2;

        positions.add(positions.get(p));
        positions.add(positions.get(p + 1));
        positions.add(positions.get(p + 2));

        normals.add(normals.get(p));
        normals.add(normals.get(p + 1));
        normals.add(normals.get(p + 2));

        texCoords.add(texCoords.get(t) + uShift);
        texCoords.add(texCoords.get(t + 1));

        return (positions.size() / 3) - 1;
    }

    private static float[] toFloatArray(java.util.ArrayList<Float> list) {
        float[] out = new float[list.size()];
        for (int i = 0; i < list.size(); i++) {
            out[i] = list.get(i);
        }
        return out;
    }

    public static MeshData generate(float radius, int resolution, Utilities.PNG heightMap, float heightScale) {
        if (resolution < 2) {
            throw new IllegalArgumentException("Resolution must be at least 2.");
        }

        Vector3f[] faceDirections = new Vector3f[]{
                new Vector3f(1.0f, 0.0f, 0.0f),
                new Vector3f(-1.0f, 0.0f, 0.0f),
                new Vector3f(0.0f, 1.0f, 0.0f),
                new Vector3f(0.0f, -1.0f, 0.0f),
                new Vector3f(0.0f, 0.0f, 1.0f),
                new Vector3f(0.0f, 0.0f, -1.0f)
        };

        int verticesPerFace = resolution * resolution;
        int totalVertices = 6 * verticesPerFace;
        int quadsPerFace = (resolution - 1) * (resolution - 1);
        int totalIndices = 6 * quadsPerFace * 6;

        float[] positions = new float[totalVertices * 3];
        float[] normals = new float[totalVertices * 3];
        float[] textureCoordinates = new float[totalVertices * 2];
        int[] indices = new int[totalIndices];

        int vertexIndex = 0;
        int indexOffset = 0;

        for (Vector3f localUp : faceDirections) {
            Vector3f axisA = new Vector3f(localUp.y, localUp.z, localUp.x);
            Vector3f axisB = new Vector3f(localUp).cross(axisA);

            int faceVertexStart = vertexIndex;

            for (int y = 0; y < resolution; y++) {
                for (int x = 0; x < resolution; x++) {
                    float percentX = (float) x / (float) (resolution - 1);
                    float percentY = (float) y / (float) (resolution - 1);

                    Vector3f pointOnCube = new Vector3f(localUp)
                            .add(new Vector3f(axisA).mul((percentX - 0.5f) * 2.0f))
                            .add(new Vector3f(axisB).mul((percentY - 0.5f) * 2.0f));

                    Vector3f pointOnSphere = cubeToSphere(pointOnCube).normalize();

                    float[] uv = computeSphericalUV(pointOnSphere, radius);
                    float u = uv[0];
                    float v = uv[1];

                    float heightValue = sampleHeight(heightMap, u, v);
                    float elevation = heightValue * heightScale;

                    Vector3f displacedPosition = new Vector3f(pointOnSphere).mul(radius + elevation);

                    int p = vertexIndex * 3;
                    positions[p] = displacedPosition.x;
                    positions[p + 1] = displacedPosition.y;
                    positions[p + 2] = displacedPosition.z;

                    int t = vertexIndex * 2;
                    textureCoordinates[t] = u;
                    textureCoordinates[t + 1] = v;

                    vertexIndex++;
                }
            }

            for (int y = 0; y < resolution - 1; y++) {
                for (int x = 0; x < resolution - 1; x++) {
                    int i0 = faceVertexStart + y * resolution + x;
                    int i1 = i0 + 1;
                    int i2 = i0 + resolution;
                    int i3 = i2 + 1;

                    indices[indexOffset++] = i0;
                    indices[indexOffset++] = i2;
                    indices[indexOffset++] = i1;

                    indices[indexOffset++] = i1;
                    indices[indexOffset++] = i2;
                    indices[indexOffset++] = i3;
                }
            }
        }

        computeSmoothNormals(positions, indices, normals);

        return splitTriangleUVSeams(positions, normals, textureCoordinates, indices);
    }

    private static Vector3f cubeToSphere(Vector3f p) {
        float x2 = p.x * p.x;
        float y2 = p.y * p.y;
        float z2 = p.z * p.z;

        float x = (float) (p.x * Math.sqrt(1.0 - (y2 / 2.0) - (z2 / 2.0) + (y2 * z2 / 3.0)));
        float y = (float) (p.y * Math.sqrt(1.0 - (z2 / 2.0) - (x2 / 2.0) + (z2 * x2 / 3.0)));
        float z = (float) (p.z * Math.sqrt(1.0 - (x2 / 2.0) - (y2 / 2.0) + (x2 * y2 / 3.0)));

        return new Vector3f(x, y, z);
    }

    private static float[] computeSphericalUV(Vector3f unitPosition, float radiusIgnored) {
        float theta = (float) Math.atan2(-unitPosition.z, unitPosition.x);
        float phi = (float) Math.acos(-unitPosition.y);

        float u = (theta + (float) Math.PI) / (2.0f * (float) Math.PI);
        float v = 1.0f - phi / (float) Math.PI;

        return new float[]{u, v};
    }

    private static float sampleHeight(Utilities.PNG heightMap, float u, float v) {
        if (heightMap == null) {
            return 0.0f;
        }

        u = u - (float) Math.floor(u);
        v = Math.max(0.0f, Math.min(1.0f, v));

        int width = heightMap.getWidth();
        int height = heightMap.getHeight();

        int x = Math.min(width - 1, (int) (u * (width - 1)));
        int y = Math.min(height - 1, (int) ((1.0f - v) * (height - 1)));

        int index = (y * width + x) * 4;

        int r = heightMap.getData().get(index) & 0xFF;
        int g = heightMap.getData().get(index + 1) & 0xFF;
        int b = heightMap.getData().get(index + 2) & 0xFF;

        return (r + g + b) / (3.0f * 255.0f);
    }

    private static void computeSmoothNormals(float[] positions, int[] indices, float[] normals) {
        Arrays.fill(normals, 0.0f);

        // Accumulate area-weighted face normals into buckets keyed by the (welded)
        // vertex position. The six cube faces are generated as independent grids, so
        // vertices that lie on a shared cube edge are distinct indices at the SAME 3D
        // position. Welding by position makes those coincident vertices share a single
        // averaged normal, which removes the lighting seams that otherwise appear along
        // the twelve cube edges once the sphere is lit.
        java.util.HashMap<String, Vector3f> welded = new java.util.HashMap<>();

        Vector3f p0 = new Vector3f();
        Vector3f p1 = new Vector3f();
        Vector3f p2 = new Vector3f();
        Vector3f e1 = new Vector3f();
        Vector3f e2 = new Vector3f();
        Vector3f faceNormal = new Vector3f();

        for (int i = 0; i < indices.length; i += 3) {
            readPosition(positions, indices[i], p0);
            readPosition(positions, indices[i + 1], p1);
            readPosition(positions, indices[i + 2], p2);

            p1.sub(p0, e1);
            p2.sub(p0, e2);
            e1.cross(e2, faceNormal);

            accumulateWelded(welded, p0, faceNormal);
            accumulateWelded(welded, p1, faceNormal);
            accumulateWelded(welded, p2, faceNormal);
        }

        Vector3f n = new Vector3f();
        for (int v = 0; v < positions.length / 3; v++) {
            int base = v * 3;
            Vector3f acc = welded.get(positionKey(positions[base], positions[base + 1], positions[base + 2]));

            if (acc != null && acc.lengthSquared() > 1.0e-12f) {
                n.set(acc).normalize();
            } else {
                // Degenerate triangle fan: fall back to the outward radial direction.
                n.set(positions[base], positions[base + 1], positions[base + 2]).normalize();
            }

            normals[base] = n.x;
            normals[base + 1] = n.y;
            normals[base + 2] = n.z;
        }
    }

    private static String positionKey(float x, float y, float z) {
        // Quantize to ~1/4096 world units so coincident vertices (which differ only by
        // float rounding) collapse to one key, while genuinely distinct grid vertices
        // (spaced far wider apart) stay separate.
        long qx = Math.round(x * 4096.0);
        long qy = Math.round(y * 4096.0);
        long qz = Math.round(z * 4096.0);
        return qx + "," + qy + "," + qz;
    }

    private static void accumulateWelded(java.util.HashMap<String, Vector3f> welded, Vector3f position, Vector3f faceNormal) {
        String key = positionKey(position.x, position.y, position.z);
        Vector3f acc = welded.get(key);
        if (acc == null) {
            acc = new Vector3f();
            welded.put(key, acc);
        }
        acc.add(faceNormal);
    }

    private static void readPosition(float[] positions, int vertexIndex, Vector3f out) {
        int p = vertexIndex * 3;
        out.set(positions[p], positions[p + 1], positions[p + 2]);
    }

    public static final class MeshData {
        public final float[] positions;
        public final float[] normals;
        public final float[] textureCoordinates;
        public final int[] indices;

        public MeshData(float[] positions, float[] normals, float[] textureCoordinates, int[] indices) {
            this.positions = positions;
            this.normals = normals;
            this.textureCoordinates = textureCoordinates;
            this.indices = indices;
        }

        public int getIndexCount() {
            return this.indices.length;
        }
    }
}