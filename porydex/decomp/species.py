import dataclasses
import pathlib

from porydex.common import name_key
from porydex.decomp.abilities import Ability
from porydex.decomp.enums import showdown_color, showdown_egg_groups, showdown_gender, showdown_types
from porydex.decomp.items import Item
from porydex.decomp.learnsets import load_gift_egg_species, load_tm_moves, parse_learnset
from porydex.decomp.loaders import load_constants, load_json
from porydex.decomp.moves import Move
from porydex.decomp.names import forme_name, resolve_species

STAT_KEYS: dict[str, str] = {
    'hp': 'hp',
    'attack': 'atk',
    'defense': 'def',
    'special_attack': 'spa',
    'special_defense': 'spd',
    'speed': 'spe',
}

SKIPPED_SPECIES: frozenset[str] = frozenset({'SPECIES_NONE', 'SPECIES_EGG', 'SPECIES_BAD_EGG'})

UNOBTAINABLE_SPECIES: frozenset[str] = frozenset({
    'Chansey', 'Mewtwo', 'Mew',
    'Blissey', 'Lugia', 'Ho-Oh', 'Celebi',
    'Slakoth', 'Vigoroth', 'Slaking', 'Nincada', 'Shedinja', 'Kyogre', 'Groudon', 'Rayquaza', 'Jirachi',
    'Deoxys', 'Deoxys-Attack', 'Deoxys-Defense', 'Deoxys-Speed',
    'Happiny', 'Dialga', 'Palkia', 'Heatran', 'Regigigas', 'Giratina', 'Manaphy', 'Darkrai', 'Shaymin', 'Arceus',
})

BASE_FORMES: dict[str, str] = {
    'deoxys': 'Normal',
    'burmy': 'Plant',
    'wormadam': 'Plant',
    'shellos': 'West',
    'gastrodon': 'West',
    'giratina': 'Altered',
    'shaymin': 'Land',
    'cherrim': 'Overcast',
    'arceus': 'Normal',
}

COSMETIC_FORME_NAMES: dict[tuple[str, str], str] = {
    ('unown', 'exc'): 'Exclamation',
    ('unown', 'que'): 'Question',
    ('shellos', 'east_sea'): 'East',
    ('gastrodon', 'east_sea'): 'East',
    ('cherrim', 'sunny'): 'Sunshine',
    ('arceus', 'mystery'): 'Fairy',
}

@dataclasses.dataclass(frozen=True)
class EvoMethod:
    type: str
    condition: str = ''

EVO_METHODS: dict[str, EvoMethod] = {
    'EVO_LEVEL_HAPPINESS': EvoMethod('levelFriendship'),
    'EVO_LEVEL_HAPPINESS_DAY': EvoMethod('levelFriendship', 'during the day'),
    'EVO_LEVEL_HAPPINESS_NIGHT': EvoMethod('levelFriendship', 'at night'),
    'EVO_LEVEL': EvoMethod('level'),
    'EVO_TRADE': EvoMethod('trade'),
    'EVO_TRADE_WITH_HELD_ITEM': EvoMethod('tradeItem', 'while holding'),
    'EVO_USE_ITEM': EvoMethod('useItem'),
    'EVO_LEVEL_ATK_GT_DEF': EvoMethod('level', 'with more Attack than Defense'),
    'EVO_LEVEL_ATK_EQ_DEF': EvoMethod('level', 'with equal Attack and Defense'),
    'EVO_LEVEL_ATK_LT_DEF': EvoMethod('level', 'with more Defense than Attack'),
    'EVO_LEVEL_PID_LOW': EvoMethod('level', 'based on personality'),
    'EVO_LEVEL_PID_HIGH': EvoMethod('level', 'based on personality'),
    'EVO_LEVEL_NINJASK': EvoMethod('level'),
    'EVO_LEVEL_SHEDINJA': EvoMethod('level', 'with an empty party slot and a spare Poké Ball'),
    'EVO_LEVEL_BEAUTY': EvoMethod('levelExtra', 'with maximum Beauty'),
    'EVO_USE_ITEM_MALE': EvoMethod('useItem', 'if Male'),
    'EVO_USE_ITEM_FEMALE': EvoMethod('useItem', 'if Female'),
    'EVO_LEVEL_WITH_HELD_ITEM_DAY': EvoMethod('levelHold', 'during the day'),
    'EVO_LEVEL_WITH_HELD_ITEM_NIGHT': EvoMethod('levelHold', 'at night'),
    'EVO_LEVEL_KNOW_MOVE': EvoMethod('levelMove'),
    'EVO_LEVEL_SPECIES_IN_PARTY': EvoMethod('levelParty'),
    'EVO_LEVEL_MALE': EvoMethod('level', 'if Male'),
    'EVO_LEVEL_FEMALE': EvoMethod('level', 'if Female'),
    'EVO_LEVEL_MAGNETIC_FIELD': EvoMethod('levelExtra', 'in a special magnetic field'),
    'EVO_LEVEL_MOSS_ROCK': EvoMethod('levelExtra', 'near a Moss Rock'),
    'EVO_LEVEL_ICE_ROCK': EvoMethod('levelExtra', 'near an Ice Rock'),
}

