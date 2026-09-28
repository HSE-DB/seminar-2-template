from erd_helpers import assert_relationships


PUML_FILE = "library.puml"


def test_entity_count(diagram):
    assert diagram.entity_count == 6, (
        f"Ожидается 6 сущностей, найдено {diagram.entity_count}"
    )


def test_relationship_types(diagram):
    assert_relationships(diagram, one_to_many=5, many_to_many=1)
