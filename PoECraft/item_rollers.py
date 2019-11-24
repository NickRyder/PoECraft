import random
import numpy as np
from RePoE import base_items, item_classes, essences, fossils, mods, mod_types
from collections import Counter
from PoECraft.mod_collector import collect_mods_and_tags
from PoECraft.cached_weight_draw import CachedWeightDraw


influence_to_tags = dict(shaper="shaper_tag", elder="elder_tag")

def spawn_tags_to_add_tags_array(spawn_tags, affix_data):
    adds_tags = [None] * len(affix_data)
    for index in range(len(affix_data)):
        bit_adds_tags = 0
        for tag in affix_data[index]["adds_tags"]:
            if tag in spawn_tags:
                bit_adds_tags += 2**spawn_tags.index(tag)
        adds_tags[index] = bit_adds_tags
    return adds_tags

def get_base_item_by_name(name):
    for base_item in base_items.values():
        if base_item["name"] == name:
            return base_item

def get_fossil_by_name(name):
    for fossil in fossils.values():
        if fossil["name"] == name:
            return fossil

class ExplictlessItem():
    '''A class to represent an item without explicit mods in PoE'''

    def set_implicit_stats(self, max_implicit_rolls=True):
        self.implicit_stats = {}

        for mod_key in self.implicits:
            mod = mods[mod_key]
            for stat in mod["stats"]:
                id = stat["id"]
                if id not in self.implicit_stats:
                    self.implicit_stats[id] = []
                if max_implicit_rolls:
                    self.implicit_stats[id].append([stat["max"], stat["max"]])
                else:
                    self.implicit_stats[id].append([stat["min"], stat["max"]])



    def __init__(self, base_item_name, influences = [], ilvl = 100, implicits = [], quality = 20, fractured_mods = []):
        self.base_item_entry = get_base_item_by_name(base_item_name)

        self.tags = []
        #make all of the properties of base_item_entry properties of this class
        for key, value in self.base_item_entry.items():
            setattr(self, key, value)

        self.ilvl = ilvl
        
        for influence in influences:
            self.tags.append(influence_to_tags[influence])

        self.quality = quality
        self.fractured_mods = fractured_mods

        #Handle custom implicits for synthesis
        if len(implicits) > 0:
            self.implicits = implicits
        self.set_implicit_stats()



def unpack_fossils(fossil_names):
    '''
    Takes in a list of fossil_names (which are keys in RePoE.fossil) and generates:
    added_mods: mods to add to the mod pool 
    forced_mods: mods which must spawn on the item
    global_generation_weights: 
    '''
    forced_mod_names = []
    added_mod_names = []
    global_generation_weights = []
    for fossil_name in fossil_names:
        fossil_data = get_fossil_by_name(fossil_name)
        if fossil_data["rolls_lucky"]:
            is_sanctified = True

        forced_mod_names += fossil_data["forced_mods"]
        added_mod_names += fossil_data["added_mods"]
        for mod_weights in fossil_data["positive_mod_weights"] + fossil_data["negative_mod_weights"]:
            global_generation_weights.append(mod_weights)
    return forced_mod_names, added_mod_names, global_generation_weights

def unpack_essences(essence_names):
    '''
    Takes in a list of essence_names (which are values for the key 'name' in RePoE.essence) and generates:
    forced_mod_names: all the mods which must spawn by using tehse essences
    '''
    forced_mod_names = []
    for essence_name in essence_names:
        found_essence = False
        for essence_entry in essences.values():
            if essence_entry["name"] == essence_name:
                found_essence = True
                forced_mod_names += [essence_entry["mods"][self.item_class]]
        assert found_essence, "essence name not in json"
    return forced_mod_names


class ExplicitModRoller():
    '''A class to quickly simulate using currency on an item in PoE'''

    def clear_item(self):
        self.prefix_N = 0
        self.suffix_N = 0
        self.affix_indices = []
        self.affix_keys = []
        self.affix_groups = []
        self.tags = 0

   

    def __init__(self, explicitless_item: ExplictlessItem,  fossil_names = [], essence_names = []):

        self.base_explicitless_item = explicitless_item

        fossils_added_mod_names, fossils_forced_mod_names, fossils_global_generation_weights = unpack_fossils(fossil_names)

        essences_forced_mod_names = unpack_essences(essence_names)
        appended_mod_dictionary = {}
        for name in fossils_forced_mod_names + fossils_added_mod_names + essences_forced_mod_names:
            appended_mod_dictionary[name] = mods[name]

        starting_tags = set(explicitless_item.tags)
        starting_tags.add("default")
        self.base_dict, realized_spawn_tags = collect_mods_and_tags(domains=[explicitless_item.domain], starting_tags=starting_tags, appended_mod_dictionary=appended_mod_dictionary, ilvl=self.base_explicitless_item.ilvl)

        ##Order the keys and data
        self.affix_keys = list(self.base_dict.keys())
        self.affix_data = [self.base_dict[key] for key in self.affix_keys]

        new_spawn_tags = list(realized_spawn_tags.difference(starting_tags))
        self.adds_tags = spawn_tags_to_add_tags_array(new_spawn_tags, self.affix_data)

        self.cached_weight_draw = CachedWeightDraw(starting_tags=starting_tags, new_spawn_tags=new_spawn_tags, affix_values_list=self.affix_data, global_generation_weights=fossils_global_generation_weights)

        self.forced_affix_indices = []
        for forced_mod in essences_forced_mod_names + fossils_forced_mod_names:
            self.forced_affix_indices.append(self.affix_keys.index(forced_mod))


    def add_affix(self, affix_index):
        self.affix_indices.append(affix_index)
        affix_key = self.affix_keys[affix_index]
        self.affix_keys.append(affix_key)

        self.tags = self.tags | self.adds_tags[affix_index]

        if self.cached_weight_draw.spawn_tags_to_prefix_Q[affix_index]:
            self.prefix_N += 1
        else:
            self.suffix_N += 1


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
            new_affix_idx = self.cached_weight_draw.affix_draw(current_tags=self.tags, current_affixes=self.affix_indices, prefix_N=self.prefix_N, suffix_N=self.suffix_N)
            self.add_affix(new_affix_idx)

    def get_affix_groups(self):
        affix_groups = []
        for affix_key in self.affix_keys:
            affix_groups.append(self.base_dict[affix_key]["group"])
        return affix_groups

    def get_total_stats(self):
        stats = self.base_explicitless_item.implicit_stats.copy()
        for affix_key in self.affix_keys:
            for stat in self.base_dict[affix_key]["stats"]:
                if stat["id"] not in stats:
                    stats[stat["id"]] = []
                stats[stat["id"]].append([stat["min"], stat["max"]])
        return stats

    def __str__(self):
        return str(self.affix_keys)




