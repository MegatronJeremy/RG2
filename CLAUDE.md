# CLAUDE.md — radni okvir za RG2 repozitorijum

Repozitorijum predmeta **Računarska grafika 2** (13M111RG2, master ETF Beograd): materijali
sa nastave, domaći zadaci i projekti. Ovaj repo je i sam **submodule** super-projekta
`MegatronJeremy/ETF-Master`. Pregled sadržaja je u [README.md](README.md), kompletan spisak
materijala sa linkovima u [INDEX.md](INDEX.md).

## Layout

```
materijali/        # prezentacije, predavanja (arhiva), vezbe, seminarski, dodatni, propozicije
domaci/<godina>/   # domaći zadaci; svaki u svom folderu (npr. domaci/2025/dz1/)
Snowstorm-Engine/  # render engine (ugnježdeni git submodule)
```

- **Folderi sa sadržajem → mala slova** (`materijali`, `vezbe`, `dz1`), bez naših slova sa
  kvačicama (`vezbe`, ne `vežbe`). **Imena projekata → PascalCase** (`Snowstorm-Engine`).
- Domaći **nisu** submoduli — žive direktno u ovom repou. Submodule je rezervisan za
  samostalne, ponovo-upotrebljive projekte (kao Snowstorm-Engine).

## Standardni kvalitetski okvir (poštuj na svakoj izmeni)

1. **Jedan inkrement po koraku.** Svaki korak ostavlja repo u pokretljivom stanju.
2. **Commit + push nakon svakog koraka.** Commit u relevantnom repou (RG2 ili submodule), zatim
   ako je dirnut submodule — bump pokazivača u nadređenom repou i push i njega, da remote uvek
   bude konzistentan. Poruke commit-a na srpskom, kratke i konkretne.
2b. **Code review u chatu pre push-a.** Za svaku novu funkcionalnost/izmenu, pre nego što
   gurneš (`git push` + bump pokazivača), prikaži pregled koda u razgovoru — kao što bi
   senior inženjer pregledao PR. Pokaži konkretne snippet-e **sa dovoljno okolnog koda**
   (funkcija/blok u kome izmena živi, linije iznad i ispod — ne izolovane fragmente, već
   kako se pravi PR diff čita), sa komentarima koji objašnjavaju *zašto* je nešto urađeno
   tako, kompromise, ne-očigledne invarijante, rizike i šta treba dodatno proveriti. Navedi
   šta jeste/nije verifikovano
   (posebno vizuelne/headless rupe). Lokalni commit pre review-a je u redu; kapija je na
   **push**. Guraj (oba repoa) tek nakon što Vuk odobri.
3. **Git higijena.** Nikad ne commit-uj `target/`, `.idea/`, `*.iml`, IDE/build artefakte
   (vidi `domaci/2025/dz1/.gitignore`). Originalne velike `.zip` materijale čuvaj u izvornom
   obliku, ne raspakuj ih u repo bez razloga.
4. **Verify-before-claim.** Pre tvrdnje o kodu/ponašanju proveri naspram **stvarnog fajla ili
   komande** (otvori, `grep`, build), ne iz imena ili pretpostavke. Što ne možeš potvrditi —
   označi kao pretpostavku.
5. **Grafiku potvrdi vizuelno.** OpenGL rezultat se ne može verifikovati headless — traži
   GPU/displej i NEWT prozor. Tvrdnju „radi/izgleda ispravno" donosi tek nakon pokretanja i
   screenshot-a; inače jasno reci da nije vizuelno potvrđeno.
6. **Jezik:** kod, komentari i identifikatori na **engleskom**; komunikacija sa Vukom na srpskom.

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
