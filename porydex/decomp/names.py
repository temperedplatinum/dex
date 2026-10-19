import dataclasses

from porydex.common import name_key

MOVE_OVERRIDES: dict[str, str] = {
    'MOVE_FAINT_ATTACK': 'Feint Attack',
    'MOVE_HI_JUMP_KICK': 'High Jump Kick',
    'MOVE_SMELLING_SALT': 'Smelling Salts',
}

ITEM_OVERRIDES: dict[str, str] = {
    'ITEM_PARLYZ_HEAL': 'Paralyze Heal',
    'ITEM_X_DEFENSE': 'X Defense',
    'ITEM_X_SPECIAL': 'X Sp. Atk',
    'ITEM_ENERGYPOWDER': 'Energy Powder',
    'ITEM_TINYMUSHROOM': 'Tiny Mushroom',
    'ITEM_SECRETPOTION': 'Secret Potion',
}

SPECIES_OVERRIDES: dict[str, str] = {
    'NIDORAN♀': 'Nidoran-F',
    'NIDORAN♂': 'Nidoran-M',
    'FARFETCH’D': 'Farfetch’d',
}

HIDDEN_POWER_PREFIX = 'MOVE_HP_'

@dataclasses.dataclass(frozen=True)
class ShowdownName:
    key: str
    name: str

def _resolve(preferred: str, constant_suffix: str, vanilla: dict[str, dict]) -> ShowdownName:
    for key in (name_key(preferred), name_key(constant_suffix)):
        if key in vanilla:
            return ShowdownName(key, vanilla[key]['name'])
    return ShowdownName(name_key(preferred), preferred)

def _hidden_power(constant: str) -> str | None:
    if not constant.startswith(HIDDEN_POWER_PREFIX):
        return None
    return f'Hidden Power {constant.removeprefix(HIDDEN_POWER_PREFIX).title()}'

def resolve_move(constant: str, game_name: str, vanilla: dict[str, dict]) -> ShowdownName:
    preferred = MOVE_OVERRIDES.get(constant) or _hidden_power(constant) or game_name
    return _resolve(preferred, constant.removeprefix('MOVE_'), vanilla)

def resolve_ability(constant: str, game_name: str, vanilla: dict[str, dict]) -> ShowdownName:
    return _resolve(game_name, constant.removeprefix('ABILITY_'), vanilla)

def resolve_item(constant: str, game_name: str, vanilla: dict[str, dict]) -> ShowdownName:
    preferred = ITEM_OVERRIDES.get(constant, game_name)
    return _resolve(preferred, constant.removeprefix('ITEM_'), vanilla)

def resolve_species(game_name: str) -> ShowdownName:
    name = SPECIES_OVERRIDES.get(game_name, game_name.title())
    return ShowdownName(name_key(name), name)

def forme_name(form_dir: str) -> str:
    return '-'.join(word.title() for word in form_dir.split('_'))
