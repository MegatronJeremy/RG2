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

| Skripta | Sta proizvodi |
|---|---|
| `thesis_shots.py` | 18 snimaka u `latex/figures/`: teaser, senke (tvrde/meke), refleksije (bez/RT), GI (bez/sa), path-traced referenca, osam `render.debugview` rezima, i screen-space naspram RT par |
| `raycount_denoise_sweep.py` | Tabele 4.3 i 4.4 (kvalitet i GPU cena po broju zraka, evaluacija denoiser-a) + slike `spp_sweep_*.png` i `denoise_compare_*.png`, plus `raycount_denoise_results.json` |

```
py thesis_shots.py
py raycount_denoise_sweep.py
```

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
