cimport PoECraft.performance._prng as _prng

# ctypedef unsigned int comparetype

cdef unsigned int _bisect_right_diff_arrays(unsigned int *base_array, unsigned int **diff_arrays, unsigned int diff_array_N, unsigned int item, unsigned int array_length):
    '''
    This method takes in a base_array, and an array of diff_arrays (in the form of a pounsigned inter and a pounsigned inter to pounsigned inters)
    It forms a bisect on base_array - sum_i diff_arrays
    '''
    cdef unsigned int litem
    cdef unsigned int mid
    cdef unsigned int lo = 0
    cdef unsigned int hi = array_length
    cdef unsigned int diff_array_idx
    
    while (lo < hi):
        mid = (lo + hi) // 2
        litem = base_array[mid]
        for diff_array_idx in range(diff_array_N):
            litem -= diff_arrays[diff_array_idx][mid]
        if item < litem:
            hi = mid
        else:
            lo = mid + 1
    return lo


cdef unsigned int _weighted_draw(unsigned int *base_array, unsigned int **diff_arrays, unsigned int diff_array_N,  unsigned int array_length):
    cdef unsigned int max_roll = base_array[diff_array_N]
    cdef unsigned int diff_array_idx

    for diff_array_idx in range(diff_array_N):
        max_roll -= diff_arrays[diff_array_idx][diff_array_N]
    
    cdef unsigned int random_int = _prng._bounded_rand(max_roll)

    cdef unsigned int random_affix = _bisect_right_diff_arrays(base_array, diff_arrays, diff_array_N, random_int, array_length)
    return random_affix