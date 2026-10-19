import argparse
import json
import pathlib

import porydex.config
import porydex.showdown

from porydex.decomp.abilities import load_abilities
from porydex.decomp.encounters import LOCATION_ORDER, load_encounters
from porydex.decomp.items import load_items
from porydex.decomp.loaders import load_json
from porydex.decomp.moves import load_moves
from porydex.decomp.species import (
    UNOBTAINABLE_SPECIES,
    learnsets_to_showdown,
    load_species,
    species_to_showdown,
)
from porydex.decomp.sprites import export_sprites

VANILLA_DIR = pathlib.Path('vanilla')

def config_show(_):
    porydex.config.load()
    print(f'path to decomp:    {str(porydex.config.decomp)}')
    print(f'output directory:  {str(porydex.config.output)}')
    print(f'output format:     {str(porydex.config.format)}')

def config_set(args):
    porydex.config.load()
    update = False

    if args.decomp:
        assert args.decomp.resolve().exists(), f'specified decomp directory {args.decomp} does not exist'
        porydex.config.decomp = args.decomp.resolve()
        update = True

    if args.output:
        porydex.config.output = args.output.resolve()
        update = True

    if args.format:
        porydex.config.format = args.format
        update = True

    if update:
        porydex.config.save()
    else:
        print('No config options given; nothing to do')

def config_clear(_):
    porydex.config.clear()

def extract(_):
    porydex.config.load()
    porydex.config.output.mkdir(parents=True, exist_ok=True)

    decomp = porydex.config.decomp
    vanilla = {name: load_json(VANILLA_DIR / f'{name}.json') for name in ('moves', 'abilities', 'items')}
    moves = load_moves(decomp, vanilla['moves'])
    abilities = load_abilities(decomp, vanilla['abilities'])
    items = load_items(decomp, vanilla['items'])
    species = load_species(decomp, moves, abilities, items, UNOBTAINABLE_SPECIES)

    data = {
        'moves': {key: moves[key].to_showdown() for key in sorted(moves)},
        'species': species_to_showdown(species),
        'learnsets': learnsets_to_showdown(species),
        'encounters': {
            key: location.to_showdown()
            for key, location in load_encounters(decomp, species, LOCATION_ORDER).items()
        },
        'abilities': {key: ability.to_showdown() for key, ability in abilities.items()},
        'items': {key: item.to_showdown() for key, item in items.items()},
    }

    if porydex.config.format == porydex.config.OutputFormat.json:
        for name, contents in data.items():
            with open(porydex.config.output / f'{name}.json', 'w', encoding='utf-8') as outf:
                json.dump(contents, outf, indent=4, ensure_ascii=False)
    else:
        porydex.showdown.index(**data)
        export_sprites(species, porydex.config.output.parent / 'sprites')

def main():
    argp = argparse.ArgumentParser(prog='porydex',
                                   description='generate data exports from a pokeplatinum decomp for showdown dex')
    subp = argp.add_subparsers(required=True)

    config_p = subp.add_parser('config', help='configuration options for porydex')
    config_subp = config_p.add_subparsers(required=True)

    config_show_p = config_subp.add_parser('show', help='show configured options for porydex')
    config_show_p.set_defaults(func=config_show)

    config_set_p = config_subp.add_parser('set', help='set configurable options for porydex')
    config_set_p.add_argument('-d', '--decomp', action='store',
                              help='path to the root of your pokeplatinum decomp repository; default: ../plat-hack-decomp',
                              type=pathlib.Path)
    config_set_p.add_argument('-o', '--output', action='store',
                              help='path to output directory for extracted data files; default: ./site/data',
                              type=pathlib.Path)
    config_set_p.add_argument('-f', '--format',
                              help='format for output files',
                              type=porydex.config.OutputFormat.argparse,
                              choices=list(porydex.config.OutputFormat))
    config_set_p.set_defaults(func=config_set)

    config_clear_p = config_subp.add_parser('clear', help='clear configured options')
    config_clear_p.set_defaults(func=config_clear)

    extract_p = subp.add_parser('extract', help='run data extraction')
    extract_p.set_defaults(func=extract)

    args = argp.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
