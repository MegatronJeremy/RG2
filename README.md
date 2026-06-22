# Računarska grafika 2 (RG2)

Materijali, zadaci i projekti sa predmeta **Računarska grafika 2** — izborni predmet
master studija na [Elektrotehničkom fakultetu Univerziteta u Beogradu](https://www.etf.bg.ac.rs/).

> Zvanični sajt predmeta: <https://rti.etf.bg.ac.rs/rti/ms1rg2/>

## Sadržaj repozitorijuma

| Folder | Opis |
| --- | --- |
| [`materijali/prezentacije/`](materijali/prezentacije/) | Aktuelne prezentacije sa predavanja (uvod, vektorska algebra, transformacije, OpenGL, Unity) |
| [`materijali/predavanja/`](materijali/predavanja/) | Stariji/arhivski materijali sa predavanja (OpenGL fiksni i programabilni protok, Unity) |
| [`materijali/vezbe/`](materijali/vezbe/) | Materijali sa vežbi (OpenGL osnovno, OpenGL shaders, Unity) |
| [`materijali/seminarski/`](materijali/seminarski/) | Spisak tema i šablon za seminarski rad |
| [`materijali/dodatni/`](materijali/dodatni/) | Dodatna literatura |
| [`materijali/RG2_Propozicije.pdf`](materijali/RG2_Propozicije.pdf) | Propozicije polaganja predmeta |
| [`domaci/`](domaci/) | Domaći zadaci po godinama |
| [`Snowstorm-Engine/`](Snowstorm-Engine/) | Projekat — render engine (git submodule) |

Kompletan spisak svih fajlova sa direktnim linkovima nalazi se u **[INDEX.md](INDEX.md)**.

## Snowstorm-Engine (submodule)

`Snowstorm-Engine/` je zaseban git repozitorijum uključen kao **submodule**
([MegatronJeremy/Snowstorm-Engine](https://github.com/MegatronJeremy/Snowstorm-Engine)).
Pri kloniranju je potrebno inicijalizovati submodule:

```bash
git clone --recurse-submodules https://github.com/MegatronJeremy/RG2
# ili, ako je repo već kloniran:
git submodule update --init --recursive
```

## Struktura

```
RG2/
├── README.md
├── INDEX.md
├── Snowstorm-Engine/        # submodule (render engine)
├── domaci/
│   └── 2025/
└── materijali/
    ├── prezentacije/
    ├── predavanja/
    ├── vezbe/
    ├── seminarski/
    ├── dodatni/
    └── RG2_Propozicije.pdf
```

## Napomena

Materijali su preuzeti sa zvaničnog sajta predmeta i organizovani radi lakšeg
snalaženja. Autorska prava nad materijalima pripadaju predmetnim nastavnicima i
saradnicima. Veliki `.zip` arhive (OpenGL/Unity demo projekti i vežbe) čuvaju se
u originalnom obliku.
