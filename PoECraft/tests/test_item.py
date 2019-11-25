from RePoE import mods
from PoECraft.item_rollers import ExplicitModRoller, ExplictlessItem
from PoECraft.mod_collector import generate_all_possible_affixes_and_tags
from tqdm import tqdm
from collections import Counter

'''
smoke test
'''



test_item_mod_name = ["FireResist1", "IncreasedLife0", "IncreasedLife1", "IncreasedMana3", "ColdResist1", "LightningResist1", "StunRecovery2"]

test_item_mod_dictionary = {}
for mod_name in test_item_mod_name:
    test_item_mod_dictionary[mod_name] = mods[mod_name]

relevant_start_tags, added_tags, affixes = generate_all_possible_affixes_and_tags(starting_tags=["default", "belt"], mod_pool=test_item_mod_dictionary)
roller = ExplicitModRoller(ExplictlessItem("Leather Belt"))
roller.setup_cached_weight_draw(affixes,relevant_start_tags,added_tags)

def affix_counter_simulation(item_roller: ExplicitModRoller, trial_N = 10 ** 6):

    mod_counter = Counter()
    for trial_idx in tqdm(range(trial_N)):
        item_roller.roll_item()
        for affix_key in item_roller.affix_keys_current:
            if affix_key not in mod_counter:
                mod_counter[affix_key] = 0
            mod_counter[affix_key] += 1
    return mod_counter

def divide_counter(counter:Counter, dividend):
    divided_counter = {}
    for key, value in counter.items():
        divided_counter[key] = value/dividend
    return divided_counter


def counter_to_percentages(counter:Counter):
    total_sum = 0
    for key, value in counter.items():
        total_sum += value
    return divide_counter(counter, total_sum)
print(roller.cached_weight_draw.spawn_tags_to_spawn_weight)
print(roller.affix_key_pool)
trial_N = 10 ** 1
mod_counter = affix_counter_simulation(roller, trial_N = trial_N)
print(divide_counter(mod_counter, trial_N))