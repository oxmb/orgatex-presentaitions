---
title: "OX-Label und OX-Button: Firmware-Strategie"
subtitle: "Entscheidungsgrundlage für den Vertrieb"
author: Manoel Brunnen
date: 2026-07-01
---

## Ausgangslage

- Gleiche Hardware (nRF9151) für OX-Label und OX-Button
- Produktidentität entsteht erst durch Firmware und Cloud-Konfiguration
- Aktuell: eine gemeinsame Firmware mit Feature-Flags für beide Produkte
- Frage: Weiter so, oder sauber trennen?

## Was braucht welches Produkt?

- OX-Label: API-Abfrage (Inhalt vom Server) und Button-Flow
- OX-Button: nur Button-Flow
- Beide Produkte benötigen Onboarding über ThingsBoard (Claiming und OTA)

## Szenario A: Getrennte Firmwares

- Zwei unabhängige Firmware-Produkte: ox-label und ox-button
- Je ein eigenes ThingsBoard Device Profile mit eigenem OTA-Kanal
- Gerät erhält beim Onboarding das produktspezifische Firmware-Image via OTA
- Upgrade Button auf Label: neues OTA-Image erforderlich
- Jede Firmware enthält nur die eigenen Features (kein ungenutzter Code der anderen Produktlinie)

## Szenario A: OTA-Flow

::: columns
:::: column
- Kunde kauft OX-Label oder OX-Button
- Onboarding: Claiming über ThingsBoard
- OTA-Dashboard zeigt verfügbares Firmware-Update an
- Gerät lädt Firmware beim nächsten OTA-Intervall
- Sofortige Aktualisierung: Gerät 10 Sekunden lang gedrückt halten
::::
:::: column
![](assets/mockups/ota-dashboard.png)
::::
:::

## Szenario B: Kombinierte Firmware

::: columns
:::: column
- Eine Firmware für beide Produkte
- ThingsBoard Server-Attribute (Feature-Flags) schalten Funktionen an oder ab
- OX-Label: API und Button aktiv
- OX-Button: nur Button aktiv
- Upgrade Button auf Label: Flag-Änderung in ThingsBoard reicht, kein OTA
::::
:::: column
![](assets/mockups/feature-flags.png)
::::
:::

## Vergleich

| Kriterium | A: Getrennte Firmwares | B: Kombiniert + Flags |
|---|---|---|
| Wartungsaufwand | Zwei separate Produkte zu pflegen | Ein Codebase, aber Flag-Komplexität |
| Flexibilität | Kein spontaner Upgrade ohne OTA | Flag-Wechsel reicht für Upgrade |
| Kundenerfahrung | OTA beim Onboarding nötig | Kein OTA-Schritt beim Onboarding |
| Time-to-Market | Besser: Fokus auf wichtigere FW, keine Projektabhängigkeiten | Schlechter: jede Änderung muss beide Use Cases berücksichtigen |

## Zur Entscheidung

- **Szenario A wählen wenn:** Entwicklungsfokus und saubere Produkttrennung wichtiger als Zero-Touch-Upgrade
- **Szenario B wählen wenn:** Einfacher Upgrade-Pfad Button auf Label und kein OTA beim Onboarding oberste Priorität
