import json

from src.globals import file_list_path, skill_tag_ids, target_dir
from src.models.json_structure import SkillTag


def process_file_list():
    """
    Use RemoteLocalizeFileList.json to get useful data lists.

    Gets skillTag files to use for skillTagPersistence later
    """
    with open(file_list_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    skill_tag_list: list[str] = data["skillTag"]

    for filename in skill_tag_list:
        path = target_dir / filename / ".json"

        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        data_list: list[SkillTag] = data["dataList"]
        for item in data_list:
            skill_tag_ids.append(item["id"])
