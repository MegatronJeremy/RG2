# 4. Analiza

The chapter Đukić singled out: measure the system and compare against the Ch2 solutions. **Every
number here must be produced by a run, never estimated.** Tables below are placeholders with the
measurement method noted; fill from actual `perf-bench` / metric runs. Mark any claim not backed by
a run as an assumption.

## 4.1 Metodologija

EXPAND:
- **Hardware:** primary AMD Radeon RX 7900 XTX (RDNA3, gfx1100); list driver + OS. (Cross-vendor is
  future work, not this thesis.)
- **Scene(s):** Sponza (perf-bench default) = 10 lights (3 spot + 6 point + 1 directional); state
  resolution. `StressScene` (mesh grid) available for scaling tests.
- **Fair-comparison controls (from memory, learned the hard way):** static camera for any A/B (no
  `--camera.path`, which desyncs frames); clear the shader cache before trusting a GPU metric;
  perf baselines are per-machine/per-resolution; `config.ignore` isolates the benchmark from
  persisted CVars.
- **Perf method:** `perf-bench` averages per-pass GPU timestamps over a fixed frame budget past a
  15-frame warmup; the config matrix `rt-off -> shadows -> +ao -> +refl -> +gi` enables one effect
  at a time. **Caveat:** the "Forward-ms delta = effect cost" shorthand is only literal for shadows
  and reflections (inline in Forward). GI and AO run as their own half-res passes with separate
  scopes (`GI`/`AO`/`*Upsample`), so attribute their cost from those per-pass-scope deltas plus
  `totalGpuMs`, not the Forward delta alone.
- **Quality method:** PSNR / SSIM (GPU `MetricsPass`) against a ground-truth reference; the engine's
  GT is a 2nd full-res unjittered forward, optionally `render.gt.ssaa` 2x + linear-HDR downsample
  (anti-aliased reference). **Caveat:** the GT path forces raster shadows (`forceRasterShadow=true`),
  so with RT shadows on, the metric is RT-vs-raster, not RT-vs-reference-RT. Decide handling before
  quoting any shadow PSNR (measure non-shadow effects against GT, add an RT-shadow GT path, or state
  the caveat). State exactly how the reference is generated.

## 4.2 Cena po efektu (GPU ms)

Method: adjacent-config delta from the perf-bench matrix (4.1). Fill from a real run on the stated HW.

| Config | Forward ms | Denoise ms | Total frame ms | Δ vs prev = effect cost |
|---|---|---|---|---|
| rt-off | | | | baseline |
| +shadows | | | | shadows |
| +ao | | | | AO |
| +refl | | | | reflections |
| +gi | | | | GI |

EXPAND: comment on which effect dominates (memory: RT sun-shadows are the biggest cost, half-res
denoise pattern is what keeps AO/GI affordable) and why.

## 4.3 Broj zrakova naspram kvaliteta i brzine

EXPAND: sweep spp (and ray length / bounce count where relevant) per effect; plot PSNR/SSIM and ms
vs spp; identify the knee (the point past which more rays stop paying). This is the central
quality/perf tradeoff the research question asks about.

## 4.4 Evaluacija denoiser-a (SVGF)

EXPAND:
- Noisy (denoiser off) vs denoised vs reference: PSNR/SSIM gain from SVGF at fixed low spp.
- Temporal stability (the metric or the ghosting/lag observation under motion).
- Denoiser cost (ms) vs the quality it buys; tie to the `GIDenoise.comp` occupancy limit from Ch3.

## 4.5 Poređenje sa postojećim rešenjima

EXPAND (this is the "compare vs Ch2" Đukić asked for):
- **vs screen-space (SSAO/SSR/SSGI):** same scene, show the off-screen/disocclusion cases where the
  RT version is correct and the screen-space one is not; note the cost difference honestly.
- **vs offline reference (path trace):** quality gap at real-time budget; how close the denoised
  hybrid gets and where it visibly diverges.
- **Positioning vs Lumen/RTXGI/ReSTIR:** qualitative, honest. The contribution is an integrated,
  measured, open ray-query implementation, not beating a production GI system.

## 4.6 Zauzetost i cena šejdera (opciono)

EXPAND: RGA static occupancy (VGPR/LDS/spills) per RT/denoise shader; the one occupancy-limited
shader (`GIDenoise.comp`). Mark as static/theoretical (RGA), distinct from achieved occupancy (RGP).

---

**Verified vs assumed:** keep a running list at the bottom of each results section stating which
numbers came from a run (with the config) and which are still expected/assumed. Do not let an
assumed number read as a measured one.
