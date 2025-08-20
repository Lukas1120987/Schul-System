import json
import os

BASE_PATH = os.path.dirname(__file__)

class Translator:
    def __init__(self, lang="de"):
        filename = os.path.join(BASE_PATH, f"lang-{lang}.json")
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        else:
            self.translations = {}

    def t(self, key, **kwargs):
        text = self.translations.get(key, key)
        if kwargs:
            return text.format(**kwargs)
        return text
