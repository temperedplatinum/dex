import pytest

from porydex.decomp.abilities import load_abilities
from porydex.decomp.encounters import (
    LOCATION_NAME_OVERRIDES,
    EncounterSlot,
    _add_location,
    load_encounters,
    load_honey_tree_levels,
    load_slot_rates,
)
from porydex.decomp.items import load_items
from porydex.decomp.moves import load_moves
from porydex.decomp.species import load_species

@pytest.fixture
def locations(decomp):
    species = load_species(decomp, load_moves(decomp, {}), load_abilities(decomp, {}), load_items(decomp, {}))
    return load_encounters(decomp, species)

def test_slot_rates_parsed_from_c_thresholds(decomp):
    assert load_slot_rates(decomp) == {
        'land': [20, 15, 10, 10, 10, 10, 5, 5, 5, 5, 4, 1],
        'surf': [20, 20, 20, 20, 10, 10],
    }

def test_honey_tree_levels_parsed_from_c(decomp):
    assert load_honey_tree_levels(decomp) == (5, 15)

def test_locations_skip_empty_and_zero_rate_files(locations):
    assert list(locations) == ['route212north', 'route212south', 'losttower1f', 'losttower2f', 'honeytrees']

def test_shared_labels_get_file_suffixes(locations):
    assert [location.name for location in locations.values()] == [
        'Route 212 (North)',
        'Route 212 (South)',
        'Lost Tower (1F)',
        'Lost Tower (2F)',
        'Honey Trees',
    ]

def test_name_overrides_replace_label_and_suffix(decomp, monkeypatch):
    monkeypatch.setitem(LOCATION_NAME_OVERRIDES, 'encounters_route_212_south', 'Route 212 (Swamp)')
    species = load_species(decomp, load_moves(decomp, {}), load_abilities(decomp, {}), load_items(decomp, {}))
    locations = load_encounters(decomp, species)
    assert locations['route212swamp'].name == 'Route 212 (Swamp)'
    assert 'route212south' not in locations

MEADOW = {'land': (EncounterSlot('bulbasaur', 5, 5, 100),)}
FOREST = {'land': (EncounterSlot('ivysaur', 5, 5, 100),)}

def test_identical_tables_merge_into_one_location():
    locations = {}
    _add_location(locations, 'encounters_chateau_hall', 'Old Chateau', MEADOW)
    _add_location(locations, 'encounters_chateau_attic', 'Old Chateau', MEADOW)
    assert list(locations) == ['oldchateau']
    assert locations['oldchateau'].methods == MEADOW

def test_merging_different_tables_is_rejected():
    locations = {}
    _add_location(locations, 'encounters_chateau_hall', 'Old Chateau', MEADOW)
    with pytest.raises(ValueError, match='encounters_chateau_attic'):
        _add_location(locations, 'encounters_chateau_attic', 'Old Chateau', FOREST)

def test_inaccessible_locations_are_excluded(decomp, monkeypatch):
    monkeypatch.setattr(
        'porydex.decomp.encounters.INACCESSIBLE_LOCATION_FILES',
        frozenset({'encounters_route_212_south'}),
    )
    species = load_species(decomp, load_moves(decomp, {}), load_abilities(decomp, {}), load_items(decomp, {}))
    locations = load_encounters(decomp, species)
    assert 'route212south' not in locations
    assert locations['route212'].name == 'Route 212'

def test_land_slots_merge_by_species(locations):
    assert locations['route212north'].to_showdown()['land'] == [
        {'species': 'bulbasaur', 'minLvl': 5, 'maxLvl': 6, 'rate': 35},
        {'species': 'ivysaur', 'minLvl': 7, 'maxLvl': 16, 'rate': 65},
    ]

def test_surf_drops_empty_slots_and_keeps_level_ranges(locations):
    assert locations['route212north'].to_showdown()['surf'] == [
        {'species': 'shellos', 'minLvl': 20, 'maxLvl': 30, 'rate': 40},
        {'species': 'rotom', 'minLvl': 20, 'maxLvl': 30, 'rate': 10},
    ]

def test_replacement_and_fishing_tables_are_ignored(locations):
    assert set(locations['route212north'].methods) == {'land', 'surf'}

def test_honey_tree_rates_are_weight_percentages(locations):
    assert locations['honeytrees'].to_showdown() == {
        'name': 'Honey Trees',
        'honey': [
            {'species': 'bulbasaur', 'minLvl': 5, 'maxLvl': 15, 'rate': 83.3},
            {'species': 'rotom', 'minLvl': 5, 'maxLvl': 15, 'rate': 16.7},
        ],
    }

def test_locations_follow_given_order_then_unlisted(decomp):
    species = load_species(decomp, load_moves(decomp, {}), load_abilities(decomp, {}), load_items(decomp, {}))
    order = ('honeytrees', 'losttower2f', 'route212south')
    assert list(load_encounters(decomp, species, order)) == [
        'honeytrees', 'losttower2f', 'route212south', 'route212north', 'losttower1f',
    ]

def test_unknown_location_in_order_is_rejected(decomp):
    species = load_species(decomp, load_moves(decomp, {}), load_abilities(decomp, {}), load_items(decomp, {}))
    with pytest.raises(ValueError, match='route999'):
        load_encounters(decomp, species, ('route999',))
