from collections.abc import Callable
from re import Match
from typing import Any, Literal, NotRequired, TypedDict

# === COMMON TYPE FOR UNKNOWN JSON ===
JSONType = dict[str, Any] | list[Any] | str | int | float | bool | None


# === CONFIG ===
_ReplaceChangeRegex = TypedDict(
    "_ReplaceChangeRegex",
    {
        "from": str,
        "to": str | Callable[[Match[str]], str],
        "regex": Literal[True],
    },
)
_ReplaceChangePlain = TypedDict(
    "_ReplaceChangePlain",
    {
        "from": str,
        "to": str,
        "regex": NotRequired[Literal[False]],
    },
)
ReplaceChange = _ReplaceChangeRegex | _ReplaceChangePlain

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


# === StatusFile ===
class StatusItem(TypedDict):
    name: str
    id: str
