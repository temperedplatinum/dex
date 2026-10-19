import dataclasses
import pathlib

from porydex.decomp.c_tables import parse_constant_table
from porydex.decomp.enums import showdown_category, showdown_contest_type, showdown_type
from porydex.decomp.loaders import load_constants, load_json, load_text_bank
from porydex.decomp.names import resolve_move

JSON_FLAGS: dict[str, str] = {
    'MOVE_FLAG_MAKES_CONTACT': 'contact',
    'MOVE_FLAG_CAN_PROTECT': 'protect',
    'MOVE_FLAG_CAN_MAGIC_COAT': 'reflectable',
    'MOVE_FLAG_CAN_SNATCH': 'snatch',
    'MOVE_FLAG_CAN_MIRROR_MOVE': 'mirror',
}

C_FLAG_TABLES: dict[tuple[str, str], str] = {
    ('src/battle/battle_lib.c', 'sSoundMoves'): 'sound',
    ('src/battle/battle_lib.c', 'sWindMoves'): 'wind',
    ('src/battle/battle_lib.c', 'sJawMoves'): 'bite',
    ('src/battle/battle_lib.c', 'sSlicingMoves'): 'slicing',
    ('src/battle/battle_lib.c', 'sPunchingMoves'): 'punch',
    ('src/battle/battle_lib.c', 'sAuraAndPulseMoves'): 'pulse',
    ('src/battle/battle_script.c', 'sPowderMoves'): 'powder',
}

TARGETS: dict[str, str] = {
    'RANGE_SINGLE_TARGET': 'normal',
    'RANGE_RANDOM_OPPONENT': 'randomNormal',
    'RANGE_ADJACENT_OPPONENTS': 'allAdjacentFoes',
    'RANGE_ALL_ADJACENT': 'allAdjacent',
    'RANGE_USER': 'self',
    'RANGE_USER_SIDE': 'allySide',
    'RANGE_FIELD': 'all',
    'RANGE_OPPONENT_SIDE': 'foeSide',
    'RANGE_ALLY': 'adjacentAlly',
    'RANGE_USER_OR_ALLY': 'adjacentAllyOrSelf',
    'RANGE_SINGLE_TARGET_ME_FIRST': 'adjacentFoe',
    'RANGE_ALL': 'all',
}

ENGINE_DECIDED_RANGE = 'RANGE_SINGLE_TARGET_SPECIAL'

HIGH_CRIT_EFFECTS: frozenset[str] = frozenset({
    'BATTLE_EFFECT_HIGH_CRITICAL',
    'BATTLE_EFFECT_HIGH_CRITICAL_BURN_HIT',
    'BATTLE_EFFECT_HIGH_CRITICAL_POISON_HIT',
    'BATTLE_EFFECT_CHARGE_TURN_HIGH_CRIT',
    'BATTLE_EFFECT_CHARGE_TURN_HIGH_CRIT_FLINCH',
})

ALWAYS_CRIT_EFFECT = 'BATTLE_EFFECT_ALWAYS_CRIT'

@dataclasses.dataclass(frozen=True)
class Move:
    key: str
    num: int
    name: str
    type: str
    category: str
    base_power: int
    accuracy: int | bool
    pp: int
    priority: int
    target: str
    flags: frozenset[str]
    contest_type: str
    description: str
    crit_ratio: int = 1
    will_crit: bool = False

    def to_showdown(self) -> dict:
        move = {
            'num': self.num,
            'name': self.name,
            'type': self.type,
            'category': self.category,
            'basePower': self.base_power,
            'accuracy': self.accuracy,
            'pp': self.pp,
            'priority': self.priority,
            'target': self.target,
            'flags': {flag: 1 for flag in sorted(self.flags)},
            'contestType': self.contest_type,
            'desc': self.description,
            'shortDesc': self.description,
        }
        if self.crit_ratio > 1:
            move['critRatio'] = self.crit_ratio
        if self.will_crit:
            move['willCrit'] = True
        return move

def _load_c_flags(decomp: pathlib.Path) -> dict[str, set[str]]:
    c_flags: dict[str, set[str]] = {}
    for (source, table), flag in C_FLAG_TABLES.items():
        for constant in parse_constant_table(decomp / source, table, 'MOVE_'):
            c_flags.setdefault(constant, set()).add(flag)
    return c_flags

def _target(move_range: str, vanilla_move: dict | None) -> str:
    if move_range == ENGINE_DECIDED_RANGE:
        return (vanilla_move or {}).get('target', 'normal')
    return TARGETS[move_range]

def _parse_move(num: int,
                constant: str,
                data: dict,
                description: str,
                c_flags: set[str],
                vanilla: dict[str, dict]) -> Move:
    resolved = resolve_move(constant, data['name'], vanilla)
    effect = data['effect']['type']
    return Move(
        key=resolved.key,
        num=num,
        name=resolved.name,
        type=showdown_type(data['type']),
        category=showdown_category(data['class']),
        base_power=data['power'],
        accuracy=data['accuracy'] or True,
        pp=data['pp'],
        priority=data['priority'],
        target=_target(data['range'], vanilla.get(resolved.key)),
        flags=frozenset({JSON_FLAGS[f] for f in data['flags'] if f in JSON_FLAGS} | c_flags),
        contest_type=showdown_contest_type(data['contest']['type']),
        description=description,
        crit_ratio=2 if effect in HIGH_CRIT_EFFECTS else 1,
        will_crit=effect == ALWAYS_CRIT_EFFECT,
    )

def load_moves(decomp: pathlib.Path, vanilla: dict[str, dict]) -> dict[str, Move]:
    descriptions = load_text_bank(decomp, 'move_descriptions')
    c_flags = _load_c_flags(decomp)
    moves: dict[str, Move] = {}
    for num, constant in enumerate(load_constants(decomp, 'moves')):
        path = decomp / 'res' / 'battle' / 'moves' / constant.removeprefix('MOVE_').lower() / 'data.json'
        if constant == 'MOVE_NONE' or not path.exists():
            continue
        move = _parse_move(num, constant, load_json(path), descriptions[num], c_flags.get(constant, set()), vanilla)
        moves[move.key] = move
    return moves
