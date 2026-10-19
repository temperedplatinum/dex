import pathlib

import pytest

@pytest.fixture
def decomp() -> pathlib.Path:
    return pathlib.Path(__file__).parent / 'fixtures' / 'decomp'
