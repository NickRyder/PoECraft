from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller, Influence
from tqdm import tqdm
from PoECraft.utils.visualizations import statistics, discrete_cdf, plot_show
from RePoE import fossils
from itertools import combinations
import numpy

"""
This script uses PoECraft and the poe.ninja api to calculate the best fossil
combo to get a desired outcome, (best in expected chaos)

Only measures binary outcomes
"""


def get_ninja_prices(name, league_name="Metamorph"):
    prices = {}
    import requests

    ninja_result = requests.get(
        f"https://poe.ninja/api/data/itemoverview?league={league_name}&type={name}"
    ).json()
    for entry in ninja_result["lines"]:
        prices[entry["name"]] = entry["chaosValue"]
    return prices


resonator_prices = get_ninja_prices("Resonator")
fossil_prices = get_ninja_prices("Fossil")

resonator_socket_to_price = {
    1: resonator_prices["Primitive Chaotic Resonator"],
    2: resonator_prices["Potent Chaotic Resonator"],
    3: resonator_prices["Powerful Chaotic Resonator"],
}


def get_odds_from_fossils(fossils, item, criteria, trial_N=10 ** 6):
    # Now we set up the roller with the dense fossil:
    roller = ExplicitModRoller(
        item, fossil_names=fossils  # essence_names=["Deafening Essence of Loathing"]
    )

    count = 0
    for _ in range(trial_N):
        # roll the item
        roller.roll_item()
        if criteria(roller):  # top_redeemer and top_delve:
            count += 1

    return count / trial_N


def get_best_fossil_combos(with_these_fossils, item, criteria):

    fossil_names = set([fossil["name"] for fossil in fossils.values()])
    for fixed_fossil in with_these_fossils:
        fossil_names.remove(fixed_fossil)

    trial_N = 10 ** 6

    fossil_to_percent = {}

    fixed_fossil_N = len(with_these_fossils)
    for socket_count in range(1, 4):
        if fixed_fossil_N <= socket_count:
            fossil_subsets = list(
                combinations(fossil_names, socket_count - fixed_fossil_N)
            )

            for fossil_subset in tqdm(fossil_subsets, total=len(fossil_subsets)):
                odds = get_odds_from_fossils(
                    list(fossil_subset) + with_these_fossils,
                    item,
                    criteria,
                    trial_N=trial_N,
                )
                price = sum(
                    [
                        fossil_prices[fossil]
                        for fossil in list(fossil_subset) + with_these_fossils
                    ]
                )

                fossil_to_percent[frozenset(fossil_subset)] = (
                    (1 / odds) * (price + resonator_socket_to_price[socket_count])
                    if odds != 0
                    else float("inf")
                )

    def sort_dict_by_value(x):
        return {
            k: v for k, v in sorted(x.items(), key=lambda item: item[1], reverse=True)
        }

    return sort_dict_by_value(fossil_to_percent)


if __name__ == "__main__":
    # Here we generate a base item which is a ilvl 100 vaal regalia with a single synthesis implicit, and 30 quality
    # hubris_circlet_item = ExplictlessItem(
    #     "Hubris Circlet", quality=30, ilvl=86, influences=[Influence.REDEEMER]
    # )

    # def double_mana_criteria(item_roller):
    #     top_influence = (
    #         "ReducedManaReservationInfluence2" in item_roller.affix_keys_current
    #     )
    #     top_delve = "DelveHelmetReducedManaReserved1" in item_roller.affix_keys_current
    #     return top_influence and top_delve

    # print(
    #     get_best_fossil_combos(["Lucent Fossil", "Bound Fossil"], hubris_circlet_item, double_mana_criteria)
    # )

    astral_item = ExplictlessItem(
        "Astral Plate", quality=30, ilvl=86, influences=[Influence.CRUSADER]
    )

    vaal_regalia = ExplictlessItem(
        "Vaal Regalia", quality=30, ilvl=86, influences=[Influence.HUNTER]
    )
    bow = ExplictlessItem("Recurve Bow", quality=30, ilvl=84, influences=[])

    def explode_criteria(item_roller):
        explode = "HolyPhysicalExplosionInfluence1" in item_roller.affix_keys_current
        top_delve = "DelveHelmetReducedManaReserved1" in item_roller.affix_keys_current
        return explode

    def double_crit_criteria(item_roller):
        top_attack = (
            "AdditionalCritWithAttacksInfluence2_" in item_roller.affix_keys_current
        )
        top_spell = (
            "AdditionalCritWithSpellsInfluence2" in item_roller.affix_keys_current
        )
        return top_attack and top_spell

    def kyle_criteria(item_roller):
        c1 = "DelveWeaponSocketedSpellsDamageFinal2h1" in item_roller.affix_keys_current
        c2 = "DelveWeaponVaalSoulCost2h1" in item_roller.affix_keys_current
        return c1 and c2

    odds = get_best_fossil_combos(
        ["Aetheric Fossil", "Bloodstained Fossil"], bow, kyle_criteria
    )
    print(odds)

    # item_names = [
    #     "Plate Vest",
    #     "Shabby Jerkin",
    #     "Simple Robe",
    #     "Scale Vest",
    #     "Chainmail Vest",
    #     "Padded Vest",
    # ]
    # for item_name in item_names:

    #     item = ExplictlessItem(
    #         item_name, quality=30, ilvl=86, influences=[Influence.CRUSADER]
    #     )
    #     odds = get_odds_from_fossils(
    #         ["Aetheric Fossil", "Dense Fossil", "Pristine Fossil"],
    #         item,
    #         explode_criteria,
    #         trial_N=10 ** 7,
    #     )
    #     print(f"{item_name:20} {odds}")

    # print(get_best_fossil_combos(['Aetheric Fossil'], astral_item, explode_criteria))
