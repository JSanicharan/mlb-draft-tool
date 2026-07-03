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
if __name__ == "__main__":
    test_seasons = [
        {"stat": {"baseOnBalls": "40", "strikeOuts": "145"}},
        {"stat": {"baseOnBalls": "47", "strikeOuts": "175"}},
    ]
    print(get_plate_discipline(test_seasons))