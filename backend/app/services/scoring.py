import math
from scipy.stats import percentileofscore
from app.services import league_references
def get_calculated_ops(seasons:list ) -> float:
    decay = 0.7
    weighted_sum = 0
    total_weight = 0

    seasons_reversed_list = list(reversed(seasons))
    for i in range(len(seasons_reversed_list)):
        season = seasons_reversed_list[i]
        ops = float(season["stat"]["ops"])
        weight = decay ** i
        weighted_sum = weighted_sum + (ops * weight)
        total_weight = total_weight + weight
        
    return weighted_sum / total_weight

def get_plate_discipline(seasons: list) -> float:
    walks = 0 
    strikeouts = 0
    for i in range(len(seasons)):
        season = seasons[i]
        walk = float(season["stat"]["baseOnBalls"])
        strikeout = float(season["stat"]["strikeOuts"])
        walks += walk
        strikeouts += strikeout
    
    if strikeouts == 0:
        return 0 
    else:
        return walks/strikeouts

def get_calculated_iso(seasons:list ) -> float:
    decay = 0.7
    weighted_sum = 0
    total_weight = 0


    seasons_reversed_list = list(reversed(seasons))
    for i in range(len(seasons_reversed_list)):
        season = seasons_reversed_list[i]
        season_avg = float(season["stat"]["avg"])
        season_slg = float(season["stat"]["slg"])
        weight = decay ** i
        iso = season_slg - season_avg
        weighted_sum = weighted_sum + (iso * weight)
        total_weight = total_weight + weight 
        

    return weighted_sum / total_weight

def get_mean(values: list) -> float:
    total = 0 
    for i in range(len(values)):
        total += values[i]
    return total / len(values)

def get_variance(values:list) -> float:
    total = 0
    average = get_mean(values)
    for i in range(len(values)):
        deviation = (average - values[i])**2
        total += deviation
    return total / len(values)
def get_standard_deviation(values:list) -> float:
    result = get_variance(values)
    return math.sqrt(result)

def get_consistency_score(values: list) -> float:
    result = get_standard_deviation(values)
    return 1 / (1+result)

def get_age_multiplier(age: int) -> float:
    peak_age = 28
    k = 0.003
    multiplier = 1 - k * (age-peak_age) ** 2
    floor = 0.5
    if multiplier < floor:
        return floor 
    else: 
        return multiplier

def get_position_multiplier(position: str) -> float:
    if position in ["LF", "CF", "RF"]:
        position = "OF"
    multipliers = {
        "C": 1.20,
        "SS": 1.15,
        "2B": 1.15,
        "3B": 1.05,
        "OF": 1.00,
        "1B": 0.95,
        "DH": 0.90,
    }
    return multipliers.get(position, 1.00)

def get_defense_modifier(seasons: list) -> float:
    total = 0
    count = 0
    for i in range(len(seasons)):
        season = seasons[i]
        chances = float(season["stat"].get("chances", 0))
        if chances == 0:
            continue
        current_percent = float(season["stat"].get("fielding", 1.0))
        total += current_percent
        count += 1

    if count == 0:
        return 1.0

    return total / count

def get_draft_score(offense_seasons: list, fielding_seasons: list, age: int, position: str, reference_distributions: dict = None) -> float:
    ops_values = []
    for season in offense_seasons:
        ops_values.append(float(season["stat"]["ops"]))
    ops = get_calculated_ops(offense_seasons)
    discipline = get_plate_discipline(offense_seasons)
    iso = get_calculated_iso(offense_seasons)

    if reference_distributions is None:
        reference_distributions = league_references.reference_distributions

    consistency = get_consistency_score(ops_values)
    scaled_ops = get_percentile_score(ops, reference_distributions["ops"])
    scaled_discipline = get_percentile_score(discipline, reference_distributions["discipline"])
    scaled_iso = get_percentile_score(iso, reference_distributions["iso"])
    a_multiplier = get_age_multiplier(age)
    p_multiplier = get_position_multiplier(position)
    d_multiplier = get_defense_modifier(fielding_seasons)

    base_score = (scaled_ops * 0.4) + (scaled_discipline * 0.25) + (scaled_iso * 0.2) + (consistency * 0.15)
    final_score = base_score * a_multiplier * p_multiplier * d_multiplier
    return final_score

def get_percentile_score(value: float, distribution : list) -> float:

    result = percentileofscore(distribution, value)
    result = result / 100
    return result

