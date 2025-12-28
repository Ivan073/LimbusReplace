import json
import os
from globals import file_list_path, target_dir, skill_tag_ids
from json_structure import SkillTag


def process_file_list():
    """Use RemoteLocalizeFileList.json to get useful data lists"""
    with open(file_list_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    skillTag_list: list[str] = data["skillTag"]

    for filename in skillTag_list:
        path = os.path.join(target_dir, filename + ".json")

        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        data_list: list[SkillTag] = data["dataList"]
        for item in data_list:
            skill_tag_ids.append(item["id"])
