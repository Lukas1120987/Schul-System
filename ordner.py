import json
import os

DEFAULT_PATH = "data"

def get_data_path():
    """Liest den Speicherpfad aus setup.json oder gibt Default zurück."""
    if os.path.exists("setup.json"):
        try:
            with open("setup.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("data_path", DEFAULT_PATH)
        except Exception as e:
            print(f"[Fehler beim Laden von setup.json]: {e}")
            return DEFAULT_PATH
    else:
        return DEFAULT_PATH


# BEISPIEL --------------------------------------
# import os
#from ordner import get_data_path
#
#USER_JSON_PATH = os.path.join(get_data_path(), "users.json")

