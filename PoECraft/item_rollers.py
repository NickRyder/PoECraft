from itertools import combinations, chain, product
import random
import numpy as np
from RePoE import base_items, item_classes, essences, fossils, mods, mod_types
import copy
from collections import Counter



def _get_positive_spawn_weight_tags(affix, starting_tags) -> set:
    '''
    Takes in an affix dict and a set of starting_tags
    Finds all positive weight tags in spawn_weights
    Ignores all spawn_weights if one of our starting tags forces a spawn_weight of zero
    '''
    pos_spawn_weight_tags = set()
    for spawn_weight in affix["spawn_weights"]:
        if spawn_weight["weight"] == 0:
            #We read the spawn_weights in order they are listed
            #If we find one which gives matches a tag we have we in starting_tags, we ignore
            if spawn_weight["tag"] in starting_tags:
                break
        elif spawn_weight["weight"] > 0:
            pos_spawn_weight_tags.add(spawn_weight["tag"])
        else:
            raise ValueError("spawn_weights should be nonnegative")

    return pos_spawn_weight_tags


# TODO: MAYBE?: this should take in some generic item type and calculate the possible mods that 
# can roll on that item. This will allow support for items which have some odd non-spawnable
# mods on them (like league specific mod drops)
# TODO: currently includes more tags than necessary (includes all possible relevant tags)
def generate_all_possible_affixes_and_tags(starting_tags, mod_pool):
    '''
    :param starting_tags: set containing all the starting_tags on the item we are rolling
    :param mod_pool: a dictionary containing all possible mods possible to roll on our item
    :return: spawn_tags, affixes
            spawn_tags -   all possible tags which can spawn from rolling this item
            affixes -      final mod pool of all things that can spawn
    '''

    affixes = {}
    added_new_affixes = True

    while added_new_affixes:
    
        added_new_affixes = False

        total_pos_spawn_weights_tags = set()

        for key, affix in mod_pool.items():
            # We want to only consider affixes which have a positive spawn weight for one of our potential tags
            # We also want to keep track of which tags affect this affix, whether they show up as any spawn_weight (even 0)
            # or they show up as a generation_weight

            #important that we only block starting_tags here, as there could be routes of crafting which spawn some tags and not others which affects blocking
            pos_spawn_weights_tags = _get_positive_spawn_weight_tags(affix, starting_tags)
            total_pos_spawn_weights_tags = total_pos_spawn_weights_tags.union(pos_spawn_weights_tags)

            spawn_weight_tags = set([spawn_weight["tag"] for spawn_weight in affix["spawn_weights"]])
            assert pos_spawn_weights_tags.issubset(spawn_weight_tags), "pos_spawn_weight_tags should be subset of spawn_weight_tags"

            add_tags = set()
            if len(pos_spawn_weights_tags) > 0:
                if key not in affixes:
                    affixes[key] = affix
                    added_new_affixes = True

                add_tags = add_tags.union(set(affix["adds_tags"]))

    spawn_tags = set(starting_tags.copy())
    spawn_tags = spawn_tags.union(add_tags)    

    return spawn_tags, affixes

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

