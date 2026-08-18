# Implementation notes (verified ground truth for expansion)

Facts pulled from a source deep-dive (file:line tags). This is the reference for expanding Ch3/Ch4
without re-reading everything or fabricating. Re-verify a line before quoting a number in the final
text; code moves.

## RT shadows (`Engine/Shaders/DefaultLit.frag.hlsl`, `SS_RAYTRACING` permutation)

- Hard: 1 ray/light, `RayQuery<ACCEPT_FIRST_HIT_AND_END_SEARCH | CULL_NON_OPAQUE>`,
  `TraceRayInline(SceneTLAS, ...)` (L107-127). Origin offset `posWS + Ng*0.02 + L*0.01` (L111).
- Soft: `SHADOW_RAY_COUNT = 2` rays, jittered in a disk ⊥ L (uniform-disk + golden-ratio +
  frame-rotated IGN), averaged to a penumbra (L131,140-178). Sun cone `tan(SunAngularRadius)` (L199);
  point/spot `LightSourceRadius / dist` (L230,276).
- Per-light inside directional/point/spot loops (L536,556,584). `tMax=1e30` sun, `dist-0.05` local.
- `ShadowSoft` CVar picks hard/soft; `RTShadowEnabled` else raster shadow-map fallback (L193,204).

## Ambient occlusion (`Engine/Shaders/AO.comp.hlsl`)

- Half-res (`render.ao.scale`, 0.5), compute `[numthreads(8,8,1)]`.
- Rays/pixel `render.ao.rays` [1,16], default 2. Cosine hemisphere, IGN-rotated, TBN basis.
  Occupancy-only `ACCEPT_FIRST_HIT_AND_END_SEARCH`.
- `TMax=AORadius`; per-hit `1 - saturate(t/AORadius)`, scaled by `AOIntensity`.
- Inputs: `GBufferNormal` (oct normal .xy, roughness .z), `GBufferDepth` (D32). World pos from
  depth + `InvViewProj`.
- Writes `float4(ao,ao,ao, meanHitT)`: hit distance in .a for a REBLUR-style hit-dist guide.

## Reflections (`Engine/Shaders/Reflection.comp.hlsl`)

- **Full-res** (1:1 G-buffer), `[numthreads(8,8,1)]`.
- Reflect view vector off the **normal-mapped shading normal** (`GBufferShading`). Closest-hit
  `RayQuery<CULL_NON_OPAQUE>` (no accept-first).
- Glossy: cone jitter `roughness * ReflConeScale`, IGN-rotated, averaged over `render.reflections.rays`
  [1,16] default 1. `roughness==0` => one sharp ray.
- Hit shading `ShadeSurfaceHit` (`RTHitShading.hlsli` L134-161): geometry table (device-address
  vtx/idx + barycentric UV + bindless albedo), re-light sun+shadow-ray+IBL, **one bounce**. Miss =
  `PrefilteredCubeIndex` sky. Fresnel/BRDF/`ReflIntensity` applied later in forward.

## Global illumination (`Engine/Shaders/GI.comp.hlsl`)

- **Half-res** (`render.gi.scale`, 0.5). Diffuse indirect, **1 bounce** (`ShadeSurfaceHit` doesn't
  re-trace).
- SPP `render.gi.rays` [1,16] default 2. Cosine hemisphere + per-pixel/per-frame IGN rotation.
  `TMax=GIRange`, `CULL_NON_OPAQUE`. Miss = sky cube.
- Output = incoming **irradiance only** (receiver albedo multiplied at full res in forward). Forward
  REPLACES diffuse ambient with this (Lumen/RTXGI model, DefaultLit L590-600).

## Acceleration structures (`Platform/Vulkan/`)

- BLAS per mesh, lazy + cached (`Mesh::GetOrBuildBLAS`, `VulkanBlas.cpp`), opaque tris,
  `PREFER_FAST_TRACE`, built once via `ImmediateSubmit`.
