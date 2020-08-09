import random
import numpy as np
from RePoE import base_items, item_classes, essences, fossils, mods, mod_types
from collections import Counter
from PoECraft.mod_collector import (
    collect_mods_and_tags,
    generate_all_possible_affixes_and_tags,
)
from PoECraft.cached_weight_draw import CachedWeightDraw
from PoECraft.utils.performance import timer

from PoECraft.performance._draw_affix import affix_draw

from enum import Enum


class Influence(Enum):
    SHAPER = "shaper_tag"
    ELDER = "elder_tag"
    REDEEMER = "redeemer_tag"
    CRUSADER = "crusader_tag"
    WARLORD = "warlord_tag"
    HUNTER = "hunter_tag"


def spawn_tags_to_add_tags_array(spawn_tags, affix_data_list):
    """
    takes in all possible added tags and all affixes.
    For each affix generates a bit string which represents which tags are added
    """
    affix_to_added_tags_bitstring = [None] * len(affix_data_list)
    for index in range(len(affix_data_list)):
        bit_adds_tags = 0
        for tag in affix_data_list[index]["adds_tags"]:
            if tag in spawn_tags:
                bit_adds_tags += 2 ** (len(spawn_tags) - 1 - spawn_tags.index(tag))
        affix_to_added_tags_bitstring[index] = bit_adds_tags
    return affix_to_added_tags_bitstring


def get_base_item_by_name(name):
    for base_item in base_items.values():
        if base_item["name"] == name:
            return base_item


def get_fossil_by_name(name):
    for fossil in fossils.values():
        if fossil["name"] == name:
            return fossil


class ExplictlessItem:
    """A class to represent an item without explicit mods in PoE"""

    def set_implicit_stats(self, max_implicit_rolls=True):
        self.implicit_stats = {}

        for mod_key in self.implicits:
            mod = mods[mod_key]
            for stat in mod["stats"]:
                id = stat["id"]
                if id not in self.implicit_stats:
                    self.implicit_stats[id] = np.empty((0, 2))
                if max_implicit_rolls:
                    self.implicit_stats[id] = np.vstack(
                        [self.implicit_stats[id], np.array([stat["max"], stat["max"]])]
                    )
                else:
                    self.implicit_stats[id] = np.vstack(
                        [self.implicit_stats[id], np.array([stat["min"], stat["max"]])]
                    )

    def __init__(
        self,
        base_item_name,
        influences=[],
        ilvl=100,
        implicits=[],
        quality=20,
        fractured_mods=[],
        extra_tags=None,
    ):
        self.base_item_entry = get_base_item_by_name(base_item_name)

        self.extra_tags = extra_tags if extra_tags is not None else []
        # make all of the properties of base_item_entry properties of this class
        for key, value in self.base_item_entry.items():
            setattr(self, key, value)

        self.tags += self.extra_tags
        self.ilvl = ilvl

        item_class = self.base_item_entry["item_class"]
        for influence in influences:
            influence_tag = item_classes[item_class][influence.value]
            self.tags.append(influence_tag)

        self.quality = quality
        self.fractured_mods = fractured_mods

        # Handle custom implicits for synthesis
        if len(implicits) > 0:
            self.implicits = implicits
        self.set_implicit_stats()

def unpack_fossils(fossil_names):
    """
    Takes in a list of fossil_names (which are keys in RePoE.fossil) and generates:
    added_mods: mods to add to the mod pool 
    forced_mods: mods which must spawn on the item
    global_generation_weights: 
    """
    forced_mod_names = []
    added_mod_names = []
    global_generation_weights = []
    for fossil_name in fossil_names:
        fossil_data = get_fossil_by_name(fossil_name)
        if fossil_data["rolls_lucky"]:
            is_sanctified = True

        forced_mod_names += fossil_data["forced_mods"]
        added_mod_names += fossil_data["added_mods"]
        for mod_weights in (
            fossil_data["positive_mod_weights"] + fossil_data["negative_mod_weights"]
        ):
            global_generation_weights.append(mod_weights)
    return forced_mod_names, added_mod_names, global_generation_weights


def unpack_essences(essence_names, item_class):
    """
    Takes in a list of essence_names (which are values for the key 'name' in RePoE.essence) and generates:
    forced_mod_names: all the mods which must spawn by using tehse essences
    """
    forced_mod_names = []
    for essence_name in essence_names:
        found_essence = False
        for essence_entry in essences.values():
            if essence_entry["name"] == essence_name:
                found_essence = True
                forced_mod_names += [essence_entry["mods"][item_class]]
        assert found_essence, "essence name not in json"
    return forced_mod_names


