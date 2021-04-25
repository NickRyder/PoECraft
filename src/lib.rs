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

    Ok(())
}