def get_stat_breakdown(offense_seasons: list, reference_distributions: dict = None) -> dict:
    if reference_distributions is None:
        reference_distributions = league_references.reference_distributions

    if not offense_seasons:
        return {"scoring_stats": [], "baseline_stats": []}
    recent = offense_seasons[-1]["stat"]
    home_runs = float(recent["homeRuns"])
    runs = float(recent["runs"])
    rbi = float(recent["rbi"])
    avg = float(recent["avg"])
    stolen_bases = float(recent["stolenBases"])
    hit = float(recent["hits"])
    ops = float(recent["ops"])
    walk = float(recent["baseOnBalls"])
    strikeout = float(recent["strikeOuts"])
    discipline = walk/strikeout
    slg = float(recent["slg"])
    iso = slg - avg

    home_runs_percent = round(100 * get_percentile_score(home_runs, reference_distributions["home_runs"]))
    runs_percent = round(100 * get_percentile_score(runs, reference_distributions["runs"]))
    rbi_percent = round(100 * get_percentile_score(rbi, reference_distributions["rbi"]))
    stolen_bases_percent = round(100 * get_percentile_score(stolen_bases, reference_distributions["stolen_bases"]))
    avg_percent = round(100 * get_percentile_score(avg, reference_distributions["avg"]))
    hits_percent = round(100 * get_percentile_score(hit, reference_distributions["hits"]))

    ops_percent = round(100 * get_percentile_score(ops, reference_distributions["ops"]))
    iso_percent = round(100 * get_percentile_score(iso, reference_distributions["iso"]))
    discipline_percent = round(100 * get_percentile_score(discipline, reference_distributions["discipline"]))

    scoring_stats = [
        {"label": "HR", "value": int(home_runs), "percentile": home_runs_percent},
        {"label": "R", "value": int(runs), "percentile": runs_percent},
        {"label": "RBI", "value": int(rbi), "percentile": rbi_percent},
        {"label": "SB", "value": int(stolen_bases), "percentile": stolen_bases_percent},
        {"label": "AVG", "value": round(avg, 3), "percentile": avg_percent},
        {"label": "H", "value": int(hit), "percentile": hits_percent},
    ]

    baseline_stats = [
        {"label": "OPS", "value": round(ops, 3), "percentile": ops_percent},
        {"label": "ISO", "value": round(iso, 3), "percentile": iso_percent},
        {"label": "Discipline", "value": round(discipline, 2), "percentile": discipline_percent},
    ]

    return {"scoring_stats": scoring_stats, "baseline_stats": baseline_stats}

def get_ml_features(offense_seasons: list, fielding_seasons: list, age: int, position: str, draft_score: float, reference_distributions: dict = None) -> list:
    if reference_distributions is None:
        reference_distributions = league_references.reference_distributions

    recent = offense_seasons[-1]["stat"]

    ops = get_calculated_ops(offense_seasons)
    discipline = get_plate_discipline(offense_seasons)
    iso = get_calculated_iso(offense_seasons)

    home_runs = float(recent["homeRuns"])
    stolen_bases = float(recent["stolenBases"])
    walks = float(recent["baseOnBalls"])
    strikeouts = float(recent["strikeOuts"])
    plate_appearances = float(recent["plateAppearances"])

    walk_rate = walks / plate_appearances
    strikeout_rate = strikeouts / plate_appearances

    age_multiplier = get_age_multiplier(age)
    position_value = get_position_multiplier(position)

    ops_scaled = get_percentile_score(ops, reference_distributions["ops"])
    discipline_scaled = get_percentile_score(discipline, reference_distributions["discipline"])
    iso_scaled = get_percentile_score(iso, reference_distributions["iso"])
    home_runs_scaled = get_percentile_score(home_runs, reference_distributions["home_runs"])
    stolen_bases_scaled = get_percentile_score(stolen_bases, reference_distributions["stolen_bases"])

    return [
        ops_scaled,
        discipline_scaled,
        iso_scaled,
        age_multiplier,
        position_value,
        draft_score,
        home_runs_scaled,
        stolen_bases_scaled,
        walk_rate,
        strikeout_rate,
        plate_appearances,
    ]

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

def get_calculated_fip(seasons: list, fip_constant: float) -> float:
    decay = 0.7
    weighted_sum = 0
    total_weight = 0

    seasons_reversed_list = list(reversed(seasons))
    for i in range(len(seasons_reversed_list)):
        season = seasons_reversed_list[i]
        stat = season["stat"]
        home_runs = float(stat["homeRuns"])
        walks = float(stat["baseOnBalls"])
        hit_by_pitch = float(stat.get("hitByPitch", 0))
        strikeouts = float(stat["strikeOuts"])
        innings_pitched = parse_innings_pitched(stat["inningsPitched"])

        fip = (((13 * home_runs) + (3 * (walks + hit_by_pitch)) - (2 * strikeouts)) / innings_pitched) + fip_constant
        weight = decay ** i
        weighted_sum += fip * weight
        total_weight += weight

    return weighted_sum / total_weight

def get_calculated_whip(seasons: list) -> float:
    decay = 0.7
    weighted_sum = 0
    total_weight = 0

    seasons_reversed_list = list(reversed(seasons))
    for i in range(len(seasons_reversed_list)):
        season = seasons_reversed_list[i]
        whip = float(season["stat"]["whip"])
        weight = decay ** i
        weighted_sum += whip * weight
        total_weight += weight

    return weighted_sum / total_weight

