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

Putanja `../latex` je nerekurzivna namerno: `main.tex` i `chapters/` postoje u oba foldera, pa bi rekurzivna putanja učitala englesku verziju.

U probnom izdanju reference na glave 3-4 (`ch:implementacija`, `ch:analiza`, `sec:*`, `tab:gpus`, `tab:shadow-strategy`, `fig:ssvsrt-refl`) ostaju `??` dok se te glave ne prevedu.

## Poznata ograničenja

- Generisani makroi (`\perfTopEffectAMD` i dr.) daju engleske reči i tačku kao decimalni znak; srpska verzija zahteva `--lang sr` u `tools/gen_*.py`.
- Prevod nije pregledao Vuk; kalkovi se ne mogu proveriti alatom.
