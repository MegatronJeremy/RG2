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
  prijava/           #   prijava teme: formular, uputstvo, pravilnik, skripta koja popunjava formular
  teza/              #   tekst rada: teza/latex/ (izvor), teza/tools/ (generisanje slika), radne beleske
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
     (`pdflatex` dvaput, radi unakrsnih referenci) i proveri
     **exit kod** komande (ne grepovan log — može promaći pravu grešku) i da je `main.pdf` **noviji**
     od svih izmenjenih `.tex` fajlova pre nego što tvrdiš da je teza ažurirana. Isto važi za svaki
     drugi generisani artefakt (kompajliran kod, build izlaz): proveri da je stvarno rebuild-ovan
     (timestamp), ne pretpostavljaj na osnovu toga što je komanda pokrenuta.
6. **Grafiku potvrdi vizuelno.** OpenGL rezultat se ne može verifikovati headless — traži
   GPU/displej i NEWT prozor. Tvrdnju „radi/izgleda ispravno" donosi tek nakon pokretanja i
   screenshot-a; inače jasno reci da nije vizuelno potvrđeno.
7. **Jezik:** kod, komentari i identifikatori na **engleskom**; komunikacija sa Vukom na srpskom;
   `master-rad/prijava/` i slični administrativni ETF dokumenti isključivo na
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
merenja u `data/`; literatura je rucno slozena `thebibliography` u `chapters/99-literatura.tex`
(nema BibTeX koraka, pa nema ni `.bib` fajla koji bi mogao da se razidje sa njom). **LaTeX u `latex/` je jedini izvor
istine** za predaju: paralelne markdown verzije poglavlja su obrisane jer su zastarevale i pravile
drugo mesto koje neko moze slucajno da izmeni. U `teza/` ostaju samo radne beleske koje nemaju
parnjaka u tezi (`glossary.md`, `notes-implementation.md`, `literatura.md`, `README.md`).

**Slike i brojevi se generisu, ne crtaju.** `teza/tools/` drzi skripte koje proizvode svaku
renderovanu sliku u `latex/figures/` i tabele 4.3 i 4.4; vidi [tools/README.md](master-rad/teza/tools/README.md)
za spisak sta koja skripta pravi. Zavisnost ide samo nadole (teza uvozi `Scripts/*.py` iz
Snowstorm-Engine submodule-a, nikad obrnuto), pa endzin ostaje samostalan projekat.

