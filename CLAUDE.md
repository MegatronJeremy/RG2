# CLAUDE.md — radni okvir za RG2 repozitorijum

Repozitorijum predmeta **Računarska grafika 2** (13M111RG2, master ETF Beograd): materijali
sa nastave, domaći zadaci i projekti. Ovaj repo je i sam **submodule** super-projekta
`MegatronJeremy/ETF-Master`. Pregled sadržaja je u [README.md](README.md), kompletan spisak
materijala sa linkovima u [INDEX.md](INDEX.md).

## Layout

```
materijali/          # prezentacije, predavanja (arhiva), vezbe, seminarski, dodatni, propozicije
domaci/<godina>/     # domaći zadaci; svaki u svom folderu (npr. domaci/2025/dz1/)
master-rad/          # Vukov master rad
  teza/              #   tekst rada: markdown radne verzije + teza/latex/ (izvor teze, vidi ispod)
  Snowstorm-Engine/  #   render engine (ugnježdeni git submodule), evaluaciona platforma za rad
```

- **Folderi sa sadržajem → mala slova** (`materijali`, `vezbe`, `dz1`), bez naših slova sa
  kvačicama (`vezbe`, ne `vežbe`). **Imena projekata → PascalCase** (`Snowstorm-Engine`).
- Domaći **nisu** submoduli — žive direktno u ovom repou. Submodule je rezervisan za
  samostalne, ponovo-upotrebljive projekte (kao Snowstorm-Engine). `master-rad/teza` takođe
  živi direktno u repou (nije submodule) — samo Snowstorm-Engine unutar `master-rad/` jeste.

## Standardni kvalitetski okvir (poštuj na svakoj izmeni)

1. **Jedan inkrement po koraku.** Svaki korak ostavlja repo u pokretljivom stanju.
2. **Commit + push nakon svakog koraka.** Commit u relevantnom repou (RG2 ili Snowstorm-Engine
   submodule), zatim ako je dirnut submodule — bump pokazivača u nadređenom repou i push i njega,
   da remote uvek bude konzistentan. Poruke commit-a na srpskom, kratke i konkretne.
3. **Code review u chatu pre push-a.** Za svaku novu funkcionalnost/izmenu, pre nego što
   gurneš (`git push` + bump pokazivača), prikaži pregled u razgovoru — kao što bi senior
   inženjer pregledao PR. Pokaži konkretne snippet-e **sa dovoljno okolnog koda** (funkcija/blok
   u kome izmena živi, linije iznad i ispod — ne izolovane fragmente, već kako se pravi PR diff
   čita), sa objašnjenjem *zašto* je nešto urađeno tako, kompromisima, ne-očiglednim
   invarijantama, rizicima i šta treba dodatno proveriti. Navedi eksplicitno šta JESTE i šta
   NIJE verifikovano (posebno vizuelne/headless rupe, vidi tačku 5). Lokalni commit pre review-a
   je u redu; kapija je na **push**. Guraj (oba repoa) tek nakon što Vuk odobri.
4. **Git higijena.** Nikad ne commit-uj `target/`, `.idea/`, `*.iml`, IDE/build artefakte
   (vidi `domaci/2025/dz1/.gitignore`, `master-rad/teza/latex/.gitignore`). Originalne velike
   `.zip` materijale čuvaj u izvornom obliku, ne raspakuj ih u repo bez razloga.
5. **Verify-before-claim.** Pre tvrdnje o kodu/sadržaju/ponašanju proveri naspram **stvarnog
   fajla ili komande** (otvori, `grep`, build/kompajliraj), ne iz imena ili pretpostavke. Što ne
   možeš potvrditi — označi kao pretpostavku. Ovo pokriva i brojeve: nikad ne navodi merenje,
   benchmark ili kvantitativni rezultat koji nisi stvarno proizveo — nedovršeno merenje se tako i
   kaže, izmišljen broj je gori od "još nisam izmerio".
   - **Izmena izvora ≠ regenerisan artefakt.** Menjanje `.tex`/`.md`/koda ne znači da je PDF/build
     ažuran. Nakon svake izmene LaTeX izvora u `master-rad/teza/latex/`, ponovo kompajliraj
     (`pdflatex` dvaput radi unakrsnih referenci, `bibtex` ako su menjane reference) i proveri
     **exit kod** komande (ne grepovan log — može promaći pravu grešku) i da je `main.pdf` **noviji**
     od svih izmenjenih `.tex` fajlova pre nego što tvrdiš da je teza ažurirana. Isto važi za svaki
     drugi generisani artefakt (kompajliran kod, build izlaz): proveri da je stvarno rebuild-ovan
     (timestamp), ne pretpostavljaj na osnovu toga što je komanda pokrenuta.
6. **Grafiku potvrdi vizuelno.** OpenGL rezultat se ne može verifikovati headless — traži
   GPU/displej i NEWT prozor. Tvrdnju „radi/izgleda ispravno" donosi tek nakon pokretanja i
   screenshot-a; inače jasno reci da nije vizuelno potvrđeno.
7. **Jezik:** kod, komentari i identifikatori na **engleskom**; komunikacija sa Vukom na srpskom;
   `master-rad/obrazlozenje_teme.md` i slični administrativni ETF dokumenti isključivo na
   srpskoj ćirilici (osim ustaljenih tehničkih termina — `VK_KHR_ray_query`, SVGF, PSNR/SSIM i
   sl. — koji ostaju u originalu, kako je uobičajeno u domaćoj literaturi).
