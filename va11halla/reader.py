import os.path
import random
import json
from time import time
from .config import Settings

import urllib.request
import aiohttp

random.seed(int(time()))


class Script:
    """Класс, описывающий скрипт
    lines - кол-во линий в дне
    name - название"""
    dict: dict

    def __init__(self, raw_dict):
        self.dict = raw_dict

    def __repr__(self):
        return "Script " + self.dict['filename']

    @property
    def lines(self) -> int:
        return self.dict['lines']

    @property
    def name(self) -> str:
        return self.dict["filename"]


class Dialogue:
    """Диалог.
    script - Script
    character - имя персонажа
    text - содержимое диалога
    line - линия в скрипте"""
    script: Script
    character: str
    text: str
    line: int

    lang: str = None

    def __init__(self, script, character, line, text, lang=None):
        if type(script) is not Script:
            self.script = Script(script)
        else:
            self.script = script
        self.character, self.line, self.text = character, line, text
        self.lang = lang

    def __repr__(self):
        return f'"{self.character}: {self.text}" on line: {self.line}'

    def __str__(self):
        return self.text

    @staticmethod
    def from_grouped_dial(raw_dict, character, lang=None):
        return Dialogue(raw_dict['script'], character, raw_dict['line'], raw_dict['text'], lang=lang)

    @staticmethod
    def from_scripts_dial(raw_dict, script, lang=None):
        return Dialogue(script, raw_dict['character'], raw_dict['line'], raw_dict['text'], lang=lang)


class Va11ReaderException(Exception):
    pass


class CharacterNotFound(Va11ReaderException):
    def __init__(self, name, script=None):
        self.name = name
        self.script = None if script is None else script

    def __str__(self):
        if self.script:
            return f"Character {self.name} in script {self.script} not found"
        return f"Character {self.name} not found"


class ScriptNotFound(Va11ReaderException):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return f"Script {self.filename} not found"


class ScriptLineDoesNotExists(Va11ReaderException):
    def __init__(self, script_info=None, error_line=None):
        self.script = script_info
        self.error_line = error_line

    def __str__(self):
        return f"{self.script['filename']} has {self.script['lines']} lines"


