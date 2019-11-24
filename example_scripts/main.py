from import_clipboard import *
from item_rollers import *
from visualizations import *
from evaluation_funcs import *
from repoe_import import *
import os
from tqdm import tqdm

# file_texts = set()
#
# for filename in os.listdir("Data"):
#     if filename.endswith(".txt") or filename.endswith(".py"):
#         text = open("Data/" + filename).read()
#         if "Rarity" in text:
#             file_texts.add(text)
#
#     else:
#         continue
#
# classes = set()
# for base in repoe_data["base_items"].values():
#     classes.add(base["item_class"])
#
# class_representatives = {}
# for class_ in classes:
#     starting_bases = set()
#     starting_tags = set()
#     for key, base in repoe_data["base_items"].items():
#         if base["item_class"] == class_ and base["release_state"] == "released":
#             if frozenset(base["tags"]) not in starting_tags:
#                 starting_tags.add(frozenset(base["tags"]))
#                 starting_bases.add(key)
#     class_representatives[class_] = starting_bases
#
#
# # mod
# seen_weight = {}
# def get_synthesis_probabilities(mod, item_class):
#     probabilities = {}
#     for stat in mod["stats"]:
#         for entry in repoe_data["synthesis_implicits"]:
#             if entry["stat"]["id"] == stat["id"] and item_class in entry["item_classes"]:
#                 for mod_name in entry["mods"]:
#                     if mod_name not in probabilities:
#                         probabilities[mod_name] = 0
#                     weight = (1*stat["min"] + 1*stat["max"])/2/entry["stat"]["value"]
#                     # print((1*stat["min"] + 1*stat["max"])/2)
#                     probabilities[mod_name] += weight
#                     if stat["id"] not in seen_weight:
#                         seen_weight[stat["id"]] = 0
#                     if seen_weight[stat["id"]] < weight:
#                         seen_weight[stat["id"]] = weight
#
#
#     for probability in probabilities.values():
#         if probability < 0:
#             raise ValueError("negative probability")
#     return probabilities
#
# def get_synthesis_possibilities(mod, item_class):
#     probabilities = {}
#     for stat in mod["stats"]:
#         for entry in repoe_data["synthesis_implicits"]:
#             if entry["stat"]["id"] == stat["id"] and item_class in entry["item_classes"]:
#                 for mod_name in entry["mods"]:
#                     if mod_name not in probabilities:
#                         probabilities[mod_name] = 0
#                     weight = (1*stat["min"] + 1*stat["max"])/2/entry["stat"]["value"]
#                     # print((1*stat["min"] + 1*stat["max"])/2)
#                     probabilities[mod_name] += weight
#                     if stat["id"] not in seen_weight:
#                         seen_weight[stat["id"]] = 0
#                     if seen_weight[stat["id"]] < weight:
#                         seen_weight[stat["id"]] = weight
#
#
#     for probability in probabilities.values():
#         if probability < 0:
#             raise ValueError("negative probability")
#     return probabilities
# from itertools import *
# #first key synthesis implicit, second key mod it can come from, value is probability
# synthesis_mods_dict = {}
# seen_mod_base = set()

# for entry in repoe_data["synthesis_implicits"]:
#     for mod, base in product(entry["mods"], entry["item_classes"]):
#         mod_base_combo = frozenset([mod,base])
#         if frozenset([mod,base]) not in synthesis_mods_dict:
#             synthesis_mods_dict[frozenset([mod,base])] = {}
#         for base_item_key in class_representatives[base]:
#             base_item_entry = repoe_data["base_items"][base_item_key]
#             item_roller = base_item(base_item_entry)
#             for mod_key, mod_value in item_roller.hash_weight_dict.base_dict.items():
#                 for stat in mod_value["stats"]:
#                     if stat["id"] == entry["stat"]["id"]:
#                         weights = get_synthesis_probabilities(mod_value, base)
#                         seen_mod_base.add(frozenset([mod_key, base]))
#                         total = sum(weights.values())
#                         probability = weights[mod]/total
#                         print(weights)
#                         print(mod, mod_key, base, probability)
#                         # if mod_key in synthesis_mods_dict[mod_base_combo] and synthesis_mods_dict[mod_base_combo][mod_key] != probability:
#                         #     raise ValueError("conflicting probabilities")
#                         synthesis_mods_dict[mod_base_combo][mod_key] = probability
#
# import csv
#
# with open('output.csv', 'w') as csv_file:
#     csvwriter = csv.writer(csv_file, delimiter='\t')
#     for session in synthesis_mods_dict:
#         for item in synthesis_mods_dict[session]:
#             csvwriter.writerow([session, item, synthesis_mods_dict[session][item]])

# json.dump(synthesis_mods_dict, open("synthesis_mods_dict", "w"), indent=1)

# for class_, representatives_ in class_representatives.items():
#     for representative in representatives_:
#         base_item_entry = repoe_data["base_items"][representative]
#
#         mod_sums = {}
#         for mod_key, mod_value in base_item(base_item_entry).hash_weight_dict.base_dict.items():
#             probabilities = get_synthesis_probabilities(mod_value, class_)
#             mod_sums[mod_key] = sum(probabilities.values())
#
#         worst_key = min(mod_sums, key=mod_sums.get)
#         best_key = max(mod_sums, key=mod_sums.get)
#         print(class_, base_item_entry["name"], worst_key, mod_sums[worst_key], best_key, mod_sums[best_key])
#         import operator
#         print(sorted(mod_sums.items(), key=operator.itemgetter(1)))
#
# max_key = max(seen_weight, key=seen_weight.get)
# min_key = min(seen_weight, key=seen_weight.get)
# print(max_key, seen_weight[max_key], min_key, seen_weight[min_key])


