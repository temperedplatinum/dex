import pathlib
import re

from porydex.decomp.c_tables import read_without_comments, table_body

TM_ENTRY = re.compile(r'\[\s*TMHM_ID\(\s*(\w+)\s*\)\s*\]\s*=\s*(MOVE_\w+)')
GIFT_EGG = re.compile(r'\bGiveEgg\s+(SPECIES_\w+)')

def load_tm_moves(decomp: pathlib.Path) -> dict[str, str]:
    return dict(TM_ENTRY.findall(table_body(decomp / 'src' / 'item.c', 'sTMHMMoves')))

def load_gift_egg_species(decomp: pathlib.Path) -> frozenset[str]:
    scripts = (decomp / 'res' / 'field' / 'scripts').glob('*.s')
    return frozenset(species for path in scripts for species in GIFT_EGG.findall(read_without_comments(path)))

def parse_learnset(raw: dict,
                   tm_moves: dict[str, str],
                   move_keys: dict[str, str],
                   include_egg_moves: bool = True) -> dict[str, list[str]]:
    sources = [
        *((move, f'L{level}') for level, move in raw.get('by_level', [])),
        *((tm_moves[tm], 'M') for tm in raw.get('by_tm', [])),
        *((move, 'T') for move in raw.get('by_tutor', [])),
        *((move, 'E') for move in raw.get('egg_moves', []) if include_egg_moves),
    ]

    learnset: dict[str, list[str]] = {}
    for move, code in sources:
        codes = learnset.setdefault(move_keys[move], [])
        if code not in codes:
            codes.append(code)
    return learnset
