---
title: "OX-Label und OX-Button: Firmware-Strategie"
subtitle: "Entscheidungsgrundlage für den Vertrieb"
author: Manoel Brunnen
date: 2026-07-01
---

## Ausgangslage

- Gleiche Hardware für **OX-Label** und **OX-Button**
- Die Produktidentität entsteht erst durch Firmware und Cloud-Konfiguration
- Aktuell: eine gemeinsame Firmware mit Feature-Flags für beide Produkte
- Frage: Weiter so, oder sauber trennen?

## Was braucht welches Produkt?

- **OX-Label**: API für Inhalte und den Button-Flow
- **OX-Button**: nur den Button-Flow
- Beide brauchen Onboarding über ThingsBoard

## Szenario A: Kombinierte Firmware

::: columns
:::: column
- Eine Firmware für beide Produkte
- ThingsBoard-Feature-Flags schalten Funktionen an oder ab
- **OX-Label**: API und Button aktiv
- **OX-Button**: nur Button aktiv
- Upgrade **OX-Button** auf **OX-Label**: Flag-Änderung reicht, kein OTA
::::
:::: column
![](assets/mockups/feature-flags.png)
::::
:::

## Szenario B: Getrennte Firmwares

- Zwei getrennte Firmwares: Label-Firmware nur API, Button-Firmware nur Button
- Je ein eigenes ThingsBoard Device Profile mit eigenem OTA-Kanal
- **OX-Label**: wechselt die Firmware per OTA
- **OX-Button**: fest auf Button-Firmware, kein Wechsel
- Jede Firmware enthält nur ihre eigenen Funktionen

## Szenario B: OTA-Flow

::: columns
:::: column
- Kunde kauft **OX-Label** oder **OX-Button**
- Onboarding per Claiming über ThingsBoard
- **OX-Label**: Firmware im OTA-Dashboard wählen
- **OX-Button**: bleibt fest auf Button-Firmware
- Update beim nächsten OTA-Intervall. Sofort: Gerät 10 Sekunden gedrückt halten.
::::
:::: column
![](assets/mockups/ota-dashboard.png)
::::
:::

## Vergleich

| Kriterium | A: Kombiniert + Flags | B: Getrennte Firmwares |
|---|---|---|
| Wartungsaufwand | Ein Codebase, aber Flag-Komplexität | Zwei Firmwares zu pflegen |
| Flexibilität | Flag-Wechsel reicht für Upgrade | Kein Wechsel ohne OTA |
| Kundenerfahrung | Kein OTA-Schritt nötig | **OX-Label** wechselt per OTA; **OX-Button** bleibt Button |
| Time-to-Market | Schlechter: jede Änderung betrifft beide Produkte | Besser: Fokus auf die wichtigere Firmware |

## Zur Entscheidung

- **Szenario A wählen wenn:** Der einfache Upgrade-Pfad **OX-Button** auf **OX-Label** ohne OTA zählt am meisten
- **Szenario B wählen wenn:** Entwicklungsfokus und saubere Trennung der Produkte zählen am meisten
