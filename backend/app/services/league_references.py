import httpx
import asyncio

reference_distributions = None

MIN_PLATE_APPEARANCES = 400

async def fetch_qualified_hitters(season: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://statsapi.mlb.com/api/v1/stats",
            params={
                "stats": "season",
                "group": "hitting",
                "season": season,
                "sportId": "1",
                "limit": "500",
            },
        )
        return response.json()

def build_reference_distributions(raw_data: dict):
    players = raw_data["stats"][0]["splits"]
    ops = []
    discipline = []
    iso = []

    for i in range(len(players)):
        player = players[i]
        stat = player["stat"]

        plate_appearances = float(stat.get("plateAppearances", 0))
        if plate_appearances < MIN_PLATE_APPEARANCES:
            continue

        strikeout = float(stat["strikeOuts"])
        if strikeout == 0:
            continue

        ops.append(float(stat["ops"]))

        walk = float(stat["baseOnBalls"])
        discipline.append(walk / strikeout)

        season_avg = float(stat["avg"])
        season_slg = float(stat["slg"])
        iso.append(season_slg - season_avg)

    return {
        "ops": ops,
        "discipline": discipline,
        "iso": iso,
    }

async def refresh_reference_data():
    global reference_distributions
    data = await fetch_qualified_hitters(2025)
    reference_distributions = build_reference_distributions(data)
    print("Qualified hitters in OPS distribution:", len(reference_distributions["ops"]))

async def build_training_reference_distributions(seasons: list) -> dict:
    training_distributions = {}
    for season in seasons:
        raw_data = await fetch_qualified_hitters(season)
        training_distributions[season] = build_reference_distributions(raw_data)
    return training_distributions