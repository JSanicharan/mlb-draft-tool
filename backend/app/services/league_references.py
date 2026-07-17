import httpx
import asyncio
from datetime import datetime

reference_distributions = None

MIN_PLATE_APPEARANCES = 400
FULL_SEASON_QUALIFIER = 502
SEASON_START_MONTH = 3
SEASON_END_MONTH = 10

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
    home_runs = []
    runs = []
    rbis = []
    stolen_bases = []
    avgs = []
    hits = []

    for i in range(len(players)):
        player = players[i]
        stat = player["stat"]

        plate_appearances = float(stat.get("plateAppearances", 0))
        if plate_appearances < MIN_PLATE_APPEARANCES:
            continue

        strikeout = float(stat["strikeOuts"])
        if strikeout == 0:
            continue

        walk = float(stat["baseOnBalls"])
        discipline.append(walk / strikeout)

        season_avg = float(stat["avg"])
        season_slg = float(stat["slg"])
        iso.append(season_slg - season_avg)

        ops.append(float(stat["ops"]))
        home_runs.append(float(stat["homeRuns"]))
        runs.append(float(stat["runs"]))
        rbis.append(float(stat["rbi"]))
        stolen_bases.append(float(stat["stolenBases"]))
        avgs.append(float(stat["avg"]))
        hits.append(float(stat["hits"]))

    return {
        "ops": ops,
        "discipline": discipline,
        "iso": iso,
        "home_runs": home_runs,
        "runs": runs,
        "rbi": rbis,
        "stolen_bases": stolen_bases,
        "avg": avgs,
        "hits": hits,
    }

def get_current_season_min_plate_appearances() -> int:
    now = datetime.now()
    current_year = now.year
    season_start = datetime(current_year, SEASON_START_MONTH, 20)
    season_end = datetime(current_year, SEASON_END_MONTH, 1)

    if now < season_start:
        progress = 0.05
    elif now > season_end:
        progress = 1.0
    else:
        elapsed = (now - season_start).days
        total = (season_end - season_start).days
        progress = elapsed / total

    scaled = int(FULL_SEASON_QUALIFIER * progress)
    return max(scaled, 50)

def build_current_season_reference_distributions(raw_data: dict):
    min_pa = get_current_season_min_plate_appearances()
    players = raw_data["stats"][0]["splits"]
    ops = []
    discipline = []
    iso = []
    home_runs = []
    runs = []
    rbis = []
    stolen_bases = []
    avgs = []
    hits = []

    for i in range(len(players)):
        player = players[i]
        stat = player["stat"]

        plate_appearances = float(stat.get("plateAppearances", 0))
        if plate_appearances < min_pa:
            continue

        strikeout = float(stat["strikeOuts"])
        if strikeout == 0:
            continue

        walk = float(stat["baseOnBalls"])
        discipline.append(walk / strikeout)

        season_avg = float(stat["avg"])
        season_slg = float(stat["slg"])
        iso.append(season_slg - season_avg)

        ops.append(float(stat["ops"]))
        home_runs.append(float(stat["homeRuns"]))
        runs.append(float(stat["runs"]))
        rbis.append(float(stat["rbi"]))
        stolen_bases.append(float(stat["stolenBases"]))
        avgs.append(float(stat["avg"]))
        hits.append(float(stat["hits"]))

    return {
        "ops": ops,
        "discipline": discipline,
        "iso": iso,
        "home_runs": home_runs,
        "runs": runs,
        "rbi": rbis,
        "stolen_bases": stolen_bases,
        "avg": avgs,
        "hits": hits,
    }

async def refresh_reference_data():
    global reference_distributions
    current_year = datetime.now().year
    data = await fetch_qualified_hitters(current_year)
    reference_distributions = build_current_season_reference_distributions(data)

async def build_training_reference_distributions(seasons: list) -> dict:
    training_distributions = {}
    for season in seasons:
        raw_data = await fetch_qualified_hitters(season)
        training_distributions[season] = build_reference_distributions(raw_data)
    return training_distributions