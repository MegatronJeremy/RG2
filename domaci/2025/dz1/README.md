# DZ1 — Planeta Zemlja (OpenGL 4)

Prvi domaći iz RG2: simulacija planete Zemlje (cube-sphere, height-map teren, Phong
senčenje, normal/specular mape, skybox, interaktivna kamera). Postavka: [postavka.pdf](postavka.pdf).

## Pokretanje

Najlakše preko priložene skripte (auto-detektuje Maven i JDK — i sa PATH-a i iz
IntelliJ/JetBrains instalacije):

```powershell
.\run.ps1            # interaktivni meni
.\run.ps1 run        # build + pokreni simulaciju
.\run.ps1 build      # samo build (package)
.\run.ps1 clean      # ocisti target/
.\run.ps1 check      # prikazi koje mvn/java koristi (+ verzije)
```

**Ručno preko Mavena** (ako su `mvn` i `java` na PATH-u):

```bash
mvn compile exec:java        # pokreni (main: opengl4.dz1.Main)
mvn package                  # build
```

**Iz IDE-a:** otvori `pom.xml` kao projekat i pokreni klasu `opengl4.dz1.Main`.

> Zahteva GPU/displej — otvara se NEWT prozor. Zavisnosti (JogAmp JOGL 2.6.0, JOML,
> pngdecoder) se povlače Mavenom; JOGL sam raspakuje native biblioteke u runtime-u.

## Kontrole

| Akcija | Kontrola |
| --- | --- |
| Zoom (približavanje/udaljavanje) | točkić miša (srednji taster) |
| Rotacija oko Y ose | levi taster + horizontalno pomeranje |
| Rotacija oko X ose | levi taster + vertikalno pomeranje |

## Struktura

```
src/main/java/opengl4/
├── common/   # framework sa nastave (kamera, shader-programi, scene, teksture)
└── dz1/      # resenje: CubeSphereGenerator, EarthMesh/EarthShaderProgram,
              #          SkyboxMesh/SkyboxShaderProgram, EditorCameraView, Main
src/main/resources/opengl4/dz1/   # GLSL shaderi + teksture (earth/height/normal/specular, skybox)
```
