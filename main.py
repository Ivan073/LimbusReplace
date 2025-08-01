import json
import time
from tkinter import Tk
from tkinter.filedialog import askdirectory

from line_profiler_pycharm import profile

from move_files import move_translation_files
from replace import process_replaces
from statuses import process_statuses


@profile
def load_config():
    """Load congig from config.json"""
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


@profile
def process_files(directory, config):
    """Main file processing"""
    processed_files = []
    if config['statuses']['enabled']:
        print('Status collection...')
        processed_files = process_statuses(directory, config)
        print("Statuses collected")

    process_replaces(directory, config, processed_files)


@profile
def main():
    config = load_config()
    if config["moveFiles"]["enabled"]:
        move_translation_files(config)
    if not config["replaceFilesEnabled"]:
        return
    Tk().withdraw()
    from move_files import target_folder
    target_dir = target_folder if target_folder else askdirectory() + "/Lang/"+config["moveFiles"]["translationName"]

    if target_dir:
        start_time = time.time()
        process_files(target_dir, config)
        print("Replace complete!")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time: {elapsed_time:.2f} seconds")
    else:
        print("Directory not selected")


if __name__ == "__main__":
    main()
