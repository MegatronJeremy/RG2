# Master rad: outline and working notes

**Working title (EN):** Real-Time Hybrid Ray Tracing in a Custom Vulkan Engine:
Inline Ray-Query Shadows, Ambient Occlusion, Reflections and Global Illumination with SVGF Denoising

**Radni naslov (SR):** *(prevod na kraju; vidi [glossary.md](glossary.md))*

**Candidate:** Vuk Đorđević, 2024/3102 · Master, ETF, Univerzitet u Beogradu
**Mentor:** TBD (Đukić ne može formalno; kandidati: Drašković / Radivojević / Jocović)
**Advisor (RG2):** doc. dr Jovan Đukić

> Topic is settled: **hybrid ray tracing** (the Aug 2 email Đukić approved). The neural
> super-resolution idea in [`../predlog_teme.md`](../predlog_teme.md) is an **earlier proposal and
> is now stale** as the thesis topic; the neural work survives as *future work* (Ch5).

## Drafting conventions

- **Draft in English, submit in Serbian.** Translate per-chapter as each is finalized, not in one
  end pass. Keep terminology consistent via [glossary.md](glossary.md).
- **Short-form now, expand later.** Each section holds 1-3 real sentences plus `EXPAND:` bullets
  marking what to flesh out. This is a skeleton, not a first full draft.
- **Writing rules (global AGENTS.md):** maximal info / minimal text; no em-dashes anywhere; no
  "not just X but Y"; no rule-of-three padding; keep Vuk's voice. Every measured number must be
  produced, never estimated and stated as fact (mark assumptions).
- One chapter per file. Tracking mirrors chapters as GitHub issues on `MegatronJeremy/RG2`.

## Mandated frame (Đukić) ← Vuk's 7-section skeleton

Đukić requires 5 chapters. Vuk's proposed 7 sections fold in as subsections:

| # | Chapter (mandated) | Absorbs (Vuk's sections) | File |
|---|---|---|---|
| 1 | **Uvod** (problem + why it matters) | §1 Uvod i motivacija | [01-uvod.md](01-uvod.md) |
| 2 | **Pregled postojećih rešenja/tehnologija** | §2 Teorijska osnova + related work | [02-pregled.md](02-pregled.md) |
| 3 | **Opis implementacije** | §3 Arhitektura + §4 Četiri efekta + §5 Denoising | [03-implementacija.md](03-implementacija.md) |
| 4 | **Analiza** (compare vs existing) | §6 Evaluacija | [04-analiza.md](04-analiza.md) |
| 5 | **Zaključak** (done + future) | §7 Zaključak i budući rad | [05-zakljucak.md](05-zakljucak.md) |

References: [literatura.md](literatura.md).

## PPK vodič (applied, from `PPK_kako_napisati_diplomski_rad`)

Thesis type: **evaluacioni rad** (PPK slide 23); the contribution is the measured evaluation.
Đukić's 5 chapters line up with PPK's central-part structure (Pregled postojećih rešenja / detalja
rešenja / dobijenih rezultata), so the frame is compliant as-is.

Full document order (PPK slide 8), front + back matter around the 5 chapters:

1. Naslovna strana ([00-naslovna.md](00-naslovna.md)), sans-serif, prescribed sizes
2. Izjava zahvalnosti (optional, 1 page)
3. Sažetak + ključne reči ([00-sazetak.md](00-sazetak.md))
4. Sadržaj (auto-generated, heading depth ≤ 3)
5. Spiskovi: slika / tabela / skraćenica
6. Ch1-5
7. Literatura ([literatura.md](literatura.md))
8. Prilozi (optional)

**Length targets (PPK):** Uvod 1-1.5 str; centralni deo (Ch2-4) 30-50 str; Zaključak 1-1.5 str.
Uvod ends with the chapter-roadmap paragraph; Zaključak opens with a recap of the zadatak goals.

**Final-document formatting** (applies to the LaTeX/Word output, not this markdown): A4; margins
20 mm (or 30 mm top/bottom); body serif (antikva) 12 pt, justified, 1.0 spacing; chapter titles and
subtitles bold; every chapter starts on a new page and opens with a paragraph describing it;
paragraphs 3+ sentences; pages numbered arabic bottom-right from Uvod (front matter roman or
unnumbered); title page is the sole sans-serif page.

**Figures/tables:** numbered + captioned; **table caption above, figure caption below**; each one
referenced and explained in text; literature-sourced ones carry a reference. Keep the Spiskovi lists
in sync.

**References:** reformat [literatura.md](literatura.md) to the ETF style (Prezime Ime, "Naslov:
podnaslov," izdanje, izdavač, mesto, godina; journals add vol/issue/pp; web adds URL + access date),
ordered by citation order.

## Status

Source of truth is now the LaTeX project (`latex/`); the markdown chapters remain as English
scratch. "Expanded" below tracks the LaTeX chapter content.

| Part | Skeleton | Expanded (EN) | Translated (SR) |
|---|---|---|---|
| Naslovna | ☑ | ☑ | ☐ |
| Sažetak | ☑ | ☑ | ☐ |
| 1 Uvod | ☑ | ☑ | ☐ |
| 2 Pregled | ☑ | ☑ | ☐ |
| 3 Implementacija | ☑ | ☑ | ☐ |
| 4 Analiza | ☑ | ◐ | ☐ |
| 5 Zaključak | ☑ | ☑ | ☐ |

(◐ Ch4: methodology written; result tables/plots pending real GPU measurement.)

## Open logistics (from Đukić's email)

- Pick a formal mentor (professor with a PhD).
- Find the prodekan's email with the master-rad deadlines (prijava teme, predaja, ...).
- Meeting with Đukić 21.08. or later for open questions.
- RG2: defend both domaći; no seminarski needed since the master covers it.
