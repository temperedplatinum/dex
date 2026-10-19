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
}

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

def load_encounters(decomp: pathlib.Path, species: dict[str, Species]) -> dict[str, Location]:
    species_keys = {mon.constant: mon.key for mon in species.values() if not mon.base_species}
    slot_rates = load_slot_rates(decomp)
    location_names = load_text_bank_by_id(decomp, 'location_names')

    populated: list[tuple[str, str, dict[str, tuple[EncounterSlot, ...]]]] = []
    for file_stem, label in _location_files(decomp).items():
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
        locations[name_key(name)] = Location(name_key(name), name, methods)

    honey = _honey_tree(decomp, species_keys)
    locations[honey.key] = honey
    return locations
