import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import cast

from data_collection.file_list import file_list
from data_collection.globals import compiled_patterns, config, skill_tag_ids, target_dir
from replacement.statuses import add_status_regex
from src.models.json_structure import JSONType, ReplaceRule
from utils.files import collect_files
from utils.parsing import split_sentences


def process_replaces(status_files: list[str]):
    replace_config = config["replace"]

    if config["statuses"]["enabled"]:
        add_status_regex(replace_config, status_files)

    files = _get_replacement_files()
    file_count = len(files)
    processed_count = 0

    # Pattern compilation for performance boost
    for replace in replace_config:
        for change in replace["changes"]:
            if change.get("regex", False) and change["from"] not in compiled_patterns:
                compiled_patterns[change["from"]] = re.compile(rf"{change['from']}")

    for filename in files:
        path = target_dir / filename
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)

            active_replaces = [
                r for r in replace_config if filename not in r.get("ignoredFiles", [])
            ]
            modified_data = recursive_replace(data, active_replaces)

            with open(path, "w", encoding="utf-8-sig") as f:
                json.dump(modified_data, f, indent=4, ensure_ascii=False)

            print(f"{filename} processed ({processed_count + 1}/{file_count})")

        except FileNotFoundError:
            print(f"{filename} not found ({processed_count + 1}/{file_count})")
        except Exception as e:
            print(f"Error in file {filename}: {e!s}")
        finally:
            processed_count += 1


def _get_replacement_files():
    if config["limitedDirectories"]:
        return collect_files(
            file_list,
            "skill",
            "passive",
            "buf",
            "buffAbilities",
            "keyword",
            "egoGifts",
        )
    else:
        return list(filter(lambda x: x.endswith(".json"), os.listdir(target_dir)))


def recursive_replace(data: JSONType, replace_list: list[ReplaceRule]):
    """Recursive replace in JSON fields"""
    if isinstance(data, dict):
        for key in data:
            for replace_config in replace_list:
                if key in replace_config["fields"] and isinstance(data[key], str):
                    data[key] = replace_in_string(data[key], replace_config)
            data[key] = recursive_replace(data[key], replace_list)
    elif isinstance(data, list):

        def process_item(item: JSONType) -> JSONType:
            return recursive_replace(item, replace_list)

        data = list(ThreadPoolExecutor().map(process_item, data))

    return data


def replace_in_string(data: str, replace_config: ReplaceRule):
    """Replacement via regex in acquired strings"""
    skill_tag_persistence: bool = config["skillTagPersistence"]
    sentences = split_sentences(data)
    processed_sentences: list[str] = []
    skill_tag_regex = re.compile(
        r"^(?:<[^>]+>\s*)*((?:\[(?:" + "|".join(skill_tag_ids) + r")])+)"
    )

    for sentence in sentences:
        skill_tag_match = (
            skill_tag_regex.match(sentence) if skill_tag_persistence else None
        )

        for change in replace_config.get("changes", []):
            from_pattern = change["from"]
            to_pattern = change.get("to", "")
            use_regex = change.get("regex", False)

            if use_regex:
                pattern = compiled_patterns[from_pattern]
                if not pattern:
                    raise Exception("Pattern not compiled")
                try:
                    if skill_tag_match:
                        first_part = sentence[: skill_tag_match.end()]
                        rest_of_sentence = sentence[skill_tag_match.end() :]
                        rest_of_sentence = pattern.sub(to_pattern, rest_of_sentence)
                        sentence = (
                            f"{first_part}{rest_of_sentence}"
                            if rest_of_sentence
                            else first_part
                        )
                    else:
                        sentence = pattern.sub(to_pattern, sentence)
                except Exception as e:
                    print(
                        f"Failed to apply <{from_pattern}> to <{sentence}>: {e}\n"
                        f"pattern: {pattern}\n"
                        f"to: {to_pattern}\n"
                    )
            else:
                sentence = sentence.replace(from_pattern, cast(str, to_pattern))

        processed_sentences.append(sentence)

    return "".join(processed_sentences)
