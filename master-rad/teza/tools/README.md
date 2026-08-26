# Alati za generisanje slika i brojeva u tezi

Svaka renderovana slika u `latex/figures/` i svaki izmereni broj u glavama 3 i 4 dolazi odavde ili
iz benchmark skripti endzina. Nista se ne crta rucno i nista se ne prepisuje iz screenshot-a.

## Zavisnosti

Skripte uvoze `Scripts/quality-bench.py` i `Scripts/perf-bench.py` iz `../../Snowstorm-Engine`, pa
traze inicijalizovan submodule i **build-ovan** `Snowstorm-Runtime` (i `Snowstorm-Editor` za
perf merenja):

```
cmake --build ../../Snowstorm-Engine/build --config Debug
```

Zavisnost ide samo u jednom smeru: teza zna za endzin, endzin ne zna za tezu. Zato ove skripte zive
ovde a ne u `Snowstorm-Engine/Scripts/`.

Traze pravi GPU (Vulkan), pa se ne mogu pokrenuti na CI-ju.

## Skripte

Generatori se dele na one koji traze GPU (snimci i sweep-ovi) i one koji samo citaju vec
committovane baseline-e, pa se izvrsavaju svuda.

| Skripta | GPU | Sta proizvodi |
|---|---|---|
| `thesis_shots.py` | da | 29 snimaka u `latex/figures/`: teaser, senke (mapa/RT, tvrde/meke), refleksije (bez/SSR/RT), GI (bez/sa, polovicna/puna rezolucija), path-traced referenca, deset `render.debugview` rezima, i screen-space naspram RT parovi |
| `raycount_denoise_sweep.py` | da | `raycount_denoise_results.json` plus slike `spp_sweep_*.png` i `denoise_compare_*.png` |
| `gen_perf_tables.py` | ne | `data/perf-{effects,passes,shadow-strategy,macros}.tex` iz `Scripts/perf-baseline/` |
| `gen_perf_plots.py` | ne | `data/{ladder,passcost-vendor,quality-spread}.dat` za pgfplots |
| `gen_quality_tables.py` | ne | `data/{quality,raycount,denoise-eval,motion,motion-probes}.tex` i `quality-macros.tex` |
| `gen_shader_tables.py` | ne | `data/shader-occupancy.tex` i `data/occupancy-{curve,marks}.dat` iz RGA baseline-a |

Svaki generator ima `--check`, koji ne pise nista i vraca ne-nulti kod ako je izlaz zastareo u
odnosu na baseline. To je kapija: ako `--check` prijavi STALE, brojevi u tezi vise ne odgovaraju
merenjima.

```
py thesis_shots.py
py raycount_denoise_sweep.py
for g in gen_perf_tables gen_perf_plots gen_quality_tables gen_shader_tables; do py $g.py --check; done
```

### Alati za analizu teksta

Ne proizvode nista u tezi; sluze za odrzavanje.

| Skripta | Cemu sluzi |
|---|---|
| `trim_inventory.py` | Snima skup citata, generisanih makroa, izmerenih decimala i labela pre skracivanja i uporedjuje posle (`snapshot` / `compare`). Skracivanje sme da brise recenice, ne sme da izgubi merenje ili citat; ovim se to proverava umesto da se tvrdi. Brojeve broji samo u prozi, jer su decimale unutar TikZ koordinata i sirina slika raspored, ne merenje. |
| `section_sizes.py` | Broj reci po `\section`, da skracivanje gadja najvece blokove umesto da svuda pomalo struze. Broji i sadrzaj plutajucih okruzenja, pa je sekcija sa dosta slika naduvana u odnosu na svoju prozu. |
| `find_dupes.py` | Parovi recenica koje tvrde isto na dva mesta, rangirani po deljenim retkim recima. Brisanje druge tvrdnje ne gubi informaciju, za razliku od brisanja jedinstvenog pasusa. |

`.capture-cache/` je medjukorak (`.npy` readback po snimku) i gitignore-ovan je.

## Brojevi koji ne dolaze odavde

Tabele 4.2 (cena po efektu), 4.5 (per-pass) i 4.7 (zauzetost) citaju se iz committovanih baseline-a
u endzinu, ne iz ovih skripti:

```
cd ../../Snowstorm-Engine
py Scripts/perf-bench.py --gpu 9070      # verifikuje da baseline-i i dalje vaze
py Scripts/rga-occupancy.py --spv-dir Engine/cache/shaders-cook
```

Baseline-i su kljucirani po adapteru (`Scripts/perf-baseline/<uredjaj>/`), pa brojevi za 9070 XT i
5070 dolaze iz iste generacije merenja pri istoj rezoluciji i fiksiranoj pozi kamere.

## Poza kamere

`rot` je `[pitch, yaw, roll]` u radijanima i **pozitivan pitch gleda NAGORE**
(`TransformComponent` gradi Y*X*Z nad -Z napred). Imena poza u `thesis_shots.py` opisuju sta se
zaista vidi, ne znak ugla.
