import json
from typing import Any, cast

from file_list import file_list
from src.globals import config, status_id_name_map, target_dir
from src.models.json_structure import StatusItem
from utils.helpers import collect_files


def find_statuses():
    """Find files that supposed to contain statuses according to config"""
    ignored_files = config["statuses"]["ignoredFiles"]
    processed_files: list[str] = []

    status_files = collect_files(file_list, "keyword", "buf")

    for filename in status_files:
        if filename in ignored_files:
            continue

        path = target_dir / filename
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)

            add_statuses(data)
            processed_files.append(filename)

            with open(path, "w", encoding="utf-8-sig") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"Status file error in {filename}: {e!s}")

    return processed_files


def add_statuses(data: Any):
    """Add statuses to dictionary from json"""
    data_list = data.get("dataList")
    if not isinstance(data_list, list):
        return data

    data_list = cast(list[Any], data_list)
    status_item_list = [
        cast(StatusItem, item) for item in data_list if isinstance(item, dict)
    ]
    for item in status_item_list:
        name = item.get("name")
        id_ = item.get("id")
        if id_ and name:
            status_id_name_map[id_] = name
    return data
