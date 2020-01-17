import requests
from RePoE import mods
from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller, Influence
from tqdm import tqdm


def get_ninja_prices(name, league_name="Metamorph"):
    prices = {}
    import requests

    ninja_result = requests.get(
        f"https://poe.ninja/api/data/itemoverview?league={league_name}&type={name}"
    ).json()
    for entry in ninja_result["lines"]:
        try:
            prices[entry["name"]] = entry["chaosValue"]
        except KeyError:
            prices[entry["currencyTypeName"]] = entry["chaosEquivalent"]
    return prices


currency_prices = get_ninja_prices("Currency")


def get_alt_prices(mod_name, item, trial_N=10 ** 8):
    generation_type = mods[mod_name]["generation_type"]
    roller = ExplicitModRoller(item, max_pre=1, max_suff=1)
    count = 0
    alt = 0
    aug = 0

    for _ in tqdm(range(trial_N)):
        roller.roll_item_magic()
        alt += 1
        if mod_name in roller.affix_keys_current:
            count += 1
        else:
            aug_prefix = generation_type == "prefix" and roller.prefix_N == 0
            aug_suffix = generation_type == "suffix" and roller.suffix_N == 0
            if aug_prefix or aug_suffix:
                roller.roll_one_affix()
                aug += 1
                if mod_name in roller.affix_keys_current:
                    count += 1

    print(f"alt {alt} aug {aug}")
    return (alt / count) * currency_prices["Orb of Alteration"] + (
        aug / count
    ) * currency_prices["Orb of Augmentation"]


if __name__ == "__main__":
    mod_name = "HolyPhysicalExplosionInfluence1"
    astral_item = ExplictlessItem(
        "Astral Plate", quality=30, ilvl=86, influences=[Influence.CRUSADER]
    )
    print(get_alt_prices(mod_name, astral_item))
    # alt 100000000 aug 28373602
    # 270.5354074635609
