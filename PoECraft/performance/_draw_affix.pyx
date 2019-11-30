
# from PoECraft.cached_weight_draw import CachedWeightDraw
# from PoECraft.item_rollers import ExplicitModRoller

cimport PoECraft.performance._bisect as _bisect


from libc.stdlib cimport malloc, free

import numpy as np
cimport numpy as np

DTYPE = np.uint32
ctypedef np.uint32_t DTYPE_t

def affix_draw(explicit_mod_roller):
    '''
    Takes in current tags, affixes, prefix number, suffix number, and rolls a new affix.

    Uses all of the precomputed hashing from above.

    This method should be the main performance blocker.
    '''
    cached_weight_draw = explicit_mod_roller.cached_weight_draw
    cdef unsigned int prefix_N = explicit_mod_roller.prefix_N
    cdef unsigned int suffix_N = explicit_mod_roller.suffix_N
    cdef unsigned int max_pre = explicit_mod_roller.max_pre
    cdef unsigned int max_suff = explicit_mod_roller.max_suff
    cdef unsigned int current_tags = explicit_mod_roller.tags_current
    current_affixes = explicit_mod_roller.affix_indices_current

    cdef bint maxed_out_prefixes = prefix_N == max_pre
    cdef bint maxed_out_suffixes = suffix_N == max_suff

    cdef np.ndarray base_array

    #if prefixes/suffixes/tags have changed, recalculate weights from all affix changes
    if not maxed_out_prefixes and not maxed_out_suffixes:
        base_array = <np.ndarray>cached_weight_draw.weights_cummulative[current_tags]
    elif maxed_out_prefixes and not maxed_out_suffixes:
        base_array = <np.ndarray>cached_weight_draw.suffixes_cummulative[current_tags]
    elif not maxed_out_prefixes and maxed_out_suffixes:
        base_array = <np.ndarray>cached_weight_draw.prefixes_cummulative[current_tags]
    else:
        raise ValueError("can't add affix to full item")

    cdef DTYPE_t *base_array_pointer = <DTYPE_t *>base_array.data

    cdef unsigned int diff_arrays_N = 0
    cdef unsigned int array_N = len(current_affixes)
    if not maxed_out_prefixes:
        diff_arrays_N += array_N
    if not maxed_out_suffixes:
        diff_arrays_N += array_N

    cdef DTYPE_t **diff_arrays = <DTYPE_t **> malloc(diff_arrays_N * sizeof(DTYPE_t))
    cdef unsigned int diff_array_idx = 0
    #For each affix already on the item, remove it's group
    cdef np.ndarray diff_array
    cdef int affix
    for affix in current_affixes:
        if prefix_N < max_pre:
            diff_array = <np.ndarray>cached_weight_draw.group_diff_prefix_cummulative[current_tags][affix]
            diff_arrays[diff_array_idx] = <DTYPE_t *>diff_array.data
            diff_array_idx += 1
        if suffix_N < max_suff:
            diff_array = <np.ndarray>cached_weight_draw.group_diff_suffix_cummulative[current_tags][affix]
            diff_arrays[diff_array_idx] = <DTYPE_t *>diff_array.data
            diff_array_idx += 1

    cdef unsigned int draw_array_length = len(explicit_mod_roller.affix_key_pool)

    cdef unsigned int random_affix = _bisect._weighted_draw(base_array_pointer, diff_arrays, diff_arrays_N, draw_array_length)
    free(diff_arrays)
    return random_affix