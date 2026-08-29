import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import cast

from file_list import file_list
from src.globals import compiled_patterns, config, skill_tag_ids, target_dir
from src.models.json_structure import JSONType, Match, ReplaceRule
from utils.helpers import collect_files


def split_sentences(data: str):
    """Split string into sentences"""
    # Split by ". "
    sentences = re.split(r"(?<=\.) ", data)
    sentences_with_space = [
        sentence + (" " if i < len(sentences) - 1 else "")
        for i, sentence in enumerate(sentences)
    ]
    # Split by \n
    final_result: list[str] = []
    for sentence in sentences_with_space:
        split_by_newline = sentence.split("\n")
        for i, part in enumerate(split_by_newline):
            if "\n" in sentence and i < len(split_by_newline) - 1:
                final_result.append(part + "\n")
            else:
                final_result.append(part)

    return final_result


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


def invert_map_with_warnings(ordered_status_names: list[tuple[str, str]]):
    """Convert list of (id, name) pairs to dict name -> id. Ids with same name both stored, but only first used."""
    name_to_ids: dict[str, list[str]] = {}

    # TODO: Check logic / rename
    for id_, name in ordered_status_names:
        if name not in name_to_ids:
            name_to_ids[name] = []
        name_to_ids[name].append(id_)

    name_to_id: dict[str, str] = {}
    for name, ids in name_to_ids.items():
        # This can potentially result in incorrect status icon
        name_to_id[name] = ids[0]
    return name_to_id


def add_status_regex(replace_config: list[ReplaceRule], status_files: list[str]):
    """Replace status names and ids with linked sprites"""
    from src.statuses import status_id_name_map

    ordered_status_names = sorted(
        status_id_name_map.items(), key=lambda x: len(x[0]), reverse=True
    )
    status_names = [re.escape(name) for _, name in ordered_status_names]
    status_ids = [re.escape(id_) for id_, _ in ordered_status_names]
    pattern_names = (
        r'(?<!<link=")(?<!sprite name=")(?<!\[)\b('
        + "|".join(status_names)
        + r')\b(?![\]">])'
    )
    pattern_ids = r"\[(" + "|".join(status_ids) + r")\]"

    name_to_id = invert_map_with_warnings(ordered_status_names)

    def repl_name(match: Match[str]):
        name = match.group(1)
        id_ = name_to_id[name]
        return f'<link="{id_}"><sprite name="{id_}"></link>'

    def repl_id(match: Match[str]):
        id_ = match.group(1)
        return f'<link="{id_}"><sprite name="{id_}"></link>'

    status_sprite_remove: ReplaceRule = {
        "fields": ["desc"],
        "changes": [
            {
                "from": r"<sprite [^>]+><color[^>]+><u><link[^>]+>([^>]+)</color></link></u>",
                "to": r"\1",
                "regex": True,
            }
        ],
        "ignoredFiles": status_files,
    }
    status_name_replace: ReplaceRule = {
        "fields": ["desc"],
        "changes": [{"from": pattern_names, "to": repl_name, "regex": True}],
        "ignoredFiles": status_files,
    }
    status_id_replace: ReplaceRule = {
        "fields": ["desc"],
        "changes": [{"from": pattern_ids, "to": repl_id, "regex": True}],
        "ignoredFiles": status_files,
    }
    replace_config.append(status_sprite_remove)
    replace_config.append(status_name_replace)
    replace_config.append(status_id_replace)


def get_replacement_files():
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


def process_replaces(status_files: list[str]):
    replace_config = config["replace"]

    if config["statuses"]["enabled"]:
        add_status_regex(replace_config, status_files)

    files = get_replacement_files()
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

            processed_count += 1
            print(f"{filename} processed ({processed_count}/{file_count})")

        except Exception as e:
            print(f"Error in file {filename}: {e!s}")
