import json
from re import Pattern
from json_structure import Config

data_dir: str = ""  # LimbusCompany_Data path
source_dir: str = ""  # Path to original translation
target_dir: str = ""  # Path to resulting translation
file_list_path: str = ""  # Path to RemoteLocalizeFileList.json

config = None  # Config file json

compiled_patterns: dict[
    str, Pattern[str]
] = {}  # Dictionary of compiled regex patterns to boost performance

status_id_name_map: dict[
    str, str
] = {}  # Dictionary of status names to unify status ids and names

skill_tag_ids: list[
    str
] = []  # List of skill tag ids (to be ignored in replaces if enabled)


def init_globals():
    global data_dir, config, source_dir, target_dir, file_list_path
    from tkinter import filedialog

    config = load_config()
    data_dir = filedialog.askdirectory()
    source_dir = (
        data_dir
        + "/Assets/Resources_moved/Localize/"
        + config["moveFiles"]["sourceTranslation"]
    )
    target_dir = data_dir + "/Lang/" + config["moveFiles"]["translationName"]
    file_list_path = (
        data_dir + "/Assets/Resources_moved/Localize/RemoteLocalizeFileList.json"
    )


def load_config() -> Config:
    """Load config from config.json"""
    with open("config.json", "r", encoding="utf-8-sig") as f:
        return json.load(f)


init_globals()
