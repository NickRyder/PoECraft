from RePoE import mods
from PoECraft.item_rollers import ExplicitModRoller, ExplictlessItem
from PoECraft.mod_collector import generate_all_possible_affixes_and_tags
from tqdm import tqdm
from collections import Counter

'''
smoke test

rolls an item with 7 affixes, equal weight, 4 prefixes, 3 suffixes. 2 of the suffixes share a mod group, none of the others do.
this effectively only tests mod group rolling
'''

test_item_mod_name = ["FireResist1", "IncreasedLife0", "IncreasedLife1", "IncreasedMana3", "ColdResist1", "LightningResist1", "AttackerTakesDamage1"]
affix_key_to_label = {"FireResist1": "C", "ColdResist1": "C", "LightningResist1": "C", "IncreasedLife0": "A", "IncreasedLife1": "A", "IncreasedMana3": "B", "AttackerTakesDamage1": "B"}

def simulator_grab_label_counts(item_roller: ExplicitModRoller, trial_N = 10 ** 6):

    affix_combo_counter = {}
    for trial_idx in tqdm(range(trial_N)):
        item_roller.roll_item()
        labels = []
        for affix_key in item_roller.affix_keys_current:
            labels.append(affix_key_to_label[affix_key])
        labels.sort()
        labels = tuple(labels)
        if labels in affix_combo_counter:
            affix_combo_counter[labels] += 1
        else:
            affix_combo_counter[labels] = 1

    return affix_combo_counter

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


def exact_type_numbers():
    l = ['A', 'A', 'B', 'B', 'C', 'C', 'C']
    def generate_total_depth_types(current_items, total_depth):
        remaining_to_prob = {}
        def draw_from_current_items(current_items, probability = 1, depth = 0, chosen_affixes = []):
            if depth < total_depth:
                for idx in range(len(current_items)):
                    current_items_leaf = current_items.copy()
                    chosen_affixes_leaf = chosen_affixes.copy()
                    chosen_affixes_leaf.append(current_items_leaf[idx])
                    if current_items_leaf[idx] == 'A':
                        current_items_leaf = [i for i in current_items_leaf if i != 'A']
                    else:
                        del current_items_leaf[idx]
                    draw_from_current_items(current_items_leaf, probability * 1/len(current_items), depth = depth + 1,chosen_affixes=chosen_affixes_leaf )
            else:
                chosen_affixes.sort()
                final_items = tuple(chosen_affixes)
                if final_items not in remaining_to_prob:
                    remaining_to_prob[final_items] = 0
                remaining_to_prob[final_items] += probability
        draw_from_current_items(current_items)
        return remaining_to_prob
        
    affix_4 = generate_total_depth_types(l,4)
    affix_5 = generate_total_depth_types(l,5)
    affix_6 = generate_total_depth_types(l,6)
    total_affixes = {}
    for key, value in affix_6.items():
        total_affixes[key] = value * 1/12
    for key, value in affix_5.items():
        total_affixes[key] = value * 3/12
    for key, value in affix_4.items():
        total_affixes[key] = value * 8/12
    return total_affixes

def test_single_tag():
    roller = ExplicitModRoller(ExplictlessItem("Searching Eye Jewel"))
    bow_idx = roller.affix_key_pool.index("AbyssAddedLightningDamageWithBowsJewel4")
    print(bin(roller.tags_current))
    roller.add_affix(bow_idx)
    print(bin(roller.tags_current))
    print(roller.cached_weight_draw.spawn_tags_to_spawn_weight[roller.tags_current])
    wand_idx = roller.affix_key_pool.index("AbyssAddedFireDamageWithWandsJewel4")
    assert roller.cached_weight_draw.spawn_tags_to_spawn_weight[roller.tags_current][wand_idx] == 0, "wands and bows should block"

    print("REMOVED MODS:")
    base = roller.cached_weight_draw.weights_cummulative[roller.tags_current]
    last = 0
    for idx, weight in enumerate(base):
        if last == weight:
            print(roller.affix_key_pool[idx])
        last = weight

    diff = roller.cached_weight_draw.group_diff_prefix_cummulative[roller.tags_current][bow_idx]
    last = 0
    for idx, weight in enumerate(diff):
        if last != weight:
            print(roller.affix_key_pool[idx])
        last = weight

    diff = roller.cached_weight_draw.group_diff_suffix_cummulative[roller.tags_current][bow_idx]
    last = 0
    for idx, weight in enumerate(diff):
        if last != weight:
            print(roller.affix_key_pool[idx])
        last = weight


