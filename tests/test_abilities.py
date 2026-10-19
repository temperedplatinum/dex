import pytest

from porydex.decomp.abilities import load_abilities

VANILLA_ABILITIES = {
    'stench': {'name': 'Stench', 'rating': 0.5, 'flags': {}},
    'overgrow': {'name': 'Overgrow', 'rating': 2, 'flags': {'breakable': 1}},
}

@pytest.fixture
def abilities(decomp):
    return load_abilities(decomp, VANILLA_ABILITIES)

def test_load_abilities_skips_none(abilities):
    assert list(abilities) == ['stench', 'overgrow', 'megasol']

def test_known_ability_uses_game_description_and_vanilla_rating(abilities):
    assert abilities['stench'].to_showdown() == {
        'num': 1,
        'name': 'Stench',
        'rating': 0.5,
        'flags': {},
        'desc': 'The stench helps keep wild Pokémon away.',
        'shortDesc': 'The stench helps keep wild Pokémon away.',
    }

def test_known_ability_keeps_vanilla_flags(abilities):
    assert abilities['overgrow'].flags == {'breakable': 1}

def test_custom_ability_gets_default_rating(abilities):
    assert abilities['megasol'].to_showdown() == {
        'num': 3,
        'name': 'Mega Sol',
        'rating': 1,
        'flags': {},
        'desc': 'Acts as if under harsh sunlight.',
        'shortDesc': 'Acts as if under harsh sunlight.',
    }
