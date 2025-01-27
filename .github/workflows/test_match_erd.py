import pytest
import re
import os

def read_puml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

@pytest.fixture
def puml_content():
    return read_puml_file("./src/relationships_match.puml")

def test_match_entity_count(puml_content):
    """Проверка количества сущностей в диаграмме матчей"""
    entities = re.findall(r'entity\s+[""]?\w+[""]?', puml_content, re.IGNORECASE)
    assert len(entities) == 3, \
        f"Ожидается 3 сущности, найдено {len(entities)}"

def test_match_relationship_types(puml_content):
    """Проверка типов связей в диаграмме матчей"""
    # Связи Матч-Команда (должны быть как one-to-many, так как одна команда участвует во многих матчах)
    team_relations = len(re.findall(r'[""]?\*[""]?\s*--[>o]\s*[""]?1[""]?', puml_content))
    assert team_relations == 3, \
        f"Ожидается 3 связи many-to-one, найдено {team_relations}"

    # Проверка отсутствия many-to-many связей
    many_to_many = len(re.findall(r'[""]?\*[""]?\s*--[>o]\s*[""]?\*[""]?', puml_content))
    assert many_to_many == 0, \
        f"Не должно быть связей many-to-many, найдено {many_to_many}"