- **TLAS full rebuild every dirty frame** (`MODE_BUILD_KHR`, no refit), `vkDeviceWaitIdle`+`Destroy`
  first (`VulkanTlas.cpp` L100-149). One instance per (Transform+Mesh), `instanceCustomIndex=i`.
- `TlasBuildSystem` in `SystemPhase::PreRender`, gated on `IsSceneDirtyThisFrame` (camera excluded),
  so a static scene does NOT rebuild.
- Extensions: `VK_KHR_acceleration_structure`, `VK_KHR_ray_query`, `VK_KHR_deferred_host_operations`;
  features spliced when `m_RayTracingSupported` (`VulkanContext.cpp` L362-466). **Inline ray-query
  only, no RT-pipeline extension.**

## Denoiser (SVGF, shared): `Render/Denoiser.{hpp,cpp}`, `Components/DenoiserInstance.hpp`

- Signal-agnostic; owns one `GITemporalPass` + one `GIDenoisePass`. Entry points `Temporal()` then
  `Atrous()`. Per-viewport state (`History[2]`, `Moments[2]`, `Scratch[2]` ping-pongs) in the
  `DenoiserInstance` component.
- **Shared by 3 signals: GI, AO, reflections** (`ViewportEffects.cpp` GI :219/:268, AO :438/:482,
  Reflections :655/:703). Header comment saying "GI and reflections" is stale; AO wired identically.
  AO alone uses the hit-distance guide (`HitDistPhi`), GI/refl pass 0 (no-op).
- Temporal (`GITemporal.comp.hlsl`, half-res): reproject by motion vectors `prev_uv = uv - velocity`;
  depth-relative disocclusion reject + 3×3 YCoCg-ish neighborhood color clamp (velocity-aware
  gamma); SVGF history-length accumulation `histLen=min(prev.b*depthConf+1,32)`, `alpha=max(alphaMin,
  1/histLen)`; temporal variance `μ2-μ1²`, 7×7 spatial fallback for young pixels (<4).
- À-trous (`GIDenoise.comp.hlsl`): 5×5 B3-spline tap, doubling stride `step=1<<i`, ≤5 iterations
  (`GIDenoisePass.cpp:45`). Edge-stops: normal `pow(dot,8)`, relative-depth `exp(-dRel*KDepthScale)`,
  **variance-guided luma** `exp(-|Δluma|/(LumaPhi*sqrt(varBlur)+eps))` (SVGF core, gated LumaPhi>0),
  + AO-only hit-dist term. Point-fetched guides.

## TAA / temporal resolve: `Render/Passes/TemporalResolvePass`, `Engine/Shaders/TemporalResolve.frag.hlsl`

- Jitter Halton(2,3), **16-phase** ring (`CameraJitterSystem.cpp:53`; helper default 8 overridden).
- Full-res resolve: closest-depth velocity dilation, Catmull-Rom history, **YCoCg** neighborhood
  clip, Karis rounded-box (3×3 + 5-tap cross) in tonemap-weighted space, velocity-aware gamma,
  slope-aware depth disocclusion.
- **Pure linear-HDR accumulation, no in-pass sharpen** (explicit comment). Matches the #44 invariant.

## Deviations from stock SVGF (for Ch3.5 "conditions/assumptions")

- No albedo demodulation *inside* the denoiser (albedo multiplied post-upsample).
- Extra neighborhood color clamp in the temporal pass (not in stock SVGF; added for moving-edge /
  reflection ghosting).
- Half-res GI/AO temporal+spatial (SVGF is full-res).
- Variance edge-stop is toggleable (`LumaPhi=0` disables it).
- α clamp differs (histLen capped 32; alphaMin from `1-MaxBlend`).

## Render graph + eval infra: `Render/RenderGraph.{hpp,cpp}`, `Systems/RenderSystem.cpp`

