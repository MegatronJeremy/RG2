# DZ2 — Interaktivna simulacija vodene površi (Unity)

Drugi domaći iz **Računarske grafike 2**. Postavka: [`../DZ2_2025.pdf`](../DZ2_2025.pdf).

Vodena površ se simulira mapom visina koja se **u svakom frejmu iznova računa na GPU-u
preko Compute programa za senčenje**, pre crtanja. Iz mape visina se na isti način pravi
i mapa normala. Površ je mreža trouglova čija se temena izdižu čitanjem visine u vertex
shader-u; u vodi se ogleda ambijent (cube map) i spekular usmerenog svetla, a prozirnost
opada sa uglom između normale i pravca pogleda. Korisnik talasa vodu „šaranjem" kursora.

## Tehnologija

- **Unity 2022.3.4f1** (LTS), **Built-in Render Pipeline**
- Compute shader (HLSL) za mapu visina i normala; vodeni shader u CG/HLSL-u

## Pokretanje

Najlakše preko priloženih skripti (same nađu Unity čija verzija odgovara
`ProjectSettings/ProjectVersion.txt`):

```
run-editor.bat       # otvori projekat u Editoru sa scenom Water, pa pritisni Play
run-game.bat         # build standalone playera u Build\ i pokreni ga
```

Oba su tanki omotači oko `run.ps1`, koji prima i `build` (samo build) i `check`
(koji Unity se koristi, da li je Editor otvoren, kad je player build-ovan).
Batch build ne može preko projekta koji Editor drži zaključanim, pa `run-game.bat`
traži zatvoren Editor i to jasno kaže umesto da pukne.

**Ručno:**

1. Otvori projekat `dz2/` u Unity Hub-u (verzija 2022.3.4f1).
2. Otvori scenu [`Assets/Scenes/Water.unity`](Assets/Scenes/Water.unity).
3. Ako refleksija izgleda bledo (nema skybox-a posle svežeg checkout-a), pokreni
   meni **`RG2 → Generate Sky Cubemap`** (generiše `SkyCubemap.cubemap` + skybox
   materijal i postavlja ga kao skybox scene), pa sačuvaj scenu.
4. Pritisni **Play**.

> Editor traži aktivnu licencu (prijava na Unity nalog kroz Hub); bez nje i `-batchmode`
> odbija da krene sa „No valid Unity Editor license found".

**Interakcija:** drži **levi klik** i prevlači mišem po površi da napraviš talase.
Intenzitet i veličina poteza se podešavaju u Inspektoru (komponenta *Water Simulation*).

## Struktura

```
Assets/
├── Scenes/Water.unity            # scena (površ, kamera, svetlo, skybox)
├── Scripts/WaterSimulation.cs    # mesh, dispatch compute-a, interakcija, parametri
├── Shaders/
│   ├── WaterSim.compute          # kerneli: init, korak (difuzija/talas), normale, splash
│   └── Water.shader              # vertex displacement + refleksija + spekular + Fresnel
├── Editor/SkyboxCubemapGenerator.cs  # generiše cube map nebo (meni RG2)
├── Editor/PlayerBuild.cs         # build standalone playera (meni RG2 + run.ps1)
├── SkyCubemap.cubemap            # generisani skybox (cube map koji se ogleda u vodi)
└── SkyboxMaterial.mat
run.ps1, run-editor.bat, run-game.bat   # pokretanje u Editoru / kao standalone player
```

`PlayerBuild` prosleđuje scenu eksplicitno, pa `ProjectSettings/EditorBuildSettings.asset`
ostaje prazan i build radi na svežem checkout-u bez podešavanja Build Settings-a.
Shader `RG2/Water` se traži preko `Shader.Find` u runtime-u, pa ga ništa u sceni ne
referencira; zato je upisan u **Always Included Shaders**, inače ga build izbaci i površ
u playeru ispadne magenta (u Editoru se ta razlika ne vidi).

## Kako radi (protok)

Svaki simulacioni korak (`WaterSimulation.StepSimulation`):

1. **Mapa visina** (`CSStep` / `CSStepWave`) — ping-pong između dve `RFloat` teksture.
2. **Mapa normala** (`CSNormals`) — iz nagiba visina, po formuli iz postavke
   `normal = normalize(-dx·s, 1, -dy·s)`.
3. **Crtanje** — `Water.shader`: vertex faza diže temena iz mape visina (`tex2Dlod`),
   fragment faza računa refleksiju cube mape (`unity_SpecCube0`), Blinn-Phong spekular
   usmerenog svetla i Fresnel prozirnost (`alpha = lerp(minAlpha, 1, fresnel)`).

Interakcija (`CSSplash`) ubacuje talas na mestu kursora; pozicija se dobija presekom
zraka iz kamere sa osnovnom ravni površi.

### Dva režima simulacije

Postavka daje pseudokod koji je **difuzija** (`next = (1-damp)·current + damp·prosek4`),
ali priložena slika rezultata prikazuje **talase koji se šire i interferiraju** — što
difuzija ne proizvodi. Zato postoje oba režima (`Mode` u Inspektoru):

| Režim | Formula | Ponašanje |
| --- | --- | --- |
| **Diffusion** | doslovno po pseudokodu | površ se izglađuje; bez putujućih talasa |
| **Wave** | talasna jednačina `next = damp·(prosek4/2 − prethodni)` | koncentrični ripple-ovi koji se šire i interferiraju (kao slika u postavci) |

Wave režim kreće od mirne (ravne) vode; difuzija od nasumične mape.

## Mapiranje na zahteve postavke

- [x] Mapa visina u runtime-u, svaki frejm, preko Compute shader-a (`CSStep`)
- [x] Mapa normala na isti način, istih dimenzija (`CSNormals`)
- [x] Početna mapa visina inicijalizovana (nasumično / mirno), `damp` i dimenzije empirijski
- [x] Površ kao mreža trouglova; visine temena iz teksture u vertex shader-u
- [x] Podesiva boja vode
- [x] Refleksija ambijenta (cube map) + spekular usmerenog svetla
- [x] Prozirnost opada sa porastom ugla normala–pogled (Fresnel)
- [x] Bez kaustike i refrakcije
- [x] Interakcija kursorom; intenzitet talasa podesiv iz Editora

## Parametri (komponenta *Water Simulation*)

| Parametar | Uloga | Preporuka (Wave) |
| --- | --- | --- |
| `Mode` | difuzija ili talasna jednačina | Wave |
| `Damp Factor` | difuzija: brzina izglađivanja; Wave: prigušenje talasa | ~0.97 |
| `Restore Factor` | povratak ka mirnom nivou (samo difuzija) | 0.02 |
| `Simulation Rate` | koraka/sec — manji = sporije širenje talasa | ~30 |
| `Height Map Size` | rezolucija mapa; veći = finiji i sporiji talasi | 256–512 |
| `Max Wave Height` | amplituda izdizanja temena | 0.5–0.8 |
| `Normal Strength` | koliko talasi hvataju svetlo/refleksiju | ~6 |
| `Water Color` / `Reflectivity` / `Shininess` | boja, udeo refleksije, oštrina odsjaja | — |
| `Fresnel Power` / `Min Alpha` | oštrina Fresnel prelaza / prozirnost odozgo | 5 / ~0.5 |
| `Interaction Strength` / `Brush Radius` | jačina i veličina poteza mišem | — |
