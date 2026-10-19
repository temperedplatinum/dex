from porydex.decomp.loaders import load_constants, load_text_bank

def test_load_constants_keeps_file_order(decomp):
    assert load_constants(decomp, 'pokemon_types') == [
        'TYPE_NORMAL',
        'TYPE_FIGHTING',
        'TYPE_STEEL',
        'TYPE_FAIRY',
        'NUM_POKEMON_TYPES',
    ]

def test_load_constants_strips_explicit_values(decomp):
    assert load_constants(decomp, 'gender_ratios') == [
        'GENDER_RATIO_MALE_ONLY',
        'GENDER_RATIO_FEMALE_12_5',
        'GENDER_RATIO_NO_GENDER',
    ]

def test_load_text_bank_reads_single_line_messages(decomp):
    assert load_text_bank(decomp, 'move_names') == ['-', 'Pound', 'Karate Chop']

def test_load_text_bank_joins_wrapped_lines(decomp):
    assert load_text_bank(decomp, 'move_descriptions')[:3] == [
        '',
        'The foe is physically pounded with a long tail or a foreleg, etc.',
        '',
    ]
