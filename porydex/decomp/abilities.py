import dataclasses
import pathlib

from porydex.decomp.loaders import load_constants, load_text_bank
from porydex.decomp.names import resolve_ability

CUSTOM_RATING = 1

@dataclasses.dataclass(frozen=True)
class Ability:
    key: str
    num: int
    name: str
    description: str
    rating: float
    flags: dict[str, int] = dataclasses.field(default_factory=dict)

    def to_showdown(self) -> dict:
        return {
            'num': self.num,
            'name': self.name,
            'rating': self.rating,
            'flags': self.flags,
            'desc': self.description,
            'shortDesc': self.description,
        }

def load_abilities(decomp: pathlib.Path, vanilla: dict[str, dict]) -> dict[str, Ability]:
    names = load_text_bank(decomp, 'ability_names')
    descriptions = load_text_bank(decomp, 'ability_descriptions')
    abilities: dict[str, Ability] = {}
    for num, constant in enumerate(load_constants(decomp, 'abilities')):
        if constant == 'ABILITY_NONE':
            continue

        resolved = resolve_ability(constant, names[num], vanilla)
        known = vanilla.get(resolved.key, {})
        abilities[resolved.key] = Ability(
            key=resolved.key,
            num=num,
            name=resolved.name,
            description=descriptions[num],
            rating=known.get('rating', CUSTOM_RATING),
            flags=known.get('flags', {}),
        )
    return abilities
