import pytest
from PIL import Image

from porydex.decomp.abilities import load_abilities
from porydex.decomp.items import load_items
from porydex.decomp.moves import load_moves
from porydex.decomp.species import load_species
from porydex.decomp.sprites import export_sprites

@pytest.fixture
def species(decomp):
    return load_species(decomp, load_moves(decomp, {}), load_abilities(decomp, {}), load_items(decomp, {}))

def test_sprite_sources_prefer_male_then_female_then_form(species):
    assert species['bulbasaur'].sprite.name == 'male_front.png'
    assert species['ivysaur'].sprite.name == 'female_front.png'
    assert species['abomasnowmega'].sprite.parts[-3:] == ('forms', 'mega', 'front.png')
    assert species['rotom'].sprite is None
    assert species['shellos'].sprite is None

def test_export_writes_one_sprite_per_species_with_a_source(species, tmp_path):
    (tmp_path / 'stale.png').write_bytes(b'')
    assert export_sprites(species, tmp_path) == 5
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        'abomasnow.png',
        'abomasnowmega.png',
        'bulbasaur.png',
        'ivysaur.png',
        'rotomwash.png',
    ]

def test_exported_sprite_is_first_frame_on_transparent_canvas(species, tmp_path):
    export_sprites(species, tmp_path)
    with Image.open(tmp_path / 'bulbasaur.png') as sprite:
        assert sprite.size == (96, 96)
        assert sprite.mode == 'P'
        assert sprite.info['transparency'] == 0
        colours = {index for _, index in sprite.getcolors()}
        assert colours == {0, 1}
        assert sprite.getpixel((8 + 30, 16 + 30)) == 1
        assert sprite.getpixel((0, 0)) == 0
