import time

from file_list import process_file_list
from globals import config, target_dir
from move_files import move_translation_files
from replace import process_replaces
from statuses import find_statuses


def process_files():
    """Main file processing"""
    processed_files = []
    if config["statuses"]["enabled"]:
        print("Status collection...")
        processed_files = find_statuses()
        print("Statuses collected")
    process_replaces(processed_files)


def main():
    if config["moveFiles"]["enabled"]:
        move_translation_files()
    if not config["replaceFilesEnabled"]:
        return
    # Tk().withdraw()

    if target_dir:
        start_time = time.time()
        process_file_list()
        process_files()
        print("Replace complete!")
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Execution time: {elapsed_time:.2f} seconds")
    else:
        print("Directory not selected")


if __name__ == "__main__":
    main()
