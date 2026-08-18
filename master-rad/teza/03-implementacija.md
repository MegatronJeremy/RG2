# 3. Opis implementacije

The core chapter: how the four effects and the denoiser are built inside Snowstorm Engine. Every
concrete claim here is checkable against the source; keep file/pass names exact.

## 3.1 Snowstorm Engine (pregled)

EXPAND:
- What the platform provides so the thesis is about the RT path, not engine-writing: EnTT ECS,
  Systems/Singletons/Services, a backend-agnostic `Render/` layer over a Vulkan RHI
  (`Platform/Vulkan/`, volk + VMA + spirv-reflect), HLSL compiled to SPIR-V via dxc, ImGui editor.
- Scope the description tightly; cite AGENTS.md architecture only as far as the render path needs.

## 3.2 Render graf i struktura frejma

EXPAND (verified order, see notes-implementation.md):
- `RenderGraph` is a flat insertion-ordered pass list; each pass gets a named GPU timestamp scope
  (this is what the perf tables in Ch4 read).
- Real per-viewport order: DepthNormal (G-buffer) -> Velocity -> **GI -> GITemporal -> GIDenoise ->
  GIUpsample** -> **AO -> AOTemporal -> AODenoise -> AOUpsample** -> **Reflection -> temporal ->
  denoise** -> **Forward** `DefaultLit` (inline RT shadows + early-Z prepass + Sky; samples the
  already-denoised+upsampled GI/AO/reflection textures) -> Upscale -> TemporalResolve (TAA) ->
  LdrChain (tonemap -> FXAA -> Sharpen) -> Compare (GT + metrics).
- Key structural point: GI/AO/reflections run as compute passes **before** forward, which then
  consumes their results; RT shadows are the one effect inline in forward. Explain why (the G-buffer
  they need, and letting forward do one lit combine).
- The half-res (GI/AO) + G-buffer-prepass + bilateral-upsample pattern, and why (cost). Reflections
  are full-res.
- Diagram of the frame graph.

## 3.3 Izgradnja struktura ubrzanja (BLAS/TLAS)

EXPAND (verified):
- BLAS per mesh (lazy, cached, `PREFER_FAST_TRACE`). TLAS **full rebuild each dirty frame** (no
  refit path), gated on `IsSceneDirtyThisFrame` (camera excluded), so a static scene skips it; runs
  in `SystemPhase::PreRender`. Discuss the rebuild-vs-refit tradeoff as a limitation (Ch5).
- One TLAS instance per (Transform+Mesh) entity, `instanceCustomIndex=i` feeding the geometry table
  in `RTHitShading.hlsli`.
- Inline ray-query only: `VK_KHR_ray_query` + `VK_KHR_acceleration_structure`, no RT-pipeline
  extension (ties back to 1.2).

## 3.4 Četiri efekta preko inline ray query

Shared structure: each effect traces `RayQuery` against the TLAS; hit shading via
`Engine/Shaders/Include/RTHitShading.hlsli`.

### 3.4.1 Senke (RT shadows)
EXPAND: inline visibility ray per light in the forward pass (`Engine/Shaders/DefaultLit.frag.hlsl`);
hard vs soft (cone/area sampling); why shadows live in the forward pass, not a separate one.

### 3.4.2 Ambijentalna okluzija (AO)
EXPAND: `Engine/Shaders/AO.comp.hlsl`, half-res, hemisphere-sampled short rays over the depth+normal
G-buffer; ray length / falloff; feeds the shared denoiser.

### 3.4.3 Refleksije (reflections)
EXPAND: `Engine/Shaders/Reflection.comp.hlsl`, **full-res** (unlike half-res AO/GI). Reflect the
view vector off the normal-mapped shading normal; glossy via roughness-scaled cone jitter over
`render.reflections.rays` (default 1); closest-hit shaded via `RTHitShading.hlsli` (one bounce:
sun + shadow ray + IBL); Fresnel/BRDF applied later in forward.

### 3.4.4 Globalno osvetljenje (GI)
EXPAND: `Engine/Shaders/GI.comp.hlsl`, half-res diffuse indirect, bounce count, cosine sampling;
temporal + spatial denoise is what makes it usable. This is the headline effect.

## 3.5 Denoising (SVGF)

EXPAND:
- The reusable, signal-agnostic denoiser (`Render/Denoiser.{hpp,cpp}`, `Components/DenoiserInstance.hpp`)
  shared by **three signals: GI, AO, and reflections** (one instance per signal; AO alone uses the
  hit-distance guide). This reuse is a design-decision worth calling out.
- Temporal reprojection + variance (`Render/Passes/GITemporalPass`, `Engine/Shaders/GITemporal.comp.hlsl`).
- Variance-guided à-trous spatial filter (`Render/Passes/GIDenoisePass`,
  `Engine/Shaders/GIDenoise.comp.hlsl`); edge-stopping on depth/normal/luminance.
- Deviations from the paper (what was simplified and why); `GIDenoise.comp` is the occupancy-limited
  shader (192 VGPR, 8/16 waves) per the RGA gate; tie to Ch4.

## 3.6 TAA / temporal resolve

EXPAND: `Render/Passes/TemporalResolvePass`, `Engine/Shaders/TemporalResolve.frag.hlsl`; jitter,
history reprojection via motion vectors, neighborhood clamp; runs in linear HDR (accumulation only;
display-space sharpening stays post-tonemap, the #44 invariant).

## 3.7 Reproducibilnost i alati

EXPAND: how the evaluation in Ch4 is produced and kept honest: CVar registry (effect toggles),
`perf-bench` (per-pass GPU timings, A/B config matrix), `smoke-test` (validation/crash gate),
`rga-occupancy` (static register/occupancy gate), GPU timestamp scopes (`BeginGpuScope`), the
Performance panel. This subsection is what makes Ch4's numbers reproducible.
