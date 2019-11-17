
from repoe_import import repoe_data
affix_strings = {}

for stat_translation in repoe_data["stat_translations"]:
    # if len(set(stat_translation["ids"]).intersection(ignore)) == 0:
    for string in stat_translation["English"]:
        affix_string = string["string"]
        # for condition_dict in string["condition"]:
        #     conditions = conditions.union(condition_dict.keys())
        if affix_string not in affix_strings:
            affix_strings[affix_string] = []
        affix_strings[affix_string].append(stat_translation)




index_handlers_multipliers = {'negate' : -1, 'canonical_stat' : 1, 'divide_by_fifteen_0dp' : 15, 'per_minute_to_per_second_1dp' : 60,
                     'divide_by_twenty_then_double_0dp' : 10, '60%_of_value' : 5.0/3, 'divide_by_one_hundred_2dp' : 100,
                     'milliseconds_to_seconds_0dp' : 1000, 'per_minute_to_per_second_2dp_if_required' : 60,
                     'deciseconds_to_seconds' : 10, 'divide_by_ten_0dp' : 10, 'multiplicative_damage_modifier' : 1,
                     'milliseconds_to_seconds' : 1000, 'mod_value_to_item_class' : 1, 'old_leech_percent' : 1, 'old_leech_permyriad' : 10000,
                     '30%_of_value' : 10.0/3, 'per_minute_to_per_second_0dp' : 60, 'per_minute_to_per_second' : 60, 'divide_by_two_0dp' : 2,
                     'milliseconds_to_seconds_2dp' : 1000, 'divide_by_one_hundred' : 100}


import difflib
import re

#First chunk: rarity, name, type
#Second chunk:
def get_stat_possibilities(text, verbose = False):
    text_chunk_lines = [text_chunk.splitlines() for text_chunk in text.split("--------\n")]

    rarity = text_chunk_lines[0][0][8:]
    base_type = text_chunk_lines[0][-1]

    if verbose:
        print(rarity)
        print(base_type)
        print(text_chunk_lines)



    assert text_chunk_lines[-1][0] != "Corrupted", "Corrupted items not supported currently"
    elder = False
    shaper = False
    if text_chunk_lines[-1][0] == "Elder Item":
        elder = True
        text_chunk_lines.pop()

    if text_chunk_lines[-1][0] == "Shaper Item":
        shaper = True
        text_chunk_lines.pop()

    ilvl = 100
    for chunk in text_chunk_lines:
        if "Item Level: " in chunk[0]:
            ilvl = int(chunk[0][12:])

    assert rarity != "Unique", "Unique items not supported currently"
    assert rarity != "Currency", "Currency items not supported currently"
    assert rarity != "Gem", "Gem items not supported currently"

    affix_lines = text_chunk_lines[-1]

    stat_possibilities_per_line = []

    for affix_line in affix_lines:
        if verbose: print(affix_line)
        affix_string_guess = difflib.get_close_matches(affix_line, affix_strings.keys())[0]
        if verbose: print(affix_string_guess)

        affix_line_stat_possibilites = []

        for stat_translation_entry in affix_strings[affix_string_guess]:
            affix_line_stat_possibility = {}
            for string_entry in stat_translation_entry["English"]:
                if string_entry["string"] == affix_string_guess:
                    insert_indices = [i for i in range(len(affix_string_guess)) if affix_string_guess[i] == "{"]
                    insert_condition_indices = [int(affix_string_guess[i+1]) for i in insert_indices]
                    defluffed_affix_line = [affix_line]
                    if len(insert_indices) > 0:
                        fluff_strings = [affix_string_guess[0:insert_indices[0]]] + [affix_string_guess[insert_indices[i]+3:insert_indices[i+1]] for i in range(len(insert_indices)-1)] + [affix_string_guess[insert_indices[-1]+3:]]

                        for fluff in fluff_strings:
                            if fluff != '':
                                new_segments = []
                                for segment in defluffed_affix_line:
                                    new_segments += [not_empty for not_empty in segment.split(fluff) if not_empty != '']
                                defluffed_affix_line = new_segments

                    for index, (condition, format, index_handlers) in enumerate(zip(string_entry["condition"],string_entry["format"], string_entry["index_handlers"])):
                        if format != "ignore":
                            string_index = insert_condition_indices.index(index)
                            value = defluffed_affix_line[string_index]
                            if format == "#%":
                                value = value[:-1]
                            elif format == "+#%":
                                value = value[1:-1]
                            elif format == "+#":
                                value = value[1:]
                            elif format != "#":
                                raise ValueError("unrecognized format string: " + format)
                            value = float(value)

                            for index_handler in index_handlers:
                                value *= index_handlers_multipliers[index_handler]
                            value = int(value)
                            if ("min" in condition and condition["min"] > value) or ("max" in condition and condition["max"] < value):
                                raise ValueError("string doesnt meet conditionals")
                            affix_line_stat_possibility[stat_translation_entry["ids"][index]] = value
            affix_line_stat_possibilites.append(affix_line_stat_possibility)
        stat_possibilities_per_line.append(affix_line_stat_possibilites)
    return stat_possibilities_per_line, base_type, ilvl, elder, shaper

