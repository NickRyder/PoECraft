#![allow(clippy::unnecessary_wraps)]
use itertools::enumerate;
use pyo3::prelude::*;
use std::collections::HashMap;
mod _affix_draw;
mod _explicit_mod_roller;
mod _weighted_draw;

use crate::_affix_draw::*;
use crate::_explicit_mod_roller::*;

#[pymodule]
fn poe_craft(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<CachedAffixDrawer>()?;

    m.add_class::<ExplicitModRoller>()?;

    #[pyfn(m, "get_alt_aug_count", aug_when_prefix = true, aug_when_suffix = true)]
    fn get_alt_aug_count(
        roller: &mut ExplicitModRoller,
        trial_n: u32,
        aug_when_prefix: bool,
        aug_when_suffix: bool,
    ) -> (u32, u32, HashMap<String, u32>) {
        let mut mod_counts: Vec<u32> = Vec::with_capacity(roller.affix_key_pool.len() as usize);

        let mut alt: u32 = 0;
        let mut aug: u32 = 0;

        for _ in 0..trial_n {
            roller.roll_item_magic();
            alt += 1;

            if (aug_when_prefix && roller.suffix_n == 0)
                || (aug_when_suffix && roller.prefix_n == 0)
            {
                roller.roll_one_affix();
                aug += 1;
            }

            for &affix_idx in &roller.affix_indices_current[..roller.prefix_n + roller.suffix_n] {
                let affix_idx = affix_idx.expect("affix should not be None");
                mod_counts[affix_idx] += 1;
            }
        }

        let mut mod_name_counts: HashMap<String, u32> = HashMap::new();
        for (idx, mod_count) in enumerate(mod_counts) {
            mod_name_counts.insert(roller.affix_key_pool[idx].clone(), mod_count);
        }
        (alt, aug, mod_name_counts)
    }

    #[pyfn(m, "test_roll_batch")]
    fn roll(roller: &mut ExplicitModRoller, trial_n: u32) {
        for _ in 0..trial_n {
            roller.roll_item();
        }
    }
    Ok(())
}
