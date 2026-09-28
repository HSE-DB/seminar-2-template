from erd_helpers import assert_relationships


PUML_FILE = "relationships_match.puml"


def test_match_entity_count(diagram):
    assert diagram.entity_count == 3, (
        f"Ожидается 3 сущностей, найдено {diagram.entity_count}"
    )


def test_match_relationship_types(diagram):
    assert_relationships(diagram, one_to_many=3, many_to_many=0)
