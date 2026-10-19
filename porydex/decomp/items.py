import csv
import dataclasses
import pathlib
import re

from porydex.decomp.c_tables import parse_constant_table, read_without_comments
from porydex.decomp.enums import showdown_type
from porydex.decomp.loaders import load_constants, load_text_bank
from porydex.decomp.names import resolve_item

PLACEHOLDER_DESCRIPTION = '???'

ITEM_CONSTANT = re.compile(r'\bITEM_\w+')
FIELD_SOURCE_PATTERNS = ('*.s', '*.json')

@dataclasses.dataclass(frozen=True)
class Item:
    key: str
    constant: str
    num: int
    name: str
    description: str
    spritenum: int = 0
    fling_power: int = 0
    natural_gift_power: int = 0
    natural_gift_type: str | None = None
    is_pokeball: bool = False
    mega_stone: str | None = None
    mega_evolves: str | None = None
    item_user: tuple[str, ...] = ()
    placed: bool = False

    def to_showdown(self) -> dict:
        item: dict = {
            'num': self.num,
            'name': self.name,
            'spritenum': self.spritenum,
            'desc': self.description,
            'shortDesc': self.description,
        }
        if self.fling_power:
            item['fling'] = {'basePower': self.fling_power}
        if self.natural_gift_power and self.natural_gift_type:
            item['naturalGift'] = {'basePower': self.natural_gift_power, 'type': self.natural_gift_type}
        if self.is_pokeball:
            item['isPokeball'] = True
        if self.mega_stone:
            item['megaStone'] = self.mega_stone
            item['megaEvolves'] = self.mega_evolves
        if self.item_user:
            item['itemUser'] = list(self.item_user)
        return item

def _load_item_data(decomp: pathlib.Path) -> dict[str, dict[str, str]]:
    with open(decomp / 'res' / 'items' / 'pl_item_data.csv', 'r', encoding='utf-8', newline='') as f:
        return {row['item']: row for row in csv.DictReader(f)}

def _natural_gift_type(value: str) -> str | None:
    return showdown_type(value) if value.startswith('TYPE_') else None

def load_placed_items(decomp: pathlib.Path) -> set[str]:
    field = decomp / 'res' / 'field'
    placed = {
        constant
        for pattern in FIELD_SOURCE_PATTERNS
        for path in field.rglob(pattern)
        for constant in ITEM_CONSTANT.findall(read_without_comments(path))
    }
    shop = decomp / 'src' / 'overlay007' / 'shop_menu.c'
    return placed | set(parse_constant_table(shop, 'sBPStoreItems', 'ITEM_'))

def load_items(decomp: pathlib.Path, vanilla: dict[str, dict]) -> dict[str, Item]:
    names = load_text_bank(decomp, 'item_names')
    descriptions = load_text_bank(decomp, 'item_descriptions')
    item_data = _load_item_data(decomp)
    placed = load_placed_items(decomp)
    items: dict[str, Item] = {}
    for num, constant in enumerate(load_constants(decomp, 'items')):
        if constant == 'ITEM_NONE' or not constant.startswith('ITEM_'):
            continue

        resolved = resolve_item(constant, names[num], vanilla)
        known = vanilla.get(resolved.key, {})
        data = item_data.get(constant, {})
        description = descriptions[num]
        items[resolved.key] = Item(
            key=resolved.key,
            constant=constant,
            num=num,
            name=resolved.name,
            description='' if description == PLACEHOLDER_DESCRIPTION else description,
            spritenum=known.get('spritenum', 0),
            fling_power=int(data.get('flingPower', 0)),
            natural_gift_power=int(data.get('naturalGiftPower', 0)),
            natural_gift_type=_natural_gift_type(data.get('naturalGiftType', '')),
            is_pokeball=data.get('fieldPocket') == 'POCKET_BALLS',
            mega_stone=known.get('megaStone'),
            mega_evolves=known.get('megaEvolves'),
            item_user=tuple(known.get('itemUser', ())),
            placed=constant in placed,
        )
    return items
