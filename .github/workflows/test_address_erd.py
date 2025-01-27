import pytest
import re

def read_puml_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

@pytest.fixture
def puml_content():
    return read_puml_file("./src/relationships_address.puml")

def test_address_entity_count(puml_content):
    """Проверка количества сущностей в диаграмме адресов"""
    entities = re.findall(r'entity\s+[""]?\w+[""]?', puml_content, re.IGNORECASE)
    assert len(entities) == 5, \
        f"Ожидается 5 сущностей, найдено {len(entities)}"

def test_address_relationship_types(puml_content):
    """Проверка типов связей в диаграмме адресов"""
    # Все связи должны быть один-ко-многим (1--*)
    one_to_many = len(re.findall(r'[""]?1[""]?\s*--[>o]\s*[""]?\*[""]?', puml_content))
    assert one_to_many == 4, \
        f"Ожидается 4 связи один-ко-многим, найдено {one_to_many}"

    # Проверка отсутствия других типов связей
    many_to_many = len(re.findall(r'[""]?\*[""]?\s*--[>o]\s*[""]?\*[""]?', puml_content))
    assert many_to_many == 0, \
        f"Ожидается 0 связей многие-ко-многим, найдено {many_to_many}"

    one_to_one = len(re.findall(r'[""]?1[""]?\s*--[>o]\s*[""]?1[""]?', puml_content))
    assert one_to_one == 0, \
        f"Ожидается 0 связей один-к-одному, найдено {one_to_one}"