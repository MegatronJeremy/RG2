# 5. Zaključak

> PPK order (slide 30/52): open with a recap of the goals set in the **zadatak**, then a critical
> review of the most significant results (advantages, limitations, application areas), then future
> work. Keep to 1-1.5 pages.

## 5.1 Rezime (osvrt na ciljeve iz zadatka)

EXPAND: restate the zadatak goals and what was achieved against them, in the terms Ch1's research
question set. One paragraph: four ray-query effects integrated into a rasterized forward renderer, a
self-implemented SVGF denoiser, and a per-effect cost + quality evaluation on RDNA3. Pull the
headline numbers from Ch4 once they exist (do not pre-write them). Note application areas
(real-time engines that want correct off-screen lighting without a full path tracer).

## 5.2 Ograničenja

EXPAND (be honest, it strengthens the defense):
- Single GPU / single scene class; diffuse GI only; hard-ish shadows.
- Ray budgets kept low to stay real-time -> reliance on denoising, with its ghosting/lag failure
  modes under fast motion.
- `GIDenoise.comp` occupancy limit; TLAS rebuild cost for dynamic scenes.
- Inline ray query gives up hardware ray scheduling / recursion the RT pipeline would provide.

## 5.3 Budući rad

EXPAND:
- **ReSTIR / ReSTIR GI:** better sampling for many lights and indirect, replacing the naive
  per-light / cosine sampling.
- **Neural reconstruction:** the earlier super-resolution / temporal-upscaling thread folds in here.
  The engine already has a temporal neural net (`NeuralUpscalePass`) that wins on LPIPS vs bilinear;
  a natural next step is a neural denoiser/upscaler replacing or augmenting SVGF, and the
  cross-vendor cooperative-matrix inference study from the original proposal.
- **More RT lights:** the MegaLights-lite plan (half-res, denoised, eventually-stochastic RT shadows
  for all lights on the shared denoiser).
- **DX12 backend / cross-vendor** measurements to generalize the perf story beyond RDNA3.
