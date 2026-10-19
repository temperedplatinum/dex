import dataclasses
import pathlib
import re

from porydex.common import name_key
from porydex.decomp.loaders import load_json, load_text_bank_by_id
from porydex.decomp.species import Species

WILD_ENCOUNTERS_SOURCE = pathlib.Path('src') / 'overlay006' / 'wild_encounters.c'
MAP_HEADERS_SOURCE = pathlib.Path('include') / 'data' / 'map_headers.h'
ENCOUNTERS_DIR = pathlib.Path('res') / 'field' / 'encounters'

SLOT_FUNCTIONS: dict[str, str] = {
    'land': 'GetGroundEncounterSlot',
    'surf': 'GetWaterEncounterSlot',
}

LOCATION_NAME_OVERRIDES: dict[str, str] = {
    'encounters_mt_coronet_1f_north_room_1': 'Mt. Coronet 1F North',
    'encounters_mt_coronet_1f_north_room_2': 'Mt. Coronet 1F North (Route 216 Exit)',
    'encounters_mt_coronet_outside_north': 'Coronet Mountaintop North',
    'encounters_mt_coronet_outside_south': 'Coronet Mountaintop South',
    'encounters_turnback_cave_pillar_1_room_1': '??? Area 1',
    'encounters_turnback_cave_pillar_1_room_2': '??? Area 2',
    'encounters_turnback_cave_pillar_1_room_3': '??? Area 3',
    'encounters_turnback_cave_pillar_1_room_5': '??? Area 4',
    'encounters_route_204_south': 'Route 204',
    'encounters_route_204_north': 'Route 204',
    'encounters_lake_verity': 'Lake Verity',
    'encounters_lake_verity_low_water': 'Lake Verity',
    'encounters_ruin_maniac_cave_short': 'Ruin Maniac Cave',
    'encounters_ruin_maniac_cave_long': 'Ruin Maniac Cave',
    'encounters_maniac_tunnel': 'Ruin Maniac Cave',
    **{
        f'encounters_solaceon_ruins_{room}': 'Solaceon Ruins'
        for room in (
            'maniac_tunnel_room',
            'room_1_northwest_dead_end',
            'room_1_southeast_dead_end',
            'room_2',
            'room_2_northeast_dead_end',
            'room_2_southeast_dead_end',
            'room_3',
            'room_3_northwest_dead_end',
            'room_3_southwest_dead_end',
            'room_4',
            'room_4_southeast_dead_end',
            'room_5',
            'room_5_southwest_dead_end',
            'room_5_southeast_deadend',
            'room_6',
            'room_6_northwest_dead_end',
            'room_6_southeast_dead_end',
            'room_7',
        )
    },
    **{
        f'encounters_great_marsh_{area}': f'Great Marsh Area {first} & {first + 1}'
        for first in (1, 3, 5)
        for area in (first, first + 1)
    },
    **{
        f'encounters_old_chateau{room}': 'Old Chateau'
        for room in (
            '',
            '_dining_area',
            '_side_rooms',
            '_corridor',
            '_back_west_room',
            '_back_middle_west_room',
            '_back_middle_room',
            '_back_middle_east_room',
            '_back_east_room',
        )
    },
}

INACCESSIBLE_LOCATION_FILES: frozenset[str] = frozenset({
    'encounters_turnback_cave_pillar_1_room_4',
    'encounters_turnback_cave_pillar_1_room_6',
    *(f'encounters_turnback_cave_pillar_2_room_{room}' for room in range(1, 7)),
    *(f'encounters_turnback_cave_pillar_3_room_{room}' for room in range(1, 6)),
})

