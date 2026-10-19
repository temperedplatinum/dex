import pathlib
import re

COMMENTS = re.compile(r'//[^\n]*|/\*.*?\*/', re.S)

def table_body(path: pathlib.Path, table: str) -> str:
    source = COMMENTS.sub('', path.read_text(encoding='utf-8'))
    pattern = rf'\b{re.escape(table)}\s*\[\]\s*=\s*\{{(.*?)\}};'
    match = re.search(pattern, source, re.S)
    if not match:
        raise ValueError(f'table {table} not found in {path}')
    return match.group(1)

def parse_constant_table(path: pathlib.Path, table: str, prefix: str) -> list[str]:
    return re.findall(rf'\b{re.escape(prefix)}\w+', table_body(path, table))
