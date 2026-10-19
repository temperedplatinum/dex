# Tempered Platinum Dex

A fork of [Porydex](https://github.com/lhearachel/porydex)'s Showdown Dex, rebuilt to support Tempered Platinum. All data is extracted directly from the game's [pokeplatinum](https://github.com/pret/pokeplatinum) decomp.

**Expanded Features**:

- **Decomp-sourced data**: species, moves, abilities, items and learnsets are read straight from the decomp's JSON data, text banks and C tables, so the dex always matches the game.

- **Updated Move Data**: base power, accuracy, PP, priority, targets and flags (sound, punch, bite, slicing, wind, pulse, powder) match in-game values, with in-game descriptions.

- **Updated Pokémon Data**: stats, types, hidden abilities, evolutions, alternate forms and Mega Evolutions (including new Mega Stones), plus level-up, TM/HM, tutor and egg move learnsets.

- **In-game text**: ability and item descriptions come from the game's own text banks.

Live dex:

- https://temperedplatinum.github.io/dex/

## Features

- **Instant search**: results appear as you type.
- **Filter search**: type a filter like `prankster, twave` and press Enter to find Pokémon matching every condition.
- **Panel UI**: pages open side by side, so you can compare without losing your place.
- **Inexact search**: typos still find what you meant.
- **Abbreviation search**: `tbolt` finds Thunderbolt, `bp` finds Baton Pass.

## Updating the data

The dex is a static site. The extractor reads the decomp locally and writes the generated data files to `site/data/`; neither the decomp nor the ROM is ever deployed.

```bash
make setup
source .venv/bin/activate
porydex config set --decomp ../plat-hack-decomp
porydex extract
```

Commit the regenerated `site/data/` and push to `main`. GitHub Actions deploys `site/` to GitHub Pages.

Edit the decomp, not the files in `site/data/`, as they are overwritten on every extract. The only hand-maintained data lives in `vanilla/`.

## Testing

Serve `site/` locally and open http://localhost:8000:

```bash
python -m http.server -d site
```

Run the extractor's tests with:

```bash
make test
```

## License

This dex is distributed under the terms of the [AGPLv3](./LICENSE), inherited from [Porydex](https://github.com/lhearachel/porydex) by Lhea.

The frontend is based on the [Pokémon Showdown Dex](https://github.com/Zarel/Pokemon-Showdown-Dex), which is MIT-licensed.
