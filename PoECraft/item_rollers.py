from itertools import combinations, chain, product
import random
import numpy as np
from RePoE import base_items, item_classes, essences, fossils, mods, mod_types
import copy
from collections import Counter
from PoECraft.mod_collector import collect_mods_and_tags
from PoECraft.cached_weight_draw import Cached_Weight_Draw

def get_mod_type_generation_weight_for_affix(affix, mod_type_tags):
    '''

    '''
    generation_weight = 1
    for weight in mod_type_tags:
        tag = weight["tag"]
        weighting = weight["weight"]
        if tag in mod_types[affix["type"]]["tags"]:
            generation_weight *= weighting/100.0
    return generation_weight

def get_generation_weight_for_affix(affix, tags):
    '''

    '''
    generation_weight = 1
    for generation_weight_rule in affix["generation_weights"]:
        if generation_weight_rule["tag"] in tags:
            generation_weight *= generation_weight_rule["weight"]/100.0
            #reads top to bottom like spawn_weights
            break
    return generation_weight
    
def get_spawn_weighting(affix, tags, mod_type_tags):
    spawn_weights = affix["spawn_weights"]

    generation_weight = 1

    #TODO: need to determine affect of sanctifieds
    # if self.is_sanctified:
    #     generation_weight *= (1 + affix["required_level"] / 100.0)

    #change generation weight by global effect (caused by using fossils)
    generation_weight *= get_mod_type_generation_weight_for_affix(affix, mod_type_tags)

    #change generation weight by local effect (caused by adding affixes)
    generation_weight *= get_generation_weight_for_affix(affix, tags)

    for spawn_weight in spawn_weights:
        if spawn_weight["tag"] in tags:
            weight = spawn_weight["weight"]
            rounded_weight = int(generation_weight * weight)
            assert weight == 0 or rounded_weight > 0 or generation_weight == 0, str(generation_weight) + " " + str(spawn_weight["weight"])
            return rounded_weight

    raise ValueError("spawn_weights did not contain appropriate tag for spawning")


def tags_to_spawn_weights(tags: set, global_generation_weights, affix_data):
    spawn_weights = [get_spawn_weighting(affix_datum, tags, global_generation_weights) for affix_datum in affix_data]

    return np.array(spawn_weights)



def spawn_tags_to_add_tags_array(spawn_tags, affix_data):
    adds_tags = [None] * len(affix_data)
    for index in range(len(affix_data)):
        bit_adds_tags = 0
        for tag in affix_data[index]["adds_tags"]:
            if tag in spawn_tags:
                bit_adds_tags += 2**spawn_tags.index(tag)
        adds_tags[index] = bit_adds_tags
    return adds_tags

def generate_prefix_suffix_lookups(affix_data):
    affix_N = len(affix_data)
    prefix_bits = np.zeros(affix_N, dtype=bool)
    suffix_bits = np.zeros(affix_N, dtype=bool)

    for index in range(affix_N):
        if affix_data[index]["generation_type"] == "prefix":
            prefix_bits[index] = True
        elif affix_data[index]["generation_type"] == "suffix":
            suffix_bits[index] = True
    return prefix_bits, suffix_bits