@dataclasses.dataclass(frozen=True)
class Evolution:
    method: EvoMethod
    target: str
    level: int = 0
    item: str | None = None
    move: str | None = None
    party_species: str | None = None

@dataclasses.dataclass(frozen=True)
class Species:
    key: str
    constant: str
    num: int
    name: str
    types: tuple[str, ...]
    base_stats: dict[str, int]
    abilities: dict[str, str]
    height_m: float
    weight_kg: float
    color: str
    egg_groups: tuple[str, ...]
    gender: dict
    catch_rate: int = 0
    evolutions: tuple[Evolution, ...] = ()
    learnset: dict[str, list[str]] | None = None
    base_species: str | None = None
    forme: str | None = None
    base_forme: str | None = None
    other_formes: tuple[str, ...] = ()
    cosmetic_formes: tuple[str, ...] = ()
    required_item: str | None = None
    obtainable: bool = True
    sprite: pathlib.Path | None = None

    def to_showdown(self) -> dict:
        mon: dict = {
            'num': self.num,
            'name': self.name,
            'types': list(self.types),
            'baseStats': self.base_stats,
            'abilities': self.abilities,
            'heightm': self.height_m,
            'weightkg': self.weight_kg,
            'color': self.color,
            'eggGroups': list(self.egg_groups),
            **self.gender,
        }
        if self.catch_rate:
            mon['catchRate'] = self.catch_rate
        if self.base_species:
            mon['baseSpecies'] = self.base_species
            mon['forme'] = self.forme
        if self.base_forme:
            mon['baseForme'] = self.base_forme
        if self.other_formes:
            mon['otherFormes'] = list(self.other_formes)
        if self.cosmetic_formes:
            mon['cosmeticFormes'] = list(self.cosmetic_formes)
        if self.required_item:
            mon['requiredItem'] = self.required_item
            mon['battleOnly'] = self.base_species
        mon['tier'] = 'obtainable' if self.obtainable else 'unobtainable'
        return mon

@dataclasses.dataclass(frozen=True)
class _Lookups:
    ability_names: dict[str, str]
    item_names: dict[str, str]
    move_keys: dict[str, str]
    move_names: dict[str, str]
    mega_stones: dict[str, str]
    unplaced_stones: frozenset[str]
    tm_moves: dict[str, str]
    egg_species: frozenset[str] = frozenset()

def _abilities(constants: list[str], names: dict[str, str]) -> dict[str, str]:
    slots: dict[str, str] = {}
    for slot, constant in zip(('0', '1', 'H'), constants):
        name = names.get(constant)
        if name and (slot == 'H' or name not in slots.values()):
            slots[slot] = name
    return slots

def _evolution(entry: list, lookups: _Lookups) -> Evolution:
    method, *params, target = entry
    if method not in EVO_METHODS:
        raise ValueError(f'unrecognized evolution method: {method}')

    fields: dict = {}
    for param in params:
        if isinstance(param, int):
            fields['level'] = param
        elif param.startswith('ITEM_'):
            fields['item'] = lookups.item_names[param]
        elif param.startswith('MOVE_'):
            fields['move'] = lookups.move_names[param]
        elif param.startswith('SPECIES_'):
            fields['party_species'] = param
    return Evolution(EVO_METHODS[method], target, **fields)

def _species(constant: str,
             num: int,
             name: str,
             data: dict,
             height_m: float,
             weight_kg: float,
             lookups: _Lookups,
             **formes) -> Species:
    is_mega = bool(formes.get('required_item'))
    return Species(
        key=name_key(name),
        constant=constant,
        num=num,
        name=name,
        types=tuple(showdown_types(data['types'])),
        base_stats={STAT_KEYS[stat]: value for stat, value in data['base_stats'].items()},
        abilities=_abilities(data['abilities'], lookups.ability_names),
        height_m=height_m,
        weight_kg=weight_kg,
        color=showdown_color(data['body_color']),
        egg_groups=tuple(showdown_egg_groups(data['egg_groups'])),
        gender=showdown_gender(data['gender_ratio']),
        catch_rate=data.get('catch_rate', 0),
        evolutions=tuple(_evolution(entry, lookups) for entry in data.get('evolutions', [])),
        learnset=None if is_mega else parse_learnset(
            data['learnset'],
            lookups.tm_moves,
            lookups.move_keys,
            include_egg_moves=constant in lookups.egg_species,
        ),
        **formes,
    )

def _form_dirs(mon_dir: pathlib.Path, registry: dict[str, str]) -> list[str]:
    data_forms = [form for form, kind in registry.items() if kind == 'data']
    megas = sorted(p.parent.name for p in mon_dir.glob(f'forms/mega*/data.json'))
    return data_forms + megas