**Kompajliranje** (MiKTeX, `pdflatex` u PATH-u):
```
cd master-rad/teza/latex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex   # 2x, radi TOC-a i unakrsnih referenci
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

Maven projekat, **Java 9**. Postavka je u [DZ1_2025.pdf](domaci/2025/dz1/DZ1_2025.pdf).

**Zavisnosti:** JogAmp JOGL 2.6.0 (`jogl-all-main` + `gluegen-rt-main`, nose native biblioteke),
JOML 1.9.15 (matematika), `pngdecoder` (učitavanje slika).

**Struktura izvora** (`src/main/java/opengl4/`):
- `common/` — framework sa nastave (kamera, shader-programi, graphics objekti, scene, teksture).
  Ne menjati bez razloga; deli se sa drugim OpenGL zadacima.
- `dz1/` — rešenje zadatka: `CubeSphereGenerator`, `EarthMesh`/`EarthShaderProgram`,
  `SkyboxMesh`/`SkyboxShaderProgram`, `EditorCameraView`/`EarthView`, `Main`.
- GLSL šejderi i teksture: `src/main/resources/opengl4/dz1/`.

**Pokretanje** (traži displej + GPU):
```
# iz IDE-a: pokreni klasu opengl4.dz1.Main
# ili preko skripte, koja sama nadje mvn i JDK: domaci/2025/dz1/run.ps1 run
# ili rucno preko Mavena (konfiguracija exec plugina je u pom.xml):
mvn -f domaci/2025/dz1/pom.xml compile exec:exec
```
Goal je **`exec:exec`**, ne `exec:java`: `exec:java` vrti aplikaciju u Mavenovom JVM-u pod
zasebnim URLClassLoader-om, gde gluegen-ov JNI ne uspe da se veze, pa `GLProfile.get(GL4)`
puca sa „GL4 not available, but: []". `exec:exec` forkuje svez JVM.

**Zahtevi postavke (checklist):** cube-sphere mreža (ravnomerna temena), height-map displacement
terena, UV po zadatim formulama, diffuse tekstura, Phong senčenje sa jednim belim tačkastim
svetlom, normale iz normal-mape, specular iz specular-mape, kamera (zoom scroll-om + rotacija oko
X/Y drag-om), skybox. Domaći se brani u ispitnom roku.

## Projekat: `domaci/2025/dz2` (Vodena površ, Unity)

Unity **2022.3.4f1** (LTS), **Built-in Render Pipeline**. Postavka je u
[DZ2_2025.pdf](domaci/2025/dz2/DZ2_2025.pdf). Editor traži aktivnu licencu (prijava na Unity
nalog kroz Hub); bez nje i `-batchmode` odbija da se pokrene sa „No valid Unity Editor license
found". Iza Zscaler proxyja Hub-ov downloader puca sa „certificate has expired", pa se
instalater povlači ručno sa `download.unity3d.com` i pokreće uz UAC.

**Struktura** (`Assets/`):
- `Scripts/WaterSimulation.cs`: gradi mrežu trouglova, dispatch-uje compute kernele, čita miš,
  izlaže parametre u Inspektoru.
- `Shaders/WaterSim.compute`: kerneli `CSInit`, `CSStep` (difuzija po pseudokodu),
  `CSStepWave` (talasna jednačina), `CSNormals`, `CSSplash`.
- `Shaders/Water.shader`: vertex displacement iz mape visina (`tex2Dlod`, zato
  `#pragma target 3.0`), cube-map refleksija, spekular usmerenog svetla, Fresnel prozirnost.
- `Editor/SkyboxCubemapGenerator.cs`: meni `RG2 → Generate Sky Cubemap`.
- `Scenes/Water.unity`: površ, kamera (tag `MainCamera`, traži ga `Camera.main`), usmereno svetlo.

Mrežu i materijal pravi `Start()`, pa je scena **prazna u Edit modu**; vidi se tek u Play modu.
`Library/`, `Temp/`, `Logs/`, `UserSettings/` pokriva `dz2/.gitignore` i nikad se ne commit-uju.

**Dva režima** (`Mode` u Inspektoru): `Diffusion` je doslovno pseudokod iz postavke, `Wave` je
talasna jednačina sa putujućim ripple-ovima (scena je podešena na `Wave`, jer slika rezultata u
postavci prikazuje interferenciju koju difuzija ne proizvodi). Za doslovnu podudarnost sa
pseudokodom: `Mode = Diffusion` **i** `Restore Factor = 0`, pošto taj član ne postoji u postavci.

**Zahtevi postavke (checklist):** mapa visina preko Compute shader-a u svakom frejmu pre crtanja,
mapa normala istih dimenzija po zadatoj formuli, empirijski `damp_factor`/dimenzije/`strength`,
površ kao mreža trouglova sa visinama iz teksture u vertex shader-u, podesiva boja vode,
refleksija cube mape, spekular usmerenog svetla, prozirnost opada sa porastom ugla
normala-pogled, bez kaustike i refrakcije, talasanje „šaranjem" kursora sa intenzitetom
podesivim iz Editora. Domaći se brani u ispitnom roku.

## Submodule napomene

```
git clone --recurse-submodules https://github.com/MegatronJeremy/RG2
git submodule update --init --recursive   # ako je repo već kloniran
```
Snowstorm-Engine ima sopstveni razvojni tok i `master` granu; ovde se referencira kao submodule.
