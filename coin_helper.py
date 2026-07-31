from boost_manager import boost_schedule

def apply_coin_boost(coins: int):
    multiplier = 1.0
    reasons = []

    if boost_schedule.gold_active() or boost_schedule.class_active():
        multiplier *= 2
        reasons.append("<:oathcoin:1462999179998531614> Double Gold Boost")

    if boost_schedule.current_boost() == "TRIPLE":
        multiplier *= 3
        reasons.append("<:oathcoin:1462999179998531614> TRIPLE Gold Boost")


    return int(coins * multiplier), reasons

def apply_gem_boost(coins: int):
    multiplier = 1.0
    reasons = []

    if boost_schedule.rep_active() or boost_schedule.exp_active():
        multiplier *= 2
        reasons.append("<:gems:1485660490376937502> Double Gem Boost")

    if boost_schedule.current_boost() == "TRIPLE":
        multiplier *= 3
        reasons.append("<:gems:1485660490376937502> Double Gem Boost")

    return int(coins * multiplier), reasons
