# 3. Opis implementacije

This chapter describes how the four ray-traced effects and the shared denoiser are implemented
inside the Snowstorm engine. It first scopes what the host engine provides (3.1), then the
render-graph structure the effects plug into (3.2) and the acceleration structures they trace
against (3.3), before describing each effect (3.4), the SVGF denoiser that makes the noisy effects
usable (3.5), the temporal anti-aliasing resolve (3.6), and the tooling that makes the Chapter 4
measurements reproducible (3.7). The emphasis follows the thesis focus: the ray tracing itself and
its cost, rather than an exhaustive account of every engine subsystem.

## 3.1 Snowstorm Engine (pregled)

Snowstorm is a Vulkan engine the author wrote from scratch; this thesis uses it as the host for the
ray-tracing passes and does not treat the engine itself as the contribution. The parts that matter
for the RT path are four. An EnTT-based entity-component-system whose Systems produce the per-frame
render work. A backend-agnostic `Render/` layer (`RendererAPI`, `RenderGraph`, `Pipeline`, `Shader`,
`Buffer`, `Texture`, `Material`) implemented over a Vulkan RHI in `Platform/Vulkan/`, using volk for
entry-point loading, Vulkan Memory Allocator for allocations, and spirv-reflect to derive descriptor
layouts from the compiled shaders. An HLSL shader pipeline compiled to SPIR-V through dxc. And a
bindless descriptor model, which is what lets one ray-query hit-shading routine index any mesh's
vertices, indices, and material without per-draw descriptor churn (Section 3.4). The ImGui editor
hosts the CVar console and the performance readouts used to drive and measure the effects
(Section 3.7). Everything below is a set of passes and shaders added on top of this host.

## 3.2 Render graf i struktura frejma

The renderer is organized as a `RenderGraph`: a flat, insertion-ordered list of passes, each
declaring the resources it reads and writes so the graph can insert the Vulkan layout barriers
between them. There is no dependency solver and no automatic reordering; execution order is exactly
the order in which passes are appended (`RenderGraph::Execute`). Each pass is wrapped in a named GPU
timestamp scope (`BeginGpuScope`), and those names are the per-pass rows in every performance table
in Chapter 4, so the graph structure and the measurement granularity are one and the same.

The per-viewport frame builds in this order:

> DepthNormal (G-buffer: depth + geometric normal) → Velocity (motion vectors) → GI → GITemporal →
> GIDenoise → GIUpsample → AO → AOTemporal → AODenoise → AOUpsample → Reflection → ReflectionTemporal
> → ReflectionDenoise → Forward (`DefaultLit`, including the early-Z depth prepass, inline RT shadows,
> and the sky) → Upscale → TemporalResolve (TAA) → tonemap → FXAA → Sharpen → the comparison and
> metrics passes.

The structural decision worth stating: global illumination, ambient occlusion, and reflections run
as compute passes *before* the forward pass, each writing a denoised, full-resolution texture that
the forward shader then samples. Only ray-traced shadows are traced inline, inside the forward
shader. There are two reasons. GI, AO, and reflections need the depth+normal G-buffer as their
starting surface, so they must follow DepthNormal but can precede shading. And running them ahead of
forward lets the forward pass do a single lit combine (direct lighting plus sampled indirect, AO,
and reflection) instead of interleaving trace and shade. Shadows are the exception because a shadow
ray is a cheap per-light visibility test, naturally evaluated at the point each light's contribution
is accumulated, so keeping it inline avoids allocating a separate visibility buffer per light. This
split, screen-space compute effects feeding a forward combine while shadows stay inline, follows how
hybrid renderers such as Unreal's Lumen separate their screen passes from hit lighting.

GI and AO are traced at half resolution (`render.gi.scale`, `render.ao.scale`, both 0.5 by default)
and bilaterally upsampled to full resolution before the forward pass samples them; reflections are
traced at full resolution. Half-res tracing is the single biggest cost lever for the two hemispheric
gather effects, since it quarters the ray count, and the denoiser plus the depth/normal-aware
upsample are what keep the half-res result usable. Section 4.2 quantifies what this buys.

## 3.3 Izgradnja struktura ubrzanja (BLAS/TLAS)

Ray queries trace against a two-level acceleration structure. Each unique mesh owns one bottom-level
structure (BLAS), built lazily the first time the mesh is used and cached on the mesh
(`Mesh::GetOrBuildBLAS`): opaque triangle geometry referenced by device address (positions as
R32G32B32, 32-bit indices), built once with the `PREFER_FAST_TRACE` flag. The top-level structure
(TLAS) holds one instance per (Transform, Mesh) entity, with `instanceCustomIndex` set to the
instance index so the hit shader can resolve the geometry from a table (Section 3.4).

