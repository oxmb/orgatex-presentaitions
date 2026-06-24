# Hermes-Vertriebs-Pitch: Foliendesign

Date: 2026-06-24
Status: design (pending review)

## Problem

Die Vertriebskolleginnen und -kollegen sind viel unterwegs und brauchen
niedrigschwellige Unterstützung beim Kunden: schnelle Infos, E-Mail-Entwürfe,
Posteingang im Griff. Es gibt noch kein Werkzeug dafür, und der lokale KI-Stack
(siehe `testing-infrastructure/docs/specs/2026-06-18-ai-stack-spike-design.md`)
ist zwar im Aufbau, aber im Vertrieb unbekannt.

Diese Spec beschreibt **den Inhalt und die Bebilderung der ersten echten
Präsentation**, nicht die Render-Pipeline. Die Pipeline (Pandoc-Referenz,
Makefile, `defaults.yaml`) ist in
`docs/specs/2026-06-24-orgatex-pandoc-presentations-design.md` beschrieben und
muss vorhanden sein, bevor dieses Deck gebaut werden kann.

## Ziel

1. Ein Pitch-Deck, das Hermes als KI-Assistenten für den Vertrieb vorstellt,
   anhand von vier konkreten Anwendungsfällen.
2. Buy-in im Sinne von „erst Feedback einsammeln": kein harter Beschluss,
   sondern Anwendungsfälle und Kanalwünsche der Kollegen erheben.
3. Reich bebildert über realistische Chat-Mockups (Slack-Stil).

## Zielgruppe

Vertriebskolleginnen und -kollegen, nicht-technisch, oft unterwegs. Das Deck ist
bewusst nutzenorientiert und meidet Architektur-Details. Datenresidenz erscheint
als eine Vertrauensfolie, nicht als technischer Schwerpunkt.

## Entscheidungen

| Entscheidung | Wahl | Begründung |
|--------------|------|------------|
| Sprache | Deutsch, echte Umlaute, kein Gedankenstrich | Zielgruppe; Hausregeln |
| Erzählbogen | Problem -> Lösung -> Vorschlag, ~9 Folien | Klassischer, überzeugender Buy-in-Bogen |
| Schluss-Ask | Erst Feedback einsammeln | Niedrige Schwelle; Anwendungsfälle und Kanal erheben |
| Bebilderung | Messenger-Mockups | Höchste Überzeugungskraft beim Vertriebspublikum |
| Mockup-Stil | Slack | Professioneller Look; offiziell unterstützter Hermes-Kanal; einfacher als Teams |
| Bild-Pipeline | HTML -> PNG, beides committet | Editierbarer Wortlaut, reproduzierbar |

## Foliengliederung

`presentations/hermes-vertrieb.md`. `slide-level: 2` (siehe Pipeline-Spec):
Eine Ebene-1-Überschrift (`#`) erzeugt eine Section-Header-Folie, eine
Ebene-2-Überschrift (`##`) eine Inhaltsfolie.

| # | Folie | Inhalt (Kern) | Pandoc-Layout |
|---|-------|---------------|---------------|
| 1 | Titel | „Hermes: Ein KI-Assistent für den Vertrieb" / „Weniger Routine, mehr Zeit für den Kunden" | Title Slide |
| 2 | Problem: Der Vertriebsalltag heute | Viel unterwegs, wenig Zeit am Laptop; Kundeninfos verstreut; Posteingang voll | Title and Content |
| 3 | Lösung: Was ist Hermes? | Persönlicher KI-Assistent, erreichbar über euren Arbeits-Messenger (z. B. Slack) und E-Mail; merkt sich Kontext und Schreibstil; arbeitet auch offline; eigene Instanz pro Person (kein gemeinsamer Dienst) | Title and Content |
| 4 | Kundenrecherche vor dem Termin | Text links, Slack-Mockup rechts | Two Content |
| 5 | E-Mails entwerfen | Text links, Slack-Mockup rechts | Two Content |
| 6 | Posteingang-Zusammenfassung | Text links, Slack-Mockup rechts | Two Content |
| 7 | Schnelle Antworten unterwegs | Text links, Slack-Mockup rechts | Two Content |
| 8 | Ihre Daten bleiben im Haus | Lokales Modell auf eigenem Server, kein externer Cloud-Anbieter, DSGVO-freundlich; genau dafür wurde der lokale KI-Stack gebaut | Title and Content |
| 9 | Wofür würden SIE es nutzen? | Offene Diskussion: eure Anwendungsfälle? Wäre Slack als Kanal okay, oder etwas anderes? Wie organisieren wir die Einrichtung pro Person? | Section Header |

Eine optionale Trennfolie „Vier Anwendungsfälle" (Section Header) vor Folie 4
ist möglich, wird aber zugunsten eines knappen Decks weggelassen.

## Mockup-Skripte (Slack-Stil)

Jeder Mockup ist ein kurzer, realistischer Verlauf. „Du" ist die Vertriebsperson,
„Hermes" der Assistent.

### 1. Kundenrecherche vor dem Termin

> **Du:** Hermes, ich habe morgen um 10 Uhr einen Termin bei der Bauer GmbH.
> Fass mir kurz zusammen: Was macht die Firma, wer ist mein Ansprechpartner,
> gibt es Neuigkeiten?
>
> **Hermes:** Bauer GmbH, Maschinenbau aus Augsburg, rund 200 Mitarbeiter.
> Ansprechpartner laut CRM: Klaus Müller, Einkaufsleiter. Aktuell: neue
> Produktionshalle eröffnet (Pressemitteilung letzte Woche), Expansion in die
> Lebensmittelbranche. Tipp: stell den Bezug zur neuen Halle her.

