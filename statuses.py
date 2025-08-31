import json
import os

from line_profiler import profile

from globals import config, target_dir, status_id_name_map


@profile
def find_statuses():
    """Find files that supposed to contain statuses according to config"""
    ignored_files = config['statuses']['ignoredFiles']
    processed_files = []
    required_fields = config['statuses']['fields']['required']
    optional_fields = config['statuses']['fields']['optional']

    for filename in os.listdir(target_dir):
        if not filename.endswith('.json') or filename in ignored_files:
            continue

        path = os.path.join(target_dir, filename)
        try:
            with open(path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)

            data_list = data.get("dataList")
            skip_preprocessing = False
            if isinstance(data_list, list) and data_list:
                for item in data_list:
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
                add_statuses(data)
                processed_files.append(filename)

            with open(path, 'w', encoding='utf-8-sig') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"File error in {filename}: {str(e)}")

    return processed_files


@profile
def add_statuses(data):
    """Add statuses to dictionary from json"""
    data_list = data.get("dataList")
    if isinstance(data_list, list):
        for item in data_list:
            if isinstance(item, dict):
                name = item.get("name")
                id_ = item.get("id")
                if id_ and name:
                    status_id_name_map[id_] = name
    return data