def test_single_generation_tag():

    roller = ExplicitModRoller(ExplictlessItem("Driftwood Sceptre"))

    cast_mod = roller.affix_key_pool.index("ColdDamageOverTimeMultiplier1h5")
    attack_mod = roller.affix_key_pool.index("LocalAddedColdDamage10__")
    cast_before = roller.cached_weight_draw.spawn_tags_to_spawn_weight[roller.tags_current][cast_mod]
    attack_before = roller.cached_weight_draw.spawn_tags_to_spawn_weight[roller.tags_current][attack_mod]
    roller.add_affix(cast_mod)
    cast_after = roller.cached_weight_draw.spawn_tags_to_spawn_weight[roller.tags_current][cast_mod]
    attack_after = roller.cached_weight_draw.spawn_tags_to_spawn_weight[roller.tags_current][attack_mod]
    roller.clear_item()
    assert cast_before == cast_after, "caster shouldnt change"
    assert attack_before > attack_after, "attack should change"

    cast_before = roller.cached_weight_draw.spawn_tags_to_spawn_weight[roller.tags_current][cast_mod]
    attack_before = roller.cached_weight_draw.spawn_tags_to_spawn_weight[roller.tags_current][attack_mod]
    roller.add_affix(attack_mod)
    cast_after = roller.cached_weight_draw.spawn_tags_to_spawn_weight[roller.tags_current][cast_mod]
    attack_after = roller.cached_weight_draw.spawn_tags_to_spawn_weight[roller.tags_current][attack_mod]
    roller.clear_item()
    assert attack_before == attack_after, "attack shouldnt change"
    assert cast_before > cast_after, "cast should change"


def test_smoke_tags(trial_N = 10**6):
    roller = ExplicitModRoller(ExplictlessItem("Searching Eye Jewel"))
    for trial_idx in tqdm(range(trial_N)):
        roller.roll_item()
        keys = roller.affix_keys_current
        bow_in = True in [ "Bow" in key for key in keys]
        wand_in = True in [ "Wand" in key for key in keys]
        assert not bow_in or not wand_in, "cant have both bow and wand"

def test_smoke_prefix_suffix_group():
    pass


def test_smoke(trial_N = 10 ** 6):
    test_item_mod_dictionary = {}
    for mod_name in test_item_mod_name:
        test_item_mod_dictionary[mod_name] = mods[mod_name]

    relevant_start_tags, added_tags, affixes = generate_all_possible_affixes_and_tags(starting_tags=["default", "belt"], mod_pool=test_item_mod_dictionary)
    roller = ExplicitModRoller(ExplictlessItem("Leather Belt"))
    roller.setup_cached_weight_draw(affixes,relevant_start_tags,added_tags)

    print(roller.cached_weight_draw.spawn_tags_to_spawn_weight)
    print(roller.affix_key_pool)
    mod_counter = simulator_grab_label_counts(roller, trial_N = trial_N)
    type_counter = divide_counter(mod_counter, trial_N)
    exact_counter = exact_type_numbers()

    for key, value in type_counter.items():
        exact_value = exact_counter[key] 
        relative = (exact_value-value)/exact_value
        assert abs(relative) < .1, f"exact and simulated dont match, {exact_value, value}"


if __name__ == "__main__":
    test_single_generation_tag()
    test_smoke_tags()
    test_single_tag()
    test_smoke()
