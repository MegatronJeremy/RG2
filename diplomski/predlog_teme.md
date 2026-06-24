# Predlog teme master rada

**Kandidat:** Vuk Đorđević, 2024/3102
**Mentor:** doc. dr Jovan Đukić (Računarska grafika 2, ETF)
**Studijski program:** Master, Elektrotehnički fakultet, Univerzitet u Beogradu
**Datum:** jul 2026.

---

## Naslov

**Neural super-resolution u realnom vremenu kroz Vulkan: vendor-neutralna
implementacija i cross-vendor analiza u sopstvenom render engine-u**

*(eng. Real-Time Neural Super-Resolution via Vulkan: A Vendor-Neutral
Implementation and Cross-Vendor Analysis in a Custom Render Engine)*

---

## Motivacija i istraživačko pitanje

Neuralni upscaling (DLSS, FSR3/4, XeSS) je postao standardni deo modernog
render pipeline-a: scena se renderuje na nižoj rezoluciji, a neuronska mreža je
rekonstruiše na ciljnu rezoluciju, čime se dobija performansa uz očuvan
kvalitet. Problem: **najkvalitetnija rešenja su vendor-zaključana** (DLSS je
NVIDIA-only, oslonjen na CUDA/TensorRT i Tensor core-ove). Portabilni put kroz
**Vulkan** — koji radi isti kod na AMD i NVIDIA hardveru — je slabo istražen,
naročito kroz `VK_KHR_cooperative_matrix` za matrične operacije inferencije.

**Pitanje:** Koliko se efikasno neuralni upscaling može izvesti **vendor-neutralno
kroz Vulkan compute (cooperative matrix)**, i kako se performanse i kvalitet
ponašaju **cross-vendor** (AMD RDNA3/4 vs NVIDIA Blackwell) i kroz nivoe
preciznosti (FP16 vs FP8)?

---

## Zašto je ovo doprinos (a ne reimplementacija DLSS-a)

- Cilj **nije** nadmašiti DLSS, već izmeriti nešto što skoro niko nije:
  **vendor-neutralnu Vulkan inferenciju** za real-time upscaling, fer poređenu
  na više vendora i generacija.
- **AMD u akademskoj literaturi za neural rendering je praktično odsutan** — sva
  ozbiljna poređenja idu kroz NVIDIA/CUDA. Cross-vendor Vulkan ugao je svež.
- Rezultat je **praktičan i prenosiv**: integrisan, otvoren put u realnom
  engine-u + brojevi koji kažu koliko cooperative matrix i FP8 stvarno donose
  na svakom vendoru.

---

## Platforma — Snowstorm Engine (postojeći)

Rad se gradi na autorovom engine-u (`Snowstorm-Engine`, Vulkan backend,
HLSL→SPIR-V preko DXC). Engine već poseduje:

- apstraktni renderer sa **render target**-ima i **bindless** resursima,
- **compute put** (`CommandContext::Dispatch`, `Compute` pipeline/shader stage),
- ECS, materijale (PBR-style `DefaultLit`), editor (ImGui).

Time je integraciona infrastruktura (render petlja, frame budget, resursi)
**već rešena** — fokus rada ostaje na inferenciji, ne na pisanju engine-a.

---

## Eksperimentalni dizajn

**Cilj:** spatial neural super-resolution rasterizovanog izlaza (npr. 1080p→4K).
Ulaz je besplatan — scena se renderuje na nižoj rezoluciji postojećim
pipeline-om, pa upscale-uje. (Temporalni upscaling sa motion vektorima je
opciono proširenje, ne osnovni obim.)

**Model:** pretreniran, lagan SR model (npr. ESPCN / FSRCNN klase ili lagani
EDSR), uvezen kao težine — **bez treniranja od nule**. Težište je inferencija
i integracija.

**Implementacija inferencije (u engine-u, HLSL compute → SPIR-V):**

| Varijanta | Tehnika | Svrha |
|---|---|---|
| Baseline | naivni compute matmul, FP16 | referenca, radi svuda |
| Opt. 1 | `VK_KHR_cooperative_matrix`, FP16 | hardverski matrix put |
| Opt. 2 | cooperative matrix, FP8 (gde podržano) | maksimalna efikasnost |

**Hardver (sve preko istog Vulkan koda):**
- AMD RDNA4 — Radeon RX 9070 XT, 9060 XT
- AMD RDNA3 — Radeon RX 7900 XTX
- NVIDIA Blackwell — RTX 5070