def _get_spawnable_mods_for_item(domains,ilvl):
    '''
    Trim by removing all affixes that can't be crafted and are in the wrong domains
    '''

    spawnable_mods = {}

    for affix_key in list(mods.keys()):
        affix_value = mods[affix_key]
        is_prefix_or_suffix = affix_value["generation_type"] in ["prefix", "suffix"]
        is_in_domains = affix_value["domain"] in domains
        is_not_essence = not affix_value["is_essence_only"]
        is_ilvl_appropriate = affix_value["required_level"] <= ilvl


        if is_prefix_or_suffix and is_in_domains and is_not_essence and is_ilvl_appropriate:
            spawnable_mods[affix_key] = affix_value
    return spawnable_mods


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





    def __init__(self, mods, starting_tags, domains = ['item'], global_generation_weights = [], added_mods = {}, is_sanctified = False, ilvl = 100):
        '''

        '''
        self.global_generation_weights = global_generation_weights

        starting_tags = set(starting_tags)
        starting_tags.add("default")

        self.is_sanctified = is_sanctified

        spawnable_mods = _get_spawnable_mods_for_item(domains, ilvl)
        mod_pool = {**spawnable_mods, **added_mods}

        #further reduce the mod pool by looking at spawn weights and tags
        self.realized_spawn_tags, mod_pool = generate_all_possible_affixes_and_tags(starting_tags, mod_pool)

        self.base_dict = {**mod_pool, **added_mods}

        ##TRYING BIT STRINGS
        self.affix_keys = list(self.base_dict.keys())
        self.affix_data = [self.base_dict[key] for key in self.affix_keys]
        affix_N = len(self.affix_keys)

        new_spawn_tags = list(self.realized_spawn_tags.difference(starting_tags))

        tag_N = 2 ** len(new_spawn_tags)

        assert len(new_spawn_tags) <= 16, "too many spawn tags"

        self.spawn_weights = np.empty((tag_N, affix_N), dtype=int)
        self.adds_tags = [None] * affix_N

        self.prefix_bits = np.zeros(affix_N, dtype=bool)
        self.suffix_bits = np.zeros(affix_N, dtype=bool)

        for tag_combo in product([0,1], repeat=len(new_spawn_tags)):
            tags = [new_spawn_tags[index] for index in range(len(new_spawn_tags)) if tag_combo[index] == 1]
            out = 0
            for bit in tag_combo:
                out = (out << 1) | bit
            self.spawn_weights[out] = self.fillout_tags(starting_tags.union(tags))


        for index in range(len(self.affix_data)):
            bit_adds_tags = 0
            for tag in self.affix_data[index]["adds_tags"]:
                if tag in new_spawn_tags:
                    bit_adds_tags += 2**new_spawn_tags.index(tag)
            self.adds_tags[index] = bit_adds_tags

        for index in range(affix_N):
            if self.affix_data[index]["generation_type"] == "prefix":
               self.prefix_bits[index] = True
            elif self.affix_data[index]["generation_type"] == "suffix":
                self.suffix_bits[index] = True




        self.sums_weights = np.empty((tag_N, affix_N))
        self.sums_prefix_bits = np.empty((tag_N, affix_N))
        self.sums_suffix_bits = np.empty((tag_N, affix_N))
        self.sums_group_prefix_bits = np.empty((tag_N, affix_N, affix_N))
        self.sums_group_suffix_bits = np.empty((tag_N, affix_N, affix_N))



        for index in range(tag_N):
            partial_sums = 0
            prefix_sum = 0
            suffix_sum = 0
            for affix_index in range(affix_N):
                partial_sums += self.spawn_weights[index][affix_index]
                if self.affix_data[affix_index]["generation_type"] == "prefix":
                    prefix_sum += self.spawn_weights[index][affix_index]
                else:
                    suffix_sum += self.spawn_weights[index][affix_index]
                self.sums_weights[index][affix_index] = partial_sums
                self.sums_prefix_bits[index][affix_index] = prefix_sum
                self.sums_suffix_bits[index][affix_index] = suffix_sum

                prefix_group_sum = 0
                suffix_group_sum = 0
                for affix_index2 in range(affix_N):
                    if self.affix_data[affix_index]["group"] == self.affix_data[affix_index2]["group"]:
                        if self.affix_data[affix_index2]["generation_type"] == "prefix":
                            prefix_group_sum += self.spawn_weights[index][affix_index2]
                        else:
                            suffix_group_sum += self.spawn_weights[index][affix_index2]
                    self.sums_group_prefix_bits[index][affix_index][affix_index2] = prefix_group_sum
                    self.sums_group_suffix_bits[index][affix_index][affix_index2] = suffix_group_sum




    def fillout_tags(self, tags: set):

        spawn_weights = np.empty(len(self.affix_keys))

        for index in range(len(self.affix_keys)):
            affix_key = self.affix_keys[index]
            affix_data = self.affix_data[index]

            spawn_weights[index] = get_spawn_weighting(affix_data, tags)

        return spawn_weights



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
            mod = RePoE.mods[mod_key]
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
        self.hash_weight_dict = hash_weight_dict(base_dict, starting_tags, domain= domains, added_mods= added_mod_dictionary, global_generation_weights=global_generation_weights, is_sanctified = is_sanctified, ilvl = ilvl )

        for forced_mod in forced_mod_names:
            self.forced_affix_indices.append(self.hash_weight_dict.affix_keys.index(forced_mod))


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

    if item.hash_weight_dict.prefix_bits[affix_index]:
        item.prefix_N += 1
    else:
        item.suffix_N += 1




def append_affix(item, max_pre = 3, max_suff = 3):
    prefix_N = item.prefix_N
    suffix_N = item.suffix_N
    hash_weight_dict = item.hash_weight_dict
    affixes = item.affix_indices
    tags = item.tags

    sum_weights = hash_weight_dict.sums_weights[tags].copy()

    if prefix_N == max_pre:
        sum_weights -= hash_weight_dict.sums_prefix_bits[tags]
    if suffix_N == max_suff:
        sum_weights -= hash_weight_dict.sums_suffix_bits[tags]

    for affix in affixes:
        if prefix_N < max_pre:
            sum_weights -= hash_weight_dict.sums_group_prefix_bits[tags][affix]
        if suffix_N < max_suff:
            sum_weights -= hash_weight_dict.sums_group_suffix_bits[tags][affix]

    affix_index_draw = weighted_draw_sums(sum_weights)

    add_affix(item, affix_index_draw)


def chaos_item(item):
    forced_affix_indices = item.forced_affix_indices

    rand_seed = 12 * random.random()

    if rand_seed < 1:
        affix_N = 6
    elif rand_seed < 4:
        affix_N = 5
    else:
        affix_N = 4


    item.clear_item()

    for forced_affix_index in forced_affix_indices:
        add_affix(item, forced_affix_index)

    for roll_index in range(len(forced_affix_indices), affix_N):
        append_affix(item)




