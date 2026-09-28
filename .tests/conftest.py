import pytest

from erd_helpers import read_diagram


@pytest.fixture
def diagram(request):
    return read_diagram(request.module.PUML_FILE)
