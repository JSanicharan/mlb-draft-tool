from dotenv import load_dotenv
load_dotenv()
from app.services.ai_summary import generate_ai_summary
from fastapi import FastAPI 
from app.services.mlb_client import search_player, get_career_offense_stats, get_career_fielding_stats, get_player_bundle, get_pitcher_bundle
from app.services.scoring import get_draft_score, get_stat_breakdown, get_ml_features, get_pitcher_draft_score, get_pitcher_stat_breakdown
from fastapi.middleware.cors import CORSMiddleware
from app.services import league_references
from app.services.ml_model import predict_ml_score

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await league_references.refresh_reference_data()
    await league_references.refresh_pitcher_reference_data()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mlb-draft-tool.vercel.app", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok"}
@app.get("/players/search")
async def search_players(name:str):
    result = await search_player(name)
    return result

@app.get("/players/{player_id}/stats")
async def hitting_stats(player_id : int):
    result = await get_career_offense_stats(player_id)
    return result

@app.get("/players/{player_id}/fielding")
async def fielding_stats(player_id : int):
    result = await get_career_fielding_stats(player_id)
    return result

@app.get("/players/{player_id}/draft-score")
async def draft_score(player_id :int):
    bundle = await get_player_bundle(player_id)

    result = get_draft_score(bundle["offense_seasons"], bundle["fielding_seasons"], bundle["age"], bundle["position"])
    return result
     
@app.get("/players/{player_id}/profile")
async def profile(player_id: int):    
    bundle = await get_player_bundle(player_id)
    draft_score = get_draft_score(bundle["offense_seasons"], bundle["fielding_seasons"], bundle["age"], bundle["position"])
    stat_breakdown = get_stat_breakdown(bundle["offense_seasons"])
    headshot_url = (f"https://img.mlbstatic.com/mlb-photos/image/upload/w_180,q_auto:best/v1/people/{player_id}/headshot/67/current")

    ml_features = get_ml_features(bundle["offense_seasons"], bundle["fielding_seasons"], bundle["age"], bundle["position"], draft_score)
    ml_score = predict_ml_score(ml_features)

    recent_season_stat = bundle["offense_seasons"][-1]["stat"] if bundle["offense_seasons"] else {}
    ai_summary = None #generate_ai_summary(
        #player_name=bundle["name"],
        #position=bundle["position"],
        #draft_score=draft_score,
        #stats=recent_season_stat,
    #)

    return {
        "player": {
            "name": bundle["name"],
            "team": bundle["team"],
            "position": bundle["position"],
            "age": bundle["age"],
            "bat_side": bundle["bat_side"],
            "throw_side": bundle["throw_side"],
            "headshot_url": headshot_url,
        },
        "draft_score": draft_score,
        "ml_score": round(float(ml_score), 2),
        "ai_summary": None, #ai_summary,
        "scoring_stats" : stat_breakdown["scoring_stats"],
        "baseline_stats" : stat_breakdown["baseline_stats"]

    }

@app.get("/leaderboard")
def leaderboard(category: str, limit: int = 20):
    is_pitcher_category = category in league_references.PITCHER_CATEGORY_LABELS

    if is_pitcher_category:
        if league_references.pitcher_leaderboard_data is None:
            return {"error": "Pitcher leaderboard data not loaded yet"}
        source_data = league_references.pitcher_leaderboard_data
        label = league_references.PITCHER_CATEGORY_LABELS[category]
        reverse_sort = category not in league_references.PITCHER_LOWER_IS_BETTER
    else:
        if league_references.leaderboard_data is None:
            return {"error": "Leaderboard data not loaded yet"}
        valid_categories = list(league_references.CATEGORY_LABELS.keys())
        if category not in valid_categories:
            return {"error": f"Invalid category. Must be one of: {valid_categories + list(league_references.PITCHER_CATEGORY_LABELS.keys())}"}
        source_data = league_references.leaderboard_data
        label = league_references.CATEGORY_LABELS[category]
        reverse_sort = True

    sorted_players = sorted(source_data, key=lambda p: p[category], reverse=reverse_sort)
    top_players = sorted_players[:limit]

    results = []
    for player in top_players:
        headshot_url = (
            f"https://img.mlbstatic.com/mlb-photos/image/upload/w_180,q_auto:best/v1/people/{player['player_id']}/headshot/67/current"
        )
        results.append({
            "player_id": player["player_id"],
            "name": player["name"],
            "team": player["team"],
            "headshot_url": headshot_url,
            "value": player[category],
        })

    return {
        "category": category,
        "label": label,
        "players": results,
    }

