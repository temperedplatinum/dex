import pytest

from porydex.decomp.names import (
    ShowdownName,
    forme_name,
    resolve_ability,
    resolve_item,
    resolve_move,
    resolve_species,
)

VANILLA_MOVES = {
    'doubleslap': {'name': 'Double Slap'},
    'feintattack': {'name': 'Feint Attack'},
    'paraboliccharge': {'name': 'Parabolic Charge'},
    'hiddenpowerbug': {'name': 'Hidden Power Bug'},
}

VANILLA_ABILITIES = {
    'electromorphosis': {'name': 'Electromorphosis'},
}

VANILLA_ITEMS = {
    'brightpowder': {'name': 'Bright Powder'},
}

@pytest.mark.parametrize('constant, game_name, expected', [
    ('MOVE_DOUBLESLAP', 'DoubleSlap', ShowdownName('doubleslap', 'Double Slap')),
    ('MOVE_FAINT_ATTACK', 'Faint Attack', ShowdownName('feintattack', 'Feint Attack')),
    ('MOVE_PARABOLIC_CHARGE', 'ParabolcChrge', ShowdownName('paraboliccharge', 'Parabolic Charge')),
    ('MOVE_HP_BUG', 'HP Bug', ShowdownName('hiddenpowerbug', 'Hidden Power Bug')),
    ('MOVE_HP_FAIRY', 'HP Fairy', ShowdownName('hiddenpowerfairy', 'Hidden Power Fairy')),
])
def test_resolve_move(constant, game_name, expected):
    assert resolve_move(constant, game_name, VANILLA_MOVES) == expected

@pytest.mark.parametrize('constant, game_name, expected', [
    ('ABILITY_ELECTROMORPHOSIS', 'Electromorphsis', ShowdownName('electromorphosis', 'Electromorphosis')),
    ('ABILITY_MEGA_SOL', 'Mega Sol', ShowdownName('megasol', 'Mega Sol')),
])
def test_resolve_ability(constant, game_name, expected):
    assert resolve_ability(constant, game_name, VANILLA_ABILITIES) == expected

@pytest.mark.parametrize('constant, game_name, expected', [
    ('ITEM_BRIGHTPOWDER', 'BrightPowder', ShowdownName('brightpowder', 'Bright Powder')),
    ('ITEM_PARLYZ_HEAL', 'Parlyz Heal', ShowdownName('paralyzeheal', 'Paralyze Heal')),
    ('ITEM_X_SPECIAL', 'X Special', ShowdownName('xspatk', 'X Sp. Atk')),
    ('ITEM_POKE_RADAR', 'Poké Radar', ShowdownName('pokeradar', 'Poké Radar')),
])
def test_resolve_item(constant, game_name, expected):
    assert resolve_item(constant, game_name, VANILLA_ITEMS) == expected

@pytest.mark.parametrize('game_name, expected', [
    ('BULBASAUR', ShowdownName('bulbasaur', 'Bulbasaur')),
    ('MR. MIME', ShowdownName('mrmime', 'Mr. Mime')),
    ('HO-OH', ShowdownName('hooh', 'Ho-Oh')),
    ('PORYGON-Z', ShowdownName('porygonz', 'Porygon-Z')),
    ('MIME JR.', ShowdownName('mimejr', 'Mime Jr.')),
    ('NIDORAN♀', ShowdownName('nidoranf', 'Nidoran-F')),
    ('FARFETCH’D', ShowdownName('farfetchd', 'Farfetch’d')),
])
def test_resolve_species(game_name, expected):
    assert resolve_species(game_name) == expected

@pytest.mark.parametrize('form_dir, expected', [
    ('mega', 'Mega'),
    ('mega_x', 'Mega-X'),
    ('mega_z', 'Mega-Z'),
    ('wash', 'Wash'),
])
def test_forme_name(form_dir, expected):
    assert forme_name(form_dir) == expected
