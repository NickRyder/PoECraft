import numpy as np
from copy import deepcopy

pdps_dict = {
    "local_minimum_added_physical_damage": [],
    "local_maximum_added_physical_damage": [],
    "physical_damage_+%": [],
    "local_attack_speed_+%": [],
    "local_item_quality_+": [],
}

crafts_affixes = {
    "LocalPhysicalDamagePercent": "prefix",
    "PhysicalDamage": "prefix",
    "IncreasedAttackSpeed": "suffix",
    "CriticalStrikeChanceIncrease": "suffix",
    "": None,
}


def price_pdps(pdps):
    if pdps < 300:
        return 0
    elif pdps < 400:
        return 10 ** (1 + (pdps - 300) * 1.6 / 100)
    elif pdps < 600:
        return 10 ** ((1.0 / 18000.0) * (pdps - 400) ** 2 + 2.6)
    else:
        return 66408


# def pdps_from_affixes(item):
#     pdps_dict = {"local_minimum_added_physical_damage": [], "local_maximum_added_physical_damage": [],
#                   "local_physical_damage_+%": [], "local_attack_speed_+%": [], "local_item_quality_+": []}
#     affix_groups = []
#     prefix_n = item.prefix_n
#     suffix_n = item.suffix_n
#
#     affixes = item.affix_keys
#     affix_dict = item.hash_weight_dict.base_dict
#
#     for affix in affixes:
#
#         affix_groups.append(affix_dict[affix]["group"])
#         for stat in affix_dict[affix]["stats"]:
#             id = stat["id"]
#             if id in pdps_dict:
#                 pdps_dict[id].append([stat["min"], stat["max"]])
#
#     crafts = average_pdps(pdps_dict)
#     open_affixes = [None]
#     if prefix_n < 3:
#         open_affixes.append("prefix")
#     elif suffix_n < 3:
#         open_affixes.append("suffix")
#
#     sorted_crafts = sorted(crafts, key=crafts.get)
#     sorted_crafts.reverse()
#     for craft in sorted_crafts:
#         if craft not in affix_groups and crafts_affixes[craft] in open_affixes:
#             # if craft == "IncreasedAttackSpeed":
#             #     print("ias")
#             return crafts[craft]


pdps_stats = {
    "local_minimum_added_physical_damage",
    "local_maximum_added_physical_damage",
    "local_physical_damage_+%",
    "local_attack_speed_+%",
    "local_item_quality_+",
}
pdps_groups = {
    "LocalPhysicalDamagePercent": "prefix",
    "PhysicalDamage": "prefix",
    "IncreasedAttackSpeed": "suffix",
    "CriticalStrikeChanceIncrease": "suffix",
    "": None,
}
es_groups = {
    "DefencesPercent": "prefix",
    "BaseLocalDefences": "prefix",
    "BaseLocalDefencesAndLife": "prefix",
    "Dexterity": "suffix",
    "Strength": "suffix",
    "": None,
}


def best_craft(item, craft_groups, eval_func, verbose=False):

    prefix_n = item.prefix_n
    suffix_n = item.suffix_n

    affix_groups = item.affix_groups

    crafts = eval_func(item)

    open_affixes = [None]
    if prefix_n < 3:
        open_affixes.append("prefix")
    elif suffix_n < 3:
        open_affixes.append("suffix")

    sorted_crafts = sorted(crafts, key=crafts.get)
    sorted_crafts.reverse()
    for craft in sorted_crafts:
        if craft not in affix_groups and craft_groups[craft] in open_affixes:
            if verbose:
                print(craft)
            return crafts[craft]


