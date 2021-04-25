use pyo3::prelude::*;
use rand::Rng;

use crate::_affix_draw::*;
use crate::_weighted_draw::*;

// #[pyclass(subclass)]
// #[derive(Clone, Copy)]
// pub struct Item {
//     #[pyo3(get)]
//     prefix_n: usize,
//     #[pyo3(get)]
//     suffix_n: usize,
//     #[pyo3(get)]
//     max_pre: usize,
//     #[pyo3(get)]
//     max_suf: usize,
//     #[pyo3(get)]
//     tags_current: usize,
//     #[pyo3(get)]
//     affix_indices_current: [Option<usize>; 6],
// }

#[pyclass(subclass)]
pub struct ExplicitModRoller {
    #[pyo3(get)]
    pub affix_indices_current: [Option<usize>; 6], //Vec<usize>,
    #[pyo3(get)]
    pub affix_key_pool: Vec<String>,
    #[pyo3(get)]
    pub tags_current: usize,
    #[pyo3(get)]
    pub affix_to_added_tags_bitstring: Vec<usize>,
    #[pyo3(get)]
    pub prefix_n: usize,
    #[pyo3(get)]
    pub suffix_n: usize,
    #[pyo3(get)]
    pub max_pre: usize,
    #[pyo3(get)]
    pub max_suf: usize,
    // #[pyo3(get)]
    forced_affix_indices: Vec<usize>, //Box<[usize]>,
    pub cached_weight_draw: CachedAffixDrawer,
    // forced_affix_indices: int
    // base_explicitless_item: int
}

#[pymethods]
impl ExplicitModRoller {
    #[new]
    fn new(
        affix_key_pool: Vec<String>,
        affix_to_added_tags_bitstring: Vec<usize>,
        // prefix_q: PyReadonlyArray1<bool>,
        // suffix_q: PyReadonlyArray1<bool>,
        max_pre: usize,
        max_suf: usize,
        forced_affix_indices: Vec<usize>,
        cached_weight_draw: CachedAffixDrawer,
    ) -> Self {
        ExplicitModRoller {
            affix_indices_current: [None; 6],
            affix_key_pool,
            tags_current: 0,
            affix_to_added_tags_bitstring,
            prefix_n: 0,
            suffix_n: 0,
            max_pre,
            max_suf,
            forced_affix_indices, //.into_boxed_slice(),
            cached_weight_draw,
        }
    }

    fn rust_print(&mut self) -> PyResult<()> {
        println!("{:?}", self.affix_indices_current);
        println!("{:?}", self.affix_key_pool);
        println!("{:?}", self.tags_current);
        println!("{:?}", self.affix_to_added_tags_bitstring);
        println!("{:?}", self.prefix_n);
        println!("{:?}", self.suffix_n);
        Ok(())
    }

    #[getter]
    fn affix_keys_current(&self) -> PyResult<Vec<String>> {
        Ok(self
            .affix_indices_current //[..self.prefix_n + self.suffix_n]
            .iter()
            .filter_map(|&x| x)
            .map(|x| self.affix_key_pool[x].clone())
            .collect())
    }

    fn add_affix(&mut self, affix_index: usize) -> PyResult<()> {
        self.affix_indices_current[(self.prefix_n + self.suffix_n)] = Some(affix_index);

        self.tags_current |= self.affix_to_added_tags_bitstring[affix_index];

        if self.cached_weight_draw.prefix_q[affix_index] {
            self.prefix_n += 1;
        } else {
            self.suffix_n += 1;
        }
        Ok(())
    }

    fn roll_one_affix(&mut self) -> PyResult<()> {
        let new_affix_idx = self._affix_draw();
        self.add_affix(new_affix_idx)
    }

    fn clear_item(&mut self) -> PyResult<()> {
        self.prefix_n = 0;
        self.suffix_n = 0;
        self.tags_current = 0;
        self.affix_indices_current = [None; 6];

        Ok(())
    }

    fn roll_item(&mut self) -> PyResult<()> {
        self.roll_item_with_max(self.max_pre + self.max_suf)
    }

    fn roll_item_with_max(&mut self, max_affixes: usize) -> PyResult<()> {
        let affix_n: usize;

        let mut rng = rand::thread_rng();
        if max_affixes == 6 {
            let rand_seed = rng.gen_range(0..12);
            if rand_seed < 1 {
                affix_n = 6;
            } else if rand_seed < 4 {
                affix_n = 5;
            } else {
                affix_n = 4;
            }
        } else if max_affixes == 4 {
            let rand_seed = rng.gen_range(0..3);
            if rand_seed < 2 {
                affix_n = 3;
            } else {
                affix_n = 4;
            }
        } else if max_affixes == 2 {
            let rand_seed = rng.gen_range(0..2);
            if rand_seed < 1 {
                affix_n = 1;
            } else {
                affix_n = 2;
            }
        } else {
            panic!("Unknown max_affixes {}", max_affixes);
        }

        self.clear_item()?;

        for &forced_affix_index in &self.forced_affix_indices {
            // inline add_affix because of &mut self problems

            self.affix_indices_current[(self.prefix_n + self.suffix_n)] = Some(forced_affix_index);
            self.tags_current |= self.affix_to_added_tags_bitstring[forced_affix_index];

            if self.cached_weight_draw.prefix_q[forced_affix_index] {
                self.prefix_n += 1;
            } else {
                self.suffix_n += 1;
            }
        }

        for _ in self.forced_affix_indices.len()..affix_n {
            self.roll_one_affix()?;
        }
        Ok(())
    }

    pub fn _affix_draw(&mut self) -> usize {
        let maxed_out_prefixes: bool = self.prefix_n == self.max_pre;
        let maxed_out_suffixes: bool = self.suffix_n == self.max_suf;

        let base_array: &[u32];

        // if prefixes/suffixes/tags have changed, recalculate weights from all affix changes
        if !maxed_out_prefixes && !maxed_out_suffixes {
            base_array = &self.cached_weight_draw.weights_cumulative[self.tags_current];
        } else if maxed_out_prefixes && !maxed_out_suffixes {
            base_array = &self.cached_weight_draw.suffixes_cumulative[self.tags_current];
        } else if !maxed_out_prefixes && maxed_out_suffixes {
            base_array = &self.cached_weight_draw.prefixes_cumulative[self.tags_current];
        } else {
            panic!("can't add affix to full item")
        }

        weighted_draw(&base_array, &self)
    }
}

impl ExplicitModRoller {
    #[inline(always)]
    pub fn _value_from_base_array(&self, base_array: &[u32], idx: usize) -> u32 {
        let mut item = base_array[idx];

        for &affix in &self.affix_indices_current[..self.prefix_n + self.suffix_n] {
            let affix = affix.expect("affix should not be None");
            // for idx in 0..(prefix_n + suffix_n) {
            // let affix = current_affixes[idx];//.expect("affix out of bounds");
            if self.prefix_n < self.max_pre {
                let diff_array: &[u32] =
                    &self.cached_weight_draw.group_diff_prefix_cumulative[self.tags_current][affix];
                item -= diff_array[idx];
            }
            if self.suffix_n < self.max_suf {
                let diff_array: &[u32] =
                    &self.cached_weight_draw.group_diff_suffix_cumulative[self.tags_current][affix];
                item -= diff_array[idx];
            }
        }
        item
    }
}
