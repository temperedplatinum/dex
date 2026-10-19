import json
import pathlib
import typing

def load_json(path: pathlib.Path) -> typing.Any:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_constants(decomp: pathlib.Path, name: str) -> list[str]:
    with open(decomp / 'generated' / f'{name}.txt', 'r', encoding='utf-8') as f:
        return [line.split('=')[0].strip() for line in f if line.strip()]

def load_text_bank(decomp: pathlib.Path, name: str) -> list[str]:
    messages = load_json(decomp / 'res' / 'text' / f'{name}.json')['messages']
    return [_flatten(message.get('en_US', '')) for message in messages]

def _flatten(text: str | list[str]) -> str:
    joined = ''.join(text) if isinstance(text, list) else text
    return ' '.join(joined.split())
