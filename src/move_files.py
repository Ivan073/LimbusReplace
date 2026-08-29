import os
import shutil
from pathlib import Path

from data_collection.globals import config, source_dir, target_dir


def move_fonts():
    # Path to the target directory for fonts
    font_target_dir = Path(target_dir) / "Font"

    # Remove the folder if it already exists
    if font_target_dir.exists():
        shutil.rmtree(font_target_dir)

    # Create necessary subdirectories
    (font_target_dir / "Context").mkdir(parents=True, exist_ok=True)
    (font_target_dir / "Title").mkdir(parents=True, exist_ok=True)

    # Source: resources/Font relative to the project root
    project_root = Path(__file__).resolve().parent.parent
    src = project_root / "resources" / "Font"

    # Copy the directory tree
    shutil.copytree(src, font_target_dir, dirs_exist_ok=True)


def copy_source_files():
    """Recursive file copy from source to target"""
    prefix = config["moveFiles"]["sourceTranslation"].upper() + "_"
    for root, _, files in os.walk(source_dir):
        relative_path = os.path.relpath(root, source_dir)

        target_path = target_dir / relative_path
        os.makedirs(target_path, exist_ok=True)

        for file in files:
            should_remove_prefix = file.startswith(prefix) and file.endswith(".json")
            new_filename = file[len(prefix) :] if should_remove_prefix else file

            source_file_path = os.path.join(root, file)
            target_file_path = target_path / new_filename

            shutil.copy2(source_file_path, target_file_path)

    print("Copy finished!")


def move_translation_files():
    try:
        copy_source_files()
        move_fonts()
    except Exception:
        print("Failed to copy files")
