# 1. Uvod

## 1.1 Problem i motivacija

Real-time rendering has long approximated the global light-transport effects that make an image
look real (indirect illumination, contact shadows, glossy reflections, ambient occlusion) because
solving them exactly per frame was too expensive. Rasterization resolves primary visibility
cheaply but has no native notion of "what else can this point see," so these effects are faked with
screen-space or precomputed methods that break whenever the needed information is off-screen or
dynamic. Hardware ray tracing (RTX / RDNA2+) makes per-pixel visibility queries against the whole
scene feasible at interactive rates, which reopens these effects as first-class, physically-grounded
passes.

EXPAND:
- The accuracy vs performance tension, stated concretely (what screen-space AO/SSR/SSGI get wrong,
  with the off-screen/disocclusion failure cases).
- Why *full* path tracing is still out of budget for real-time on this class of hardware -> motivates
  a hybrid split (rasterize primary, ray-trace secondary) and heavy reliance on denoising.
- One or two figures: same scene, screen-space vs ray-traced effect, to make the gap visible.

## 1.2 Zašto hibridni pristup i zašto ray query (a ne RT-pipeline)

The chosen design rasterizes the primary view and adds ray-traced effects as passes on top, using
Vulkan **inline ray query** (`VK_KHR_ray_query`) rather than the separate ray tracing pipeline.
Ray query lets any shader stage trace a ray inline, with no shader binding table and no second
pipeline type, so effects drop into an existing forward renderer as ordinary compute/fragment passes.

EXPAND:
- Ray query vs ray tracing pipeline: integration cost, flexibility, where each wins; why inline fits
  an incremental "add one effect at a time" engine.
- The tradeoff being accepted (no hardware SBT scheduling / no recursive TraceRay) and why it is fine
  for these effects.

## 1.3 Cilj i istraživačko pitanje

Goal: implement shadows, ambient occlusion, reflections, and global illumination through inline ray
query in a self-written Vulkan engine, and measure the cost and quality of each. Research question:
what does each effect cost on the frame budget, and how do ray count and denoising trade quality
against time?

EXPAND:
- Sharpen into measurable sub-questions (per-effect ms; spp vs PSNR/SSIM; denoiser on/off; half-res
  vs full-res).
- Scope line: single scene class, single primary GPU (RX 7900 XTX), diffuse GI, offline-quality
  reference for the quality metrics.

## 1.4 Doprinosi

EXPAND (turn into prose once Ch3/Ch4 are firm):
- An integrated, open (public-domain) hybrid ray-query implementation of four effects in one engine.
- A per-effect GPU cost breakdown produced by a reproducible A/B benchmark harness (perf-bench).
- An evaluation of a self-implemented SVGF denoiser on the AO/GI signals (quality gain, cost,
  temporal stability).
- The reusable half-res + G-buffer-prepass + denoise pattern shared across effects.

## 1.5 Struktura rada

EXPAND: one short paragraph mapping Ch2 (background + existing solutions) -> Ch3 (implementation) ->
Ch4 (evaluation vs those solutions) -> Ch5 (conclusion, future work).
