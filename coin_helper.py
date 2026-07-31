from boost_manager import boost_schedule

def apply_coin_boost(coins: int):
    multiplier = 1.0
    reasons = []

    if boost_schedule.coins_active():
        multiplier *= 2
        reasons.append("<:oathcoin:1462999179998531614> Double Coin Boost")

    if boost_schedule.triple_active():
        multiplier *= 3
        reasons.append("<:oathcoin:1462999179998531614> TRIPLE Coin Boost")

    return int(coins * multiplier), reasons


def apply_gem_boost(gems: int):
    multiplier = 1.0
    reasons = []

    if boost_schedule.gems_active():
        multiplier *= 2
        reasons.append("<:gems:1485660490376937502> Double Gem Boost")

    if boost_schedule.triple_active():
        multiplier *= 3
        reasons.append("<:gems:1485660490376937502> TRIPLE Gem Boost")

    return int(gems * multiplier), reasons