The TLAS is rebuilt in full on every frame the scene is marked dirty (`TlasBuildSystem`, in the
`PreRender` phase). There is no refit path: a dirty frame destroys and rebuilds the structure
(`MODE_BUILD_KHR`) behind a device wait. The dirty check excludes the camera, so a scene whose
geometry and transforms are static does not rebuild the TLAS even as the camera moves, which is the
common case for the benchmark scene. A full rebuild on every dynamic frame is heavier than a refit
would be; this is called out as a limitation in Chapter 5 and was chosen for implementation
simplicity given that the test scenes are largely static.

The engine uses inline ray queries only. It enables `VK_KHR_ray_query` and
`VK_KHR_acceleration_structure` (plus `VK_KHR_deferred_host_operations` for the build) but not the
ray-tracing-pipeline extension, consistent with the rationale in Section 1.2. There is no shader
binding table; every trace is a `RayQuery` object created inside an otherwise ordinary compute or
fragment shader.

## 3.4 Četiri efekta preko inline ray query

All four effects share the same core operation: construct a ray, create a `RayQuery` against the
scene TLAS, run its traversal loop, and act on the result. They differ in where the ray starts, how
many are cast, what a hit returns, and whether the query needs the closest hit or merely any hit.
The effects that shade their hits (reflections and GI, plus the secondary lighting they evaluate)
share one routine, `ShadeSurfaceHit` in `RTHitShading.hlsli`, which resolves the hit triangle
through the bindless geometry table and evaluates a single bounce of lighting. Shadows and AO need
only a visibility answer and use the cheaper any-hit traversal.

### 3.4.1 Senke (RT shadows)

Shadows are the one effect traced inline in the forward shader (`DefaultLit.frag.hlsl`, in the
`SS_RAYTRACING` permutation), evaluated per light as that light's contribution is accumulated. A
shadow ray is a pure visibility test, so it uses the cheapest traversal: `RayQuery` with
`ACCEPT_FIRST_HIT_AND_END_SEARCH | CULL_NON_OPAQUE`, which stops at the first opaque hit rather than
searching for the closest. Any committed hit between the surface and the light marks the surface as
shadowed. The ray origin is offset along the geometric normal and toward the light
(`positionWS + Ng*0.02 + L*0.01`) to avoid self-intersection.

Two quality levels are exposed through the `render.shadows.soft` CVar. The hard path casts one ray
straight at the light. The soft path casts `SHADOW_RAY_COUNT = 2` rays whose directions are jittered
inside a disk perpendicular to the light direction, and averages the hits into a penumbra factor in
[0,1]. The disk radius encodes the light's angular size: the sun uses `tan(SunAngularRadius)`, while
point and spot lights use `LightSourceRadius / distanceToLight`, so a physically larger or nearer
source gives a softer edge. Directions are decorrelated per pixel and per frame with an
interleaved-gradient-noise hash, spreading the two-sample penumbra across frames for the temporal
accumulator to resolve (Section 3.6). Each light traces its own ray or rays inside the directional,
point, and spot loops; the sun uses an effectively infinite `tMax`, local lights clamp `tMax` just
short of the light. With ray-traced shadows disabled the shader falls back to raster shadow maps.

Keeping shadows inline reuses the light loop the forward shader already runs and avoids a separate
per-light visibility buffer. The cost is that shadow tracing is folded into the forward-pass timing
rather than isolated in its own scope, which Section 4.2 accounts for.

### 3.4.2 Ambijentalna okluzija (AO)

Ambient occlusion is a compute pass (`AO.comp.hlsl`) run at half resolution. For each pixel it
reconstructs world position from the depth G-buffer and casts `render.ao.rays` short rays (default
2, clamped to [1,16]) over the cosine-weighted hemisphere around the geometric normal, oriented by a
tangent basis and rotated per pixel by interleaved gradient noise. Occlusion is a visibility query,
so it too uses `ACCEPT_FIRST_HIT_AND_END_SEARCH`. Rays are limited to `render.ao.radius`
(`TMax = AORadius`); a hit contributes `1 - saturate(t / AORadius)`, so nearer occluders darken
more, and the result is scaled by `render.ao.intensity`.

The pass writes `float4(ao, ao, ao, meanHitT)`: the occlusion value, and in alpha the mean distance
to the occluders. That hit distance is not cosmetic; it drives a hit-distance-guided term in the
denoiser (Section 3.5), the same idea NVIDIA's ReBLUR uses to scale the spatial filter by how far
the occluder was. The half-resolution result is denoised and bilaterally upsampled before the
forward pass multiplies it into the ambient term.

