# Anki-Automation
Making the process of creating and maintaining Anki cards as frictionless and Ai oriented as possibel without relying on external tools

conda create --name anki_pipeline_env -c conda-forge python=3.10 pyyaml requests markdown2

Damit die nun korrekt generierten HTML-Tabellen auch ansprechend aussehen, müssen wir dem Anki-Notiztyp einmalig die nötigen CSS-Regeln hinzufügen.

**So geht's:**
1.  Öffnen Sie Anki auf Ihrem Desktop.
2.  Gehen Sie im Menü auf **Werkzeuge** -> **Notiztypen verwalten**.
3.  Wählen Sie den Notiztyp aus, den Sie für die Karten verwenden (z.B. "Basic" oder den Namen, den Sie in Ihrer YAML-Datei angeben).
4.  Klicken Sie auf der rechten Seite auf den Button **Karten...**.
5.  Es öffnet sich ein Fenster mit drei Hauptbereichen: "Vorderseite-Vorlage", "Rückseite-Vorlage" und auf der linken Seite ein Feld namens **Styling**. Das Styling-Feld ist das, was wir brauchen. Es wird von allen Karten dieses Typs geteilt.
6.  Scrollen Sie im Styling-Feld ganz nach unten und **fügen Sie den folgenden CSS-Code am Ende hinzu**:

```css

/* --- STYLING FÜR TABELLEN --- */
table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
  font-size: 0.9em;
  /* Stellt sicher, dass die Tabelle nicht die Textfarbe der Karte erbt */
  color: #000000; 
}

/* 
  GRUNDREGEL FÜR ALLE ZELLEN (th & td):
  Dies ist der wichtigste Teil. Wir definieren einen hellen Standard-Look
  für JEDE Zelle, unabhängig vom Anki-Theme.
*/
th, td {
  border: 1px solid #cccccc;
  padding: 8px;
  text-align: left;
  background-color: #ffffff; /* Standardhintergrund IMMER weiß */
}

/* 
  SPEZIALREGEL FÜR KOPFZELLEN (th):
  Diese Regel überschreibt nur den Hintergrund der Kopfzellen.
  Die schwarze Textfarbe wird von der Regel oben geerbt.
*/
th {
  background-color: #f2f2f2; /* Leichter grauer Hintergrund für Header */
  font-weight: bold;
}

/* 
  SPEZIALREGEL FÜR GERADE ZEILEN (tr:nth-child(even)):
  Diese Regel überschreibt den Hintergrund der Datenzellen (td)
  in jeder zweiten Zeile für bessere Lesbarkeit (Zebra-Look).
*/
tr:nth-child(even) td {
  background-color: #f9f9f9; /* Ganz leicht grauer Hintergrund für gerade Zeilen */
}

```

Klicken Sie auf **Speichern** und schließen Sie die Fenster. Alle bestehenden und zukünftigen Karten dieses Typs, die eine Tabelle enthalten, werden nun automatisch mit diesen schönen Linien und Formatierungen angezeigt.

---

### Anki-Notiztyp für LaTeX vorbereiten

Anki kann LaTeX-Code mit Hilfe der MathJax-Bibliothek direkt auf der Karte in schön formatierte Formeln umwandeln. Dazu müssen wir dem Karten-Template sagen, dass es diese Bibliothek laden soll.

**So geht's:**
1.  Öffnen Sie Anki auf Ihrem Desktop.
2.  Gehen Sie zu **Werkzeuge** -> **Notiztypen verwalten**.
3.  Wählen Sie Ihren Notiztyp (z.B. "Basic") und klicken Sie auf **Karten...**.
4.  Es öffnet sich das Fenster mit "Vorderseite-Vorlage", "Rückseite-Vorlage" und "Styling".
5.  Fügen Sie den folgenden Code-Block **ganz am Ende** der **Vorderseite-Vorlage** ein.
6.  Fügen Sie denselben Code-Block auch **ganz am Ende** der **Rückseite-Vorlage** ein. (Es muss in beiden sein, falls Formeln auf der Vorder- oder Rückseite erscheinen).

```html
<!-- LÄDT MATHJAX FÜR DIE DARSTELLUNG VON LATEX-FORMELN -->
<script>
  if (typeof MathJax === "undefined") {
    var script = document.createElement("script");
    script.type = "text/javascript";
    script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js";
    document.head.appendChild(script);
  }
</script>
```

Klicken Sie auf **Speichern**. Ihr Anki ist nun bereit, LaTeX zu rendern.