### 2. E-Mails entwerfen

> **Du:** Hermes, entwirf eine Antwort an Herrn Müller von der Bauer GmbH. Er
> fragt nach einem Termin nächste Woche für die Angebotspräsentation.
>
> **Hermes:** Klar. Entwurf: „Sehr geehrter Herr Müller, vielen Dank für Ihre
> Nachricht. Für die Angebotspräsentation schlage ich Dienstag, den 30.06., um
> 14:00 Uhr vor. Passt Ihnen das? Mit freundlichen Grüßen ..."
>
> **Du:** Mach es etwas lockerer.
>
> **Hermes:** „Hallo Herr Müller, danke für Ihre Nachricht! Wie wäre es mit
> Dienstag, 30.06., um 14 Uhr für die Präsentation? Sagen Sie gern Bescheid.
> Beste Grüße ..."

### 3. Posteingang-Zusammenfassung

> **Du:** Was ist heute früh wichtig im Posteingang?
>
> **Hermes:** 3 von 14 Mails brauchen dich heute: 1) Bauer GmbH bestätigt Termin
> Di 14 Uhr. 2) Frau Schmidt (Meier KG) bittet um ein aktualisiertes Angebot bis
> Freitag. 3) Buchhaltung: Reisekostenabrechnung Mai fehlt noch. Der Rest sind
> Newsletter und CCs, das kann warten.

### 4. Schnelle Antworten unterwegs

> **Du:** *(vom Handy)* Kunde fragt gerade: Liefern wir Modell X auch in
> Edelstahl? Schnell bitte!
>
> **Hermes:** Ja. Modell X gibt es in Edelstahl (V2A), Aufpreis 12 %, Lieferzeit
> 3 Wochen. Soll ich dir das Datenblatt schicken?

## Asset-Pipeline

Erweiterung der bestehenden Pandoc-Pipeline um gerenderte Mockup-Bilder.

```
assets/mockups/<name>.html ──(build-mockups.sh)──▶ assets/mockups/<name>.png
                                                            │
presentations/hermes-vertrieb.md ──![](...)─────────────────┘
```

### Repository-Erweiterung

```
assets/mockups/*.html        committet (Mockup-Quelle, editierbar)
assets/mockups/*.png         committet (gerendert)
scripts/build-mockups.sh     committet
```

### Komponenten

1. `assets/mockups/*.html`
   - Vier Dateien, je ein Slack-ähnlicher Chat-Verlauf in HTML/CSS,
     selbst-enthalten (Inline-CSS), fester Viewport für ein vorhersagbares Bild.
2. `scripts/build-mockups.sh`
   - Rendert jede HTML-Datei per Headless-Chromium zu PNG
     (`--headless --screenshot --window-size=...`).
   - Idempotent; überschreibt die PNGs.
3. `Makefile` (neues Ziel)
   - `make mockups` - rendert alle Mockups neu.
   - Das Deck-Ziel hängt von den vorhandenen PNGs ab.

### Einbindung im Markdown

Zwei-Spalten-Folie nach Pipeline-Konvention:

```markdown
## Kundenrecherche vor dem Termin

::: columns
::: column
- Situation: gleich beim Kunden, keine Zeit
- Hermes liefert die Kurzfassung vorab
- Ergebnis: vorbereitet ins Gespräch
:::
::: column
![](../assets/mockups/recherche.png)
:::
:::
```

## Authoring-Konventionen

- `slide-level: 2` wie in der Pipeline-Spec.
- Zwei-Spalten-Folien über `::: columns` / `::: column` (Mapping auf Two
  Content / Zwei Inhalte).
- Titelblock über Pandoc-Metadaten (`% Titel`, `% Autor`, `% Datum`) oder
  YAML-Front-Matter.

## Testing / Verifikation

- `make mockups` erzeugt vier PNGs ohne Fehler; Bilder zeigen lesbaren Slack-Stil.
- `make output/hermes-vertrieb.pptx` rendert ohne `Couldn't find layout`-Warnung.
- Output-Deck entpacken: Use-Case-Folien nutzen das Zwei-Inhalte-Layout, Bilder
  sind eingebettet.
- Headless mit LibreOffice öffnen: Deck zeigt ORGATEX-Branding und Mockups.

## Offene Punkte / Risiken

- **Keine Mandantenfähigkeit.** Es gibt keinen gemeinsamen Hermes-Dienst; jede
  Person braucht eine eigene Instanz und installiert/betreibt sie selbst. Das
  Deck spricht das offen an (Folie 3 als „eigene Instanz pro Person", Folie 9 als
  Frage „wie organisieren wir die Einrichtung?"). Wo die Instanzen laufen
  (zentral auf dem Stack-Host vs. pro Person) und wieviel Hilfestellung
  nicht-technische Nutzer brauchen, ist vor einem Rollout zu klären.
- **Slack ist noch nicht im Einsatz.** Das Deck schlägt Slack als Kanal vor; die
  tatsächliche Einführung ist Teil der Diskussion (Folie 9) und vor einer Zusage
  zu klären.
- **Teams-Inbound** (falls später gewünscht) braucht einen öffentlichen
  HTTPS-Webhook, der lokale Stack ist aber tailnet-only. Für diesen Pitch nicht
  relevant, da Slack vorgeschlagen wird.
- **Chromium** wird als Build-Abhängigkeit fürs Mockup-Rendering benötigt.
- **Abhängigkeit:** Dieses Deck setzt die implementierte Pandoc-Pipeline voraus
  (`2026-06-24-orgatex-pandoc-presentations-design.md`). Reihenfolge in der
  Umsetzungsplanung beachten: Pipeline zuerst, dann Mockups, dann Deck.
