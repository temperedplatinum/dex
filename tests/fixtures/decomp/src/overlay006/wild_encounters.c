static u8 GetGroundEncounterSlot(void)
{
    u8 roll = LCRNG_RandMod(100);

    if (roll < 20) {
        return 0;
    } else if (roll >= 20 && roll < 35) {
        return 1;
    } else if (roll >= 35 && roll < 45) {
        return 2;
    } else if (roll >= 45 && roll < 55) {
        return 3;
    } else if (roll >= 55 && roll < 65) {
        return 4;
    } else if (roll >= 65 && roll < 75) {
        return 5;
    } else if (roll >= 75 && roll < 80) {
        return 6;
    } else if (roll >= 80 && roll < 85) {
        return 7;
    } else if (roll >= 85 && roll < 90) {
        return 8;
    } else if (roll >= 90 && roll < 95) {
        return 9;
    } else if (roll >= 95 && roll < 99) {
        return 10;
    }

    return 11;
}

static u8 GetWaterEncounterSlot(void)
{
    u8 roll = LCRNG_RandMod(100);

    if (roll < 20) {
        return 0;
    } else if (roll < 40) {
        return 1;
    } else if (roll < 60) {
        return 2;
    } else if (roll < 80) {
        return 3;
    } else if (roll < 90) {
        return 4;
    }

    return 5;
}

void CreateWildMon_HoneyTree(FieldSystem *fieldSystem, FieldBattleDTO *battleParams)
{
    Pokemon *firstPartyMon;

    int species = HoneyTree_GetSpecies(fieldSystem);

    Party *playerParty = SaveData_GetParty(fieldSystem->saveData);
    firstPartyMon = Party_GetPokemonBySlotIndex(playerParty, 0);

    WildEncounters_FieldParams encounterFieldParams;
    InitEncounterFieldParams(fieldSystem, firstPartyMon, NULL, &encounterFieldParams);

    u8 levelVariance = 15 - 5 + 1;

    u8 level = 5 + LCRNG_RandMod(levelVariance);

    HoneyTree_Unslather(fieldSystem);
    battleParams->battleStatusMask |= BATTLE_STATUS_HONEY_TREE;
    CreateWildMon(species, level, 1, &encounterFieldParams, firstPartyMon, battleParams);

    return;
}
