import json
from tkinter import filedialog
import os
import shutil

source_folder = ""
target_folder = ""
config_path = ""


def select_source_folder(config):
    global source_folder, target_folder, config_path
    data_folder = filedialog.askdirectory()
    source_folder = data_folder + "/Assets/Resources_moved/Localize/"+config["moveFiles"]["sourceTranslation"]
    config_path = data_folder + "/Lang/"
    target_folder = data_folder + "/Lang/"+config["moveFiles"]["translationName"]


def create_config(path, config):
    path = os.path.join(path, 'config.json')
    if not os.path.exists(path) or config["moveFiles"]["replaceConfig"]:
        config_data = {
            "lang": config["moveFiles"]["translationName"]
        }
        with open(path, 'w') as f:
            json.dump(config_data, f, indent=4)


def copy_files(config):
    """Recursive file copy from source to target"""
    global source_folder, target_folder, config_path
    for root, dirs, files in os.walk(source_folder):
        relative_path = os.path.relpath(root, source_folder)

        target_path = os.path.join(target_folder, relative_path)
        os.makedirs(target_path, exist_ok=True)

        prefix = config["moveFiles"]["sourceTranslation"].upper()+"_"

        for file in files:
            if file.endswith('.json') and file.startswith(prefix):
                new_filename = file[len(prefix):]
            else:
                new_filename = file

            source_file_path = os.path.join(root, file)
            target_file_path = os.path.join(target_path, new_filename)

            try:
                shutil.copy2(source_file_path, target_file_path)
            except Exception as e:
                print(f"Copy error in {file}: {e}")

    create_config(config_path, config)
    print(f"Copy finished!")


def move_translation_files(config):
    select_source_folder(config)
    copy_files(config)
