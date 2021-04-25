#![allow(clippy::unnecessary_wraps)]
use pyo3::prelude::*;
mod _affix_draw;
mod _explicit_mod_roller;
mod _weighted_draw;

use crate::_affix_draw::*;
use crate::_explicit_mod_roller::*;

#[pymodule]
fn poe_craft(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<CachedAffixDrawer>()?;

    m.add_class::<ExplicitModRoller>()?;

    #[pyfn(m, "get_alt_aug_count")]
    fn get_alt_aug_count(
        roller: &mut ExplicitModRoller,
        mod_name: String,
        generation_type: String,
        trial_n: u32,
    ) -> (u32, u32, u32) {
        let mut count: u32 = 0;
        let mut alt: u32 = 0;
        let mut aug: u32 = 0;

        for _ in 0..trial_n {
            roller.roll_item_magic();
            alt += 1;
            if roller.affix_keys_current().unwrap().contains(&mod_name) {
                count += 1
            } else {
                let aug_prefix = (generation_type == "prefix") && (roller.prefix_n == 0);
                let aug_suffix = (generation_type == "suffix") && (roller.suffix_n == 0);
                if aug_prefix || aug_suffix {
                    roller.roll_one_affix();
                    aug += 1;
                    if roller.affix_keys_current().unwrap().contains(&mod_name) {
                        count += 1
                    }
                }
            }
        }
        (alt, aug, count)
    }

    #[pyfn(m, "test_roll_batch")]
    fn roll(roller: &mut ExplicitModRoller, trial_n: u32) {
        for _ in 0..trial_n {
            roller.roll_item();
        }
    }
    Ok(())
}
