import os
import shutil

from line_profiler_pycharm import profile

from globals import source_dir, target_dir, config


@profile
def add_font_folder():
    os.makedirs(target_dir + '/Font/Context', exist_ok=True)
    os.makedirs(target_dir + '/Font/Title', exist_ok=True)


@profile
def move_fonts():
    path = target_dir + '/Font/'
    if os.path.exists(path):
        shutil.rmtree(path)
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Font')
    shutil.copytree(src, path)


@profile
def copy_source_files():
    """Recursive file copy from source to target"""
    for root, dirs, files in os.walk(source_dir):
        relative_path = os.path.relpath(root, source_dir)

        target_path = os.path.join(target_dir, relative_path)
        os.makedirs(target_path, exist_ok=True)

        prefix = config["moveFiles"]["sourceTranslation"].upper() + "_"

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

    print(f"Copy finished!")


@profile
def move_translation_files():
    copy_source_files()
    # Empty font folders are necessary for translation to load for some reason
    add_font_folder()
    # Right now lack of fonts means that translation won't be applied
    if config["moveFiles"]["moveFont"]:
        move_fonts()
