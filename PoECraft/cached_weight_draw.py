import numpy as np
from itertools import product
from RePoE import mod_types
import random

## Weight calculation helpers

def get_mod_type_generation_weight_for_affix(affix, mod_type_tags):
    '''
    Given an affix and a list of mod_type tags, generates the generation weight based on those mod_type tags for the affix entry.
    More details on crafting process in README.md
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
    Given an affix and a list of tags, generates the generation weight based on those mod_type tags for the affix entry.
    More details on crafting process in README.md
    '''
    generation_weight = 1
    for generation_weight_rule in affix["generation_weights"]:
        if generation_weight_rule["tag"] in tags:
            generation_weight *= generation_weight_rule["weight"]/100.0
            #reads top to bottom like spawn_weights
            break
    return generation_weight
    
def get_spawn_weighting(affix, tags, mod_type_tags):
    '''
    Given an affix, tags, and mod_type tags, returns the raw spawn_weight.
    '''
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


def tags_to_spawn_weights(tags: set, global_generation_weights, affix_values_list):
    spawn_weights = [get_spawn_weighting(affix_value, tags, global_generation_weights) for affix_value in affix_values_list]

    return np.array(spawn_weights)

class CachedWeightDraw():
    '''
    This class creates cached objects to enable quick rolling of items at any state.

    To accomplish this it uses the following ideas:
    -To do a weighted draw the fastest method is to have a list of cumulative sums, generate a random number, and bisect to find the appropriate index for that draw.
    -There are a small enough number of tag configurations that we can preprocess the cumulative sums for each tag configuration ahead of time
    -To handle the change of weights from groups being excluded, we generate cumulative sums for each group so we can quickly modify the cummulative sums of the tag configuration to adapt to our currently chosen groups
    -Finally we need to handle prefixes and suffixes, so for each of these we keep separate caches for prefixes and suffixes

    This class has a draw random index command which draws an index using the cached objects
    '''

    weight_dtype = np.float


    def __init__(self, starting_tags, added_spawn_tags, affix_values_list, global_generation_weights):
        self.affix_values_list = affix_values_list

        #(tag_N, affix_N): Here we generate the raw spawn weights for each affix given a set of tags on our item
        self.spawn_tags_to_spawn_weight = self.spawn_tags_to_spawn_weight_arrays(added_spawn_tags,starting_tags=starting_tags, global_generation_weights=global_generation_weights)
        #(tag_N, affix_N): 
        self.weights_cummulative, self.prefixes_cummulative, self.suffixes_cummulative = self.generate_spawn_tag_lookup_tables(spawn_tags_to_spawn_weight=self.spawn_tags_to_spawn_weight)
        #(tag_N, affix_N, affix_N): 
        self.group_diff_prefix_cummulative, self.group_diff_suffix_cummulative = self.generate_group_diffs_lookup_tables(spawn_tags_to_spawn_weight=self.spawn_tags_to_spawn_weight)
        
        #(affix_N, dtype=bool)
        self.prefix_Q, self.suffix_Q = self.generate_prefix_suffix_lookups()
     

    def spawn_tags_to_spawn_weight_arrays(self,spawn_tags, starting_tags, global_generation_weights) -> np.array:
        
        tag_N = 2 ** len(spawn_tags)

        assert len(spawn_tags) <= 16, "too many spawn tags"

        spawn_weight_array = np.empty((tag_N, len(self.affix_values_list)), dtype=int)

        for tag_combo in product([0,1], repeat=len(spawn_tags)):
            tags = [spawn_tags[index] for index in range(len(spawn_tags)) if tag_combo[index] == 1]
            out = 0
            for bit in tag_combo:
                out = (out << 1) | bit
            spawn_weight_array[out] = tags_to_spawn_weights(starting_tags.union(tags),global_generation_weights=global_generation_weights, affix_values_list=self.affix_values_list)
        return spawn_weight_array

    def generate_group_diffs_lookup_tables(self, spawn_tags_to_spawn_weight: np.array):
        '''
        Group diffs allow us to quickly get the weights for our mods by starting with the weights based off of our tags and prefix/suffix status, and then subtracting off the weights due to the group restrictions.

        spawn_tags_to_spawn_weight: (tag_N, affix_N) array which yields the weight of an affix with the given tags
        affix_values_list: an ordered list of the affixes our item can roll whose values are dictionaries from RePoE.mods
        '''
        tag_N, affix_N = spawn_tags_to_spawn_weight.shape
        assert len(self.affix_values_list) == affix_N, "need the number affixes to match"
            
        group_diff_prefix_cummulative = np.empty((tag_N, affix_N, affix_N), dtype=self.weight_dtype)
        group_diff_suffix_cummulative = np.empty((tag_N, affix_N, affix_N), dtype=self.weight_dtype)

        for tag_idx in range(tag_N):
            for affix_to_diff_idx, affix_to_diff_data in enumerate(self.affix_values_list):
                prefix_group_sum = 0
                suffix_group_sum = 0
                for affix_idx, affix_data in enumerate(self.affix_values_list):

                    if affix_to_diff_data["group"] == affix_data["group"]:
                        if affix_data["generation_type"] == "prefix":
                            prefix_group_sum += spawn_tags_to_spawn_weight[tag_idx][affix_idx]
                        else:
                            suffix_group_sum += spawn_tags_to_spawn_weight[tag_idx][affix_idx]
                    group_diff_prefix_cummulative[tag_idx][affix_to_diff_idx][affix_idx] = prefix_group_sum
                    group_diff_suffix_cummulative[tag_idx][affix_to_diff_idx][affix_idx] = suffix_group_sum

        return group_diff_prefix_cummulative, group_diff_suffix_cummulative


    def generate_spawn_tag_lookup_tables(self, spawn_tags_to_spawn_weight: np.array):
        '''
        Generates look up tables which take in a tag configuration and give the cummulative sums of the weights for the affixes

        spawn_tags_to_spawn_weight: (tag_N, affix_N) array which yields the weight of an affix with the given tags
        affix_values_list: an ordered list of the affixes our item can roll whose values are dictionaries from RePoE.mods
        '''
        tag_N, affix_N = spawn_tags_to_spawn_weight.shape
        assert len(self.affix_values_list) == affix_N, "need the number affixes to match"

        weights_cummulative = np.empty((tag_N, affix_N), dtype=self.weight_dtype)
        prefix_cummulative = np.empty((tag_N, affix_N), dtype=self.weight_dtype)
        suffix_cummulative = np.empty((tag_N, affix_N), dtype=self.weight_dtype)

        for index in range(tag_N):
            partial_sums = 0
            prefix_sum = 0
            suffix_sum = 0
            for affix_index, affix_data in enumerate(self.affix_values_list):
                spawn_weight = spawn_tags_to_spawn_weight[index][affix_index]
                partial_sums += spawn_weight
                if affix_data["generation_type"] == "prefix":
                    prefix_sum += spawn_weight
                else:
                    suffix_sum += spawn_weight
                weights_cummulative[index][affix_index] = partial_sums
                prefix_cummulative[index][affix_index] = prefix_sum
                suffix_cummulative[index][affix_index] = suffix_sum

        return weights_cummulative, prefix_cummulative, suffix_cummulative



    last_inputs = (False,False,False,False)
    cached_weights = None

    def affix_draw(self, current_tags, current_affixes, prefix_N, suffix_N, max_pre = 3, max_suff = 3):
        '''
        Takes in current tags, affixes, prefix number, suffix number, and rolls a new affix.

        Uses all of the precomputed hashing from above.

        This method should be the main performance blocker.
        '''
        #Get the cummulative weights for each affix based on the current tags

        maxed_out_prefixes = prefix_N == max_pre
        maxed_out_suffixes = suffix_N == max_suff

        if self.last_inputs == (current_tags, current_affixes[:-1], maxed_out_prefixes, maxed_out_suffixes):
            sum_weights = self.cached_weights
            affix = current_affixes[-1]
            if prefix_N < max_pre:
                sum_weights -= self.group_diff_prefix_cummulative[current_tags][affix]
            if suffix_N < max_suff:
                sum_weights -= self.group_diff_suffix_cummulative[current_tags][affix]
        else:
            if not maxed_out_prefixes and not maxed_out_suffixes:
                sum_weights = self.weights_cummulative[current_tags].copy()
            elif maxed_out_prefixes and not maxed_out_suffixes:
                sum_weights = self.suffixes_cummulative[current_tags].copy()
            elif not maxed_out_prefixes and maxed_out_suffixes:
                sum_weights = self.prefixes_cummulative[current_tags].copy()
            else:
                raise ValueError("can't add affix to full item")

            #For each affix already on the item, remove it's group
            for affix in current_affixes:
                if prefix_N < max_pre:
                    sum_weights -= self.group_diff_prefix_cummulative[current_tags][affix]
                if suffix_N < max_suff:
                    sum_weights -= self.group_diff_suffix_cummulative[current_tags][affix]

        self.last_inputs = (current_tags, current_affixes.copy(), maxed_out_prefixes, maxed_out_suffixes)
        self.cached_weights = sum_weights
        return weighted_draw_sums(sum_weights)


    def generate_prefix_suffix_lookups(self):
        '''

        '''
        affix_N = len(self.affix_values_list)
        prefix_bits = np.zeros(affix_N, dtype=bool)
        suffix_bits = np.zeros(affix_N, dtype=bool)

        for index in range(affix_N):
            if self.affix_values_list[index]["generation_type"] == "prefix":
                prefix_bits[index] = True
            elif self.affix_values_list[index]["generation_type"] == "suffix":
                suffix_bits[index] = True
        return prefix_bits, suffix_bits


from bisect import bisect_left
def weighted_draw_sums(sums):
    total_sum = sums[-1]
    # return np.searchsorted(sums, int(total_sum*random.random()))
    return bisect_left(sums, total_sum*random.random())
