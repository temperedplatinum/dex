import pytest

from porydex.decomp.c_tables import parse_constant_table

def test_parse_constant_table_ignores_comments(decomp):
    path = decomp / 'src' / 'battle' / 'battle_lib.c'
    assert parse_constant_table(path, 'sSoundMoves', 'MOVE_') == ['MOVE_GROWL']
    assert parse_constant_table(path, 'sJawMoves', 'MOVE_') == ['MOVE_BITE']

def test_parse_constant_table_handles_const_and_no_trailing_comma(decomp):
    path = decomp / 'src' / 'battle' / 'battle_lib.c'
    assert parse_constant_table(path, 'sAuraAndPulseMoves', 'MOVE_') == ['MOVE_WATER_PULSE', 'MOVE_AURA_SPHERE']

def test_parse_constant_table_rejects_missing_table(decomp):
    with pytest.raises(ValueError):
        parse_constant_table(decomp / 'src' / 'battle' / 'battle_lib.c', 'sMissingMoves', 'MOVE_')