class hash_weight_dict():
    #Class takes in a the list of all mods, shrinks it to only look at certain starting tags, and then generates appropriate information needed for rolling mods
    #The fastest solution was to calculate all possible partial sum strings to make weighted choice much faster


    base_dict = {}

    # seen_tag_combos = set([])
    domains = set([])

    # to_fill_tags = set([])
    global_generation_weights = []

    realized_spawn_tags = set()

    #TRYING OUT BIT STRINGS:

    affix_keys = []
    affix_data = []

    #first index is an integer which indexes new_spawn_tags
    #each row is a len(Affixes) array with spawn weights
    spawn_weights = []

    #single row of len(affix) which integers which indicate indices of new_spawn_tags
    adds_tags = []

    prefix_bits = []
    suffix_bits = []

    #first index is an integer which indexes the affix
    #each row is a len(Affixes) array with True False dependeing on whether those affixes are in the same group
    # group_bits = []


    sums_weights = []
    sums_prefix_bits = []
    sum_suffix_bits = []
    sum_group_bits = []





    def __init__(self, starting_tags, domains = ['item'], global_generation_weights = [], added_mods = {}, is_sanctified = False, ilvl = 100):
        '''

        '''
        self.global_generation_weights = global_generation_weights

        starting_tags = set(starting_tags)
        starting_tags.add("default")

        # self.is_sanctified = is_sanctified

        self.base_dict, realized_spawn_tags = collect_mods_and_tags(domains=domains, starting_tags=starting_tags, added_mods=added_mods, ilvl=ilvl)

        ##Order the keys and data
        self.affix_keys = list(self.base_dict.keys())
        self.affix_data = [self.base_dict[key] for key in self.affix_keys]

        self.spawn_tags_to_prefix_Q, self.spawn_tags_to_suffix_Q = generate_prefix_suffix_lookups(self.affix_data)

        new_spawn_tags = list(realized_spawn_tags.difference(starting_tags))
        self.adds_tags = spawn_tags_to_add_tags_array(new_spawn_tags, self.affix_data)

        #TODO: clean up further with datastructure
        self.cached_weight_draw = Cached_Weight_Draw(starting_tags=starting_tags, new_spawn_tags=new_spawn_tags, affix_data=affix_data, global_generation_weights=global_generation_weights)


def get_base_item(name):
    for base_item in base_items.values():
        if base_item["name"] == name:
            return base_item

