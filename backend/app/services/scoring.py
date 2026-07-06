import math
def get_calculated_ops(seasons:list ) -> float:
    decay = 0.7
    weighted_sum = 0
    total_weight = 0

    seasons_reversed_list = list(reversed(seasons))
    for i in range(len(seasons_reversed_list)):
        season = seasons_reversed_list[i]
        ops = float(season["stat"]["ops"])
        weight = decay ** i
        weighted_sum =weighted_sum + (ops * weight)
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
    for i in range(len(seasons)):
        season = seasons[i]
        current_percent = float(season["stat"]["fieldingPercentage"])
        total += current_percent
    return total/len(seasons)

# TODO: replace with dynamic percentile bounds from league-wide data (V2)

def normalize(value: float, min_val: float, max_val: float) -> float:
    return (value-min_val) / (max_val - min_val)


def get_draft_score(offense_seasons: list, fielding_seasons: list, age: int, position: str) -> float:
    ops_values = []
    for season in offense_seasons:
        ops_values.append(float(season["stat"]["ops"]))
    ops = get_calculated_ops(offense_seasons)
    discipline = get_plate_discipline(offense_seasons)
    iso = get_calculated_iso(offense_seasons)
    
    consistency = get_consistency_score(ops_values)
    scaled_ops = normalize(ops, 0.55, 1.05)
    scaled_discipline = normalize(discipline, 0.15, 0.7)
    scaled_iso  = normalize(iso, 0.08, 0.3)
    a_multiplier = get_age_multiplier(age)
    p_multiplier = get_position_multiplier(position)
    d_multiplier = get_defense_modifier(fielding_seasons)

    base_score = (scaled_ops * 0.4) + (scaled_discipline * 0.25) + (scaled_iso * 0.2) +(consistency * 0.15)
    final_score = base_score * a_multiplier * p_multiplier * d_multiplier
    return final_score