def _cosmetic_formes(species_dir: str, base_name: str, registry: dict[str, str]) -> tuple[str, ...]:
    return tuple(
        f'{base_name}-{COSMETIC_FORME_NAMES.get((species_dir, form), forme_name(form))}'
        for form, kind in registry.items()
        if kind != 'data' and not form.startswith("__")
    )

def _first_existing(*paths: pathlib.Path) -> pathlib.Path | None:
    return next((path for path in paths if path.exists()), None)

def load_species(decomp: pathlib.Path,
                 moves: dict[str, Move],
                 abilities: dict[str, Ability],
                 items: dict[str, Item],
                 unobtainable: frozenset[str] = frozenset()) -> dict[str, Species]:
    lookups = _Lookups(
        ability_names={a.constant: a.name for a in abilities.values()},
        item_names={i.constant: i.name for i in items.values()},
        move_keys={m.constant: m.key for m in moves.values()},
        move_names={m.constant: m.name for m in moves.values()},
        mega_stones={i.mega_stone: i.name for i in items.values() if i.mega_stone},
        unplaced_stones=frozenset(i.name for i in items.values() if i.mega_stone and not i.placed),
        tm_moves=load_tm_moves(decomp),
        egg_species=load_gift_egg_species(decomp),
    )
    registry = load_json(decomp / 'res' / 'pokemon' / 'form_registry.json')

    species: dict[str, Species] = {}
    for num, constant in enumerate(load_constants(decomp, 'species')):
        if constant in SKIPPED_SPECIES:
            continue

        species_dir = constant.removeprefix('SPECIES_').lower()
        mon_dir = decomp / 'res' / 'pokemon' / species_dir
        data = load_json(mon_dir / 'data.json')
        dex = data['pokedex_data']
        name = resolve_species(dex['en']['name']).name
        height_m = round(dex['height_inches'] * 0.0254, 1)
        weight_kg = round(dex['weight_pounds'] * 0.45359237, 1)
        mon_registry = registry.get(species_dir, {})

        forms = {
            f'{name}-{forme_name(form)}': (form, load_json(mon_dir / 'forms' / form / 'data.json'))
            for form in _form_dirs(mon_dir, mon_registry)
        }

        base_obtainable = name not in unobtainable
        base = _species(constant, num, name, data, height_m, weight_kg, lookups,
                        obtainable=base_obtainable,
                        base_forme=BASE_FORMES.get(species_dir),
                        other_formes=tuple(forms),
                        cosmetic_formes=_cosmetic_formes(species_dir, name, mon_registry),
                        sprite=_first_existing(mon_dir / 'male_front.png', mon_dir / 'female_front.png'))
        species[base.key] = base

        for form_name, (form, form_data) in forms.items():
            required_item = lookups.mega_stones.get(form_name)
            mon = _species(f'{constant}_{form.upper()}', num, form_name, form_data, height_m, weight_kg, lookups,
                           base_species=name,
                           forme=forme_name(form),
                           required_item=required_item,
                           obtainable=base_obtainable
                               and form_name not in unobtainable
                               and required_item not in lookups.unplaced_stones,
                           sprite=_first_existing(mon_dir / 'forms' / form / 'front.png'))
            species[mon.key] = mon

    unknown = unobtainable - {mon.name for mon in species.values()}
    if unknown:
        raise ValueError(f'unobtainable species not found in decomp: {sorted(unknown)}')
    return species

def _evolution_fields(evolution: Evolution, prevo: str, species_names: dict[str, str]) -> dict:
    fields: dict = {'prevo': prevo, 'evoType': evolution.method.type}
    if evolution.level:
        fields['evoLevel'] = evolution.level
    if evolution.item:
        fields['evoItem'] = evolution.item
    if evolution.move:
        fields['evoMove'] = evolution.move
    if evolution.party_species:
        fields['evoSpecies'] = species_names[evolution.party_species]
    if evolution.method.condition:
        fields['evoCondition'] = evolution.method.condition
    return fields

def species_to_showdown(species: dict[str, Species]) -> dict[str, dict]:
    showdown = {key: mon.to_showdown() for key, mon in species.items()}
    base_by_constant = {mon.constant: mon for mon in species.values() if not mon.base_species}
    species_names = {constant: mon.name for constant, mon in base_by_constant.items()}

    for mon in species.values():
        for evolution in mon.evolutions:
            target = base_by_constant[evolution.target]
            evos = showdown[mon.key].setdefault('evos', [])
            if target.name in evos:
                continue
            evos.append(target.name)
            showdown[target.key].update(_evolution_fields(evolution, mon.name, species_names))

    return showdown

def learnsets_to_showdown(species: dict[str, Species]) -> dict[str, dict]:
    return {
        key: {'learnset': mon.learnset}
        for key, mon in species.items()
        if mon.learnset is not None
    }
