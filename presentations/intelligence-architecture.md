---
title: ORGATEX Intelligence
subtitle: "Erster Use Case: Hermes Agent"
author: Manoel Brunnen
date: 2026-06-30
---

# Ausgangslage

## Warum jetzt?

- KI-Agenten konsumieren APIs zunehmend ohne menschliche Interaktion
- Vertrieb: Kundeninformationen verteilt, Routineaufgaben binden Zeit
- ORGATEX Intelligence: KI-gestützte Abläufe mit Daten im eigenen Haus

## Rahmenbedingungen

- Budget: 10.000 EUR
- Datenschutz: kein externer Cloud-Anbieter, DSGVO-konform
- Quartalsberichte über eingesetzte Werkzeuge und Erkenntnisse

# Architektur

## Überblick

::: columns
:::: column
**Lokaler KI-Stack**

- LLM läuft auf eigenem Server (Mac Studio)
- Keine Kundendaten verlassen das Unternehmen
- Zugriff nur aus dem internen Netz (DMZ)
::::
:::: column
**Integrationen**

- Microsoft 365: Teams, Outlook, Kalender
- WhatsApp Business (Phase 2)
- CRM / Kundendatenbank (Phase 2)
::::
:::

## Datenfluss

::: columns
:::: column
1. Anfrage per Teams oder E-Mail
2. Agent liest Kontext (Kunde, Historie)
3. LLM generiert Antwort lokal
4. Agent sendet / erstellt Termin
5. Mitarbeiter genehmigt Versand
::::
:::: column
**Beteiligte Systeme**

- Ollama (lokales LLM)
- n8n (Agent-Orchestrierung)
- Microsoft Graph API (M365)
- Internes Netz / DMZ
::::
:::

# Nächste Schritte

## Fahrplan

- **Heute**: Use Cases und Anforderungen aufnehmen
- **KW 28-29**: IT-Konzept (DMZ, Netzwerk, Zugriffsschutz) → [INL-1239](https://orgatex.atlassian.net/browse/INL-1239)
- **KW 30**: Prototyp Hermes Agent auf Mac Studio
- **KW 32**: Pilotbetrieb mit Vertrieb
