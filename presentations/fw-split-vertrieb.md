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

## Welche Modi sind möglich?

| Produkt | API-Modus | Button-Modus | Umschaltbar |
|---|:---:|:---:|:---:|
| **OX-Label** | ✓ | ✓ | ✓ |
| **OX-Button** | ✗ | ✓ | ✗ |

- Gleiche Hardware, pro Produkt sind unterschiedliche Modi freigeschaltet
- **OX-Label**: beide Modi möglich, per Konfiguration umschaltbar, das flexible Produkt
- **OX-Button**: nur Button-Modus, weniger Funktionen, das günstigere Produkt

## Szenario A: Kombinierte Firmware

::: columns
:::: column
- Eine Firmware für beide Produkte
- Feature-Flags wählen den Modus, immer nur einen
- **OX-Label**: API- oder Button-Modus, per Flag umschaltbar
- **OX-Button**: fest im Button-Modus
- Upgrade **OX-Button** auf **OX-Label**: nur Flag ändern, kein OTA
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
- Update beim nächsten OTA-Intervall, bis zu 24 h ohne physischen Zugriff
- Sofort: Gerät 10 Sekunden gedrückt halten
::::
:::: column
![](assets/mockups/ota-dashboard.png)
::::
:::

## Vergleich

| Kriterium | A: Kombiniert + Flags | B: Getrennte Firmwares |
|---|---|---|
| Wartungsaufwand | ✓ Ein Codebase, aber Flag-Komplexität | ✗ Zwei Firmwares zu pflegen |
| Flexibilität | ✓ Flag-Wechsel reicht für Upgrade | ✗ Kein Wechsel ohne OTA |
| Kundenerfahrung | Kein OTA nötig | Wechsel per OTA |
| Time-to-Market | ✗ Jede Änderung betrifft beide Produkte | ✓ Fokus auf die wichtigere Firmware |

- Für **OX-Button** kein Unterschied: die Wahl betrifft allein **OX-Label**.

## Zur Entscheidung

- **Szenario A wählen wenn:** Der einfache Upgrade-Pfad **OX-Button** auf **OX-Label** ohne OTA zählt am meisten
- **Szenario B wählen wenn:** Entwicklungsfokus und saubere Trennung der Produkte zählen am meisten
