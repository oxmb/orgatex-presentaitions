# ORGATEX Corporate Identity

Verbindliche CI-Vorgaben für alle Präsentationen und Medien in diesem Repo.

Quellen:
- `~/obsidian/ORGATEX/STYLE.md` (technische Farb-/Schrift-Referenz inkl. Sphinx/XeLaTeX)
- [OX_CDDOK_05_25.pdf](https://orgatexgmbh.sharepoint.com/:b:/s/OXMarketing/IQDmlCR0X0HBQr844hlDibtNAbEo6SuS2GF20xwgXjO-gdw?e=jdtKYW)
  (Designelemente + Tonality Toolbox, Stand Oktober 2023)

## Farben

### Primärfarben (markenprägend, immer Priorität)

| Name | HEX       | RGB           | CMYK (coated) | PANTONE                             |
| ---- | --------- | ------------- | ------------- | ----------------------------------- |
| Gelb | `#ffd500` | 255 / 213 / 0 | 0/15/100/0    | Solid uncoated 108 U / coated 109 C |
| Weiß | `#ffffff` | 255 / 255 / 255 | -           | -                                   |

Gelb und Weiß bilden die markenprägende Farbkombination. Sie stehen bei jeder
Gestaltung an erster Stelle.

### Sekundärfarben (nicht markenprägend, strukturierende Funktion)

| Name       | HEX       | RGB             | CMYK      |
| ---------- | --------- | --------------- | --------- |
| Schwarz    | `#1d1d1b` | 0 / 0 / 0       | 0/0/0/100 |
| Dunkelgrau | `#6f6f6b` | 112 / 112 / 108 | 0/0/5/70  |
| Hellgrau   | `#f5f1e9` | 245 / 240 / 230 | 5/5/10/0  |

Schwarz dient primär der Typografie. Die Grautöne nur zur partiellen
Hinterlegung und Strukturierung, nie als Hauptgestaltungselement.

### Auszeichnungsfarben (nicht markenrelevant)

| Name | HEX       | RGB           | CMYK       |
| ---- | --------- | ------------- | ---------- |
| Rot  | `#e84e0f` | 230 / 80 / 15 | 0/80/100/0 |
| Cyan | `#009ed4` | 0 / 158 / 213 | 100/0/10/0 |

Nur für kleine Auszeichnungen (z. B. Infografiken), nie als Flächenfarbe.

### Erlaubte Farbkombinationen

- Gelb auf Schwarz / Schwarz auf Gelb
- Weiß auf Schwarz / Schwarz auf Weiß
- Gelb auf Weiß / Weiß auf Gelb
- Gelb / Schwarz / Weiß auf Dunkelgrau
- Gelb / Schwarz / Weiß auf Hellgrau

## Schrift

**Mundial** (Adobe Fonts) ist das primäre, markenrelevante Schriftbild.
Fallback in MS Office: **Arial**. Bevorzugte Schriftfarben: Schwarz und Weiß.

| Schnitt          | Einsatz                                   |
| ---------------- | ----------------------------------------- |
| Mundial Black    | Überschriften (Werbung)                   |
| Mundial Bold     | Überschriften (Editorial), Hervorhebungen |
| Mundial DemiBold | Zwischenüberschriften, Hervorhebungen     |
| Mundial Light    | Fließtext, Subheadlines, Introtext        |

### PDF-Ausgabe (XeLaTeX / Beamer / Sphinx)

Schrift-Mapping über fontspec (PostScript-Namen der OTF-Dateien, via
fontconfig aufgelöst). Schriftdateien liegen unter `fonts/` und werden im
Build-Image nach `/usr/share/fonts/mundial/` installiert.

| Rolle               | fontspec-Name         |
| ------------------- | --------------------- |
| Fließtext (upright) | `Mundial-Light`       |
| Fettdruck / Bold    | `Mundial-Bold`        |
| Kursiv              | `Mundial-LightItalic` |
| Fett-Kursiv         | `Mundial-BoldItalic`  |
| Monospace           | `DejaVu Sans Mono`    |

Überschriften aller Ebenen in ORGATEX-Schwarz `#1d1d1b`.

## Logo (Wortmarke / Superzeichen)

- Farbzustände der Wortmarke: gelb, weiß oder schwarz.
- Die Wortmarke steht als Absender immer auf **monochromem** Hintergrund;
  bevorzugt mit Primärfarbe Gelb (im Zeichen oder Hintergrund).
- Das Superzeichen ist einsetzbar, wenn für die Wortmarke kein Raum ist
  (z. B. Social-Media-Icons) oder als Gestaltungselement (ohne Registersymbol).
- Don'ts: Drehung, Effekte, Outlines, Mehrfarbigkeit, partielle Absenderschaft,
  Logo auf Fotomotiven oder farbigen (nicht-monochromen) Hintergründen.

## Bildwelt

Drei Kategorien: **Mensch**, **Produkt**, **Produkteinsatz**.
- Mensch: natürlich, authentisch, ungestellt; natürliche Lichtstimmung.
- Produkt: ästhetische Inszenierung, klare Ausrichtung, monochromer Hintergrund.
- Produkteinsatz: entsättigtes Gesamtbild, farbliche Produkt-Fokussierung.
Komposition: klare Linienführung, ruhige Bereiche.

## Sprache (Tonality Toolbox)

### Grundsätze

- Grundstimmung: Verlässlichkeit, Partnerschaftlichkeit, Kompetenz,
  Lösungsorientierung, Innovationsgeist. Hilfreich, einfach, aber niveauvoll.
- **Anrede: partnerschaftliches Sie** (kein Duzen; einzige mögliche Ausnahme
  HR/Azubi-Kommunikation).
- Schreibweisen: Unternehmensname **ORGATEX** in Versalien; Produktnamen als
  **EOX·PRODUKTNAME** bzw. **OX·PRODUKTNAME**.
- Gendering mit Doppelpunkt (Mitarbeiter:innen, Kund:innen); bei direkter
  Ansprache entfällt das Gendering.

### Zwei Ausprägungen

- **MÖGLICHMACHER** (Ergebnisorientierte, das Gros der Zielgruppe): kurze,
  schnörkellose, nutzenorientierte Sätze; Fakten, Zahlen, Belege; Nutzen vor
  Produktbeschreibung; Hervorhebungen als Ankerpunkte fürs Querlesen; keine
  Anglizismen ausser Fachsprache. Tonalität eher Handelsblatt.
- **WEGBEREITER** (Trendorientierte, Influencer/Multiplikatoren): Headlines mit
  News-Wert, kurze provozierende Reizworte, visuelle Sprachbilder, kräftige
  Verben; innovativ, aber geerdet.

### Dos and Don'ts

- agieren statt reagieren; "Wir wollen… / Wir werden…" statt "Wir könnten uns
  vorstellen…".
- Konkret und aktivierend: "Optimieren Sie Ihre Prozesse." statt "Dafür müssen
  die Prozesse optimiert werden."
- Präzise Nutzenargumente mit Zahlen ("höhere Klebkraft von 27 N/cm") statt
  vager Behauptungen ("kleben einfach besser").

## Don'ts (Gestaltung)

- Überladene Farbgestaltung (zu viele Flächen gleichzeitig)
- Grosse graue Flächen als Hauptgestaltungselement
- Hohe Präsenz der Auszeichnungsfarben (Rot, Cyan)
- Gestaltung ohne Primärfarben
