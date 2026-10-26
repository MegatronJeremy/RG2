# latex-sr: srpsko izdanje teze (probno, skraćenice i glave 1 do 5)

Dodatno izdanje uz englesku tezu u `../latex/` (izvor istine za sadržaj). Plan i pravila: `TRANSLATION-PLAN.md` u zajedničkom radnom prostoru tima; termini: `../glossary.md`.

- Deli sa `../latex/`: `etf.cls`, `LogoETF.png`, `figures/`, `data/` (makroi brojeva i tabele), `chapters/99-literatura.tex`. Brojevi se ne kucaju u tekstu, uvek makro.
- Prevedena poglavlja imaju ista imena fajlova, iste `\label` i `\cite` kao engleska. Sada: `chapters/00-skracenice.tex`, `chapters/01-uvod.tex`, `chapters/02-pregled.tex`, `chapters/03-implementacija.tex`, `chapters/04-analiza.tex`, `chapters/05-zakljucak.tex`.

## Build

```
cd master-rad/teza/latex-sr
TEXINPUTS=.:../latex: pdflatex -interaction=nonstopmode -halt-on-error main.tex   # 2x
```

Potreban je TeX Live sa srpskim babel-om (Debian: `texlive-lang-cyrillic` i `texlive-lang-european`, uz `texlive-latex-extra`, `texlive-pictures`, `texlive-science`); bez toga `babel` javlja `Unknown option 'serbian'`. Lokalno nema pdflatex u WSL-u, pa je build proveren u Daytona sandboxu (Debian, TeX Live iz apt-a).

Putanja `../latex` je nerekurzivna namerno: `main.tex` i `chapters/` postoje u oba foldera, pa bi rekurzivna putanja učitala englesku verziju.

## Provere

Iz `master-rad/teza/`: `py tools/<alat> --sr` za `check_refs.py`, `check_float_refs.py`, `check_abbrev_order.py` i `scan_control_chars.py`; `check_translation_parity.py` sam poredi EN i SR. `--sr` tretira glave koje još nisu prevedene kao da su u `latex/`, pa reference na njih i bibliografske stavke koje citiraju samo one nisu greška.

Poslednja provera (2026-10-24, glave 0 do 5): sva četiri `--sr` alata i parity čisti (0 problema); `pdflatex` 2x izlazni kod 0 (sandbox, Debian TeX Live), bez `! ` linija, bez nedefinisanih labela i citata. Bez Overfull upozorenja (tabela `tab:tooling` glave 3 ima p-kolonu).

## Poznata ograničenja

- Generisani makroi (`\perfTopEffectAMD` i dr.) daju engleske reči i tačku kao decimalni znak; srpska verzija zahteva `--lang sr` u `tools/gen_*.py`.
- Prevod nije pregledao Vuk; kalkovi se ne mogu proveriti alatom.
