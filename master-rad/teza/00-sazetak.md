# Sažetak (abstract) + ključne reči

PPK requires this (slide 16-18): 50-500 words (target ~250), **present tense**, declarative. Five
elements, roughly one to two sentences each. Draft in English, translate last. **Do not fabricate
the numbers** in element 5; fill from Ch4 once measured.

## Sažetak (draft)

1. **Problem.** Real-time rasterization approximates global light-transport effects (indirect
   illumination, contact shadows, glossy reflections, ambient occlusion) with screen-space and
   precomputed methods that fail on off-screen or dynamic information.

2. **Existing solutions + shortcomings.** Screen-space (SSAO/SSR/SSGI) is cheap but view-limited;
   voxel/probe methods (VXGI, DDGI) are scene-wide but low-frequency; production hybrids (Lumen)
   are closed and complex. `EXPAND` to one tight sentence.

3. **Proposed idea + why better.** This thesis integrates shadows, ambient occlusion, reflections,
   and diffuse global illumination as inline ray-query (`VK_KHR_ray_query`) passes over a rasterized
   forward renderer in a self-written Vulkan engine, denoised by a shared SVGF filter, so the effects
   are physically grounded and correct off-screen at a real-time budget.

4. **How the comparison is done.** Per-effect GPU cost is isolated with an A/B config matrix
   (one effect enabled at a time); reconstruction quality is measured with PSNR/SSIM against an
   SSAA/offline reference on a fixed scene and camera.

5. **Main numerical results.** `FILL FROM Ch4:` per-effect cost in ms on RX 7900 XTX, PSNR/SSIM
   gain from denoising, and the ray-count knee. **Leave blank until measured.**

## Ključne reči (5-10, each a 1-3 word phrase)

ray tracing u realnom vremenu; ray query; Vulkan; globalno osvetljenje; ambijentalna okluzija;
refleksije; SVGF; uklanjanje šuma; hibridno renderovanje