- Flat `std::vector<Pass>`, **insertion order, no dependency reordering**; each pass wrapped in a
  named GPU timestamp scope (`BeginGpuScope`), barriers from per-pass Reads/Writes.
- Per-viewport effect order (`ViewportEffects.cpp:1428`): DepthNormal → Velocity → GI → GITemporal →
  GIDenoise → GIUpsample → AO → AOTemporal → AODenoise → AOUpsample → Reflection → ReflectionTemporal
  → ReflectionDenoise → Forward (+ early-Z prepass + Sky) → Upscale → TemporalResolve → LdrChain
  (tonemap → FXAA → Sharpen) → Compare (ForwardGT + GTDownsample + PostProcessGT + Metrics +
  DatasetExport).

## CVars for the eval sweep (`Core/EngineCVars.cpp`, all Persist)

- Shadows: `render.shadows.mode` (0 off / 1 raster / 2 RT), `.soft`, `.sun_angle_deg`, `.source_radius`.
- AO: `render.ao.rt` (default **false**), `render.ao.rays` (2), `render.ao.scale` (0.5), `.radius`,
  `.intensity`, `.temporal`, `.denoise`.
- Reflections: `render.reflections.rt` (false), `.rays` (1), `.max_roughness` (0.8), `.range` (40).
- GI: `render.gi.rt` (false), `.rays` (2), `.scale` (0.5), `.range` (8), `.intensity`.
- Shared: `render.aa` (0 none/1 FXAA/2 TAA/3 DLAA), `render.gt.ssaa` (GT supersample), `render.metrics`,
  `render.compare`, `render.metrics.log`, `dataset.export`.
- All RT effects default **off**; shadows default raster. Helpers like `AoRTActive` also gate on
  device RT support.

## Measurement infra (Ch4)

- **Per-pass GPU ms:** RenderGraph timestamp scopes → `CollectGpuScopes` (1-frame lag) →
  `PerfBenchAccumulator` → `ToJson` (avg/min/max per pass, totalGpuMs, device, config). 15-frame warmup.
- **perf-bench.py matrix:** rt-off → shadows → +ao → +refl → +gi, each `SS_RENDER_*` env, TAA on,
  `SS_CONFIG_IGNORE=1`; diff vs `Scripts/perf-baseline/`, fail >15%.
- **PSNR+SSIM:** `MetricsPass` GPU reduction, present vs GT-present (1-frame lag), gated
  `render.metrics`+`render.compare`; `render.metrics.log` for headless.
- **Ground truth:** compare mode renders a 2nd full-res **unjittered** forward into `GroundTruthTarget`;
  `render.gt.ssaa` (2×) + linear-HDR box downsample = anti-aliased reference.
- **Dataset export:** `dataset.export` writes .npy tuples (LR color, motion, HDR GT, LDR GT) + manifest.
- **Scene:** perf-bench default `Sponza.world` = **10 lights** (3 spot + 6 point + 1 directional).
  `StressScene` code-generated (grid of meshes, 2 directional lights), bakeable to `Stress.world`.

## Two measurement caveats that affect Ch4 honesty (IMPORTANT)

1. **"Forward-ms delta = per-effect cost" is only literally true for shadows and reflections** (those
   are inline in the Forward pass). GI and AO run as their own half-res passes (`GI`/`AO`/`*Upsample`
   scopes), so their cost is split across those scopes, not Forward alone. Use per-pass-scope deltas
   (and totalGpuMs), not the Forward-delta shorthand, when attributing GI/AO cost.
2. **The PSNR/SSIM ground truth forces raster shadows** (`forceRasterShadow=true` on the GT forward).
   So with RT shadows enabled, `MetricsPass` compares RT-vs-raster, not RT-vs-reference-RT. For a
   clean quality number, either measure the non-shadow effects against GT, or build an RT-shadow GT
   path, or state the caveat explicitly. Decide before quoting a shadow PSNR.
