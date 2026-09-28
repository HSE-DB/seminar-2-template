from erd_helpers import assert_relationships


PUML_FILE = "relationships_address.puml"


def test_address_entity_count(diagram):
    assert diagram.entity_count == 5, (
        f"Ожидается 5 сущностей, найдено {diagram.entity_count}"
    )


def test_address_relationship_types(diagram):
    assert_relationships(diagram, one_to_many=4, many_to_many=0)