**Potvrđena podrška (Faza 0, `vulkaninfo`):** na 9070 XT i RTX 5070 oba podržavaju
`VK_KHR_cooperative_matrix` (rev 2) sa FP16, BF16 **i FP8** (`VK_EXT_shader_float8`,
`shaderFloat8CooperativeMatrix = true`) → FP8 put je izvodljiv na oba vendora.
**Cross-vendor asimetrija (nalaz):** NVIDIA dodatno nudi `VK_NV_cooperative_vector`
i `VK_NV_cooperative_matrix2` (inference-orijentisani putevi koje AMD nema) —
zajednički vendor-neutralni imenilac je `cooperative_matrix`. Preostaje provera
7900 XTX (RDNA3, očekivano bez FP8 matrix → generacijska dimenzija) i 9060 XT.

**Merenja (po varijanti, GPU-u, rezoluciji):**
- vreme upscale-a po frejmu (ms) i uticaj na ukupni frame time,
- kvalitet rekonstrukcije: **PSNR, SSIM**, i temporalna stabilnost,
- ubrzanje cooperative matrix vs naivni compute, po vendoru,
- dobit FP8 vs FP16 (gde je FP8 cooperative matrix dostupan).

---

## Plan rada (rok: kraj septembra 2026)

| Faza | Aktivnost | Procena |
|---|---|---|
| 0 | ~~Provera `cooperative_matrix`/FP8 podrške po kartici~~ **— urađeno: FP8 potvrđen na RDNA4 + Blackwell** | ✓ |
| 1 | Low-res render → ulazni put + naivni FP16 compute upscaler u engine-u | 2 ned. |
| 2 | Uvoz pretreniranog SR modela, korektnost (PSNR/SSIM vs referenca) | 1.5 ned. |
| 3 | Cooperative matrix put (FP16), pa FP8 gde je podržan | 2.5 ned. |
| 4 | Cross-vendor merenja na 4 kartice, prikupljanje rezultata | 1.5 ned. |
| 5 | Analiza, grafici, pisanje, priprema odbrane (živi demo) | 2 ned. |

*(Rad uz puno radno vreme; AI alati za ubrzanje boilerplate-a i analize.)*

---

## Očekivani doprinosi

1. **Vendor-neutralan, otvoren Vulkan put** za real-time neural upscaling,
   integrisan u realan engine.
2. **Cross-vendor benčmark** (AMD RDNA3/4 vs NVIDIA Blackwell) sa fer, istim
   kodom — segment koji u literaturi nedostaje.
3. Konkretan nalaz: koliko cooperative matrix i FP8 stvarno donose po vendoru i
   gde je granica isplativosti za real-time upscaling.

---

## Rizici i kontrola

- **Cooperative matrix / FP8 podrška:** ako FP8 nije dostupan na svim karticama,
  fallback je FP16 (i dalje validan rad, manje agresivna preciznost). Faza 0 to
  rano utvrđuje.
- **HLSL cooperative matrix u DXC/SPIR-V:** ako put kroz HLSL bude nezreo,
  alternativa je GLSL (`GL_KHR_cooperative_matrix`) za taj shader — dokumentovati.
- **Obim:** spatial upscaling je osnovni cilj; temporalni (motion vektori) i
  denoising idu u „budući rad" ako rok pritisne.
- **Kvalitet modela:** koristi se pretreniran model; cilj nije SOTA kvalitet
  nego fer, dosledno merenje istog modela kroz varijante i vendore.

---

## Veza sa kursom, engine-om i karijerom

Tema je direktan nastavak RG2 (real-time rendering, Vulkan, shaderi) i nadograđuje
autorov postojeći engine. Inženjerski demonstrira veštine na granici grafike i
AI: real-time GPU inferencija, cooperative matrix / low-precision, cross-vendor
Vulkan, profiling render pipeline-a — što je tražen profil za neural-rendering i
GPU/AI uloge. Ciljani ishod: master rad + jak, vizuelan portfolio (živi demo na
odbrani).

---

## Literatura (početna)

1. Shi et al., *Real-Time Single Image and Video Super-Resolution (ESPCN)*, 2016.
2. Dong et al., *Accelerating the Super-Resolution CNN (FSRCNN)*, 2016.
3. NVIDIA, *DLSS* tehnička dokumentacija; AMD, *FidelityFX Super Resolution (FSR)*.
4. Khronos, *VK_KHR_cooperative_matrix* specifikacija.
5. *Hardware Acceleration of LLMs: A Comprehensive Survey*, 2024 — arXiv:2409.03384 (za kontekst low-precision inferencije).
6. Vulkan / HLSL (DXC) i SPIR-V dokumentacija.
