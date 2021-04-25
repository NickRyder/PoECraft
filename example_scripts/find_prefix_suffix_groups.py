"""script to try and find a group which spawns prefix/suffix on the same item"""

from RePoE import mods

prefix_names = set()
suffix_names = set()

for mod_name, mod_value in mods.items():
    if mod_value["generation_type"] == "prefix":
        prefix_names.add(mod_value["group"])
    if mod_value["generation_type"] == "suffix":
        suffix_names.add(mod_value["group"])
groups = prefix_names.intersection(suffix_names)

group_to_mod = {}
for group in groups:
    group_to_mod[group] = []

for mod_name, mod_value in mods.items():
    if mod_value["domain"] == "item" and mod_value["generation_type"] in [
        "prefix",
        "suffix",
    ]:
        if mod_value["group"] in groups:
            group_to_mod[mod_value["group"]].append(mod_name)
import itertools


def _get_pos_weights(mod_value):
    to_return = set()
    for spawn_Weight in mod_value["spawn_weights"]:
        if spawn_Weight["weight"] > 0:
            to_return.add(spawn_Weight["tag"])
    return to_return


for group, group_mods in group_to_mod.items():
    for mod_name_1, mod_name_2 in itertools.combinations(group_mods, 2):
        mod_value_1 = mods[mod_name_1]
        mod_value_2 = mods[mod_name_2]

        pos_tags_1 = _get_pos_weights(mod_value_1)
        pos_tags_2 = _get_pos_weights(mod_value_2)
        overlapping_tags = len(pos_tags_1.intersection(pos_tags_2)) > 0
        is_essence = mod_value_1["is_essence_only"] or mod_value_2["is_essence_only"]
        is_delve = mod_value_1["domain"] is "delve" or mod_value_2["domain"] is "delve"

        if (overlapping_tags or is_essence or is_delve) and mod_value_1[
            "generation_type"
        ] != mod_value_2["generation_type"]:
            print(mod_name_1, mod_name_2)
