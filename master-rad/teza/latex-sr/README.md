# latex-sr: srpsko izdanje teze (probno, skraćenice i glave 1, 2 i 5)

Dodatno izdanje uz englesku tezu u `../latex/` (izvor istine za sadržaj). Plan i pravila: `TRANSLATION-PLAN.md` u zajedničkom radnom prostoru tima; termini: `../glossary.md`.

- Deli sa `../latex/`: `etf.cls`, `LogoETF.png`, `figures/`, `data/` (makroi brojeva i tabele), `chapters/99-literatura.tex`. Brojevi se ne kucaju u tekstu, uvek makro.
- Prevedena poglavlja imaju ista imena fajlova, iste `\label` i `\cite` kao engleska. Sada: `chapters/00-skracenice.tex`, `chapters/01-uvod.tex`, `chapters/02-pregled.tex`, `chapters/05-zakljucak.tex`.
- Redni broj glave 5 postavlja `\setcounter{chapter}{4}` u `main.tex` posle glave 2; briše se kad se prevedu glave 3-4.

## Build

```
cd master-rad/teza/latex-sr
TEXINPUTS=.:../latex: pdflatex -interaction=nonstopmode -halt-on-error main.tex   # 2x
```

Potreban je TeX Live sa srpskim babel-om (Debian: `texlive-lang-cyrillic` i `texlive-lang-european`, uz `texlive-latex-extra`, `texlive-pictures`, `texlive-science`); bez toga `babel` javlja `Unknown option 'serbian'`. Lokalno nema pdflatex u WSL-u, pa je build proveren u Daytona sandboxu (Debian, TeX Live iz apt-a).

Putanja `../latex` je nerekurzivna namerno: `main.tex` i `chapters/` postoje u oba foldera, pa bi rekurzivna putanja učitala englesku verziju.

U probnom izdanju reference na glave 3-4 (`ch:implementacija`, `ch:analiza`, `sec:*`, `tab:gpus`, `tab:shadow-strategy`, `fig:ssvsrt-refl`) ostaju `??` dok se te glave ne prevedu.

## Provere

Iz `master-rad/teza/`: `py tools/<alat> --sr` za `check_refs.py`, `check_float_refs.py`, `check_abbrev_order.py` i `scan_control_chars.py`; `check_translation_parity.py` sam poredi EN i SR. `--sr` tretira glave koje još nisu prevedene kao da su u `latex/`, pa reference na njih i bibliografske stavke koje citiraju samo one nisu greška.

Poslednja provera (2026-10-23, glave 0, 1, 2, 5): sva četiri `--sr` alata i parity čisti (0 problema); `pdflatex` 2x izlazni kod 0, bez `! ` linija, bez nedefinisanih citata, bez Overfull. Nedefinisano ostaje samo 13 različitih labela iz glava 3-4 (gore). `tab:pipeline-vs-rayquery` u glavi 2 koristi `\tabcolsep` 4pt jer je sa 6pt prelazila margine za 8pt.

## Poznata ograničenja

- Generisani makroi (`\perfTopEffectAMD` i dr.) daju engleske reči i tačku kao decimalni znak; srpska verzija zahteva `--lang sr` u `tools/gen_*.py`.
- Prevod nije pregledao Vuk; kalkovi se ne mogu proveriti alatom.
