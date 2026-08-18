# Literatura (starter)

Working bibliography. Verify every entry (exact year, venue, authors) and reformat to the ETF
citation style before submission. Grouped by role in the thesis.

## Foundations (Ch1, Ch2)

- Kajiya, *The Rendering Equation*, SIGGRAPH 1986.
- Akenine-Möller, Haines, Hoffman, Iwanicki, *Real-Time Rendering*, 4th ed., 2018.
- Pharr, Jakob, Humphreys, *Physically Based Rendering: From Theory to Implementation* (PBRT), 4th ed.
- Möller, Trumbore, *Fast, Minimum Storage Ray/Triangle Intersection*, 1997.
- Haines, Akenine-Möller (eds.), *Ray Tracing Gems*, 2019; *Ray Tracing Gems II*, 2021 (open access).

## Vulkan / hardware ray tracing (Ch2, Ch3)

- Khronos, *Vulkan Specification*: `VK_KHR_acceleration_structure`, `VK_KHR_ray_tracing_pipeline`,
  `VK_KHR_ray_query`.
- Khronos / NVIDIA, *Vulkan Ray Tracing* tutorials (ray query vs ray tracing pipeline).
- Wald et al., *State of the Art in Ray Tracing Animated Scenes* (BVH build/update background).

## Existing real-time GI / RT solutions (Ch2, the comparison set)

- Mittring, *Finding Next Gen: CryEngine 2* (SSAO), 2007.
- Bavoil, Sainz, *Image-Space Horizon-Based Ambient Occlusion* (HBAO), 2008.
- Stachowiak, *Stochastic Screen-Space Reflections*, 2015.
- Crassin et al., *Interactive Indirect Illumination Using Voxel Cone Tracing* (VXGI), 2011.
- Majercik et al., *Dynamic Diffuse Global Illumination with Ray-Traced Irradiance Fields* (DDGI),
  JCGT 2019; NVIDIA *RTXGI*.
- Epic Games, *Lumen*, Unreal Engine documentation (hybrid SW/HW GI).
- Bitterli et al., *Spatiotemporal Reservoir Resampling for Real-Time Ray Tracing* (ReSTIR),
  SIGGRAPH 2020; Ouyang et al., *ReSTIR GI*, 2021.

## Denoising / temporal (Ch3, Ch4)

- Schied et al., *Spatiotemporal Variance-Guided Filtering* (SVGF), HPG 2017. **← implemented**
- Schied et al., *Gradient Estimation for Real-Time Adaptive Temporal Filtering* (A-SVGF), 2018.
- Karis, *High Quality Temporal Supersampling* (TAA), SIGGRAPH 2014 course.
- NVIDIA, *Real-Time Denoisers (NRD)*: ReBLUR/ReLAX.
- Intel, *Open Image Denoise (OIDN)*.

## Future work (Ch5)

- NVIDIA, *DLSS* technical docs; AMD, *FidelityFX Super Resolution (FSR)*.
- (Neural reconstruction thread from the earlier proposal: ESPCN, FSRCNN, `VK_KHR_cooperative_matrix`.)
