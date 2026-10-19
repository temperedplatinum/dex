import configparser
import enum
import pathlib
import os

class OutputFormat(enum.Enum):
    json = enum.auto()
    showdown = enum.auto()

    def __str__(self) -> str:
        return self.name.lower()

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def argparse(s):
        try:
            return OutputFormat[s.lower()]
        except KeyError:
            return s

decomp: pathlib.Path = pathlib.Path('../plat-hack-decomp').resolve()
output: pathlib.Path = pathlib.Path('./site/data').resolve()
format: OutputFormat = OutputFormat.showdown

_CONFIG_FILE: pathlib.Path = pathlib.Path('porydex.ini')

def save():
    config = configparser.ConfigParser()
    config['default'] = {
        'decomp': str(decomp),
        'output': str(output),
        'format': str(format),
    }

    with open(_CONFIG_FILE, 'w', encoding='utf-8') as cfgfile:
        config.write(cfgfile)

def load():
    global decomp
    global output
    global format

    # if no config exists, ensure it exists with defaults for the next load
    if not _CONFIG_FILE.exists():
        _CONFIG_FILE.touch(exist_ok=True)
        save()
    else:
        config = configparser.ConfigParser()
        config.read(_CONFIG_FILE)

        decomp = pathlib.Path(config['default'].get('decomp', str(decomp)))
        output = pathlib.Path(config['default']['output'])
        format = OutputFormat[config['default']['format']]

def clear():
    os.remove(_CONFIG_FILE)
