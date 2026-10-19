import re

SPLIT_CHARS = re.compile(r"[\W_-]+")

def name_key(name: str) -> str:
    return ''.join(SPLIT_CHARS.split(name.replace('é', 'e'))).lower()