class base_item():

    hash_weight_dict = {}


    #temporary properties
    prefix_N = 0
    suffix_N = 0
    affix_indices = []
    affix_keys = []
    affix_groups = []
    stats = {}

    tags = 0

    #permanent properties
    forced_affix_indices = []
    item_class = ""
    properties = {}
    implicits = []

    # def get_essence_mods(self):
    #     essence_mods = {}
    #     for essence in repoe_data["essences"].values():
    #         if self.item_class in essence["mods"]:
    #             essence_mod_name = essence["mods"][self.item_class]
    #             essence_mods[essence_mod_name] = repoe_data["mods"][essence_mod_name]
    #     return essence_mods

    def clear_item(self):
        self.prefix_N = 0
        self.suffix_N = 0
        self.affix_indices = []
        self.affix_keys = []
        self.affix_groups = []
        self.stats = copy.deepcopy(self.implicit_stats)
        self.tags = 0


    def __init__(self, base_item_entry, fossil_names = [], essence_names = [], shaper = False, elder = False, domains = ["item"], ilvl = 100, implicits = [], quality = 20, max_implicit_rolls = True, fractured_mods = []):
        self.item_class = base_item_entry["item_class"]
        self.properties = base_item_entry["properties"]
        self.quality = quality

        self.implicits = base_item_entry["implicits"]
        if len(implicits) > 0:
            self.implicits = implicits

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

        self.stats = copy.deepcopy(self.implicit_stats)

        is_sanctified = False

        starting_tags = base_item_entry["tags"]

        if shaper:
            starting_tags.append(item_classes[self.item_class]["shaper_tag"])
        if elder:
            starting_tags.append(item_classes[self.item_class]["elder_tag"])

        # essence_mods = self.get_essence_mods()


        forced_mod_names = fractured_mods
        added_mod_names = []
        global_generation_weights = []

        for fossil_name in fossil_names:
            fossil_data = fossils[fossil_name]
            if fossil_data["rolls_lucky"]:
                is_sanctified = True

            forced_mod_names += fossil_data["forced_mods"]
            added_mod_names += fossil_data["added_mods"]
            for mod_weights in fossil_data["positive_mod_weights"] + fossil_data["negative_mod_weights"]:
                global_generation_weights.append(mod_weights)

        for essence_name in essence_names:
            found_essence = False
            for essence_entry in essences.values():
                if essence_entry["name"] == essence_name:
                    found_essence = True
                    forced_mod_names += [essence_entry["mods"][self.item_class]]
            assert found_essence, "essence name not in json"


        base_dict = mods

        added_mod_dictionary = {}
        for name in forced_mod_names + added_mod_names:
            added_mod_dictionary[name] = base_dict[name]

        print(added_mod_dictionary)

        ## REPLACEMENT FOR HASH_WEIGHT_DICT
        self.global_generation_weights = global_generation_weights

        starting_tags = set(starting_tags)
        starting_tags.add("default")

        # self.is_sanctified = is_sanctified

        self.base_dict, realized_spawn_tags = collect_mods_and_tags(domains=domains, starting_tags=starting_tags, added_mods=added_mods, ilvl=ilvl)

        ##Order the keys and data
        self.affix_keys = list(self.base_dict.keys())
        self.affix_data = [self.base_dict[key] for key in self.affix_keys]

        self.spawn_tags_to_prefix_Q, self.spawn_tags_to_suffix_Q = generate_prefix_suffix_lookups(self.affix_data)

        new_spawn_tags = list(realized_spawn_tags.difference(starting_tags))
        self.adds_tags = spawn_tags_to_add_tags_array(new_spawn_tags, self.affix_data)

        #TODO: clean up further with datastructure
        self.cached_weight_draw = Cached_Weight_Draw(starting_tags=starting_tags, new_spawn_tags=new_spawn_tags, affix_data=affix_data, global_generation_weights=global_generation_weights)



        for forced_mod in forced_mod_names:
            self.forced_affix_indices.append(self.affix_keys.index(forced_mod))


    def add_affix(self, affix_index):
        self.affix_indices.append(affix_index)
        affix_key = self.affix_keys[affix_index]
        self.affix_keys.append(affix_key)
        self.affix_groups.append(self.base_dict[affix_key]["group"])
        for stat in self.base_dict[affix_key]["stats"]:
            if stat["id"] not in self.stats:
                self.stats[stat["id"]] = []
            self.stats[stat["id"]].append([stat["min"], stat["max"]])

        self.affix_groups.append(self.base_dict[affix_key]["group"])

        self.tags = self.tags | self.adds_tags[affix_index]

        if self.spawn_tags_to_prefix_Q[affix_index]:
            self.prefix_N += 1
        else:
            self.suffix_N += 1




    def chaos_item(self):
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
            add_affix(self, forced_affix_index)

        for roll_index in range(len(forced_affix_indices), affix_N):
            append_affix(hash_weight_dict=self.hash_weight_dict, tags=self.tags, affixes=self.affix_indices, prefix_N=self.prefix_N, suffix_N=self.suffix_N)






    def __str__(self):
        return str(self.affix_keys)





def weighted_draw_sums(sums):
    total_sum = sums[-1]
    # return np.sum(sums < total_sum*random.random())
    return np.searchsorted(sums, total_sum*random.random())


def add_affix(item, affix_index):
    item.affix_indices.append(affix_index)
    affix_key = item.hash_weight_dict.affix_keys[affix_index]
    item.affix_keys.append(affix_key)
    item.affix_groups.append(item.hash_weight_dict.base_dict[affix_key]["group"])
    for stat in item.hash_weight_dict.base_dict[affix_key]["stats"]:
        if stat["id"] not in item.stats:
            item.stats[stat["id"]] = []
        item.stats[stat["id"]].append([stat["min"], stat["max"]])

    item.affix_groups.append(item.hash_weight_dict.base_dict[affix_key]["group"])

    item.tags = item.tags | item.hash_weight_dict.adds_tags[affix_index]

    if item.hash_weight_dict.spawn_tags_to_prefix_Q[affix_index]:
        item.prefix_N += 1
    else:
        item.suffix_N += 1



