from erd_helpers import assert_relationships


PUML_FILE = "relationships_parents.puml"


def test_parents_entity_count(diagram):
    assert diagram.entity_count in (1, 2), (
        f"Ожидается 1 или 2 сущности, найдено {diagram.entity_count}"
    )


def test_parents_relationship_types(diagram):
    test_parents_entity_count(diagram)
    # Отец и мать: две роли для Person или по две для Man и Woman.
    assert_relationships(diagram, one_to_many=2 * diagram.entity_count)
