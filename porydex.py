import argparse
import pathlib

import porydex.config

def config_show(_):
    porydex.config.load()
    print(f'path to decomp:    {str(porydex.config.decomp)}')
    print(f'output directory:  {str(porydex.config.output)}')
    print(f'output format:     {str(porydex.config.format)}')
    print(f'include mons file: {str(porydex.config.included_mons_file)}')
    print(f'custom abilities:  {str(porydex.config.custom_ability_defs)}')

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

    if args.included_species_file:
        porydex.config.included_mons_file = args.included_species_file
        update = True

    if args.custom_ability_defs:
        porydex.config.custom_ability_defs = args.custom_ability_defs
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
    raise SystemExit('extraction from the decomp is not implemented yet')

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
    config_set_p.add_argument('-i', '--included-species-file',
                              help='text file describing species to be included in the pokedex',
                              type=pathlib.Path)
    config_set_p.add_argument('-a', '--custom-ability-defs',
                              help='JSON file describing custom ability definitions and descriptions for a Showdown Dex',
                              type=pathlib.Path)
    config_set_p.set_defaults(func=config_set)

    config_clear_p = config_subp.add_parser('clear', help='clear configured options')
    config_clear_p.set_defaults(func=config_clear)

    extract_p = subp.add_parser('extract', help='run data extraction')
    extract_p.set_defaults(func=extract)

    args = argp.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
