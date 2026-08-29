from typing import Literal

from models.json_structure import FileList

FileListKey = Literal[
    "skill", "passive", "buf", "buffAbilities", "keyword", "skillTag", "egoGifts"
]


def collect_files(file_list: FileList, *keys: FileListKey) -> list[str]:
    """Collect and append .json extension to files from specified FileList fields."""
    return [f"{item}.json" for key in keys for item in file_list[key]]
