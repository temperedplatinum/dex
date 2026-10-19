import pytest

from porydex.decomp.moves import load_moves

VANILLA_MOVES = {
    'counter': {'name': 'Counter', 'target': 'scripted'},
}

@pytest.fixture
def moves(decomp):
    return load_moves(decomp, VANILLA_MOVES)

def test_load_moves_skips_none_and_keys_by_showdown_id(moves):
    assert list(moves) == ['pound', 'karatechop', 'bite', 'counter', 'frostbreath']

def test_pound_to_showdown(moves):
    assert moves['pound'].to_showdown() == {
        'num': 1,
        'name': 'Pound',
        'type': 'Normal',
        'category': 'Physical',
        'basePower': 40,
        'accuracy': 100,
        'pp': 35,
        'priority': 0,
        'target': 'normal',
        'flags': {'contact': 1, 'mirror': 1, 'protect': 1},
        'contestType': 'Tough',
        'desc': 'The foe is physically pounded with a long tail or a foreleg, etc.',
        'shortDesc': 'The foe is physically pounded with a long tail or a foreleg, etc.',
    }

def test_high_crit_effect_sets_crit_ratio(moves):
    assert moves['karatechop'].to_showdown()['critRatio'] == 2

def test_always_crit_effect_sets_will_crit(moves):
    showdown = moves['frostbreath'].to_showdown()
    assert showdown['willCrit'] is True
    assert 'critRatio' not in showdown

def test_c_table_flags_are_merged(moves):
    assert moves['bite'].flags == {'bite', 'contact', 'protect', 'mirror'}

def test_engine_decided_range_uses_vanilla_target(moves):
    assert moves['counter'].target == 'scripted'
