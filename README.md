<h1 align="center">MyCAD</h1>

<p align="center">
  <b>Korruse- ja ruumiplaanide joonistaja</b> · <b>Floor plan maker</b><br>
  Python + Tkinter · Windows / Linux / macOS<br>
  Autor / Author: Germo · Eesti 🇪🇪
</p>

<p align="center">
  <a href="#-eesti-keeles">🇪🇪 Eesti keeles</a> &nbsp;·&nbsp;
  <a href="#-in-english">🇬🇧 In English</a>
</p>

---

> ### ⬇️ Valmis programm / Ready-made program
>
> **🇪🇪 Windowsi valmis `MyCAD.exe`** on saadaval lehel **[Releases](../../releases)** või repo kaustas **[`dist/`](dist/)**.
> Pythonit pole vaja paigaldada – laadi alla ja topeltklõpsa.
>
> **🇬🇧 A ready-made Windows `MyCAD.exe`** is available under **[Releases](../../releases)** or in the repo's **[`dist/`](dist/)** folder.
> No Python installation needed – just download and double-click.

---

## 🇪🇪 Eesti keeles

### Mis see on?

MyCAD on lihtne programm maja, korteri või lao põhiplaani joonistamiseks. Joonistad seinad, lisad uksed, aknad ja mööbli ning vaatad tulemust kohe ka 3D-s.

### Võimalused

**2D-plaan**
- Seinad (kõrgus ja paksus, vaikimisi 260 / 15 cm), vabakäejooned ja mõõtmine
- Ruumid tuvastatakse automaatselt koos pindalaga
- Mitu korrust – alumise korruse seinad paistavad halli värviga läbi
- Uksed ja aknad on seina avad (laius, kõrgus, aknalaua kõrgus, avanemissuund)
- Ruudustik 20 / 10 / 5 / 1 cm, meetrid või tollid, hele või tume teema
- Topeltklõps seinal, uksel, aknal või mööblil avab selle omadused

**Mööbel**
- Valmis mööbliteek kategooriatega (elutuba, köök, magamistuba, vannituba, trepid, ladu …)
- Oma mööbli looja: joonista kuju, määra laius, sügavus ja kõrgus, vali täiskujund või riiul
- Kategooriate haldur – lisa, nimeta ümber, kustuta, muuda järjekorda
- **Virnastamine:** ese läheb all oleva eseme peale või riiulil vabale lauale
- **Riiuli eestvaade:** topeltklõps riiulil – lohista, lisa, kopeeri ja kustuta asju riiulilaudadel

**3D**
- Tarkvaraline 3D-vaade: pööra hiirega, liigu klaviatuuriga (WASD / QE, Shift = kiiremini)
- Jalutusrežiim silmade kõrgusel
- Kõik korrused või ainult aktiivne, mööbel sisse/välja
- Eksport OBJ + MTL failina (avaneb Blenderis jm)

**Muu**
- Projektid salvestatakse JSON-failidena; sulgemisel küsitakse salvestamata muudatuste kohta
- Mitu keelt (`lang/` kaust), keelt saab vahetada programmis
- **F1** avab klahvikombinatsioonide abiakna

### Käivitamine

**Variant 1 – valmis exe (Windows):** laadi `MyCAD.exe` alla [Releases](../../releases) lehelt või [`dist/`](dist/) kaustast, pane see eraldi kausta (nt `C:\Users\<nimi>\MyCAD`) ja topeltklõpsa.

**Variant 2 – Pythoniga (kõik süsteemid):**

```bash
py mycad.pyw          # Windows
python3 mycad.pyw     # Linux / macOS
```

Vaja on **Python 3.8+** koos **Tkinteriga**. Muid pakette pole vaja – programm kasutab ainult Pythoni standardteeki.
Linuxis võib Tkinter olla eraldi pakett: `sudo apt install python3-tk`.

### Exe ise tegemine (Windows)

Topeltklõpsa failil **`build.bat`**. See paigaldab vajadusel PyInstalleri ja teeb faili `dist\MyCAD.exe`.
Kui kaustas on `mycad.ico`, saab exe selle ikooni.

### Failid

