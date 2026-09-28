"""Структурные проверки IE-диаграмм, а не полный интерпретатор PlantUML."""

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


SOURCE_DIR = Path(__file__).resolve().parents[1] / "src"
_NAME = r'(?:"[^"\n]+"|[\w.$]+)'
_ENTITY = re.compile(rf"^\s*entity\s+{_NAME}", re.IGNORECASE)
_RELATIONSHIP = re.compile(
    rf"^\s*{_NAME}\s+"
    r"(?P<left>\|\||\|o|\}o|\}\|)\s*"
    r"(?:-+|\.+)(?:\[[^\]\n]+\])?(?:left|right|up|down|l|r|u|d)?(?:-+|\.+)?\s*"
    r"(?P<right>\|\||o\||o\{|\|\{)"
    rf"\s+{_NAME}\s*(?::.*)?$"
)
_COMMENTS = re.compile(r'"(?:\\.|[^"\\])*"|/\'[\s\S]*?\'/|\'[^\n]*')


def diagram_lines(content):
    # Сохраняем строки в кавычках: апостроф в имени — не начало комментария.
    content = _COMMENTS.sub(
        lambda match: match[0] if match[0].startswith('"') else "\n" * match[0].count("\n"),
        content,
    )
    block_end = None
    for line in content.splitlines():
        stripped = line.strip().lower()
        if block_end:
            if re.fullmatch(block_end, stripped):
                block_end = None
            continue
        if re.match(r"^(legend|note|header|footer|title)\b", stripped):
            keyword = stripped.split()[0]
            # Однострочные note/title/header/footer не открывают блок.
            if keyword == "legend" or (keyword == "note" and ":" not in line) or stripped == keyword:
                block_end = rf"end\s*{keyword}"
            continue
        if re.match(r"^!(?:function|procedure)\b", stripped):
            block_end = r"!end(?:function|procedure)"
            continue
        yield line


@dataclass
class Diagram:
    entity_count: int
    relationships: Counter


def parse_diagram(content):
    entities = 0
    relationships = Counter()
    for line in diagram_lines(content):
        if _ENTITY.match(line):
            entities += 1
        match = _RELATIONSHIP.fullmatch(line)
        if match:
            left_many = "}" in match["left"]
            right_many = "{" in match["right"]
            if left_many and right_many:
                kind = "many_to_many"
            elif left_many or right_many:
                kind = "one_to_many"
            else:
                kind = "one_to_one"
            relationships[kind] += 1
    return Diagram(entities, relationships)


def read_diagram(filename):
    path = SOURCE_DIR / filename
    assert path.is_file(), f"Не найден файл задания: {path}"
    content = path.read_text(encoding="utf-8-sig")
    lines = list(diagram_lines(content))
    starts = [i for i, line in enumerate(lines) if re.match(r"^\s*@startuml\b", line)]
    ends = [i for i, line in enumerate(lines) if re.match(r"^\s*@enduml\s*$", line)]
    assert len(starts) == len(ends) == 1 and starts[0] < ends[0], (
        f"{filename}: добавьте одну диаграмму между @startuml и @enduml"
    )
    return parse_diagram("\n".join(lines[starts[0] + 1:ends[0]]))


def assert_relationships(diagram, *, one_to_many, many_to_many=0, one_to_one=0):
    expected = {
        "one_to_many": (one_to_many, "один-ко-многим"),
        "many_to_many": (many_to_many, "многие-ко-многим"),
        "one_to_one": (one_to_one, "один-к-одному"),
    }
    for kind, (count, label) in expected.items():
        actual = diagram.relationships[kind]
        assert actual == count, f"Ожидается {count} связей {label}, найдено {actual}"
