import pytest

from porydex.decomp.enums import (
    showdown_category,
    showdown_color,
    showdown_contest_type,
    showdown_egg_groups,
    showdown_gender,
    showdown_type,
    showdown_types,
)

def test_showdown_type():
    assert showdown_type('TYPE_FAIRY') == 'Fairy'

def test_showdown_types_dedupes():
    assert showdown_types(['TYPE_NORMAL', 'TYPE_NORMAL']) == ['Normal']

@pytest.mark.parametrize('constants, expected', [
    (['EGG_GROUP_MONSTER', 'EGG_GROUP_GRASS'], ['Monster', 'Grass']),
    (['EGG_GROUP_WATER_1', 'EGG_GROUP_HUMAN_LIKE'], ['Water 1', 'Human-Like']),
    (['EGG_GROUP_AMORPHOUS', 'EGG_GROUP_AMORPHOUS'], ['Amorphous']),
    (['EGG_GROUP_NONE', 'EGG_GROUP_NONE'], []),
])
def test_showdown_egg_groups(constants, expected):
    assert showdown_egg_groups(constants) == expected

def test_showdown_color():
    assert showdown_color('MON_COLOR_GREEN') == 'Green'

def test_showdown_category():
    assert showdown_category('CLASS_PHYSICAL') == 'Physical'

@pytest.mark.parametrize('constant, expected', [
    ('CONTEST_TYPE_COOL', 'Cool'),
    ('CONTEST_TYPE_BEAUTY', 'Beautiful'),
    ('CONTEST_TYPE_SMART', 'Clever'),
])
def test_showdown_contest_type(constant, expected):
    assert showdown_contest_type(constant) == expected

@pytest.mark.parametrize('constant, expected', [
    ('GENDER_RATIO_MALE_ONLY', {'gender': 'M'}),
    ('GENDER_RATIO_FEMALE_ONLY', {'gender': 'F'}),
    ('GENDER_RATIO_NO_GENDER', {'gender': 'N'}),
    ('GENDER_RATIO_FEMALE_12_5', {'genderRatio': {'M': 0.875, 'F': 0.125}}),
    ('GENDER_RATIO_FEMALE_50', {'genderRatio': {'M': 0.5, 'F': 0.5}}),
    ('GENDER_RATIO_FEMALE_87_5', {'genderRatio': {'M': 0.125, 'F': 0.875}}),
])
def test_showdown_gender(constant, expected):
    assert showdown_gender(constant) == expected

def test_showdown_gender_rejects_unknown():
    with pytest.raises(ValueError):
        showdown_gender('GENDER_RATIO_SOMETHING')