def get_calculated_k9(seasons: list) -> float:
    decay = 0.7
    weighted_sum = 0
    total_weight = 0

    seasons_reversed_list = list(reversed(seasons))
    for i in range(len(seasons_reversed_list)):
        season = seasons_reversed_list[i]
        stat = season["stat"]
        if "strikeoutsPer9Inn" in stat:
            k9 = float(stat["strikeoutsPer9Inn"])
        else:
            strikeouts = float(stat["strikeOuts"])
            innings_pitched = parse_innings_pitched(stat["inningsPitched"])
            k9 = (strikeouts / innings_pitched) * 9
        weight = decay ** i
        weighted_sum += k9 * weight
        total_weight += weight

    return weighted_sum / total_weight

def get_calculated_durability(seasons: list) -> float:
    decay = 0.7
    weighted_sum = 0
    total_weight = 0

    seasons_reversed_list = list(reversed(seasons))
    for i in range(len(seasons_reversed_list)):
        season = seasons_reversed_list[i]
        innings_pitched = parse_innings_pitched(season["stat"]["inningsPitched"])
        weight = decay ** i
        weighted_sum += innings_pitched * weight
        total_weight += weight

    return weighted_sum / total_weight

def get_pitcher_draft_score(pitching_seasons: list, age: int, fip_constant: float, reference_distributions: dict = None) -> float:
    if reference_distributions is None:
        reference_distributions = league_references.pitcher_reference_distributions

    fip = get_calculated_fip(pitching_seasons, fip_constant)
    whip = get_calculated_whip(pitching_seasons)
    k9 = get_calculated_k9(pitching_seasons)
    durability = get_calculated_durability(pitching_seasons)

    scaled_fip = 1 - get_percentile_score(fip, reference_distributions["fip"])
    scaled_whip = 1 - get_percentile_score(whip, reference_distributions["whip"])
    scaled_k9 = get_percentile_score(k9, reference_distributions["k9"])
    scaled_durability = get_percentile_score(durability, reference_distributions["ip"])

    a_multiplier = get_age_multiplier(age)

    base_score = (scaled_fip * 0.4) + (scaled_whip * 0.25) + (scaled_k9 * 0.2) + (scaled_durability * 0.15)
    return base_score * a_multiplier

def get_pitcher_stat_breakdown(pitching_seasons: list, fip_constant: float, reference_distributions: dict = None) -> dict:
    if reference_distributions is None:
        reference_distributions = league_references.pitcher_reference_distributions

    if not pitching_seasons:
        return {"scoring_stats": [], "baseline_stats": []}

    recent = pitching_seasons[-1]["stat"]
    era = float(recent.get("era", 0))
    whip = float(recent.get("whip", 0))
    wins = float(recent.get("wins", 0))
    saves = float(recent.get("saves", 0))
    strikeouts = float(recent.get("strikeOuts", 0))
    innings_pitched = parse_innings_pitched(recent.get("inningsPitched", "0.0"))

    home_runs = float(recent.get("homeRuns", 0))
    walks = float(recent.get("baseOnBalls", 0))
    hit_by_pitch = float(recent.get("hitByPitch", 0))
    fip = (((13 * home_runs) + (3 * (walks + hit_by_pitch)) - (2 * strikeouts)) / innings_pitched) + fip_constant

    era_percent = round(100 * (1 - get_percentile_score(era, reference_distributions["era"])))
    whip_percent = round(100 * (1 - get_percentile_score(whip, reference_distributions["whip"])))
    wins_percent = round(100 * get_percentile_score(wins, reference_distributions["wins"]))
    saves_percent = round(100 * get_percentile_score(saves, reference_distributions["saves"]))
    strikeouts_percent = round(100 * get_percentile_score(strikeouts, reference_distributions["strikeouts"]))
    ip_percent = round(100 * get_percentile_score(innings_pitched, reference_distributions["ip"]))
    fip_percent = round(100 * (1 - get_percentile_score(fip, reference_distributions["fip"])))

    scoring_stats = [
        {"label": "W", "value": int(wins), "percentile": wins_percent},
        {"label": "SV", "value": int(saves), "percentile": saves_percent},
        {"label": "K", "value": int(strikeouts), "percentile": strikeouts_percent},
        {"label": "IP", "value": round(innings_pitched, 1), "percentile": ip_percent},
    ]

    baseline_stats = [
        {"label": "ERA", "value": round(era, 2), "percentile": era_percent},
        {"label": "WHIP", "value": round(whip, 2), "percentile": whip_percent},
        {"label": "FIP", "value": round(fip, 2), "percentile": fip_percent},
    ]

    return {"scoring_stats": scoring_stats, "baseline_stats": baseline_stats}