| Fail / kaust | Mis see on |
|---|---|
| `mycad.pyw` | Programm |
| `lang/` | Keelefailid (`et.json`, `en.json`) ja juhend uue keele lisamiseks |
| `check_translations.py` | Kontrollib tõlgete puuduvaid võtmeid |
| `build.bat` | Teeb Windowsi exe-faili |
| `Info.txt` | Põhjalik kasutusjuhend eesti keeles |

Esimesel käivitusel loob programm enda kõrvale `config.json` (seaded), `library/` (mööbliteek) ja vea korral `error.log`.
Seepärast pane programm kausta, kuhu on kirjutamisõigus (mitte `C:\Program Files`).

### Uus keel

Kopeeri `lang/en.json` → `lang/<kood>.json`, muuda `_meta` ja tõlgi tekstid. Uus keel ilmub menüüsse **Seaded → Keel**.
Kontroll: `python check_translations.py`. Täpsem juhend: [lang/README.md](lang/README.md).

📖 Põhjalik juhend: **[Info.txt](Info.txt)**

---

## 🇬🇧 In English

### What is it?

MyCAD is a simple program for drawing floor plans of a house, apartment or warehouse. Draw walls, add doors, windows and furniture, and see the result in 3D right away.

### Features

**2D plan**
- Walls (height and thickness, 260 / 15 cm by default), freehand lines and measuring
- Rooms are detected automatically with their area
- Multiple floors – walls of the floor below show through in gray
- Doors and windows are wall openings (width, height, sill height, swing direction)
- Grid 20 / 10 / 5 / 1 cm, metric or imperial units, light or dark theme
- Double-click a wall, door, window or furniture item to edit its properties

**Furniture**
- Built-in furniture library with categories (living room, kitchen, bedroom, bathroom, stairs, storage …)
- Custom furniture creator: draw a shape, set width, depth and height, choose solid or shelf
- Category manager – add, rename, delete, reorder
- **Stacking:** an item goes on top of the one below it, or onto a free shelf board
- **Shelf front view:** double-click a shelf to drag, add, copy and delete items on its boards

**3D**
- Software-rendered 3D view: orbit with the mouse, move with the keyboard (WASD / QE, Shift = faster)
- Walk mode at eye level
- All floors or only the active one, furniture on/off
- Export as OBJ + MTL (opens in Blender etc.)

**Other**
- Projects are saved as JSON files; you are asked about unsaved changes when closing
- Multiple languages (`lang/` folder), switchable inside the program
- **F1** opens the keyboard shortcuts window

### Running

**Option 1 – ready-made exe (Windows):** download `MyCAD.exe` from [Releases](../../releases) or the [`dist/`](dist/) folder, put it in its own folder (e.g. `C:\Users\<name>\MyCAD`) and double-click it.

**Option 2 – with Python (any OS):**

```bash
py mycad.pyw          # Windows
python3 mycad.pyw     # Linux / macOS
```

Requires **Python 3.8+** with **Tkinter**. No other packages – the program uses only the Python standard library.
On Linux, Tkinter may be a separate package: `sudo apt install python3-tk`.

### Building the exe yourself (Windows)

Double-click **`build.bat`**. It installs PyInstaller if needed and creates `dist\MyCAD.exe`.
If a `mycad.ico` file is in the folder, it is used as the exe icon.

### Files

| File / folder | What it is |
|---|---|
| `mycad.pyw` | The program |
| `lang/` | Language files (`et.json`, `en.json`) and a guide for adding a language |
| `check_translations.py` | Checks translations for missing keys |
| `build.bat` | Builds the Windows exe |
| `Info_EN.txt` | Full user guide in English |

On first start the program creates `config.json` (settings), `library/` (furniture library) and, if something goes wrong, `error.log` next to itself.
So keep the program in a folder you can write to (not `C:\Program Files`).

### Adding a language

Copy `lang/en.json` → `lang/<code>.json`, edit `_meta` and translate the texts. The new language appears under **Settings → Language**.
Check with `python check_translations.py`. Details: [lang/README.md](lang/README.md).

📖 Full guide: **[Info_EN.txt](Info_EN.txt)**
