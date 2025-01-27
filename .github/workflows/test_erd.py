import pytest
import re

def read_puml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

@pytest.fixture
def puml_content():
    return read_puml_file("./src/library.puml")

def test_entity_count(puml_content):
    """Проверка общего количества сущностей"""
    entities = re.findall(r'entity\s+[""]?\w+[""]?', puml_content, re.IGNORECASE)
    assert len(entities) == 6, \
        f"Ожидается 6 сущностей, найдено {len(entities)}"

def test_relationship_types(puml_content):
    """Проверка количества различных типов связей"""
    # Один-ко-многим (1--*)
    one_to_many = len(re.findall(r'[""]?1[""]?\s*--[>o]\s*[""]?\*[""]?', puml_content))
    assert one_to_many == 5, \
        f"Ожидается 5 связей один-ко-многим, найдено {one_to_many}"

    # Многие-ко-многим (*--*)
    many_to_many = len(re.findall(r'[""]?\*[""]?\s*--[>o]\s*[""]?\*[""]?', puml_content))
    assert many_to_many == 1, \
        f"Ожидается 1 связь многие-ко-многим, найдено {many_to_many}"

    # Проверка отсутствия один-к-одному (1--1)
    one_to_one = len(re.findall(r'[""]?1[""]?\s*--[>o]\s*[""]?1[""]?', puml_content))
    assert one_to_one == 0, \
        f"Ожидается 0 связей один-к-одному, найдено {one_to_one}"