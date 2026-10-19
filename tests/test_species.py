import pytest

from porydex.decomp.abilities import load_abilities
from porydex.decomp.items import load_items
from porydex.decomp.moves import load_moves
from porydex.decomp.species import (
    _abilities,
    _evolution,
    _Lookups,
    learnsets_to_showdown,
    load_species,
    species_to_showdown,
)

VANILLA_ITEMS = {
    'abomasite': {'name': 'Abomasite', 'megaStone': 'Abomasnow-Mega', 'megaEvolves': 'Abomasnow'},
}

@pytest.fixture
def species(decomp):
    return load_species(
        decomp,
        load_moves(decomp, {}),
        load_abilities(decomp, {}),
        load_items(decomp, VANILLA_ITEMS),
    )

@pytest.fixture
def dex(species):
    return species_to_showdown(species)

def test_load_species_skips_placeholders_and_adds_forms(species):
    assert list(species) == ['bulbasaur', 'ivysaur', 'abomasnow', 'abomasnowmega', 'rotom', 'rotomwash', 'shellos']

def test_base_species_to_showdown(dex):
    assert dex['bulbasaur'] == {
        'num': 1,
        'name': 'Bulbasaur',
        'types': ['Normal', 'Fairy'],
        'baseStats': {'hp': 45, 'atk': 49, 'def': 49, 'spe': 45, 'spa': 65, 'spd': 65},
        'abilities': {'0': 'Overgrow', 'H': 'Stench'},
        'heightm': 0.7,
        'weightkg': 6.9,
        'color': 'Green',
        'eggGroups': ['Monster'],
        'genderRatio': {'M': 0.875, 'F': 0.125},
        'tier': 'obtainable',
        'evos': ['Ivysaur'],
    }

def test_duplicate_abilities_and_types_collapse(dex):
    assert dex['ivysaur']['abilities'] == {'0': 'Overgrow'}
    assert dex['ivysaur']['types'] == ['Normal']

def test_first_evolution_method_per_target_wins(dex):
    assert {k: v for k, v in dex['ivysaur'].items() if k.startswith(('prevo', 'evo'))} == {
        'prevo': 'Bulbasaur',
        'evoType': 'level',
        'evoLevel': 16,
        'evos': ['Rotom'],
    }

def test_move_evolution_uses_move_name(dex):
    assert dex['rotom']['evoType'] == 'levelMove'
    assert dex['rotom']['evoMove'] == 'Bite'

def test_mega_form_links_stone_and_inherits_size(dex):
    mega = dex['abomasnowmega']
    assert mega['baseSpecies'] == 'Abomasnow'
    assert mega['forme'] == 'Mega'
    assert mega['requiredItem'] == 'Abomasite'
    assert mega['battleOnly'] == 'Abomasnow'
    assert (mega['heightm'], mega['weightkg']) == (dex['abomasnow']['heightm'], dex['abomasnow']['weightkg'])
    assert dex['abomasnow']['otherFormes'] == ['Abomasnow-Mega']

def test_data_form_from_registry(dex):
    assert dex['rotom']['otherFormes'] == ['Rotom-Wash']
    assert dex['rotomwash']['forme'] == 'Wash'
    assert dex['rotomwash']['gender'] == 'N'
    assert 'requiredItem' not in dex['rotomwash']

def test_cosmetic_formes_use_showdown_names(dex):
    assert dex['shellos']['cosmeticFormes'] == ['Shellos-East']
    assert dex['shellos']['baseForme'] == 'West'

def test_learnsets_skip_megas_but_keep_other_forms(species):
    learnsets = learnsets_to_showdown(species)
    assert 'abomasnowmega' not in learnsets
    assert learnsets['rotomwash'] == {'learnset': {'bite': ['L1']}}
    assert learnsets['bulbasaur'] == {'learnset': {
        'pound': ['L1', 'L5'],
        'karatechop': ['M', 'E'],
        'bite': ['T'],
    }}

@pytest.mark.parametrize('constants, expected', [
    (['ABILITY_A', 'ABILITY_B', 'ABILITY_B'], {'0': 'A', '1': 'B', 'H': 'B'}),
    (['ABILITY_A', 'ABILITY_NONE', 'ABILITY_A'], {'0': 'A', 'H': 'A'}),
    (['ABILITY_A', 'ABILITY_A', 'ABILITY_NONE'], {'0': 'A'}),
])
def test_hidden_ability_kept_even_when_duplicated(constants, expected):
    assert _abilities(constants, {'ABILITY_A': 'A', 'ABILITY_B': 'B'}) == expected

def test_unknown_evolution_method_is_rejected():
    with pytest.raises(ValueError):
        _evolution(['EVO_SOMETHING_NEW', 'SPECIES_IVYSAUR'], _Lookups({}, {}, {}, {}, {}, frozenset(), {}))

def test_mega_with_unplaced_stone_is_unobtainable(dex):
    assert dex['abomasnowmega']['tier'] == 'unobtainable'
    assert dex['abomasnow']['tier'] == 'obtainable'

def test_mega_with_placed_stone_is_obtainable(decomp, monkeypatch):
    monkeypatch.setattr('porydex.decomp.items.load_placed_items', lambda _: {'ITEM_ABOMASITE'})
    species = load_species(
        decomp,
        load_moves(decomp, {}),
        load_abilities(decomp, {}),
        load_items(decomp, VANILLA_ITEMS),
    )
    assert species_to_showdown(species)['abomasnowmega']['tier'] == 'obtainable'

def _species_with_unobtainable(decomp, unobtainable):
    return load_species(
        decomp,
        load_moves(decomp, {}),
        load_abilities(decomp, {}),
        load_items(decomp, VANILLA_ITEMS),
        frozenset(unobtainable),
    )

def test_unobtainable_species_and_their_forms(decomp):
    dex = species_to_showdown(_species_with_unobtainable(decomp, {'Rotom'}))
    assert dex['rotom']['tier'] == 'unobtainable'
    assert dex['rotomwash']['tier'] == 'unobtainable'
    assert dex['bulbasaur']['tier'] == 'obtainable'

def test_unobtainable_form_leaves_base_obtainable(decomp):
    dex = species_to_showdown(_species_with_unobtainable(decomp, {'Rotom-Wash'}))
    assert dex['rotom']['tier'] == 'obtainable'
    assert dex['rotomwash']['tier'] == 'unobtainable'

def test_unknown_unobtainable_name_is_rejected(decomp):
    with pytest.raises(ValueError, match='Rotomm'):
        _species_with_unobtainable(decomp, {'Rotomm'})

def test_egg_moves_only_for_gift_egg_species(decomp, monkeypatch):
    monkeypatch.setattr('porydex.decomp.species.load_gift_egg_species', lambda _: frozenset())
    learnsets = learnsets_to_showdown(_species_with_unobtainable(decomp, set()))
    assert learnsets['bulbasaur'] == {'learnset': {
        'pound': ['L1', 'L5'],
        'karatechop': ['M'],
        'bite': ['T'],
    }}
