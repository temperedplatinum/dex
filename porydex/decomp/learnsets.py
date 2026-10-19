import pathlib
import re

from porydex.decomp.c_tables import table_body

TM_ENTRY = re.compile(r'\[\s*TMHM_ID\(\s*(\w+)\s*\)\s*\]\s*=\s*(MOVE_\w+)')

def load_tm_moves(decomp: pathlib.Path) -> dict[str, str]:
    return dict(TM_ENTRY.findall(table_body(decomp / 'src' / 'item.c', 'sTMHMMoves')))

def parse_learnset(raw: dict,
                   tm_moves: dict[str, str],
                   move_keys: dict[str, str]) -> dict[str, list[str]]:
    sources = [
        *((move, f'L{level}') for level, move in raw.get('by_level', [])),
        *((tm_moves[tm], 'M') for tm in raw.get('by_tm', [])),
        *((move, 'T') for move in raw.get('by_tutor', [])),
        *((move, 'E') for move in raw.get('egg_moves', [])),
    ]

    learnset: dict[str, list[str]] = {}
    for move, code in sources:
        codes = learnset.setdefault(move_keys[move], [])
        if code not in codes:
            codes.append(code)
    return learnset