from itertools import *
def find_all_mod_combos(stat_possibilities_per_line, base_dict):
    affix_possibilities = []
    for stat_choices in product(*stat_possibilities_per_line):
        affix_possibilities += associate_mods(stat_choices, base_dict)
    return affix_possibilities


import numpy as np

def associate_mods(stat_choices, base_dict, prefix_max = 3, suffix_max = 3):
    affix_possibilities = []

    stats_combined = {}

    stats_to_mod_groups = {}

    for dict in stat_choices:
        for key in dict:
            stats_combined[key] = dict[key]
            stats_to_mod_groups[key] = set()


    mod_groups = {}




    stats_seen = set()
    for key, value in base_dict.items():
        mod_stats = set()
        for stat in value["stats"]:
            if stat["id"] != "dummy_stat_display_nothing":
                mod_stats.add(stat["id"])

        if mod_stats.issubset(stats_combined):
            stats_seen = stats_seen.union(mod_stats)
            group = value["group"]
            affix = key
            if group not in mod_groups:
                mod_groups[group] = {'' : {}}
            mod_groups[group][affix] = {}
            for stat in value["stats"]:
                if stat["id"] != "dummy_stat_display_nothing":
                    id = stat["id"]
                    mod_groups[group][affix][id] = [stat["min"], stat["max"]]
                    stats_to_mod_groups[id].add(group)
                # mod_groups[group][affix]["min"][id] += stat["min"]
                # mod_groups[group][affix]["max"][id] += stat["max"]


    #cant get all of stats
    if len(set(stats_combined).difference(stats_seen)) > 0:
        return []


    #TRIM GROUPS WHICH ARE THE SOLE GROUP THAT CONTRIBUTE TO A STAT
    for stat in stats_combined:
        if len(stats_to_mod_groups[stat]) == 1:
            single_mod_group = stats_to_mod_groups[stat].pop()

            good_affixes = {}
            for key, value in mod_groups[single_mod_group].items():
                try:
                    if stats_combined[stat] >= value[stat][0] and stats_combined[stat] <= value[stat][1]:
                        good_affixes[key] = value
                except KeyError:
                    #This happens for empty dict
                    continue
            mod_groups[single_mod_group] = good_affixes


    for affix_choice in product(*[dict.items() for dict in mod_groups.values()]):
        total_range = {}

        for stat in stats_combined:
            total_range[stat] = np.array([0,0])

        for key, min_max_dict in affix_choice:
            for id in min_max_dict:
                total_range[id] += min_max_dict[id]


        satisfies_conditions = True
        for stat in stats_combined:
            if stats_combined[stat] < total_range[stat][0] or stats_combined[stat] > total_range[stat][1]:
                satisfies_conditions = False

        if satisfies_conditions:
            new_affix_entry = []
            prefix_N = 0
            suffix_N = 0
            for affix, stats in affix_choice:
                if affix != '':
                    if base_dict[affix]["generation_type"] == "prefix":
                        prefix_N += 1
                    elif base_dict[affix]["generation_type"] == "suffix":
                        suffix_N += 1
                    else:
                        raise ValueError("not prefix or suffix")
                    new_affix_entry.append(affix)

            if prefix_N <= prefix_max and suffix_N <= suffix_max:
                affix_possibilities.append(new_affix_entry)
    return affix_possibilities