LOCATION_ORDER: tuple[str, ...] = (
    'twinleaftown', 'route201', 'lakeverity', 'sandgemtown', 'route202', 'route203', 'route204',
    'ravagedpath', 'valleywindworks', 'route205south', 'fuegoironworks', 'eternaforest', 'route205north',
    'eternacity', 'route211west', 'mtcoronet1fnorth', 'oldchateau', 'route206', 'route207',
    'mtcoronet1fsouth', 'waywardcave1f', 'waywardcaveb1f', 'oreburghcity', 'oreburghmineb1f',
    'oreburghmineb2f', 'oreburghgate1f', 'oreburghgateb1f', 'route208', 'route209',
    'losttower1f', 'losttower2f', 'losttower3f', 'losttower4f', 'losttower5f', 'solaceonruins',
    'route212north', 'trophygarden', 'route212south', 'pastoriacity',
    'greatmarsharea12', 'greatmarsharea34', 'greatmarsharea56', 'route213', 'valorlakefront', 'route214',
    'sendoffspring', 'turnbackcaveentrance', 'turnbackcavepillarroom', 'turnbackcavegiratinaroom',
    'area1', 'area2', 'area3', 'area4', 'ruinmaniaccave', 'route215', 'route210south', 'route210north',
    'celestictown', 'route211east', 'mtcoronetb1f', 'mtcoronet1fnorthroute216exit', 'route216', 'route217',
    'acuitylakefront', 'snowpointcity', 'snowpointtemple1f', 'snowpointtempleb1f', 'snowpointtempleb2f',
    'snowpointtempleb3f', 'snowpointtempleb4f', 'snowpointtempleb5f', 'fightarea', 'route225',
    'survivalarea', 'route226', 'route227', 'starkmountainoutside', 'starkmountainroom1',
    'starkmountainroom2', 'route228', 'route229', 'resortarea', 'route230', 'route218', 'canalavecity',
    'ironisland', 'ironisland1f', 'ironislandb1fleftroom', 'ironislandb1frightroom', 'ironislandb2fleftroom',
    'ironislandb2frightroom', 'ironislandb3f', 'mtcoronet2f', 'mtcoronet3f', 'coronetmountaintopsouth',
    'mtcoronet4frooms1and2', 'coronetmountaintopnorth', 'mtcoronet1ftunnelroom', 'mtcoronet4froom3',
    'mtcoronet5f', 'mtcoronet6f', 'lakevalor', 'lakeacuity', 'route219', 'route220', 'route221', 'route222',
    'sunyshorecity', 'route223', 'pokemonleague', 'victoryroad1f', 'victoryroad2f', 'victoryroadb1f',
    'victoryroad1froom1', 'victoryroad1froom2', 'victoryroad1froom3', 'route224', 'honeytrees',
)

MAP_HEADER_ENCOUNTERS = re.compile(
    r'\.wildEncountersArchiveID\s*=\s*(encounters_\w+),.*?\.mapLabelTextID\s*=\s*(\w+),',
    re.S,
)

@dataclasses.dataclass(frozen=True)
class EncounterSlot:
    species: str
    min_level: int
    max_level: int
    rate: float

    def to_showdown(self) -> dict:
        return {
            'species': self.species,
            'minLvl': self.min_level,
            'maxLvl': self.max_level,
            'rate': self.rate,
        }

@dataclasses.dataclass(frozen=True)
class Location:
    key: str
    name: str
    methods: dict[str, tuple[EncounterSlot, ...]]

    def to_showdown(self) -> dict:
        return {
            'name': self.name,
            **{method: [slot.to_showdown() for slot in slots] for method, slots in self.methods.items()},
        }

def _function_body(source: str, function: str) -> str:
    match = re.search(rf'\b{function}\([^)]*\)\s*\{{(.*?)\n\}}', source, re.S)
    if not match:
        raise ValueError(f'function {function} not found in {WILD_ENCOUNTERS_SOURCE}')
    return match.group(1)

def _rates_from_thresholds(body: str) -> list[int]:
    thresholds = [int(t) for t in re.findall(r'\broll\s*<\s*(\d+)', body)]
    bounds = [0, *thresholds, 100]
    return [high - low for low, high in zip(bounds, bounds[1:])]

def load_slot_rates(decomp: pathlib.Path) -> dict[str, list[int]]:
    source = (decomp / WILD_ENCOUNTERS_SOURCE).read_text(encoding='utf-8')
    return {method: _rates_from_thresholds(_function_body(source, function)) for method, function in SLOT_FUNCTIONS.items()}

def load_honey_tree_levels(decomp: pathlib.Path) -> tuple[int, int]:
    source = (decomp / WILD_ENCOUNTERS_SOURCE).read_text(encoding='utf-8')
    body = _function_body(source, 'CreateWildMon_HoneyTree')
    match = re.search(r'levelVariance\s*=\s*(\d+)\s*-\s*(\d+)\s*\+\s*1', body)
    if not match:
        raise ValueError('honey tree level range not found')
    return int(match.group(2)), int(match.group(1))

def _merge(slots: list[EncounterSlot]) -> tuple[EncounterSlot, ...]:
    merged: dict[str, EncounterSlot] = {}
    for slot in slots:
        if slot.species in merged:
            known = merged[slot.species]
            slot = EncounterSlot(
                slot.species,
                min(known.min_level, slot.min_level),
                max(known.max_level, slot.max_level),
                round(known.rate + slot.rate, 1),
            )
        merged[slot.species] = slot
    return tuple(merged.values())

