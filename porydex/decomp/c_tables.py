import pathlib
import re

COMMENTS = re.compile(r'//[^\n]*|/\*.*?\*/', re.S)
ASM_LINE_COMMENT = re.compile(r'@[^\n]*')

def read_without_comments(path: pathlib.Path) -> str:
    source = path.read_text(encoding='utf-8')
    if path.suffix in ('.c', '.h', '.s'):
        source = COMMENTS.sub('', source)
    if path.suffix == '.s':
        source = ASM_LINE_COMMENT.sub('', source)
    return source

def table_body(path: pathlib.Path, table: str) -> str:
    source = COMMENTS.sub('', path.read_text(encoding='utf-8'))
    pattern = rf'\b{re.escape(table)}\s*\[\]\s*=\s*\{{(.*?)\}};'
    match = re.search(pattern, source, re.S)
    if not match:
        raise ValueError(f'table {table} not found in {path}')
    return match.group(1)

def parse_constant_table(path: pathlib.Path, table: str, prefix: str) -> list[str]:
    return re.findall(rf'\b{re.escape(prefix)}\w+', table_body(path, table))
