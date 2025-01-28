import pytest
import re
import os

def read_puml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

@pytest.fixture
def puml_content():
    return read_puml_file("./src/relationships_parents.puml")

def test_parents_entity_count(puml_content):
    """Проверка количества сущностей в диаграмме родственных связей"""
    entities = re.findall(r'entity\s+[""]?\w+[""]?', puml_content, re.IGNORECASE)

    # Проверяем один из двух вариантов:
    # 1. Две сущности (Man и Woman)
    # 2. Одна сущность (Person)
    entity_count = len(entities)
    assert entity_count in [1, 2], \
        f"Ожидается либо 1 сущность, либо 2 сущности, найдено {entity_count}"

def test_relationships_variant_two_entities(puml_content):
    """Проверка связей для варианта с двумя сущностями (Man и Woman)"""
    entities = re.findall(r'entity\s+[""]?\w+[""]?', puml_content, re.IGNORECASE)
    if len(entities) == 2:
        # Проверяем наличие self-связей (родитель - ребенок того же пола)
        self_relations = len(re.findall(r'[""]?\*[""]?\s*--[>o]\s*[""]?1[""]?.*same\s*entity', puml_content, re.IGNORECASE))
        assert self_relations == 2, \
            f"Для варианта с двумя сущностями ожидается 2 self-связи, найдено {self_relations}"

        # Проверяем связи между сущностями (родитель противоположного пола)
        cross_relations = len(re.findall(r'[""]?\*[""]?\s*--[>o]\s*[""]?1[""]?.*different\s*entities', puml_content, re.IGNORECASE))
        assert cross_relations == 2, \
            f"Для варианта с двумя сущностями ожидается 2 связи между разными сущностями, найдено {cross_relations}"

def test_relationships_variant_one_entity(puml_content):
    """Проверка связей для варианта с одной сущностью (Person)"""
    entities = re.findall(r'entity\s+[""]?\w+[""]?', puml_content, re.IGNORECASE)
    if len(entities) == 1:
        # Проверяем наличие двух связей к родителям
        parent_relations = len(re.findall(r'[""]?\*[""]?\s*--[>o]\s*[""]?1[""]?', puml_content))
        assert parent_relations == 2, \
            f"Для варианта с одной сущностью ожидается 2 связи к родителям, найдено {parent_relations}"

def test_no_invalid_relationships(puml_content):
    """Проверка отсутствия некорректных связей"""
    # Проверка отсутствия many-to-many связей
    many_to_many = len(re.findall(r'[""]?\*[""]?\s*--[>o]\s*[""]?\*[""]?', puml_content))
    assert many_to_many == 0, \
        f"Не должно быть связей many-to-many, найдено {many_to_many}"

    # Проверка отсутствия one-to-one связей
    one_to_one = len(re.findall(r'[""]?1[""]?\s*--[>o]\s*[""]?1[""]?', puml_content))
    assert one_to_one == 0, \
        f"Не должно быть связей one-to-one, найдено {one_to_one}"