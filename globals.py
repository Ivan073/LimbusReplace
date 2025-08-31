import json

data_dir = None  # LimbusCompany_Data path
source_dir = None  # Path to original translation
target_dir = None  # Path to resulting translation
file_list_path = None  # Path to RemoteLocalizeFileList.json

config = None  # Config file json

compiled_patterns = {}  # Dictionary of compiled regex patterns to boost performance

status_id_name_map = {}  # Dictionary of status names to unify status ids and names

skill_tag_ids = []      # List of skill tag ids (to be ignored in replaces if enabled)


def init_globals():
    global data_dir, config, source_dir, target_dir, file_list_path
    from tkinter import filedialog
    config = load_config()
    data_dir = filedialog.askdirectory()
    source_dir = data_dir + "/Assets/Resources_moved/Localize/" + config["moveFiles"]["sourceTranslation"]
    target_dir = data_dir + "/Lang/" + config["moveFiles"]["translationName"]
    file_list_path = data_dir + "/Assets/Resources_moved/Localize/RemoteLocalizeFileList.json"


def load_config():
    """Load config from config.json"""
    with open('config.json', 'r', encoding='utf-8-sig') as f:
        return json.load(f)


init_globals()