# jewelled foil 32-60, 1.6
def average_pdps(pdps_dict, base_flat=46, base_qual=20, base_ias=1.6):

    average_flat = (
        np.sum(pdps_dict["local_minimum_added_physical_damage"])
        + np.sum(pdps_dict["local_maximum_added_physical_damage"])
    ) / 4.0
    average_phys = np.sum(pdps_dict["local_physical_damage_+%"]) / 2.0
    average_qual = np.sum(pdps_dict["local_item_quality_+"]) / 2.0
    average_ias = np.sum(pdps_dict["local_attack_speed_+%"]) / 2.0

    # average_flat = np.nan_to_num(average_flat)
    # average_phys = np.nan_to_num(average_phys)
    # average_qual = np.nan_to_num(average_qual)
    # average_ias = np.nan_to_num(average_ias)
    #
    # print(average_flat, average_phys, average_qual, average_ias)

    flat = average_flat + base_flat
    qual = 100 + base_qual + average_qual + average_phys
    ias = 100 + average_ias

    crafts = {
        "LocalPhysicalDamagePercent": flat * (qual + 124.5) * ias * base_ias / 100 ** 2,
        "PhysicalDamage": (flat + 43) * qual * ias * base_ias / 100 ** 2,
        "IncreasedAttackSpeed": max(
            flat * qual * (ias + 18) * base_ias / 100 ** 2,
            flat * (qual + 15.5) * (ias + 14.5) * base_ias / 100 ** 2,
        ),
        "CriticalStrikeChanceIncrease": flat
        * (qual + 15.5)
        * ias
        * base_ias
        / 100 ** 2,
        "": flat * qual * ias * base_ias / 100 ** 2,
    }

    return crafts


def average_es(item):
    average_flat, average_percent, average_qual = 0, 0, 0

    stat_dict = item.stats
    base_qual = item.quality

    try:
        average_flat = np.sum(stat_dict["local_energy_shield"]) / 2.0
    except KeyError:
        pass
    try:
        average_percent = np.sum(stat_dict["local_energy_shield_+%"]) / 2.0
    except KeyError:
        pass
    try:
        average_qual = np.sum(stat_dict["local_item_quality_+"]) / 2.0
    except KeyError:
        pass

    base_flat = 0
    try:
        base_flat = item.properties["energy_shield"]
    except KeyError:
        pass

    flat = average_flat + base_flat
    qual = 100 + base_qual + average_qual + average_percent

    crafts = {
        "DefencesPercent": flat * (qual + 65) / 100,
        "BaseLocalDefences": (flat + 62.5) * qual / 100,
        "BaseLocalDefencesAndLife": (flat) * (qual + 38) / 100,
        "Dexterity": flat * (qual + 16.5) / 100,
        "Strength": flat * (qual + 16.5) / 100,
        "": flat * qual / 100,
    }

    return crafts


def map_quant(affixes, base_dict):
    quant = 0
    for affix in affixes:
        affix_data = base_dict[affix]
        for stat in affix_data["stats"]:
            if stat["id"] == "map_item_drop_quantity_+%":
                quant += (stat["min"] + stat["max"]) / 2
    return quant


# import json
# with open('mods.json') as f:
#     data = json.load(f)

# print(pdps_from_affixes(["LocalIncreasedPhysicalDamagePercent8", "LocalAddedPhysicalDamage9", "LocalIncreasedPhysicalDamagePercentAndAccuracyRating8", "LocalIncreasedAttackSpeed8" ], data))
# print(pdps_from_affixes(["LocalIncreasedPhysicalDamagePercent8", "LocalAddedPhysicalDamage9", "LocalIncreasedPhysicalDamagePercentAndAccuracyRating8"], data))

# import numpy as np
# import random
# import time
# #
# N = 10**3
# trial_N = 10**7
#
#
# tic = time.time()
# for i in range(trial_N):
#     continue
# print("empty loop", time.time() - tic)
#
# tic = time.time()
# for i in range(trial_N):
#     int(random.random()*N)
# print("random.random", time.time() - tic)
#
#
# # tic = time.time()
# # for i in range(trial_N):
# #     random.randint(0,N-1)
# # print("random.randint", time.time() - tic)
#
#
# tic = time.time()
# arr = list(np.random.rand(trial_N))
# for i in range(trial_N):
#     int(arr[i]*N)
# print("numpy.random.rand", time.time() - tic)
#
#
# tic = time.time()
# arr = np.random.randint(N,size=trial_N)
# for i in range(trial_N):
#     arr[i]
# print("numpy.random.randint", time.time() - tic)
