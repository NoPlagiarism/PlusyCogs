import os

class Settings:
    VALIDATE_DOWNLOAD = True
    SUBFOLDER_WITH_DATA = "data"

    COG_FOLDER = os.path.dirname(__file__)
    LANGS_PATH = os.path.join(COG_FOLDER, "langs.json")
    ICONS_PATH = os.path.join(COG_FOLDER, "icons.json")

    DEF_LANG = "en"
    EMBED_COLOR = 0xfd1a63
    CHARACTERS_PER_PAGE = 10
    SCRIPTS_PER_PAGE = 15

    USE_VIEW = True
    VIEW_TIMEOUT = 60

    DISABLE_DOGS_LIST = False
    CHARACTERS_PER_PAGE_FILTERED = 9
    CAMEO_DOGS = ["Lord Pumplerump", "Arial Wienerton", "Lady Banner", "Dragon Fucker", "Satan's Hellper",
                  "Pesky Furball", "Wyrm Frigger", "Bangkok Bastard", "Tortilla Pope", "Cou Rage", "Dog 5",
                  "Mister Puff", "Third Barkday", "Poop-eater", "Money Shredder", "Gruff Bucket", "Wyvern Lover"]