def _method_slots(entries: list[dict], rates: list[int], species_keys: dict[str, str]) -> tuple[EncounterSlot, ...]:
    return _merge([
        EncounterSlot(
            species_keys[entry['species']],
            entry.get('level', entry.get('level_min', 0)),
            entry.get('level', entry.get('level_max', 0)),
            rate,
        )
        for entry, rate in zip(entries, rates)
        if entry['species'] != 'SPECIES_NONE'
    ])

def _location_methods(data: dict, slot_rates: dict[str, list[int]], species_keys: dict[str, str]) -> dict[str, tuple[EncounterSlot, ...]]:
    methods: dict[str, tuple[EncounterSlot, ...]] = {}
    for method, rates in slot_rates.items():
        if not data.get(f'{method}_rate'):
            continue
        slots = _method_slots(data.get(f'{method}_encounters', []), rates, species_keys)
        if slots:
            methods[method] = slots
    return methods

def _suffix(file_stem: str, location_name: str) -> str:
    words = file_stem.removeprefix('encounters_').split('_')
    target = name_key(location_name)
    matches = [
        (start, end)
        for start in range(len(words))
        for end in range(start + 1, len(words) + 1)
        if ''.join(words[start:end]) == target
    ]
    if matches:
        start, end = matches[0]
        words = words[end:] or words[:start]
    return ' '.join(word.upper() if any(c.isdigit() for c in word) else word.title() for word in words)

def _location_files(decomp: pathlib.Path) -> dict[str, str]:
    headers = (decomp / MAP_HEADERS_SOURCE).read_text(encoding='utf-8')
    return dict(MAP_HEADER_ENCOUNTERS.findall(headers))

def _honey_tree(decomp: pathlib.Path, species_keys: dict[str, str]) -> Location:
    entries = load_json(decomp / ENCOUNTERS_DIR / 'encounters_honey_tree.json')['encounters']
    total = sum(entry['weight'] for entry in entries)
    min_level, max_level = load_honey_tree_levels(decomp)
    slots = _merge([
        EncounterSlot(species_keys[entry['species']], min_level, max_level, round(entry['weight'] * 100 / total, 1))
        for entry in entries
        if entry['species'] != 'SPECIES_NONE'
    ])
    return Location(name_key('Honey Trees'), 'Honey Trees', {'honey': slots})

def _add_location(locations: dict[str, Location],
                  file_stem: str,
                  name: str,
                  methods: dict[str, tuple[EncounterSlot, ...]]):
    key = name_key(name)
    if key not in locations:
        locations[key] = Location(key, name, methods)
    elif locations[key].methods != methods:
        raise ValueError(f'{file_stem} merges into {name} but its encounters differ')

def load_encounters(decomp: pathlib.Path,
                    species: dict[str, Species],
                    order: tuple[str, ...] = ()) -> dict[str, Location]:
    species_keys = {mon.constant: mon.key for mon in species.values() if not mon.base_species}
    slot_rates = load_slot_rates(decomp)
    location_names = load_text_bank_by_id(decomp, 'location_names')

    populated: list[tuple[str, str, dict[str, tuple[EncounterSlot, ...]]]] = []
    for file_stem, label in _location_files(decomp).items():
        if file_stem in INACCESSIBLE_LOCATION_FILES:
            continue
        path = decomp / ENCOUNTERS_DIR / f'{file_stem}.json'
        methods = _location_methods(load_json(path), slot_rates, species_keys) if path.exists() else {}
        if methods:
            populated.append((file_stem, location_names[label], methods))

    name_counts: dict[str, int] = {}
    for _, name, _ in populated:
        name_counts[name] = name_counts.get(name, 0) + 1

    locations: dict[str, Location] = {}
    for file_stem, name, methods in populated:
        if file_stem in LOCATION_NAME_OVERRIDES:
            name = LOCATION_NAME_OVERRIDES[file_stem]
        elif name_counts[name] > 1 and (suffix := _suffix(file_stem, name)):
            name = f'{name} ({suffix})'
        _add_location(locations, file_stem, name, methods)

    honey = _honey_tree(decomp, species_keys)
    locations[honey.key] = honey
    return _ordered(locations, order)

def _ordered(locations: dict[str, Location], order: tuple[str, ...]) -> dict[str, Location]:
    missing = [key for key in order if key not in locations]
    if missing:
        raise ValueError(f'location order lists unknown locations: {missing}')
    return {
        **{key: locations[key] for key in order},
        **{key: location for key, location in locations.items() if key not in order},
    }
