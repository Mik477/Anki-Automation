import yaml
import requests
from pathlib import Path
from datetime import datetime
import json
import markdown2
import re # Importiert die Bibliothek für reguläre Ausdrücke

# --- KONFIGURATION ---
ANKI_CONNECT_URL = "http://localhost:8765"
WORKING_FILE = Path("work_in_progress.yaml")
ARCHIVE_DIR = Path("archive")

# --- HELPER-FUNKTION ---
def anki_request(action, **params):
    """Ein robuster Wrapper für Anfragen an AnkiConnect."""
    payload = {'action': action, 'version': 6, 'params': params}
    try:
        response = requests.post(ANKI_CONNECT_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        if result.get('error'): return None, result['error']
        return result.get('result'), None
    except requests.exceptions.RequestException as e:
        return None, f"Verbindung zu AnkiConnect fehlgeschlagen: {e}"

# --- HAUPTLOGIK DES SKRIPTS ---
def process_batch():
    print("[INFO] Starte sichere Stapelverarbeitung...")
    if not WORKING_FILE.exists() or WORKING_FILE.stat().st_size < 5:
        print("[INFO] Arbeitsdatei ist leer. Vorgang wird beendet.")
        return

    # 1. YAML parsen
    try:
        with open(WORKING_FILE, 'r', encoding='utf-8') as f:
            batch = yaml.safe_load(f)
            if not batch or 'cards' not in batch:
                print("[FEHLER] YAML ist ungültig, 'cards' fehlt oder die Datei ist leer."); return
    except yaml.YAMLError as e:
        print(f"[FEHLER] Konnte {WORKING_FILE} nicht parsen. Grund: {e}"); return

    # 2. Metadaten extrahieren & Konverter initialisieren
    deck_name = batch.get('deck', 'Default')
    default_model = batch.get('model', 'Basic')
    global_tags = batch.get('tags', [])
    # WICHTIG: Der Konverter hat jetzt die 'tables'-Erweiterung aktiviert
    html_converter = markdown2.Markdown(extras=["fenced-code-blocks", "tables"])

    # 3. Vorab-Prüfungen (Pre-flight Checks)
    try:
        model_name = batch.get('model', default_model)
        available_models, error = anki_request('modelNames')
        if error: print(f"[FEHLER] Konnte Modellnamen nicht abrufen: {error}"); return
        if model_name not in available_models:
            print(f"\n[FATALER FEHLER] Der Notiztyp (Modell) '{model_name}' wurde nicht gefunden."); return
        
        existing_decks, error = anki_request('deckNames')
        if error: print(f"[FEHLER] Konnte Decknamen nicht abrufen: {error}"); return
        if deck_name not in existing_decks:
            print(f"[INFO] Deck '{deck_name}' existiert nicht. Es wird erstellt...")
            _, error = anki_request('createDeck', deck=deck_name)
            if error: print(f"[FEHLER] Deck '{deck_name}' konnte nicht erstellt werden: {error}"); return
    except Exception as e:
        print(f"[FEHLER] Unerwarteter Fehler bei den Vorab-Prüfungen: {e}"); return
    
    notes_to_add, notes_to_update, skipped_count, collision_count = [], [], 0, 0

    # 4. Karten verarbeiten
    for card_data in batch.get('cards', []):
        if not all(k in card_data for k in ['uid', 'fields']):
            print(f"[WARNUNG] Überspringe Karte wegen fehlender 'uid' oder 'fields'. Daten: {card_data}"); continue

        # --- START: Robuste Umwandlung von Feldern (mit korrigiertem Platzhalter) ---
        processed_fields = {}
        for key, value in card_data['fields'].items():
            formulas = []
            
            # Diese Hilfsfunktion findet eine Formel, speichert sie und gibt einen sicheren Platzhalter zurück
            def store_formula_and_get_placeholder(match):
                formulas.append(match.group(0))
                # KORRIGIERTER PLATZHALTER: Enthält keine Markdown-Sonderzeichen
                return f"FORMELPLATZHALTERNUMMER{len(formulas)-1}"

            # Konvertiere Wert zu String, um Fehler bei leeren Feldern zu vermeiden
            text_with_placeholders = str(value or "")
            
            # Finde und ersetze zuerst Block-Formeln (\[...\]), dann Inline-Formeln (\(...\))
            # re.DOTALL sorgt dafür, dass auch mehrzeilige Formeln korrekt gefunden werden
            text_with_placeholders = re.sub(r'\\\[.*?\\\]', store_formula_and_get_placeholder, text_with_placeholders, flags=re.DOTALL)
            text_with_placeholders = re.sub(r'\\\(.*?\\\)', store_formula_and_get_placeholder, text_with_placeholders, flags=re.DOTALL)

            # Konvertiere den "sicheren" Markdown-Text (ohne Formeln) zu HTML
            html_content = html_converter.convert(text_with_placeholders)

            # Ersetze die Platzhalter im finalen HTML wieder durch die originalen, unversehrten Formeln
            for i, formula in enumerate(formulas):
                # KORRIGIERT: Ersetze den neuen, sicheren Platzhalter
                placeholder = f"FORMELPLATZHALTERNUMMER{i}"
                html_content = html_content.replace(placeholder, formula)
            
            processed_fields[key] = html_content
        
        card_data['fields'] = processed_fields
        # --- ENDE: Robuste Umwandlung ---

        uid_tag = f"uid:{card_data['uid']}"
        query = f'tag:"{uid_tag}"'
        existing_note_ids, error = anki_request('findNotes', query=query)
        if error: print(f"[FEHLER] AnkiConnect-Abfrage für UID {card_data['uid']} fehlgeschlagen: {error}"); continue

        if not existing_note_ids:
            # Fall 1: Keine Notiz mit dieser UID vorhanden. Es ist eine neue Karte.
            card_data['tags'] = sorted(list(set(global_tags + card_data.get('tags', [])) | {uid_tag}))
            notes_to_add.append(card_data)
        
        elif len(existing_note_ids) == 1:
            # Fall 2: Genau eine Notiz gefunden. Prüfe, ob ein Update erlaubt und nötig ist.
            note_id = existing_note_ids[0]
            
            if card_data.get('overwrite') is True:
                info_list, error = anki_request('notesInfo', notes=[note_id])
                if error or not info_list:
                    print(f"[FEHLER] Konnte Info für Notiz-ID {note_id} nicht abrufen. Überspringe."); continue
                
                note_info = info_list[0]
                if note_info['fields'] != card_data['fields']:
                    update_payload = {
                        'id': note_id, 
                        'fields': card_data['fields'],
                        'tags': sorted(list(set(global_tags + card_data.get('tags', [])) | {uid_tag}))
                    }
                    notes_to_update.append(update_payload)
                else:
                    skipped_count += 1
            else:
                print(f"[WARNUNG] Karte mit UID '{card_data['uid']}' existiert bereits, aber 'overwrite: true' ist nicht gesetzt. Update wird übersprungen.")
                collision_count += 1
        else:
            # Fall 3: Mehrere Notizen mit derselben UID gefunden.
            print(f"[WARNUNG] {len(existing_note_ids)} Notizen mit derselben UID '{card_data['uid']}' gefunden. Überspringe zur Sicherheit.")
            collision_count += 1

    # 5. Stapelaktionen durchführen
    if skipped_count > 0: print(f"[INFO] {skipped_count} Karten sind bereits aktuell.")
    if collision_count > 0: print(f"[WARNUNG] {collision_count} Karten wurden wegen existierender UID ohne 'overwrite'-Flag oder anderer Anomalien übersprungen.")
    
    if notes_to_add:
        print(f"\n[INFO] Versuche, {len(notes_to_add)} neue Notizen hinzuzufügen...")
        anki_notes_payload = [{'deckName': deck_name, 'modelName': n.get('model', default_model), 'fields': n['fields'], 'tags': n['tags']} for n in notes_to_add]
        results, error = anki_request('addNotes', notes=anki_notes_payload)
        if error: print(f"[FEHLER] Die 'addNotes'-Aktion ist fehlgeschlagen: {error}")
        else:
            success_count = len(list(filter(None, results)))
            if success_count > 0: print(f"[INFO] {success_count} / {len(notes_to_add)} Notizen erfolgreich hinzugefügt.")

    if notes_to_update:
        print(f"[INFO] Aktualisiere {len(notes_to_update)} existierende Notizen...")
        for note in notes_to_update:
            anki_request('updateNoteFields', note={'id': note['id'], 'fields': note['fields']})
            anki_request('setTags', notes=[note['id']], tags=" ".join(note['tags']))

    # 6. Zusammenfassung und Archivierung
    print("\n--- Zusammenfassung des Stapels ---")
    added_count = len(list(filter(None, locals().get('results', [])))) if 'results' in locals() else 0
    print(f"Hinzugefügt: {added_count} | Aktualisiert: {len(notes_to_update)} | Bereits aktuell: {skipped_count} | Übersprungen/Kollisionen: {collision_count}")
    print("-----------------------------------")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_filename = f"{timestamp}_{deck_name.replace('::', '-')}.yaml"
    archive_path = ARCHIVE_DIR / archive_filename
    ARCHIVE_DIR.mkdir(exist_ok=True)
    WORKING_FILE.rename(archive_path)
    print(f"[INFO] Arbeitsdatei archiviert nach: {archive_path}")
    WORKING_FILE.touch()
    print("[ERFOLG] Workflow abgeschlossen.")


if __name__ == "__main__":
    _, err = anki_request('deckNames')
    if err: print(f"[FEHLER] AnkiConnect nicht erreichbar. Bitte stellen Sie sicher, dass Anki läuft und das Add-on installiert ist.")
    else: process_batch()