8. **Pisanje: maksimum informacije, minimum teksta** — važi za tezu, commit poruke, README/INDEX,
   komentare u kodu. Bez uvoda/fraziranja, bez ponavljanja očiglednog; zadrži brojeve/imena i
   *zašto*/kompromis, izbaci vezivno tkivo između njih.
   - **Nikad em-dash (—), ni na engleskom ni na srpskom.** Simbol nije jedini problem: dublji trag
     je spajanje rečenica susedstvom umesto imenovanom vezom. Kad bi ruka posegnula za crtom, prvo
     imenuj vezu: dvotačka ako drugi deo objašnjava prvi, veznik ("pošto", "iako", "mada") ako
     kvalifikuje, zagrada za pravu digresiju, tačka-zapeta za dve nezavisne rečenice. Obična crtica
     (kao ove ovde) je u redu.
   - **Committovan sadržaj tvrdi trajne činjenice, ne status.** Bez radnog dnevnika ("dodato u ovoj
     izmeni"), bez TODO/status rečenica u tekstu teze ili komentarima ("još treba izmeriti", "za
     sada placeholder") — takav tekst zastari i traži naknadni commit da se ispravi. Status ide u
     razgovor/plan, ne u fajl. Kad tabela/pasus u tezi dobije stvarne brojeve, ukloni i najavu da su
     "placeholder" zajedno sa samim placeholderom, u istoj izmeni.

## Teza: `master-rad/teza/latex` (glavni master rad)

LaTeX izvor teze (`etf.cls`, ETF-ov template). `main.tex` je glavni fajl (naslov, autor, mentor,
apstrakt, `\input` poglavlja); poglavlja su u `chapters/*.tex`; slike u `figures/`; tabele/podaci
merenja u `data/`; literatura u `references.bib` (BibTeX). Markdown radne verzije istih poglavlja
(`master-rad/teza/*.md`, van `latex/`) su stariji radni materijal — **LaTeX u `latex/` je izvor
istine** za predaju; ne sinhronizuj automatski nazad u markdown bez razloga.

**Kompajliranje** (MiKTeX, `pdflatex`/`bibtex` u PATH-u):
```
cd master-rad/teza/latex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main            # samo ako su menjane reference.bib ili citati
pdflatex -interaction=nonstopmode -halt-on-error main.tex   # 2x ukupno, radi TOC/referenci
```
`-halt-on-error` čini da neuspeh vrati **ne-nulti exit kod** umesto da nastavi i proizvede
nepotpun PDF; proveri taj exit kod, i pregledaj `main.log` za `! ` greške i `Undefined
references/citations` pre nego što tvrdiš da je build čist (Overfull/Underfull box upozorenja su
kozmetička, ne blokiraju). `main.pdf` je namerno u `.gitignore`-u (build izlaz), pa se generiše
lokalno, nikad ne commit-uje.

**Brojevi/merenja u tezi dolaze isključivo iz `Scripts/perf-bench.py` / `quality-bench.py` /
prilagođenih sweep skripti u Snowstorm-Engine submodule-u** (vidi njegov CLAUDE.md), nikad
procenjeni ili "tipični" brojevi za tu arhitekturu.

## Projekat: `domaci/2025/dz1` — Planeta Zemlja (OpenGL 4)

Maven projekat, **Java 9**. Postavka je u [postavka.pdf](domaci/2025/dz1/postavka.pdf).

**Zavisnosti:** JogAmp JOGL 2.6.0 (`jogl-all-main` + `gluegen-rt-main`, nose native biblioteke),
JOML 1.9.15 (matematika), `pngdecoder` (učitavanje slika).

**Struktura izvora** (`src/main/java/opengl4/`):
- `common/` — framework sa nastave (kamera, shader-programi, graphics objekti, scene, teksture).
  Ne menjati bez razloga; deli se sa drugim OpenGL zadacima.
- `dz1/` — rešenje zadatka: `CubeSphereGenerator`, `EarthMesh`/`EarthShaderProgram`,
  `SkyboxMesh`/`SkyboxShaderProgram`, `EditorCameraView`, `Main`.
- GLSL šejderi i teksture: `src/main/resources/opengl4/dz1/`.

**Pokretanje** (traži displej + GPU):
```
# iz IDE-a: pokreni klasu opengl4.dz1.Main
# ili preko Mavena (exec plugin, eksplicitna main klasa):
mvn -f domaci/2025/dz1/pom.xml compile \
    org.codehaus.mojo:exec-maven-plugin:3.1.0:java -Dexec.mainClass=opengl4.dz1.Main
```

**Zahtevi postavke (checklist):** cube-sphere mreža (ravnomerna temena), height-map displacement
terena, UV po zadatim formulama, diffuse tekstura, Phong senčenje sa jednim belim tačkastim
svetlom, normale iz normal-mape, specular iz specular-mape, kamera (zoom scroll-om + rotacija oko
X/Y drag-om), skybox. Domaći se brani u ispitnom roku.

## Submodule napomene

```
git clone --recurse-submodules https://github.com/MegatronJeremy/RG2
git submodule update --init --recursive   # ako je repo već kloniran
```
Snowstorm-Engine ima sopstveni razvojni tok i `master` granu; ovde se referencira kao submodule.
