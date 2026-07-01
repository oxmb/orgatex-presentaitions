---
title: "OX-Label und OX-Button: Firmware-Strategie"
subtitle: "Entscheidungsgrundlage für den Vertrieb"
author: Manoel Brunnen
date: 2026-07-01
---

## Ausgangslage

- Gleiche Hardware für OX-Label und OX-Button
- Produktidentität entsteht erst durch Firmware und Cloud-Konfiguration
- Aktuell: eine gemeinsame Firmware mit Feature-Flags für beide Produkte
- Frage: Weiter so, oder sauber trennen?

## Was braucht welches Produkt?

- OX-Label: API-Abfrage (Inhalt vom Server) und Button-Flow
- OX-Button: nur Button-Flow
- Beide Produkte benötigen Onboarding über ThingsBoard (Claiming und OTA)

## Szenario A: Getrennte Firmwares

- Zwei unabhängige Firmware-Produkte: OX-Label und OX-Button
- Je ein eigenes ThingsBoard Device Profile mit eigenem OTA-Kanal
- OX-Label: erhält Label-Firmware via OTA beim Onboarding (API + Button aktiv)
- OX-Button: erhält Button-Firmware via OTA beim Onboarding, kann nur als Button genutzt werden
- Upgrade Button auf Label: erneutes OTA auf Label-Firmware erforderlich (explizite Entscheidung)
- Jede Firmware enthält nur die eigenen Features (kein ungenutzter Code der anderen Produktlinie)

## Szenario A: OTA-Flow

::: columns
:::: column
- Kunde kauft OX-Label oder OX-Button
- Onboarding: Claiming über ThingsBoard
- OTA-Dashboard: Label-Firmware auf OX-Label-Gerät installieren
- Gerät lädt Firmware beim nächsten OTA-Intervall (OX-Button bleibt Button)
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
| Kundenerfahrung | OX-Label via OTA; OX-Button nur Button (kein Upgrade ohne OTA) | Kein OTA-Schritt beim Onboarding oder Upgrade |
| Time-to-Market | Besser: Fokus auf wichtigere FW, keine Projektabhängigkeiten | Schlechter: jede Änderung muss beide Use Cases berücksichtigen |

## Zur Entscheidung

- **Szenario A wählen wenn:** Entwicklungsfokus und saubere Produkttrennung wichtiger als Zero-Touch-Upgrade
- **Szenario B wählen wenn:** Einfacher Upgrade-Pfad Button auf Label und kein OTA beim Onboarding oberste Priorität