### 3.4.3 Refleksije (reflections)

Reflections are a compute pass (`Reflection.comp.hlsl`) run at full resolution, the only ray-traced
effect not traced at half res, since reflection detail is view-dependent and does not tolerate the
blur that half-res tracing plus upsampling introduces. For each pixel the pass reconstructs world
position and reflects the view vector about the normal-mapped shading normal (read from a separate
shading-normal G-buffer, not the geometric normal, so normal maps are mirrored correctly). It needs
the closest hit rather than any hit, so it uses `RayQuery<CULL_NON_OPAQUE>` without early
termination.

Glossy reflections are approximated by jittering each ray inside a cone whose half-angle scales with
surface roughness (`roughness * ReflConeScale`), averaged over `render.reflections.rays` (default
1); a mirror surface (`roughness == 0`) collapses to one sharp ray. Hits are shaded by
`ShadeSurfaceHit`, which resolves the triangle through the bindless geometry table and evaluates one
bounce (sun lighting with its own shadow ray, plus image-based ambient); a miss samples the
prefiltered sky cube. The pass writes raw reflected radiance plus hit distance; the Fresnel term,
the BRDF weighting, and `render.reflections.intensity` are applied afterward in the forward pass,
where the reflection is combined with the rest of the shading.

### 3.4.4 Globalno osvetljenje (GI)

Global illumination is the headline effect and the most expensive. It is a compute pass
(`GI.comp.hlsl`) run at half resolution that computes one bounce of diffuse indirect light. For each
pixel it casts `render.gi.rays` rays (default 2, clamped to [1,16]) over the cosine-weighted
hemisphere, rotated per pixel and per frame by interleaved gradient noise, out to `render.gi.range`.
Each ray that hits geometry is shaded by `ShadeSurfaceHit` (sun plus image-based ambient, one
bounce, since the routine does not itself re-trace); a ray that misses samples the sky cube.

The pass outputs incoming irradiance only, without the receiver's albedo, which is multiplied in at
full resolution in the forward pass. This is the demodulated-irradiance convention that both the
SVGF denoiser and probe systems such as DDGI/RTXGI rely on: filtering irradiance rather than final
color keeps the denoiser's edge-stopping from being misled by albedo texture detail. The forward
pass then replaces its flat ambient term with this ray-traced indirect, the same substitution Lumen
and RTXGI make. At two rays per pixel and half resolution the raw output is very noisy; it is usable
only after the temporal-plus-spatial denoise of Section 3.5, which is the point of the whole
pipeline and the subject of much of Chapter 4.

## 3.5 Denoising (SVGF)

The ray-traced effects are sampled at one or two rays per pixel, which is far too noisy to display,
so a denoiser is not optional; it is what turns the noisy estimates into usable images. Snowstorm
implements a variant of Spatiotemporal Variance-Guided Filtering (SVGF), the standard real-time
reconstruction filter for path-traced effects, as a single reusable component.

The denoiser is signal-agnostic. One `Denoiser` class (`Render/Denoiser.{hpp,cpp}`) drives two
passes, a temporal accumulation (`Temporal`) and a spatial à-trous filter (`Atrous`), and all
per-viewport GPU state (history, moments, and scratch ping-pong textures) lives in a
`DenoiserInstance` component the caller owns. The same denoiser is instantiated three times, for GI,
AO, and reflections; each signal gets its own instance and configuration but runs identical code.
This reuse is a deliberate design choice: the noisy estimate, its variance inputs, and the
depth/normal G-buffer are the only signal-specific data, and everything else is shared. AO alone
enables the hit-distance guide from 3.4.2; GI and reflections pass a zero weight there, making that
term a no-op. Reflections reuse GI's temporal shader, worth noting as a limitation since a reflection
history has view-dependent content that a diffuse-tuned reprojection does not perfectly handle.

### 3.5.1 Temporalna akumulacija

The temporal pass (`GITemporal.comp.hlsl`, at trace resolution) reprojects the previous frame's
result by the motion vectors (`prev_uv = uv - velocity`) and blends it with the current noisy input.
History is rejected where reprojection is invalid: off-screen samples and the first frame reset to
the current input, and a relative-depth test rejects disoccluded pixels. The blend follows SVGF's
history-length scheme: a per-pixel accumulated history length, capped at 32 frames, sets the blend
weight `max(alphaMin, 1 / historyLength)`, so a freshly disoccluded pixel weights the current frame
heavily while a long-lived pixel averages many frames. First and second luminance moments accumulate
with the same weight, and their difference is the temporal variance that guides the spatial filter;
pixels too young for a stable temporal variance (history under four frames) fall back to a 7x7
spatial variance estimate.

