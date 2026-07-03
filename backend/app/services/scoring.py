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
        print(f"i={i}, ops={ops}, weight={weight}, weighted_sum={weighted_sum}, total_weight={total_weight}")
    return weighted_sum / total_weight
