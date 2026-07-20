import httpx
import asyncio
from datetime import datetime
import json

reference_distributions = None
pitcher_reference_distributions = None
fip_constant = None
FULL_SEASON_INNINGS_QUALIFIER = 162
MIN_PLATE_APPEARANCES = 400
FULL_SEASON_QUALIFIER = 502
SEASON_START_MONTH = 3
SEASON_END_MONTH = 10
GAMES_FINISHED_QUALIFIER = 45
leaderboard_data = None
CATEGORY_LABELS = {
    "home_runs": "HR",
    "runs": "R",
    "rbi": "RBI",
    "stolen_bases": "SB",
    "avg": "AVG",
    "hits": "H",
    "ops": "OPS",
    "iso": "ISO",
    "discipline": "Discipline",
}

PITCHER_CATEGORY_LABELS = {
    "wins": "W",
    "saves": "SV",
    "strikeouts": "K",
    "era": "ERA",
    "whip": "WHIP",
}

PITCHER_LOWER_IS_BETTER = {"era", "whip"}

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
        return json.loads(response.content.decode("utf-8"))

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
    global reference_distributions, leaderboard_data
    current_year = datetime.now().year
    data = await fetch_qualified_hitters(current_year)
    reference_distributions = build_current_season_reference_distributions(data)
    min_pa = get_current_season_min_plate_appearances()
    leaderboard_data = build_leaderboard(data, min_pa)

async def build_training_reference_distributions(seasons: list) -> dict:
    training_distributions = {}
    for season in seasons:
        raw_data = await fetch_qualified_hitters(season)
        training_distributions[season] = build_reference_distributions(raw_data)
    return training_distributions

def build_leaderboard(raw_data: dict, min_pa: int) -> list:
    players = raw_data["stats"][0]["splits"]
    leaderboard = []

    for i in range(len(players)):
        player_split = players[i]
        stat = player_split["stat"]

        plate_appearances = float(stat.get("plateAppearances", 0))
        if plate_appearances < min_pa:
            continue

        strikeout = float(stat.get("strikeOuts", 0))
        walk = float(stat.get("baseOnBalls", 0))
        discipline = walk / strikeout if strikeout else 0

        avg = float(stat.get("avg", 0))
        slg = float(stat.get("slg", 0))
        iso = slg - avg

        player_info = player_split.get("player", {})
        team_info = player_split.get("team", {})
        position_info = player_split.get("position", {})

        leaderboard.append({
            "player_id": player_info.get("id"),
            "name": player_info.get("fullName"),
            "team": team_info.get("name"),
            "position": position_info.get("abbreviation", ""),
            "home_runs": float(stat.get("homeRuns", 0)),
            "runs": float(stat.get("runs", 0)),
            "rbi": float(stat.get("rbi", 0)),
            "stolen_bases": float(stat.get("stolenBases", 0)),
            "avg": avg,
            "hits": float(stat.get("hits", 0)),
            "ops": float(stat.get("ops", 0)),
            "iso": iso,
            "discipline": discipline,
        })

    return leaderboard

def parse_innings_pitched(innings_pitched) -> float:
    ip_str = str(innings_pitched)
    if "." in ip_str:
        whole, fraction = ip_str.split(".")
        whole = float(whole)
        if fraction == "1":
            partial = 1 / 3
        elif fraction == "2":
            partial = 2 / 3
        else:
            partial = 0
        return whole + partial
    return float(ip_str)

async def fetch_qualified_pitchers(season: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://statsapi.mlb.com/api/v1/stats",
            params={
                "stats": "season",
                "group": "pitching",
                "season": season,
                "sportId": "1",
                "limit": "500",
            },
        )
        return json.loads(response.content.decode("utf-8"))

def compute_fip_constant(raw_data: dict) -> float:
    players = raw_data["stats"][0]["splits"]
    total_earned_runs = 0
    total_hr = 0
    total_bb = 0
    total_hbp = 0
    total_k = 0
    total_ip = 0

    for i in range(len(players)):
        stat = players[i]["stat"]
        ip = parse_innings_pitched(stat.get("inningsPitched", "0.0"))
        if ip == 0:
            continue
        total_ip += ip
        total_earned_runs += float(stat.get("earnedRuns", 0))
        total_hr += float(stat.get("homeRuns", 0))
        total_bb += float(stat.get("baseOnBalls", 0))
        total_hbp += float(stat.get("hitByPitch", 0))
        total_k += float(stat.get("strikeOuts", 0))

    if total_ip == 0:
        return 3.10

    league_era = (9 * total_earned_runs) / total_ip
    return league_era - (((13 * total_hr) + (3 * (total_bb + total_hbp)) - (2 * total_k)) / total_ip)

