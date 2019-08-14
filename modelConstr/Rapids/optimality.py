def findOptimal(gt, budget):
    selected = None
    max_mv = -1
    for config in gt.configurations:
        cost = gt.getCost(config)
        if cost > budget:
            continue
        mv = gt.getMV(config)[-1]
        if mv > max_mv:
            max_mv = mv
            selected = config
    return selected, max_mv
