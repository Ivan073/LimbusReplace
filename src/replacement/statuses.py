import re

from data_collection.globals import config
from src.models.json_structure import Match, ReplaceRule


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
    from data_collection.statuses import status_id_name_map

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

    sprite_fixes = config["statuses"]["spriteFixes"]

    def _repl_with_sprite(id_: str) -> str:
        sprite = sprite_fixes.get(id_, id_)
        return f'<link="{id_}"><sprite name="{sprite}"></link>'

    def repl_name(match: Match[str]) -> str:
        return _repl_with_sprite(name_to_id[match.group(1)])

    def repl_id(match: Match[str]) -> str:
        return _repl_with_sprite(match.group(1))

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
