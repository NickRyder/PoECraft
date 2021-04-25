import requests
from RePoE import mods
from PoECraft.item_rollers import ExplictlessItem, ExplicitModRoller, Influence
from tqdm import tqdm
from PoECraft.utils.performance import timer


from poe_craft.poe_craft import get_alt_aug_count as get_alt_aug_count_rust


def get_ninja_prices(name, league_name="Ultimatum"):
    prices = {}

    ninja_result = requests.get(
        f"https://poe.ninja/api/data/CurrencyOverview?league={league_name}&type={name}"
    ).json()
    for entry in ninja_result["lines"]:
        try:
            prices[entry["name"]] = entry["chaosValue"]
        except KeyError:
            prices[entry["currencyTypeName"]] = entry["chaosEquivalent"]
    return prices


currency_prices = get_ninja_prices("Currency")


def get_alt_prices(mod_name, item, trial_n=10 ** 7):
    generation_type = mods[mod_name]["generation_type"]
    roller = ExplicitModRoller(item)
    with timer("rust"):
        alt, aug, count = get_alt_aug_count_rust(
            roller, mod_name, generation_type, trial_n
        )
    with timer("python"):
        alt, aug, count = get_alt_aug_count(roller, mod_name, generation_type, trial_n)
    print(f"alt {alt} aug {aug}")
    return (alt / count) * currency_prices["Orb of Alteration"] + (
        aug / count
    ) * currency_prices["Orb of Augmentation"]


def get_alt_aug_count(
    roller,
    mod_name,
    generation_type,
    trial_n,
):
    count = 0
    alt = 0
    aug = 0

    for _ in tqdm(range(trial_n)):
        roller.roll_item_magic()
        alt += 1
        if mod_name in roller.affix_keys_current:
            count += 1
        else:
            aug_prefix = generation_type == "prefix" and roller.prefix_n == 0
            aug_suffix = generation_type == "suffix" and roller.suffix_n == 0
            if aug_prefix or aug_suffix:
                roller.roll_one_affix()
                aug += 1
                if mod_name in roller.affix_keys_current:
                    count += 1
    return alt, aug, count


if __name__ == "__main__":
    mod_name = "HolyPhysicalExplosionInfluence1"
    magic_astral_item = ExplictlessItem(
        "Astral Plate",
        quality=30,
        ilvl=86,
        influences=[Influence.CRUSADER],
        max_pre=1,
        max_suf=1,
    )
    print(get_alt_prices(mod_name, magic_astral_item))
    # alt 100000000 aug 28373602
    # 270.5354074635609
