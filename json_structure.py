from re import Match
from typing import Any, Callable, TypedDict, NotRequired, Union

# === COMMON TYPE FOR UNKNOWN JSON ===

JSONType = Union[dict[str, Any], list[Any], str, int, float, bool, None]

# === CONFIG ===
ReplaceChange = TypedDict(
    "ReplaceChange",
    {
        "from": str,
        "to": str | Callable[[Match[str]], str],
        "regex": NotRequired[bool],
    },
)

ReplaceRule = TypedDict(
    "ReplaceRule",
    {
        "fields": list[str],
        "changes": list[ReplaceChange],
        "ignoredFiles": NotRequired[list[str]],
    },
)


class StatusFields(TypedDict):
    required: list[str]
    optional: list[str]


class StatusConfig(TypedDict):
    enabled: bool
    fields: StatusFields
    ignoredFiles: list[str]


class MoveFilesConfig(TypedDict):
    enabled: bool
    sourceTranslation: str
    translationName: str


class Config(TypedDict):
    moveFiles: MoveFilesConfig
    replaceFilesEnabled: bool
    statuses: StatusConfig
    skillTagPersistence: bool
    replace: list[ReplaceRule]


# === SkillTag.json ===
class SkillTag(TypedDict):
    id: str
    name: str
