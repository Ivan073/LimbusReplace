import json
import os
import re
from line_profiler import profile

name_id_map = {}


@profile
def process_statuses(directory, config):
    """Find files that supposed to contain statuses according to config"""
    global name_id_map
    name_id_map = {}
    ignored_files = config['statuses']['ignoredFiles']
    processed_files = []
    required_fields = config['statuses']['fields']['required']
    optional_fields = config['statuses']['fields']['optional']

    for filename in os.listdir(directory):
        if filename.endswith('.json') and filename not in ignored_files:
            path = os.path.join(directory, filename)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                skip_preprocessing = False
                if "dataList" in data and len(data["dataList"]) > 0:
                    for item in data["dataList"]:
                        # TODO: Right now keyword files should have only string fields (this may change in future)
                        for field in required_fields:
                            if not isinstance(item.get(field), str):
                                skip_preprocessing = True
                        for field in optional_fields:
                            if item.get(field) is not None and not isinstance(item.get(field), str):
                                skip_preprocessing = True
                        if not set(required_fields).intersection(set(item.keys())) or not set(item.keys()).issubset(
                                set(required_fields + optional_fields)):
                            skip_preprocessing = True
                else:
                    skip_preprocessing = True

                if not skip_preprocessing:
                    preprocess_statuses(data, config)
                    processed_files.append(filename)

                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

            except Exception as e:
                print(f"File error in {filename}: {str(e)}")

    return processed_files


@profile
def preprocess_statuses(data, config):
    """Recording of statuses, chnage names and descriptions"""
    global name_id_map
    required_fields = config['statuses']['fields']['required']
    optional_fields = config['statuses']['fields']['optional']
    replace_icon = config['statuses']['replaceIcon']

    if "dataList" in data and isinstance(data["dataList"], list):
        for item in data["dataList"]:
            if isinstance(item, dict):
                name = item.get("name")
                desc = item.get("desc")
                id = item.get("id")

                if isinstance(name, str) and isinstance(desc, str) and desc.strip() != "" and name != replace_icon:
                    item["desc"] = f"{name}\n{desc}"

                if isinstance(name, str):
                    item["name"] = replace_icon

                if id and name:
                    name_id_map[name] = f"[{id}]"
    return data
