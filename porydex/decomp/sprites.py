import pathlib

from PIL import Image

from porydex.decomp.species import Species

FRAME_SIZE = 80
CANVAS_SIZE = 96
FRAME_OFFSET = ((CANVAS_SIZE - FRAME_SIZE) // 2, CANVAS_SIZE - FRAME_SIZE)
TRANSPARENT_INDEX = 0

def export_sprite(source: pathlib.Path, destination: pathlib.Path):
    with Image.open(source) as sheet:
        frame = sheet.crop((0, 0, FRAME_SIZE, FRAME_SIZE))
        canvas = Image.new('P', (CANVAS_SIZE, CANVAS_SIZE), TRANSPARENT_INDEX)
        canvas.putpalette(sheet.getpalette())
        canvas.paste(frame, FRAME_OFFSET)
        canvas.save(destination, 'PNG', optimize=True, transparency=TRANSPARENT_INDEX)

def export_sprites(species: dict[str, Species], output: pathlib.Path) -> int:
    output.mkdir(parents=True, exist_ok=True)
    for stale in output.glob('*.png'):
        stale.unlink()

    exported = 0
    for key, mon in species.items():
        if mon.sprite:
            export_sprite(mon.sprite, output / f'{key}.png')
            exported += 1
    return exported
