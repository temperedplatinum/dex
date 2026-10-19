EGG_GROUP_OVERRIDES: dict[str, str] = {
    'HUMAN_LIKE': 'Human-Like',
}

CONTEST_TYPE_OVERRIDES: dict[str, str] = {
    'BEAUTY': 'Beautiful',
    'SMART': 'Clever',
}

SINGLE_GENDERS: dict[str, str] = {
    'GENDER_RATIO_MALE_ONLY': 'M',
    'GENDER_RATIO_FEMALE_ONLY': 'F',
    'GENDER_RATIO_NO_GENDER': 'N',
}

def _title(constant: str, prefix: str, overrides: dict[str, str] | None = None) -> str:
    suffix = constant.removeprefix(prefix)
    if overrides and suffix in overrides:
        return overrides[suffix]
    return ' '.join(word.title() for word in suffix.split('_'))

def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(values))

def showdown_type(constant: str) -> str:
    return _title(constant, 'TYPE_')

def showdown_types(constants: list[str]) -> list[str]:
    return _unique([showdown_type(c) for c in constants])

def showdown_egg_groups(constants: list[str]) -> list[str]:
    return _unique([
        _title(c, 'EGG_GROUP_', EGG_GROUP_OVERRIDES)
        for c in constants
        if c != 'EGG_GROUP_NONE'
    ])

def showdown_color(constant: str) -> str:
    return _title(constant, 'MON_COLOR_')

def showdown_category(constant: str) -> str:
    return _title(constant, 'CLASS_')

def showdown_contest_type(constant: str) -> str:
    return _title(constant, 'CONTEST_TYPE_', CONTEST_TYPE_OVERRIDES)

def showdown_gender(constant: str) -> dict[str, str | dict[str, float]]:
    if constant in SINGLE_GENDERS:
        return {'gender': SINGLE_GENDERS[constant]}

    percent = constant.removeprefix('GENDER_RATIO_FEMALE_')
    if percent == constant:
        raise ValueError(f'unrecognized gender ratio: {constant}')

    female = float(percent.replace('_', '.')) / 100
    return {'genderRatio': {'M': 1 - female, 'F': female}}