@app.get("/pitchers/{player_id}/profile")
async def pitcher_profile(player_id: int):
    bundle = await get_pitcher_bundle(player_id)
    fip_constant = league_references.fip_constant
    draft_score = get_pitcher_draft_score(bundle["pitching_seasons"], bundle["age"], fip_constant)
    stat_breakdown = get_pitcher_stat_breakdown(bundle["pitching_seasons"], fip_constant)

    headshot_url = (f"https://img.mlbstatic.com/mlb-photos/image/upload/w_180,q_auto:best/v1/people/{player_id}/headshot/67/current")

    return {
        "player": {
            "name": bundle["name"],
            "team": bundle["team"],
            "position": bundle["position"],
            "age": bundle["age"],
            "throw_side": bundle["throw_side"],
            "headshot_url": headshot_url,
        },
        "draft_score": draft_score,
        "scoring_stats": stat_breakdown["scoring_stats"],
        "baseline_stats": stat_breakdown["baseline_stats"],
    }

@app.get("/recommendations/spot-filler")
def spot_filler_recommendation(position: str, exclude: str = "", limit: int = 5):
    excluded_ids = set()
    if exclude:
        excluded_ids = set(int(x) for x in exclude.split(",") if x)

    is_pitcher_position = position == "P"

    if is_pitcher_position:
        if league_references.pitcher_leaderboard_data is None:
            return {"error": "Pitcher data not loaded yet"}
        pool = league_references.pitcher_leaderboard_data
        rank_key = "fip"
        reverse_sort = False
    else:
        if league_references.leaderboard_data is None:
            return {"error": "Hitter data not loaded yet"}
        pool = league_references.leaderboard_data
        rank_key = "ops"
        reverse_sort = True

    candidates = [
        player for player in pool
        if player["position"] == position and player["player_id"] not in excluded_ids
    ]
    sorted_candidates = sorted(candidates, key=lambda p: p[rank_key], reverse=reverse_sort)
    top_candidates = sorted_candidates[:limit]

    results = []
    for player in top_candidates:
        headshot_url = (
            f"https://img.mlbstatic.com/mlb-photos/image/upload/w_180,q_auto:best/v1/people/{player['player_id']}/headshot/67/current"
        )
        results.append({
            "player_id": player["player_id"],
            "name": player["name"],
            "team": player["team"],
            "position": player["position"],
            "headshot_url": headshot_url,
            "rank_stat": rank_key,
            "rank_value": player[rank_key],
        })

    return {"position": position, "players": results}

@app.get("/players/browse")
def browse_players(position: str = "ALL", filters: str = "", limit: int = 100):
    is_pitcher_view = position == "P"

    if is_pitcher_view:
        if league_references.pitcher_leaderboard_data is None:
            return {"error": "Pitcher data not loaded yet"}
        pool = league_references.pitcher_leaderboard_data
    else:
        if league_references.leaderboard_data is None:
            return {"error": "Leaderboard data not loaded yet"}
        pool = league_references.leaderboard_data

    candidates = pool
    if position != "ALL":
        candidates = [p for p in candidates if p["position"] == position]

    parsed_filters = []
    if filters:
        for chunk in filters.split(","):
            if ":" not in chunk:
                continue
            stat, min_value = chunk.split(":", 1)
            try:
                parsed_filters.append((stat, float(min_value)))
            except ValueError:
                continue

    for stat, threshold in parsed_filters:
        if stat in league_references.PITCHER_LOWER_IS_BETTER:
            candidates = [p for p in candidates if stat in p and p[stat] <= threshold]
        else:
            candidates = [p for p in candidates if stat in p and p[stat] >= threshold]

    default_sort_key = "fip" if is_pitcher_view else "ops"
    reverse_sort = default_sort_key not in league_references.PITCHER_LOWER_IS_BETTER
    sorted_candidates = sorted(candidates, key=lambda p: p.get(default_sort_key, 0), reverse=reverse_sort)
    top_candidates = sorted_candidates[:limit]

    results = []
    for player in top_candidates:
        headshot_url = f"https://img.mlbstatic.com/mlb-photos/image/upload/w_180,q_auto:best/v1/people/{player['player_id']}/headshot/67/current"
        results.append({
            "player_id": player["player_id"],
            "name": player["name"],
            "team": player["team"],
            "position": player["position"],
            "headshot_url": headshot_url,
            "stats": {k: v for k, v in player.items() if k not in ("player_id", "name", "team", "position")},
        })

    return {"position": position, "count": len(results), "players": results}