from typing import List, Set
import numpy as np
from RePoE import base_items, item_classes, essences, fossils, mods
from PoECraft.mod_collector import collect_mods_and_tags
from PoECraft.cached_weight_draw import CachedAffixDrawer

from poe_craft.poe_craft import ExplicitModRoller as ExplicitModRollerRust

from enum import Enum


def test():
    print(mods)


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

    base_item_entry = None
    max_pre: int
    max_suf: int
    ilvl: int
    tags = None
    extra_tags = None
    quality: int
    fractured_mods = None
    implicits = None
    set_implicit_stats = None

    def __init__(
        self,
        base_item_name,
        influences=[],
        ilvl=100,
        implicits=[],
        quality=20,
        fractured_mods=[],
        extra_tags=None,
        max_affix=3,
        max_pre=None,
        max_suf=None,
    ):
        self.base_item_entry = get_base_item_by_name(base_item_name)

        self.max_pre = max_affix
        self.max_suf = max_affix
        if max_pre is not None:
            self.max_pre = max_pre
        if max_suf is not None:
            self.max_suf = max_suf
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
    forced_mod_names: all the mods which must spawn by using these essences
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


def forced_affix_indices_from_essences_and_fossils(
    affix_key_list: List[int],
    essences_forced_mod_names: List[str],
    fossils_forced_mod_names: List[str],
    starting_tags: Set[str],
):
    forced_affix_indices = [
        affix_key_list.index(forced_mod) for forced_mod in essences_forced_mod_names
    ]

    for forced_mod in fossils_forced_mod_names:
        positive_spawn_weight_tags = set(
            [
                spawn_weight["tag"]
                for spawn_weight in mods[forced_mod]["spawn_weights"]
                if spawn_weight["weight"] > 0
            ]
        )
        if positive_spawn_weight_tags & starting_tags:
            forced_affix_indices.append(affix_key_list.index(forced_mod))

    return forced_affix_indices


class ExplicitModRoller(ExplicitModRollerRust):
    """A class to quickly simulate using currency on an item in PoE"""

    def __new__(
        cls,
        explicitless_item: ExplictlessItem,
        fossil_names=[],
        essence_names=[],
        mods=mods,
    ):

        (
            fossils_forced_mod_names,
            fossils_added_mod_names,
            fossils_global_generation_weights,
        ) = unpack_fossils(fossil_names)

        essences_forced_mod_names = unpack_essences(
            essence_names, explicitless_item.item_class
        )

        appended_mod_dictionary = {
            name: mods[name]
            for name in fossils_forced_mod_names
            + fossils_added_mod_names
            + essences_forced_mod_names
        }

        starting_tags = set(explicitless_item.tags)
        starting_tags.add("default")
        mod_dict, relevant_starting_tags, added_spawn_tags = collect_mods_and_tags(
            domains=[explicitless_item.domain],
            starting_tags=starting_tags,
            appended_mod_dictionary=appended_mod_dictionary,
            ilvl=explicitless_item.ilvl,
        )

        affix_key_list, affix_value_list = zip(*mod_dict.items())
        added_spawn_tags = tuple(added_spawn_tags)

        affix_to_added_tags_bitstring = spawn_tags_to_add_tags_array(
            added_spawn_tags, affix_value_list
        )

        cls.cached_weight_draw = CachedAffixDrawer(
            starting_tags=relevant_starting_tags,
            added_spawn_tags=added_spawn_tags,
            affix_values_list=affix_value_list,
            global_generation_weights=fossils_global_generation_weights,
        )

        forced_affix_indices = forced_affix_indices_from_essences_and_fossils(
            affix_key_list=affix_key_list,
            essences_forced_mod_names=essences_forced_mod_names,
            fossils_forced_mod_names=fossils_forced_mod_names,
            starting_tags=starting_tags,
        )

        return super().__new__(
            cls,
            affix_key_list,
            affix_to_added_tags_bitstring,
            explicitless_item.max_pre,
            explicitless_item.max_suf,
            forced_affix_indices,
            cls.cached_weight_draw,
        )

    def roll_item_magic(self):
        return super().roll_item_magic()

    def roll_item(self):
        return super().roll_item()

    def roll_item_with_max(self, max_affixes):
        return super().roll_item_with_max(max_affixes)

    def roll_one_affix(self):
        return super().roll_one_affix()

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
