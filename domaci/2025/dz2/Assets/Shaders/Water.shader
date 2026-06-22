// Water surface shader (RG2 DZ2).
//
// Step (b): the vertex stage reads the runtime height map and displaces vertices
// vertically. The fragment stage tints by height so the waves are clearly visible.
// Lighting, cube-map reflection, specular and Fresnel transparency arrive in step (c)/(d).
Shader "RG2/Water"
{
    Properties
    {
        _WaterColor ("Water Color", Color) = (0.1, 0.3, 0.5, 1)
        _HeightMap ("Height Map", 2D) = "gray" {}
        _MaxWaveHeight ("Max Wave Height", Float) = 0.5
    }
    SubShader
    {
        Tags { "RenderType" = "Opaque" }

        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            sampler2D _HeightMap;
            float _MaxWaveHeight;
            fixed4 _WaterColor;

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float4 pos : SV_POSITION;
                float2 uv : TEXCOORD0;
                float height : TEXCOORD1;
            };

            v2f vert(appdata v)
            {
                v2f o;
                // Vertex texture fetch: tex2Dlod (explicit LOD) is required in the vertex stage.
                float h = tex2Dlod(_HeightMap, float4(v.uv, 0, 0)).r;
                // Center around 0 so the surface waves up and down symmetrically.
                v.vertex.y += (h - 0.5) * _MaxWaveHeight;

                o.pos = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                o.height = h;
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                // Temporary height tint (step b) — replaced by proper shading in step (c).
                return _WaterColor * (0.4 + i.height);
            }
            ENDCG
        }
    }
}