One addition over stock SVGF is a neighborhood color clamp: the reprojected history is clipped toward
the mean of a 3x3 current-frame neighborhood, with the clamp weakened when the pixel is static and
tightened when it moves. This is a TAA-style clamp, absent from the original SVGF, added to suppress
ghosting on moving edges and in reflections where depth/normal rejection alone is insufficient.

### 3.5.2 Prostorni à-trous filter

The spatial pass (`GIDenoise.comp.hlsl`) is the à-trous wavelet filter at the core of SVGF. Each
iteration is a 5x5 tap gather with a B3-spline kernel, and successive iterations double the tap
stride (`step = 1 << i`), so a few iterations reach wide spatial support while touching few taps. The
engine runs up to five iterations, configurable per signal.

The weights make the filter edge-aware. Each tap carries three edge-stopping terms: a normal term
`pow(saturate(dot(N, Ntap)), 8)`, a relative linearized-depth term `exp(-relativeDepth * scale)`,
and the variance-guided luminance term `exp(-|dLuma| / (LumaPhi * sqrt(variance) + eps))` that is the
defining idea of SVGF. Because the luminance weight scales with the square root of the filtered
variance, the filter blurs aggressively where the signal is noisy and preserves detail where it has
converged. Variance itself is filtered with the squared tap weights, and all guide buffers are
point-sampled to avoid bleeding across edges. The variance term can be disabled (`LumaPhi = 0`),
reducing the filter to a plain bilateral blur, which is a useful baseline in Chapter 4.

### 3.5.3 Odstupanja od SVGF i cena

The implementation departs from the paper in a few places, all noted so Chapter 4's quality numbers
are read correctly: the denoiser filters raw irradiance and remultiplies albedo after upsampling
rather than demodulating inside the filter as SVGF does; the extra temporal color clamp above is not
in SVGF; GI and AO are filtered at half resolution where SVGF is full-resolution; and the variance
edge-stop is optional. `GIDenoise.comp` is the one shader the static occupancy gate flags as
register-limited (192 VGPRs, 8 of 16 possible wavefronts on the RX 7900 XTX), which bounds its
throughput; Section 4.4 measures the denoiser's cost against the quality it recovers.

## 3.6 TAA / temporal resolve

After the forward pass produces the shaded HDR image, a temporal anti-aliasing resolve
(`TemporalResolvePass`, `TemporalResolve.frag.hlsl`) accumulates it across frames to remove aliasing
and to converge the residual noise the per-effect denoisers leave behind. The camera projection is
jittered every frame by a Halton(2,3) sequence over a 16-phase cycle, so each frame samples slightly
different sub-pixel positions. The resolve reprojects the previous output by the motion vectors (with
a closest-depth dilation so thin features fetch the right velocity), reconstructs the history with a
Catmull-Rom filter to reduce reprojection blur, and clips it against the current 3x3 neighborhood in
YCoCg space using a Karis rounded-box bound, with the clip loosened for static pixels and tightened
under motion.

The resolve runs in linear HDR and does accumulation only. This is a deliberate invariant: any
perceptual or display-space operation (sharpening, contrast) is kept out of this pass and applied
after tonemap, since a per-channel curve applied before tonemap turns an accumulation overshoot into
a hue shift. Sharpening therefore lives in a separate post-tonemap pass, not here.

## 3.7 Reproducibilnost i alati

The measurements in Chapter 4 are produced by instrumentation built into the engine, which is what
makes them reproducible rather than one-off captures. Every effect is toggled and tuned through a
console-variable registry, so a benchmark configuration is a set of CVar values (which effects are
on, ray counts, resolutions) rather than a code change, and the same CVars can be set from the
command line for headless runs. Each render-graph pass is bracketed by a GPU timestamp scope, and a
harness (`perf-bench`) averages those per-pass timings over a fixed frame budget past a warmup, writes
them to JSON, and diffs against a committed baseline; it sweeps a fixed matrix of effect
configurations so the per-pass cost of each effect can be read off directly. Reconstruction quality
is measured in-engine by a metrics pass computing PSNR and SSIM against a ground-truth image on the
GPU, where the ground truth is a second, unjittered, optionally supersampled render of the same
frame. A smoke harness boots the engine headlessly and fails on any crash or Vulkan validation error,
and a static shader-occupancy gate tracks register pressure. Section 4.1 combines these into the
evaluation methodology.
