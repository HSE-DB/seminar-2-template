"""Регрессии проверяющей системы; решения студентов не используются."""

from importlib import import_module
from pathlib import Path

import pytest

import erd_helpers
from erd_helpers import parse_diagram, read_diagram


@pytest.mark.parametrize("left", ["||", "|o", "}o", "}|"])
@pytest.mark.parametrize("right", ["||", "o|", "o{", "|{"])
@pytest.mark.parametrize("connector", ["--", "..", "-left-", "-[#red]-"])
def test_cardinalities_in_both_directions(left, right, connector):
    diagram = parse_diagram(f'A {left}{connector}{right} B : связь')
    many_sides = int("}" in left) + int("{" in right)
    expected = ["one_to_one", "one_to_many", "many_to_many"][many_sides]
    assert diagram.relationships == {expected: 1}


def test_comments_and_explanatory_blocks_are_not_diagram_elements():
    diagram = parse_diagram('''
entity A
entity "Читатель библиотеки" as B
A ||--o{ B : берет ' реальная связь
' entity Fake
' A ||--o{ B
/'
entity Fake
A ||--o{ B
'/
legend right
entity Fake
A }o--o{ B
endlegend
note right of A
entity Fake
A ||--|| B
end note
!function $example()
entity Fake
A ||--|| B
!endfunction
''')
    assert diagram.entity_count == 2
    assert diagram.relationships == {"one_to_many": 1}


def test_quoted_names_apostrophes_and_inline_notes():
    diagram = parse_diagram('''
entity "O'Brien"
note right: entity Fake
entity "Книга на полке"
"O'Brien" }o..|| "Книга на полке" : "entity Fake ||--||"
''')
    assert diagram.entity_count == 2
    assert diagram.relationships == {"one_to_many": 1}


def test_repository_example_including_formatted_entity_names():
    source = Path(__file__).resolve().parents[1] / "example.puml"
    diagram = parse_diagram(source.read_text(encoding="utf-8"))
    assert diagram.entity_count == 5
    assert diagram.relationships == {
        "one_to_many": 3, "many_to_many": 1, "one_to_one": 1,
    }


def test_paths_do_not_depend_on_working_directory(tmp_path, monkeypatch):
    source = tmp_path / "src"
    source.mkdir()
    (source / "sample.puml").write_text(
        '\ufeff@startuml\nentity A\n@enduml\n', encoding="utf-8"
    )
    monkeypatch.setattr(erd_helpers, "SOURCE_DIR", source)
    monkeypatch.chdir(tmp_path.parent)
    assert read_diagram("sample.puml").entity_count == 1


@pytest.mark.parametrize("content", [
    "", "/' Только условие задания '/", "@startuml\nentity A",
    "@enduml\n@startuml", "' @startuml\nentity A\n' @enduml",
    "@startuml\n@enduml\n@startuml\n@enduml",
])
def test_missing_or_invalid_diagram_boundaries_fail(tmp_path, monkeypatch, content):
    monkeypatch.setattr(erd_helpers, "SOURCE_DIR", tmp_path)
    (tmp_path / "sample.puml").write_text(content, encoding="utf-8")
    with pytest.raises(AssertionError, match="@startuml и @enduml"):
        read_diagram("sample.puml")


def test_missing_file_has_clear_error(tmp_path, monkeypatch):
    monkeypatch.setattr(erd_helpers, "SOURCE_DIR", tmp_path)
    with pytest.raises(AssertionError, match="Не найден файл задания"):
        read_diagram("missing.puml")


# Контрольные структуры для всех восьми проверок Classroom.
# Это проверка счётчиков, а не эталонные решения с атрибутами и ключами.
CASES = [
    ("test_erd", "", 6, "A ||--o{ B\nB ||..|{ C\nD |o--o{ D\nE ||--o{ F\nC }o--|| F\nB }o--|{ D"),
    ("test_address_erd", "address_", 5, "A ||--o{ B\nB ||--o{ C\nC ||--o{ D\nD ||--o{ E"),
    ("test_match_erd", "match_", 3, "A ||--o{ B : хозяева\nA ||--o{ B : гости\nC ||--o{ B : судит"),
    ("test_parents_erd", "parents_", 1, "A ||--o{ A : отец\nA ||--o{ A : мать"),
    ("test_parents_erd", "parents_", 2, "A ||--o{ A : отец\nA ||--o{ B : отец\nB ||--o{ A : мать\nB ||--o{ B : мать"),
]


@pytest.mark.parametrize("module_name,prefix,entity_count,links", CASES)
def test_assignment_checks_accept_valid_counts_and_reject_wrong_ones(
    module_name, prefix, entity_count, links,
):
    module = import_module(module_name)
    check_entities = getattr(module, f"test_{prefix}entity_count")
    check_links = getattr(module, f"test_{prefix}relationship_types")
    declarations = "\n".join(f"entity {chr(65 + i)}" for i in range(entity_count))
    diagram = parse_diagram(declarations + "\n" + links)
    check_entities(diagram)
    check_links(diagram)
    with pytest.raises(AssertionError):
        check_entities(parse_diagram(""))
    with pytest.raises(AssertionError):
        check_links(parse_diagram(declarations + "\n" + "\n".join(links.splitlines()[1:])))
    with pytest.raises(AssertionError):
        check_links(parse_diagram(declarations + "\n" + links + "\nA ||--|| A"))


def test_invalid_parents_entity_count_fails_instead_of_skipping():
    module = import_module("test_parents_erd")
    with pytest.raises(AssertionError, match="Ожидается 1 или 2 сущности"):
        module.test_parents_relationship_types(parse_diagram(""))