class ExplicitModRoller:
    """A class to quickly simulate using currency on an item in PoE"""

    def clear_item(self):
        self.prefix_N = 0
        self.suffix_N = 0
        self.tags_current = 0
        self.affix_indices_current = []
        self.affix_keys_current = []

    def __init__(
        self,
        explicitless_item: ExplictlessItem,
        fossil_names=[],
        essence_names=[],
        max_pre=3,
        max_suff=3,
    ):
        self.max_pre = max_pre
        self.max_suff = max_suff

        self.clear_item()
        # raise NotImplementedError("Currently a bug found by a smoke test. Unstable")
        self.base_explicitless_item = explicitless_item

        (
            fossils_forced_mod_names,
            fossils_added_mod_names,
            fossils_global_generation_weights,
        ) = unpack_fossils(fossil_names)

        essences_forced_mod_names = unpack_essences(
            essence_names, explicitless_item.item_class
        )
        appended_mod_dictionary = {}
        for name in (
            fossils_forced_mod_names
            + fossils_added_mod_names
            + essences_forced_mod_names
        ):
            appended_mod_dictionary[name] = mods[name]

        starting_tags = set(explicitless_item.tags)
        starting_tags.add("default")
        mod_dict, relevant_starting_tags, added_spawn_tags = collect_mods_and_tags(
            domains=[explicitless_item.domain],
            starting_tags=starting_tags,
            appended_mod_dictionary=appended_mod_dictionary,
            ilvl=self.base_explicitless_item.ilvl,
        )

        self.setup_cached_weight_draw(
            mod_dict=mod_dict,
            relevant_starting_tags=relevant_starting_tags,
            added_spawn_tags=added_spawn_tags,
            global_generation_weights=fossils_global_generation_weights,
        )

        self.forced_affix_indices = []
        for forced_mod in essences_forced_mod_names:
            self.forced_affix_indices.append(self.affix_key_pool.index(forced_mod))

        for forced_mod in fossils_forced_mod_names:
            positive_spawn_weight_tags = set(
                [
                    spawn_weight["tag"]
                    for spawn_weight in mods[forced_mod]["spawn_weights"]
                    if spawn_weight["weight"] > 0
                ]
            )
            if positive_spawn_weight_tags & starting_tags:
                self.forced_affix_indices.append(self.affix_key_pool.index(forced_mod))

    def setup_cached_weight_draw(
        self,
        mod_dict,
        relevant_starting_tags,
        added_spawn_tags,
        global_generation_weights=[],
    ):
        ##Order the keys, data, and added tags
        self.mod_dict = mod_dict
        self.affix_key_pool = list(self.mod_dict.keys())
        affix_data_pool = [self.mod_dict[key] for key in self.affix_key_pool]
        added_spawn_tags = tuple(added_spawn_tags)

        self.affix_to_added_tags_bitstring = spawn_tags_to_add_tags_array(
            added_spawn_tags, affix_data_pool
        )

        self.cached_weight_draw = CachedWeightDraw(
            starting_tags=relevant_starting_tags,
            added_spawn_tags=added_spawn_tags,
            affix_values_list=affix_data_pool,
            global_generation_weights=global_generation_weights,
        )

    def add_affix(self, affix_index):
        self.affix_indices_current.append(affix_index)
        affix_key = self.affix_key_pool[affix_index]
        self.affix_keys_current.append(affix_key)

        self.tags_current = (
            self.tags_current | self.affix_to_added_tags_bitstring[affix_index]
        )

        if self.cached_weight_draw.prefix_Q[affix_index]:
            self.prefix_N += 1
        else:
            self.suffix_N += 1

    def roll_item_magic(self):
        forced_affix_indices = self.forced_affix_indices

        rand_seed = random.random()
        if rand_seed < 0.5:
            affix_N = 1
        else:
            affix_N = 2

        self.clear_item()

        for forced_affix_index in forced_affix_indices:
            self.add_affix(forced_affix_index)

        for roll_index in range(len(forced_affix_indices), affix_N):
            self.roll_one_affix()

    def roll_item(self):
        forced_affix_indices = self.forced_affix_indices

        rand_seed = 12 * random.random()
        if rand_seed < 1:
            affix_N = 6
        elif rand_seed < 4:
            affix_N = 5
        else:
            affix_N = 4

        self.clear_item()

        for forced_affix_index in forced_affix_indices:
            self.add_affix(forced_affix_index)

        for roll_index in range(len(forced_affix_indices), affix_N):
            self.roll_one_affix()

    def roll_one_affix(self):
        # new_affix_idx = self.cached_weight_draw.affix_draw(current_tags=self.tags_current, current_affixes=self.affix_indices_current, prefix_N=self.prefix_N, suffix_N=self.suffix_N)
        new_affix_idx = affix_draw(self)
        self.add_affix(new_affix_idx)

    def get_affix_groups(self):
        affix_groups = []
        for affix_key in self.affix_keys_current:
            affix_groups.append(self.mod_dict[affix_key]["group"])
        return affix_groups

    def get_total_stats(self):
        """
        Returns a dict where the keys are stat_names and the values are numpy arrays of size (n,2) where the first dimension corresponds to unique sources of that stat
        stats[stat_name][i] = [min_stat_value, max_stat_value] for the ith source
        """
        stats = {}
        # first initialize on the base item
        for (
            stat_name,
            stat_ranges,
        ) in self.base_explicitless_item.implicit_stats.items():
            stats[stat_name] = stat_ranges
        # add stas for each affix
        for affix_key in self.affix_keys_current:
            for stat in self.mod_dict[affix_key]["stats"]:
                if stat["id"] not in stats:
                    stats[stat["id"]] = np.empty((0, 2))
                min_max_range_entry = np.array([stat["min"], stat["max"]])
                stats[stat["id"]] = np.vstack([stats[stat["id"]], min_max_range_entry])
        return stats

    def __str__(self):
        return str(self.affix_keys_current)