# json.dump(synthesis_mods_dict, open("synthesis_mods_dict", "w"), indent=1)

#
#
# for mod in synthesis_mods:


# crafted_es_l = []
#
# sorc_gloves = get_base_item("Sorcerer Gloves")
# get_base_item = base_item(sorc_gloves, fossil_names=["Dense Fossil"])
# for i in range(10000):
#     chaos_item(get_base_item)
#     crafted_es = best_craft(get_base_item, es_stats,es_groups, average_es)
#     crafted_es_l.append(crafted_es)

#     if crafted_es > 200:
#         print([repoe_data["mods"][key]["stats"] for key in get_base_item.affix_keys])
#         print(get_base_item.affix_keys)
#         best_craft(get_base_item, es_stats, es_groups, average_es, verbose=True)
#         print(crafted_es)
#
# print(max(crafted_es_l))


# sorc_boots = get_base_item("Vaal Regalia")
# sorc_boots_item = base_item(sorc_boots, fossil_names=["Dense Fossil"], quality = 30, implicits=["SynthesisImplicitFlatEnergyShield5_"])
#
# # print(sorc_boots_item.implicit_stats)
#
# es_craft_l = []
# for i in range(1000000):
#     chaos_item(sorc_boots_item)
#     # if "MovementVelocity6" in sorc_boots_item.affix_keys:
#     es_craft_l.append(best_craft(sorc_boots_item, es_groups, average_es))
# #
# statistics(es_craft_l)
# discrete_cdf(es_craft_l)
#
# sorc_boots = get_base_item("Vaal Regalia")
# sorc_boots_item = base_item(sorc_boots, fossil_names=["Dense Fossil"], quality = 30, implicits=["SynthesisImplicitIncreasedEnergyShield5"])
#
# es_craft_l = []
# for i in range(1000000):
#     chaos_item(sorc_boots_item)
#     # if "MovementVelocity6" in sorc_boots_item.affix_keys:
#     es_craft_l.append(best_craft(sorc_boots_item, es_groups, average_es))
#
# statistics(es_craft_l)
# discrete_cdf(es_craft_l)
# plot_show()


# wand = get_base_item("Stygian Vise")
# wand_item = base_item(wand, ilvl=86)
#
#
# ilvl_requirements = {}
# for affix in wand_item.hash_weight_dict.base_dict:
#     ilvl_requirements[affix] = wand_item.hash_weight_dict.base_dict[affix]["required_level"]
#
# sorted_ilvl_requirements = [value for (key, value) in sorted(ilvl_requirements.items())]
# for ilvl in sorted_ilvl_requirements:
#     print(ilvl)


# print(sorc_boots_item.implicit_stats)


def count_simulations_with_mods(item_class, query_mods, trial_N = 1000000):
    query_mods = set(query_mods)

    counter = 0
    for trial_idx in tqdm(range(trial_N)):
        chaos_item(item_class)
        if query_mods.issubset(item_class.affix_keys):
            counter += 1

    return counter



def affix_counter_simulation(item_class, trial_N = 1000000):

    mod_counter = Counter()

    for trial_idx in tqdm(range(trial_N)):
        chaos_item(item_class)
        for affix_key in item_class.affix_keys:
            if affix_key not in mod_counter:
                mod_counter[affix_key] = 0
            mod_counter[affix_key] += 1
    for key in mod_counter.keys():
        mod_counter[key] = mod_counter[key]

    return mod_counter


def import_i86_belts():
    directory = "Data_i86_belts"
    for filename in os.listdir(directory):
        if filename.endswith(".txt") or filename.endswith(".py"):
            text = open(directory + "/" + filename).read()

        else:
            continue

    clipboard_entries = text.split("\n&&&&&&&&&&&&&&&&&&&&\n")
    print(len(clipboard_entries))
    clipboard_entries_nonempty = set()
    for text in clipboard_entries:
        if text != "" and text != "\ufeff":
            if text in clipboard_entries_nonempty:
                print(text)
            clipboard_entries_nonempty.add(text)

    print(len(clipboard_entries_nonempty))

    mod_list = []
    for entry in clipboard_entries_nonempty:
        mod_possibilities = parse_clipboard(entry)
        assert len(mod_possibilities) == 1, "hybrid?"
        mod_list.append(parse_clipboard(entry)[0])

    print(mod_list)
    mod_counter = Counter()
    for mods in mod_list:
        for mod in mods:
            if mod not in mod_counter:
                mod_counter[mod] = 0
            mod_counter[mod] += 1
    print(mod_counter)

    print(len(clipboard_entries_nonempty))
    wand = get_base_item("Stygian Vise")
    wand_item = base_item(wand, ilvl=86, fossil_names=["Sanctified Fossil"])
    sorted_keys = sorted(wand_item.hash_weight_dict.base_dict.keys())
    for key in sorted_keys:
        if key not in mod_counter:
            print(0)
        else:
            print(mod_counter[key])



if __name__ == "__main__":
    # import_i86_belts()

    item = get_base_item("Driftwood Sceptre")
    item_class = base_item(item, ilvl=55, fossil_names=["Metadata/Items/Currency/CurrencyDelveCraftingLightning", "Metadata/Items/Currency/CurrencyDelveCraftingCold", "Metadata/Items/Currency/CurrencyDelveCraftingFire"])

    print(count_simulations_with_mods(item_class, set(["GlobalLightningSpellGemsLevel1", "GlobalSpellGemsLevel1"]),trial_N=10000000))