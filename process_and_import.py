import yaml
import requests
from pathlib import Path
from datetime import datetime
import json
import markdown2 # *** NEW: Import the markdown converter library ***

# --- CONFIGURATION ---
ANKI_CONNECT_URL = "http://localhost:8765"
WORKING_FILE = Path("work_in_progress.yaml")
ARCHIVE_DIR = Path("archive")

# --- HELPER FUNCTION ---
def anki_request(action, **params):
    """A robust wrapper for making requests to AnkiConnect."""
    payload = {'action': action, 'version': 6, 'params': params}
    try:
        response = requests.post(ANKI_CONNECT_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        if result.get('error'): return None, result['error']
        return result.get('result'), None
    except requests.exceptions.RequestException as e:
        return None, f"Connection to AnkiConnect failed: {e}"

# --- MAIN SCRIPT LOGIC ---
def process_batch():
    print("[INFO] Starting secure batch processing...")
    if not WORKING_FILE.exists() or WORKING_FILE.stat().st_size < 5:
        print("[INFO] Working file is empty. Exiting.")
        return

    # 1. Parse YAML
    try:
        with open(WORKING_FILE, 'r', encoding='utf-8') as f:
            batch = yaml.safe_load(f)
            if not batch or 'cards' not in batch:
                print("[ERROR] YAML is invalid, missing 'cards' or empty."); return
    except yaml.YAMLError as e:
        print(f"[ERROR] Could not parse {WORKING_FILE}. Reason: {e}"); return

    # 2. Extract Metadata & Initialize Converter
    deck_name = batch.get('deck', 'Default')
    default_model = batch.get('model', 'Basic')
    global_tags = batch.get('tags', [])
    # *** NEW: Create a converter instance. We enable fenced-code-blocks for our code examples. ***
    html_converter = markdown2.Markdown(extras=["fenced-code-blocks"])

    # 3. Pre-flight Checks
    try:
        model_name = batch.get('model', default_model)
        available_models, error = anki_request('modelNames')
        if error: print(f"[ERROR] Could not fetch model names: {error}"); return
        if model_name not in available_models:
            print(f"\n[FATAL ERROR] The Note Type (model) '{model_name}' was not found."); return
        
        existing_decks, error = anki_request('deckNames')
        if error: print(f"[ERROR] Could not fetch deck names: {error}"); return
        if deck_name not in existing_decks:
            print(f"[INFO] Deck '{deck_name}' does not exist. Creating it...")
            _, error = anki_request('createDeck', deck=deck_name)
            if error: print(f"[ERROR] Failed to create deck '{deck_name}': {error}"); return
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred during pre-flight checks: {e}"); return
    
    notes_to_add, notes_to_update, skipped_count, collision_count = [], [], 0, 0

    # 4. Process Cards
    for card_data in batch.get('cards', []):
        if not all(k in card_data for k in ['uid', 'fields']):
            print(f"[WARN] Skipping card due to missing 'uid' or 'fields'."); continue

        # *** NEW: Convert all field content from Markdown to HTML ***
        processed_fields = {}
        for key, value in card_data['fields'].items():
            processed_fields[key] = html_converter.convert(value)
        card_data['fields'] = processed_fields
        # *** END NEW LOGIC ***

        uid_tag = f"uid:{card_data['uid']}"
        query = f'tag:"{uid_tag}"'
        existing_note_ids, error = anki_request('findNotes', query=query)
        if error: print(f"[ERROR] AnkiConnect query failed for UID {card_data['uid']}: {error}"); continue
        if not existing_note_ids:
            card_data['tags'] = sorted(list(set(global_tags + card_data.get('tags', [])) | {uid_tag}))
            notes_to_add.append(card_data)
        else:
            note_id = existing_note_ids
            info, _ = anki_request('notesInfo', notes=[note_id])
            is_content_different = info['fields'] != card_data['fields']
            if not is_content_different: skipped_count += 1
            elif not card_data.get('overwrite', False): collision_count += 1
            else:
                update_payload = {'id': note_id, 'fields': card_data['fields'], 'tags': sorted(list(set(global_tags + card_data.get('tags', [])) | {uid_tag}))}
                notes_to_update.append(update_payload)

    # ... (The rest of the script remains largely the same, but uses the processed data) ...
    if skipped_count > 0: print(f"[INFO] {skipped_count} cards are already up-to-date.")
    if collision_count > 0: print(f"[WARN] {collision_count} cards with UID collisions were skipped.")
    
    # 5. Perform Batch Actions
    if notes_to_add:
        print(f"\n[INFO] Attempting to add {len(notes_to_add)} new notes...")
        anki_notes_payload = [{'deckName': deck_name, 'modelName': n.get('model', default_model), 'fields': n['fields'], 'tags': n['tags']} for n in notes_to_add]
        results, error = anki_request('addNotes', notes=anki_notes_payload)
        if error: print(f"[ERROR] The 'addNotes' action failed: {error}")
        else:
            success_count = len(list(filter(None, results)))
            if success_count > 0: print(f"[INFO] Successfully added {success_count} / {len(notes_to_add)} notes.")

    if notes_to_update:
        print(f"[INFO] Updating {len(notes_to_update)} existing notes...")
        for note in notes_to_update: anki_request('updateNoteFields', note={'id': note['id'], 'fields': note['fields']}); anki_request('setTags', notes=[note['id']], tags=" ".join(note['tags']))

    # 6. Final Summary and Archiving
    print("\n--- Batch Summary ---")
    print(f"Added: {len(list(filter(None, locals().get('results', []))))} | Updated: {len(notes_to_update)} | Skipped: {skipped_count} | Collisions: {collision_count}")
    print("---------------------")

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_filename = f"{timestamp}_{deck_name.replace('::', '-')}.yaml"
    archive_path = ARCHIVE_DIR / archive_filename
    ARCHIVE_DIR.mkdir(exist_ok=True)
    WORKING_FILE.rename(archive_path)
    print(f"[INFO] Archived working file to: {archive_path}")
    WORKING_FILE.touch()
    print("[SUCCESS] Workflow complete.")

if __name__ == "__main__":
    _, err = anki_request('deckNames')
    if err: print(f"[ERROR] AnkiConnect not available. Please ensure Anki is running and the add-on is installed.")
    else: process_batch()