class Va11HallaJSON:
    def __init__(self, paths, lang=None):
        """paths = (dialogue_scripts.json, dialogue_grouped.json, names.json)"""
        self.paths = paths
        self.lang = lang
        # dialogue_scripts.json
        self._dialogue_scripts = None
        self._scripts = None
        # dialogue_grouped.json
        self._dialogue_grouped = None
        # names.json
        self.names = None
        self.init_names()
        self._names_filtered = None
        self.init_names_filtered()
        self.characters = tuple(self.names.keys())
        self.characters_filtered = tuple(self.names_filtered.keys())

    def init_names(self, path=None):
        if self.names is not None:
            return
        if path is None:
            path = self.paths[2]
        with open(path, mode="r", encoding="utf-8") as f:
            self.names = json.load(f)

    def init_names_filtered(self, exclude=None):
        if exclude is None:
            exclude = Settings.CAMEO_DOGS
            if self.lang != "en":
                exclude = [self.names_reversed[char] for char in exclude]
        self._names_filtered = dict(tuple(filter(lambda x: x[0] not in exclude, self.names.items())))

    def init_scripts(self, path=None):
        if self._dialogue_scripts is not None:
            return
        if path is None:
            path = self.paths[0]
        with open(path, mode="r", encoding="utf-8") as f:
            self._dialogue_scripts = json.load(f)

    def init_grouped(self, path=None):
        if self._dialogue_grouped is not None:
            return
        if path is None:
            path = self.paths[1]
        with open(path, mode="r", encoding="utf-8") as f:
            self._dialogue_grouped = json.load(f)

    def init_scripts_list(self, dialogue_scripts=None):
        if dialogue_scripts is None:
            dialogue_scripts = self.dialogue_scripts
        self._scripts = tuple(map(lambda script: script[0]["filename"], dialogue_scripts))

    def init_all(self):
        self.init_grouped()
        self.init_scripts()
        self.init_scripts_list()

    @property
    def dialogue_scripts(self) -> list:
        if self._dialogue_scripts is None:
            self.init_scripts()
        return self._dialogue_scripts

    @property
    def dialogue_grouped(self) -> dict:
        if self._dialogue_grouped is None:
            self.init_grouped()
        return self._dialogue_grouped

    @property
    def scripts(self):
        if self._scripts is None:
            self.init_scripts_list()
        return self._scripts

    @property
    def names_reversed(self):
        return {v: k for k, v in self.names.items()}

    @property
    def names_filtered(self):
        if self._names_filtered is None:
            self.init_names_filtered()
        return self._names_filtered

    def clear_all(self):
        self._dialogue_scripts = None
        self._dialogue_grouped = None

    def get_script(self, script_name=None):
        try:
            return self.dialogue_scripts[self.scripts.index(script_name)]
        except ValueError:
            raise ScriptNotFound(script_name)

    def get_script_line(self, line_num: int, script=None, script_name: str = None, meta: Script = None):
        if script is script_name is None:
            script_name = meta.name
        if script is None:
            script = self.get_script(script_name)
        try:
            line = script[line_num-1]
            if line['type'] == 'META':
                raise ScriptLineDoesNotExists(Script(line), line_num)
            return Dialogue.from_scripts_dial(line, script[0], lang=self.lang)
        except IndexError:
            raise ScriptLineDoesNotExists(Script(script[0]), line_num)

    def random_from_scripts(self, script_name=None, character=None) -> Dialogue:
        if script_name is not None:
            script = self.get_script(script_name)
        else:
            script = random.choice(self.dialogue_scripts)
        script_info = script[0]
        if character is not None:
            character_lines = tuple(filter(lambda line: line["character"] == character, script[1:]))
            if not character_lines:
                raise CharacterNotFound(character, script_name)
            dialogue = random.choice(character_lines)
        else:
            dialogue = random.choice(script[1:])
        return Dialogue.from_scripts_dial(dialogue, script_info, lang=self.lang)

    def random_from_characters(self, character=None) -> Dialogue:
        if character is None:
            character = random.choice(tuple(self.dialogue_grouped.keys()))
        try:
            dialogues = self.dialogue_grouped[character]
        except KeyError:
            raise CharacterNotFound(character)
        dialogue = random.choice(dialogues)
        return Dialogue.from_grouped_dial(dialogue, character, lang=self.lang)


class Va11DataManager:
    def __init__(self, path):
        self.path = path
        if Settings.SUBFOLDER_WITH_DATA:
            self.path = os.path.join(self.path, Settings.SUBFOLDER_WITH_DATA)
        with open(Settings.LANGS_PATH) as f:
            self.langs = json.load(f)

    def validate(self):
        result = True
        for lang, files in self.langs.items():
            for file in files.keys():
                if not os.path.exists(os.path.join(self.path, lang, file)):
                    result = False
                    break
        return result

    @staticmethod
    def _get_json_from_url(url):
        with urllib.request.urlopen(url) as res:
            return json.loads(res.read().decode(res.headers.get_content_charset("utf-8")))

    async def async_download(self):
        self.makedirs()
        async with aiohttp.ClientSession() as session:
            for lang, name_urls in self.langs.items():
                for name, url in name_urls.items():
                    async with session.get(url) as resp:
                        json_ = await resp.json(encoding="utf-8", content_type='text/plain')
                    with open(os.path.join(self.path, lang, name), mode='w+', encoding="utf-8") as f:
                        json.dump(json_, f)

    def makedirs(self):
        for lang in self.langs.keys():
            if not os.path.exists(os.path.join(self.path, lang)):
                os.makedirs(os.path.join(self.path, lang))

    def download(self):
        self.makedirs()
        for lang, name_urls in self.langs.items():
            for name, url in name_urls.items():
                json_ = self._get_json_from_url(url)
                with open(os.path.join(self.path, lang, name), mode='w+', encoding="utf-8") as f:
                    json.dump(json_, f)

    def validate_and_download(self):
        if not self.validate():
            self.download()

    async def async_validate_and_download(self):
        if not self.validate():
            await self.async_download()

    def get_all_readers(self):
        readers = dict()
        for lang in self.langs.keys():
            readers[lang] = Va11HallaJSON((os.path.join(self.path, lang, "dialogue_scripts.json"),
                                           os.path.join(self.path, lang, "dialogue_grouped.json"),
                                           os.path.join(self.path, lang, "names.json")), lang)
        return readers
