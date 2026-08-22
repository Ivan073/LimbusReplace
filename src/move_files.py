import os
import shutil
from pathlib import Path

from src.globals import config, source_dir, target_dir


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
    for root, _, files in os.walk(source_dir):
        relative_path = os.path.relpath(root, source_dir)

        target_path = os.path.join(target_dir, relative_path)
        os.makedirs(target_path, exist_ok=True)

        prefix = config["moveFiles"]["sourceTranslation"].upper() + "_"

        for file in files:
            if file.endswith(".json") and file.startswith(prefix):
                new_filename = file[len(prefix) :]
            else:
                new_filename = file

            source_file_path = os.path.join(root, file)
            target_file_path = os.path.join(target_path, new_filename)

            try:
                shutil.copy2(source_file_path, target_file_path)
            except Exception as e:
                print(f"Copy error in {file}: {e}")

    print("Copy finished!")


def move_translation_files():
    copy_source_files()
    move_fonts()
