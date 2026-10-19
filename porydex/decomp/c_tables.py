import pathlib
import re

COMMENTS = re.compile(r'//[^\n]*|/\*.*?\*/', re.S)

def parse_constant_table(path: pathlib.Path, table: str, prefix: str) -> list[str]:
    source = COMMENTS.sub('', path.read_text(encoding='utf-8'))
    pattern = rf'\b{re.escape(table)}\s*\[\]\s*=\s*\{{(.*?)\}};'
    match = re.search(pattern, source, re.S)
    if not match:
        raise ValueError(f'table {table} not found in {path}')
    return re.findall(rf'\b{re.escape(prefix)}\w+', match.group(1))
