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
