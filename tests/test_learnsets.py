import pytest

from porydex.decomp.learnsets import load_gift_egg_species, load_tm_moves, parse_learnset

MOVE_KEYS = {
    'MOVE_POUND': 'pound',
    'MOVE_BITE': 'bite',
    'MOVE_KARATE_CHOP': 'karatechop',
}

def test_load_tm_moves_matches_by_designator_not_order(decomp):
    assert load_tm_moves(decomp) == {'TM01': 'MOVE_KARATE_CHOP', 'TM02': 'MOVE_BITE'}

def test_parse_learnset_codes_and_dedupes():
    raw = {
        'by_level': [[1, 'MOVE_POUND'], [5, 'MOVE_POUND']],
        'by_tm': ['TM01', 'TM02'],
        'by_tutor': ['MOVE_BITE'],
        'egg_moves': ['MOVE_KARATE_CHOP'],
    }
    tm_moves = {'TM01': 'MOVE_KARATE_CHOP', 'TM02': 'MOVE_BITE'}
    assert parse_learnset(raw, tm_moves, MOVE_KEYS) == {
        'pound': ['L1', 'L5'],
        'karatechop': ['M', 'E'],
        'bite': ['M', 'T'],
    }

def test_parse_learnset_rejects_unknown_move():
    with pytest.raises(KeyError):
        parse_learnset({'by_tutor': ['MOVE_MISSING']}, {}, MOVE_KEYS)

def test_gift_egg_species_come_from_give_egg_commands_ignoring_comments(decomp):
    assert load_gift_egg_species(decomp) == {'SPECIES_BULBASAUR'}

def test_parse_learnset_can_drop_egg_moves():
    raw = {'by_level': [[1, 'MOVE_POUND']], 'egg_moves': ['MOVE_BITE']}
    assert parse_learnset(raw, {}, MOVE_KEYS, include_egg_moves=False) == {'pound': ['L1']}
