# 2. Pregled postojećih rešenja i tehnologija

This chapter sets up the background needed to read Ch3 and the comparison baselines Ch4 measures
against. Two halves: the theory (2.1-2.3), then the existing real-time solutions (2.4-2.5).

## 2.1 Rasterizacija naspram trasiranja zrakova

EXPAND:
- Rasterization pipeline in one paragraph: project triangles, resolve visibility via depth buffer;
  strengths (throughput, primary visibility) and the structural limit (no scene-wide queries).
- Ray tracing in one paragraph: cast rays, intersect the scene, evaluate the rendering equation via
  sampling; strengths (arbitrary visibility) and cost (per-ray traversal, noise).
- The rendering equation as the shared target both approximate.

## 2.2 Strukture ubrzanja: BVH, TLAS/BLAS

EXPAND:
- Why a spatial acceleration structure is mandatory (naive O(rays·triangles) is hopeless).
- BVH basics; the Vulkan two-level split: BLAS (per-mesh geometry) + TLAS (per-instance transforms).
- Build vs update (refit), and what that costs per frame for dynamic scenes.

## 2.3 Trasiranje zrakova u Vulkan-u: RT-pipeline naspram ray query

EXPAND:
- The Vulkan RT extension set: `VK_KHR_acceleration_structure`, `VK_KHR_ray_tracing_pipeline`,
  `VK_KHR_ray_query`.
- Ray tracing pipeline: shader stages (raygen/closest-hit/miss/...), the SBT, hardware ray
  scheduling, recursion.
- Ray query: inline `RayQuery` from any stage, no SBT, no recursion; caller writes the traversal
  loop. Table comparing the two on integration cost, flexibility, performance.
- Justify the ray-query choice for this thesis (ties back to 1.2).

## 2.4 Postojeća real-time rešenja za GI / RT efekte

The comparison set. For each: how it works, what it approximates well, where it fails (the failure
mode Ch4 will point at).

EXPAND:
- **Screen-space:** SSAO/HBAO, SSR, SSGI. Cheap, but limited to on-screen data (off-screen and
  disocclusion artifacts). These are the cheap baseline the RT effects improve on.
- **Voxel:** VXGI / voxel cone tracing. Scene-wide but coarse, memory-heavy, leaking.
- **Probe / irradiance field:** DDGI, NVIDIA RTXGI. Ray-traced but probe-interpolated (low
  frequency, placement-sensitive).
- **Hybrid production systems:** Unreal **Lumen** (software + hardware ray tracing). The bar to
  acknowledge, not to beat.
- **Reservoir sampling:** ReSTIR, ReSTIR GI. State of the art for many-light and GI sampling;
  positioned as future work (Ch5).

## 2.5 Uklanjanje šuma (denoising) za RT

EXPAND:
- Why RT effects at real-time sample counts are noisy -> denoising is mandatory, not optional.
- **SVGF** (Schied 2017): temporal reprojection + variance-guided à-trous spatial filter. The
  method implemented in this thesis; explain enough here that Ch3 can be about *this engine's*
  version rather than re-deriving.
- A-SVGF, NVIDIA NRD (ReBLUR/ReLAX), ML denoisers (OIDN): the alternatives, one line each.
- TAA (Karis 2014) as the temporal-stability layer over the denoised result.
