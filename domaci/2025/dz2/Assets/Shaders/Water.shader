// Water surface shader (RG2 DZ2).
//
// Vertex stage: reads the runtime height map and displaces vertices vertically.
// Fragment stage (step c): per-fragment normal from the runtime normal map, then
//   - cube-map (ambient) reflection sampled from the scene environment probe,
//   - specular highlight of the directional light (Blinn-Phong),
//   - tinted by the water color.
// Fresnel-based transparency is added in step (d).
Shader "RG2/Water"
{
    Properties
    {
        _WaterColor ("Water Color", Color) = (0.1, 0.3, 0.5, 1)
        _HeightMap ("Height Map", 2D) = "gray" {}
        _NormalMap ("Normal Map", 2D) = "bump" {}
        _MaxWaveHeight ("Max Wave Height", Float) = 0.5
        _Shininess ("Shininess", Range(1, 256)) = 64
        _Reflectivity ("Reflectivity", Range(0, 1)) = 0.6
    }
    SubShader
    {
        Tags { "RenderType" = "Opaque" }

        Pass
        {
            Tags { "LightMode" = "ForwardBase" }

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            #include "Lighting.cginc"

            sampler2D _HeightMap;
            sampler2D _NormalMap;
            float _MaxWaveHeight;
            float _Shininess;
            float _Reflectivity;
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
                float3 worldPos : TEXCOORD1;
            };

            v2f vert(appdata v)
            {
                v2f o;
                // Vertex texture fetch: tex2Dlod (explicit LOD) is required in the vertex stage.
                float h = tex2Dlod(_HeightMap, float4(v.uv, 0, 0)).r;
                v.vertex.y += (h - 0.5) * _MaxWaveHeight;

                o.pos = UnityObjectToClipPos(v.vertex);
                o.worldPos = mul(unity_ObjectToWorld, v.vertex).xyz;
                o.uv = v.uv;
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                // Per-fragment object-space normal from the runtime normal map.
                float3 nObj = normalize(tex2D(_NormalMap, i.uv).xyz);
                float3 n = normalize(UnityObjectToWorldNormal(nObj));

                float3 viewDir = normalize(_WorldSpaceCameraPos - i.worldPos);
                float3 lightDir = normalize(_WorldSpaceLightPos0.xyz); // directional light

                // Cube-map (ambient) reflection from the scene environment probe.
                float3 reflDir = reflect(-viewDir, n);
                float4 envSample = UNITY_SAMPLE_TEXCUBE(unity_SpecCube0, reflDir);
                float3 reflection = DecodeHDR(envSample, unity_SpecCube0_HDR);

                // Specular component of the directional light (Blinn-Phong).
                float3 halfVec = normalize(lightDir + viewDir);
                float spec = pow(saturate(dot(n, halfVec)), _Shininess);
                float3 specular = spec * _LightColor0.rgb;

                float3 baseCol = lerp(_WaterColor.rgb, reflection, _Reflectivity);
                float3 col = baseCol + specular;
                return fixed4(col, 1.0);
            }
            ENDCG
        }
    }
}
