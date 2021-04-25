use crate::_explicit_mod_roller::*;
use rand::Rng;

#[allow(dead_code)]
fn linear_search(cumsums: &[u32], cumsum_diffs: &[&[u32]], item: u32) -> usize {
    // A simple linear search, in practice only 5% slower than binary search
    for idx in 0..cumsums.len() {
        let mut curitem: u32 = cumsums[idx];

        for cumsum_diff in cumsum_diffs {
            curitem -= cumsum_diff[idx];
        }

        if item < curitem {
            return idx;
        }
    }
    panic!("No returned value")
}

fn _bisect_right_diff_arrays(
    // function: fn(usize) -> u32,
    // hi: usize,
    cumsums: &[u32],
    explicit_mod_roller: &ExplicitModRoller,
    item: u32,
) -> usize {
    // Perform binary search on $cumsums - \sum cumsum_diffs$, searching
    // for the index of item. This is mainly used as a helper function to
    // perform a weighted draw from a bunch of u32 weights. To do the weighted
    // draw we calculate cumulative sums of the weights. To allow some of the
    // elements to be removed (draw without replacement) we allow diffs to
    // remove certain items from the pool
    //
    // # Arguments
    // * `cumsums` - a borrowed 1d array of cumulative sums
    // * `cumsum_diffs` - a borrowed 2d array, where each row is the same size
    //                    as cumsums
    // * `item` - the integer to search for in `cumsums`
    //
    // # Returns
    // an usize representing the largest idx such that, for
    // $x = cumsums - \sum cumsum_diffs$, x[idx] <= item.

    let mut current_item: u32;
    let mut lo: usize = 0;
    let mut mid: usize;
    let mut hi: usize = cumsums.len();

    while lo < hi {
        mid = (lo + hi) / 2;
        current_item = explicit_mod_roller._value_from_base_array(&cumsums, mid);

        if item < current_item {
            hi = mid;
        } else {
            lo = mid + 1;
        }
    }

    lo
}

pub fn weighted_draw(base_array: &[u32], explicit_mod_roller: &ExplicitModRoller) -> usize {
    let max_roll = explicit_mod_roller._value_from_base_array(&base_array, base_array.len() - 1);

    let mut rng = rand::thread_rng();
    let roll = rng.gen_range(0..max_roll);
    _bisect_right_diff_arrays(&base_array, &explicit_mod_roller, roll)
}
