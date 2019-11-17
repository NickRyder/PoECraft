
class Cached_Weight_Draw():
    '''
    This class creates cached objects to enable quick rolling of items at any state.

    To accomplish this it uses the following ideas:
    -To do a weighted draw the fastest method is to have a list of cumulative sums, generate a random number, and bisect to find the appropriate index for that draw.
    -There are a small enough number of tag configurations that we can preprocess the cumulative sums for each tag configuration ahead of time
    -To handle the change of weights from groups being excluded, we generate cumulative sums for each group so we can quickly modify the cummulative sums of the tag configuration to adapt to our currently chosen groups
    -Finally we need to handle prefixes and suffixes, so for each of these we keep separate caches for prefixes and suffixes

    This class has a draw random index command which draws an index using the cached objects
    '''

    def __init__(self, starting_tags, new_spawn_tags, affix_data, global_generation_weights):
        self.affix_data = affix_data
        self.spawn_tags_to_spawn_weight = self.spawn_tags_to_spawn_weight_arrays(new_spawn_tags,starting_tags=starting_tags, global_generation_weights=global_generation_weights,affix_data=self.affix_data)
        self.sums_weights, self.sums_prefix_bits, self.sums_suffix_bits = self.generate_spawn_tag_lookup_tables(spawn_tags_to_spawn_weight=self.spawn_tags_to_spawn_weight, affix_data=self.affix_data)
        self.sums_group_prefix_bits, self.sums_group_suffix_bits = self.generate_group_sums(spawn_tags_to_spawn_weight=self.spawn_tags_to_spawn_weight, affix_data=self.affix_data)
 
    def spawn_tags_to_spawn_weight_arrays(self,spawn_tags,starting_tags, global_generation_weights, affix_data) -> np.array:
        
        tag_N = 2 ** len(spawn_tags)

        assert len(spawn_tags) <= 16, "too many spawn tags"

        spawn_weight_array = np.empty((tag_N, len(affix_data)), dtype=int)

        for tag_combo in product([0,1], repeat=len(spawn_tags)):
            tags = [spawn_tags[index] for index in range(len(spawn_tags)) if tag_combo[index] == 1]
            out = 0
            for bit in tag_combo:
                out = (out << 1) | bit
            spawn_weight_array[out] = tags_to_spawn_weights(starting_tags.union(tags),global_generation_weights=global_generation_weights, affix_data=affix_data )
        return spawn_weight_array

    def generate_group_sums(self, spawn_tags_to_spawn_weight: np.array, affix_data):
        '''

        '''
        affix_N = len(affix_data)
        tag_N = spawn_tags_to_spawn_weight.shape[0]
        
        sums_group_prefix_bits = np.empty((tag_N, affix_N, affix_N))
        sums_group_suffix_bits = np.empty((tag_N, affix_N, affix_N))

        for tag_idx in range(tag_N):
            for affix1_idx in range(tag_N):
                
                prefix_group_sum = 0
                suffix_group_sum = 0
                for affix2_idx in range(affix_N):

                    if affix_data[affix1_idx]["group"] == affix_data[affix2_idx]["group"]:
                        if affix_data[affix2_idx]["generation_type"] == "prefix":
                            prefix_group_sum += spawn_tags_to_spawn_weight[tag_idx][affix2_idx]
                        else:
                            suffix_group_sum += spawn_tags_to_spawn_weight[tag_idx][affix2_idx]
                    sums_group_prefix_bits[tag_idx][affix1_idx][affix2_idx] = prefix_group_sum
                    sums_group_suffix_bits[tag_idx][affix1_idx][affix2_idx] = suffix_group_sum

        return sums_group_prefix_bits, sums_group_suffix_bits


    #TODO:cleanup
    def generate_spawn_tag_lookup_tables(self, spawn_tags_to_spawn_weight: np.array, affix_data):
        affix_N = len(affix_data)
        tag_N = spawn_tags_to_spawn_weight.shape[0]


        sums_weights = np.empty((tag_N, affix_N))
        sums_prefix_bits = np.empty((tag_N, affix_N))
        sums_suffix_bits = np.empty((tag_N, affix_N))

        for index in range(tag_N):
            partial_sums = 0
            prefix_sum = 0
            suffix_sum = 0
            for affix_index in range(affix_N):
                spawn_weight = spawn_tags_to_spawn_weight[index][affix_index]
                partial_sums += spawn_weight
                if affix_data[affix_index]["generation_type"] == "prefix":
                    prefix_sum += spawn_weight
                else:
                    suffix_sum += spawn_weight
                sums_weights[index][affix_index] = partial_sums
                sums_prefix_bits[index][affix_index] = prefix_sum
                sums_suffix_bits[index][affix_index] = suffix_sum

        return sums_weights, sums_prefix_bits, sums_suffix_bits

        

    def affix_draw(self, hash_weight_dict, tags, affixes, prefix_N, suffix_N, max_pre = 3, max_suff = 3):

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

        return affix_index_draw