from item_rollers import base_item
from item_rollers import get_base_item
def parse_clipboard(text):
    stat_possibilities, base_type, ilvl, elder, shaper = get_stat_possibilities(text)
    base_item_obj = get_base_item(base_type)

    item = base_item(base_item_obj, elder = elder, shaper = shaper, ilvl = ilvl)
    # print(item.hash_weight_dict.base_dict.keys())
    return find_all_mod_combos(stat_possibilities, item.hash_weight_dict.base_dict)


test = "Rarity: Rare\nKraken Span\nAmbush Boots\n--------\nQuality: +1% (augmented)\nEvasion Rating: 92 (augmented)\nEnergy Shield: 21 (augmented)\n--------\nRequirements:\nLevel: 64\nDex: 45\nInt: 45\n--------\nSockets: G R\n--------\nItem Level: 86\n--------\n+6 to Evasion Rating\n+4 to maximum Energy Shield\n+58 to maximum Life\n13 Life Regenerated per second\n+73 to maximum Mana\n+13% to Cold Resistance\n20% increased Stun and Block Recovery"
test2 = "Rarity: Rare\nRapture Gutter\nJewelled Foil\n--------\nOne Handed Sword\nQuality: +20% (augmented)\nPhysical Damage: 135-251 (augmented)\nCritical Strike Chance: 5.50%\nAttacks per Second: 1.60\nWeapon Range: 12\n--------\nRequirements:\nLevel: 68\nDex: 212\n--------\nSockets: G-R-R\n--------\nItem Level: 83\n--------\n+25% to Global Critical Strike Multiplier\n--------\n43% increased Physical Damage\nAdds 26 to 48 Physical Damage\n+11 to Strength\n+30 to Dexterity\n6% reduced Enemy Stun Threshold\n+52 to Accuracy Rating\n69% increased Physical Damage"
test3 = "Rarity: Rare\nBlight Finger\nDiamond Ring\n--------\nRequirements:\nLevel: 60\n--------\nItem Level: 86\n--------\n23% increased Global Critical Strike Chance\n--------\n+41 to Strength\n+353 to Accuracy Rating\n+2% chance to Evade Attacks\n6% increased Elemental Damage with Attack Skills\n--------\nElder Item"
corrupt_test = "Rarity: Rare\nKraken Span\nAmbush Boots\n--------\nQuality: +1% (augmented)\nEvasion Rating: 92 (augmented)\nEnergy Shield: 21 (augmented)\n--------\nRequirements:\nLevel: 64\nDex: 45\nInt: 45\n--------\nSockets: G R\n--------\nItem Level: 86\n--------\n+6 to Evasion Rating\n+4 to maximum Energy Shield\n+58 to maximum Life\n13 Life Regenerated per second\n+73 to maximum Mana\n+13% to Cold Resistance\n20% increased Stun and Block Recovery\n--------\nCorrupted"
test4 = "Rarity: Rare\nDire Crown\nGreat Crown\n--------\nArmour: 166 (augmented)\nEnergy Shield: 28\n--------\nRequirements:\nLevel: 67\nStr: 59\nInt: 59\n--------\nSockets: R-B\n\n--------\nItem Level: 85\n--------\n+51 to Intelligence\n+23 to Armour\n+82 to maximum Life\n30% increased Rarity of Items found\n+47% to Fire Resistance"
test5 = "Rarity: Rare\nCorpse Wrap\nPlate Vest\n--------\nArmour: 23 (augmented)\n--------\nRequirements:\nLevel: 2\n--------\nSockets: R B-G\n--------\nItem Level: 3\n--------\n+10 to Strength\n22% increased Armour\n+6 to maximum Life\nReflects 3 Physical Damage to Melee Attackers"

# print(ring_item.hash_weight_dict.base_dict)
import time

# print(parse_clipboard(test5))