def get_current_season_min_innings_pitched() -> int:
    progress_fraction = get_current_season_min_plate_appearances() / FULL_SEASON_QUALIFIER
    scaled = int(FULL_SEASON_INNINGS_QUALIFIER * progress_fraction)
    return max(scaled, 20)

def get_current_season_min_games_finished() -> int:
    progress_fraction = get_current_season_min_plate_appearances() / FULL_SEASON_QUALIFIER
    scaled = int(GAMES_FINISHED_QUALIFIER * progress_fraction)
    return max(scaled, 5)

def build_pitcher_reference_distributions(raw_data: dict) -> dict:
    global fip_constant
    fip_constant = compute_fip_constant(raw_data)
    min_ip = get_current_season_min_innings_pitched()

    players = raw_data["stats"][0]["splits"]
    fip_list = []
    whip_list = []
    k9_list = []
    ip_list = []
    era_list = []
    wins_list = []
    saves_list = []
    strikeouts_list = []

    for i in range(len(players)):
        stat = players[i]["stat"]
        innings_pitched = parse_innings_pitched(stat.get("inningsPitched", "0.0"))
        if innings_pitched < min_ip:
            continue

        home_runs = float(stat.get("homeRuns", 0))
        walks = float(stat.get("baseOnBalls", 0))
        hit_by_pitch = float(stat.get("hitByPitch", 0))
        strikeouts = float(stat.get("strikeOuts", 0))

        fip = (((13 * home_runs) + (3 * (walks + hit_by_pitch)) - (2 * strikeouts)) / innings_pitched) + fip_constant
        fip_list.append(fip)
        whip_list.append(float(stat["whip"]))

        if "strikeoutsPer9Inn" in stat:
            k9_list.append(float(stat["strikeoutsPer9Inn"]))
        else:
            k9_list.append((strikeouts / innings_pitched) * 9)

        ip_list.append(innings_pitched)
        era_list.append(float(stat.get("era", 0)))
        wins_list.append(float(stat.get("wins", 0)))
        saves_list.append(float(stat.get("saves", 0)))
        strikeouts_list.append(strikeouts)

    return {
        "fip": fip_list,
        "whip": whip_list,
        "k9": k9_list,
        "ip": ip_list,
        "era": era_list,
        "wins": wins_list,
        "saves": saves_list,
        "strikeouts": strikeouts_list,
    }

async def refresh_pitcher_reference_data():
    global pitcher_reference_distributions, pitcher_leaderboard_data
    current_year = datetime.now().year
    data = await fetch_qualified_pitchers(current_year)
    pitcher_reference_distributions = build_pitcher_reference_distributions(data)
    min_ip = get_current_season_min_innings_pitched()
    min_gf = get_current_season_min_games_finished()
    pitcher_leaderboard_data = build_pitcher_leaderboard(data, min_ip, min_gf)

def build_pitcher_leaderboard(raw_data: dict, min_ip: int, min_gf: int) -> list:
    fip_const = fip_constant if fip_constant is not None else 3.10
    players = raw_data["stats"][0]["splits"]
    leaderboard = []

    for i in range(len(players)):
        player_split = players[i]
        stat = player_split["stat"]

        innings_pitched = parse_innings_pitched(stat.get("inningsPitched", "0.0"))
        games_finished = float(stat.get("gamesFinished", 0))

        if innings_pitched < min_ip and games_finished < min_gf:
            continue

        home_runs = float(stat.get("homeRuns", 0))
        walks = float(stat.get("baseOnBalls", 0))
        hit_by_pitch = float(stat.get("hitByPitch", 0))
        strikeouts = float(stat.get("strikeOuts", 0))
        fip = (((13 * home_runs) + (3 * (walks + hit_by_pitch)) - (2 * strikeouts)) / innings_pitched) + fip_const if innings_pitched > 0 else fip_const

        player_info = player_split.get("player", {})
        team_info = player_split.get("team", {})

        leaderboard.append({
            "player_id": player_info.get("id"),
            "name": player_info.get("fullName"),
            "team": team_info.get("name"),
            "position": "P",
            "wins": float(stat.get("wins", 0)),
            "saves": float(stat.get("saves", 0)),
            "strikeouts": strikeouts,
            "era": float(stat.get("era", 0)),
            "whip": float(stat.get("whip", 0)),
            "fip": fip,
        })

    return leaderboard

pitcher_leaderboard_data = None