import json
import sys
from pathlib import Path
from re import Pattern
from tkinter import filedialog

from src.models.json_structure import Config, FileList
from utils.typedDictDefault import create_default

# ===Folder navigation===
data_dir: Path = Path()  # LimbusCompany_Data path
source_dir: Path = Path()  # Path to original translation
target_dir: Path = Path()  # Path to resulting translation
file_list: FileList = create_default(
    FileList
)  # File with categorization of other files

# ===Reusable objects===
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
    global data_dir, config, source_dir, target_dir, file_list

    config = load_config()

    # Get base directory
    selected_dir = filedialog.askdirectory()
    if not selected_dir:
        sys.exit(0)
    data_dir = Path(selected_dir)

    # Build paths using pathlib
    source_dir = (
        data_dir
        / "Assets"
        / "Resources_moved"
        / "Localize"
        / config["moveFiles"]["sourceTranslation"]
    )
    target_dir = data_dir / "Lang" / config["moveFiles"]["translationName"]
    file_list_path = (
        data_dir
        / "Assets"
        / "Resources_moved"
        / "Localize"
        / "RemoteLocalizeFileList.json"
    )

    with open(file_list_path, "r", encoding="utf-8-sig") as f:
        file_list = json.load(f)


def load_config() -> Config:
    """Load config from config.json"""
    with open("config.json", "r", encoding="utf-8-sig") as f:
        return json.load(f)


init_globals()
