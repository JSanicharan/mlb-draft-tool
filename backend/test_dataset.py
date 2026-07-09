import asyncio
from app.services.training_data import (
    fetch_all_seasons, group_by_player, build_training_pairs,
    fetch_all_fielders, build_fielding_lookup, add_labels,
    build_dataset, TRAINING_SEASONS
)
from app.services import league_references

async def run():
    await league_references.refresh_reference_data()

    hitting_data = await fetch_all_seasons(TRAINING_SEASONS)
    grouped = group_by_player(hitting_data)
    pairs = build_training_pairs(grouped)

    fielding_lookup = {}
    for season in TRAINING_SEASONS:
        raw_fielding = await fetch_all_fielders(season)
        season_lookup = build_fielding_lookup(raw_fielding)
        fielding_lookup.update(season_lookup)

    labeled_pairs = add_labels(pairs, fielding_lookup)
    X, y = build_dataset(labeled_pairs, fielding_lookup)

    print("total rows:", len(X))
    print("sample X row:", X[0])
    print("sample y value:", y[0])

asyncio.run(run())