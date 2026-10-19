import pytest

from porydex.decomp.items import load_items, load_placed_items

VANILLA_ITEMS = {
    'masterball': {'name': 'Master Ball', 'spritenum': 276, 'isNonstandard': 'Past'},
    'abomasite': {
        'name': 'Abomasite',
        'spritenum': 575,
        'megaStone': 'Abomasnow-Mega',
        'megaEvolves': 'Abomasnow',
        'itemUser': ['Abomasnow'],
        'isNonstandard': 'Past',
    },
}

@pytest.fixture
def items(decomp):
    return load_items(decomp, VANILLA_ITEMS)

def test_load_items_skips_none_and_sentinel(items):
    assert list(items) == ['masterball', 'potion', 'oranberry', 'abomasite', 'xspatk']

def test_pokeball_from_pocket_with_vanilla_sprite(items):
    assert items['masterball'].to_showdown() == {
        'num': 1,
        'name': 'Master Ball',
        'spritenum': 276,
        'desc': 'The best Poké Ball with the ultimate level of performance.',
        'shortDesc': 'The best Poké Ball with the ultimate level of performance.',
        'isPokeball': True,
    }

def test_fling_and_natural_gift_from_csv(items):
    showdown = items['oranberry'].to_showdown()
    assert showdown['fling'] == {'basePower': 10}
    assert showdown['naturalGift'] == {'basePower': 80, 'type': 'Poison'}

def test_non_battle_item_has_no_vanilla_fields(items):
    assert items['potion'].to_showdown() == {
        'num': 2,
        'name': 'Potion',
        'spritenum': 0,
        'desc': 'Restores 20 HP.',
        'shortDesc': 'Restores 20 HP.',
        'fling': {'basePower': 30},
    }

def test_mega_stone_fields_from_vanilla(items):
    showdown = items['abomasite'].to_showdown()
    assert showdown['megaStone'] == 'Abomasnow-Mega'
    assert showdown['megaEvolves'] == 'Abomasnow'
    assert showdown['itemUser'] == ['Abomasnow']
    assert 'isNonstandard' not in showdown

def test_item_missing_from_csv_and_placeholder_description(items):
    assert items['xspatk'].to_showdown() == {
        'num': 5,
        'name': 'X Sp. Atk',
        'spritenum': 0,
        'desc': '',
        'shortDesc': '',
    }

def test_placed_items_come_from_field_scripts_and_bp_store_ignoring_comments(decomp):
    assert load_placed_items(decomp) == {'ITEM_ORAN_BERRY', 'ITEM_MASTER_BALL'}

def test_items_carry_placed_flag(items):
    assert items['oranberry'].placed
    assert items['masterball'].placed
    assert not items['abomasite'].placed
