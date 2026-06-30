# Design: Vertriebspräsentation Firmware-Trennung (OXL2-1300)

**Datum:** 2026-06-30
**Deadline:** 2026-07-01
**Jira:** [OXL2-1300](https://orgatex.atlassian.net/browse/OXL2-1300)
**Verwandt:** [OXL2-1276](https://orgatex.atlassian.net/browse/OXL2-1276)

## Ziel

Entscheidungsgrundlage für den Vertrieb: Szenario A (getrennte Firmwares) vs. Szenario B (kombinierte Firmware mit Feature-Flags). Der Vertrieb soll nach der Präsentation eine Richtungsentscheidung treffen können.

## Foliensatz-Struktur (7 Folien)

### Folie 1 - Ausgangslage

- Gleiche Hardware (nRF9151) für OX-Label und OX-Button
- Produktidentität entsteht erst durch Firmware und Cloud-Konfiguration
- Aktuell: eine gemeinsame Firmware mit Feature-Flags für beide Produkte
- Frage: Weiter so, oder trennen?

### Folie 2 - Was braucht welches Produkt?

- OX-Label: API-Abfrage (Inhalt vom Server) + Button-Flow
- OX-Button: nur Button-Flow
- Beide Produkte benötigen Onboarding über ThingsBoard (Claiming + OTA)

### Folie 3 - Szenario A: Getrennte Firmwares

- Zwei unabhängige Firmware-Produkte: `ox-label` und `ox-button`
- Je ein eigenes ThingsBoard Device Profile mit eigenem OTA-Kanal
- Gerät erhält beim Onboarding das produktspezifische Firmware-Image via OTA
- Upgrade Button→Label: neues OTA-Image erforderlich (kein Zero-Touch)
- Jede Firmware enthält nur die eigenen Features (kein ungenutzter Code der anderen Produktlinie)

### Folie 4 - Szenario A: OTA-Flow (mit Mockup)

Zweispaltig:

**Links - User-Flow:**
- Kunde kauft OX-Label oder OX-Button
- Onboarding: Claiming über ThingsBoard
- OTA-Dashboard zeigt verfügbares Firmware-Update an
- Gerät lädt Firmware beim nächsten OTA-Intervall
- Sofortige Aktualisierung: 10-Sekunden-Reset am Gerät

**Rechts - Mockup:** ThingsBoard OTA-Dashboard
- Geräteliste mit aktuellem Firmware-Stand
- "Firmware-Update verfügbar"-Anzeige
- Hinweis auf Intervall vs. sofortigen Reset

### Folie 5 - Szenario B: Kombinierte Firmware (mit Mockup)

Zweispaltig:

**Links - Funktionsweise:**
- Eine Firmware für beide Produkte
- ThingsBoard Server-Side Attributes (Feature-Flags) steuern, welche Funktionen aktiv sind
- OX-Label-Flag: API + Button aktiv
- OX-Button-Flag: nur Button aktiv
- Upgrade Button→Label: Flag-Änderung in ThingsBoard reicht, kein OTA

**Rechts - Mockup:** ThingsBoard Attribute-Panel mit Feature-Flag-Konfiguration

### Folie 6 - Vergleich

| Kriterium         | A: Getrennte Firmwares                              | B: Kombiniert + Flags                          |
|-------------------|-----------------------------------------------------|------------------------------------------------|
| Wartungsaufwand   | Zwei separate Produkte zu pflegen                   | Ein Codebase, aber Flag-Komplexität            |
| Flexibilität      | Kein spontaner Upgrade ohne OTA                     | Flag-Wechsel reicht für Upgrade                |
| Kundenerfahrung   | OTA beim Onboarding nötig                           | Kein OTA-Schritt beim Onboarding               |
| Time-to-Market    | Besser: Fokus auf wichtigere FW, keine Projektabhängigkeiten | Schlechter: jede Änderung muss beide Use Cases berücksichtigen |

### Folie 7 - Zur Entscheidung

Offene Folie - kein Votum, Entscheidung beim Vertrieb:

- **Szenario A wählen wenn:** Entwicklungsfokus und saubere Produkttrennung wichtiger als Zero-Touch-Upgrade
- **Szenario B wählen wenn:** Einfacher Upgrade-Pfad Button→Label und kein OTA beim Onboarding oberste Priorität

## Mockups

### Mockup 1: ThingsBoard OTA-Dashboard

HTML-Mockup, ThingsBoard-Look (dunkles Theme, tabellarische Geräteliste).

Zeigt:
- Tabelle: Gerätename, Seriennummer, aktuelle Firmware-Version, Status
- Zeile mit "Firmware-Update verfügbar" (gelb markiert)
- Knopf "Jetzt aktualisieren"
- Hinweistext: "Aktualisierung beim nächsten OTA-Intervall. Für sofortige Aktualisierung: Gerät 10 Sekunden lang zurücksetzen."

### Mockup 2: ThingsBoard Feature-Flag-Panel

HTML-Mockup, ThingsBoard-Look.

Zeigt:
- Server-Side Attributes eines Geräts
- Attribut `ox_label_api_enabled: true/false`
- Attribut `ox_button_only: true/false`
- Edit-Knopf

## Datei

`presentations/fw-split-vertrieb.md`

## Abhängigkeiten

- Build-Pipeline für Mockups: `scripts/build-mockups.py` (vorhanden)
- Pandoc-Build: `make` (vorhanden)
- ThingsBoard-Look: angelehnt an bestehendes dunkles Dashboard-Design
