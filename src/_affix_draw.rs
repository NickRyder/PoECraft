use ndarray::{Array1, ArrayView1, ArrayView2, ArrayView3};
use numpy::{PyReadonlyArray1, PyReadonlyArray2, PyReadonlyArray3};
use pyo3::prelude::*;

#[pyclass(subclass)]
#[derive(Clone)]
pub struct CachedAffixDrawer {
    #[pyo3(get)]
    pub weights_cumulative: Vec<Vec<u32>>,
    #[pyo3(get)]
    pub prefixes_cumulative: Vec<Vec<u32>>,
    #[pyo3(get)]
    pub suffixes_cumulative: Vec<Vec<u32>>,
    #[pyo3(get)]
    pub group_diff_prefix_cumulative: Vec<Vec<Vec<u32>>>,
    #[pyo3(get)]
    pub group_diff_suffix_cumulative: Vec<Vec<Vec<u32>>>,
    pub prefix_q: Array1<bool>,
    pub suffix_q: Array1<bool>,
}

fn array_1_to_vec(x: ArrayView1<u32>) -> Vec<u32> {
    x.to_owned().into_iter().map(|&x| x).collect()
}

fn array_2_to_vec_vec(x: ArrayView2<u32>) -> Vec<Vec<u32>> {
    x.outer_iter().map(|x| array_1_to_vec(x)).collect()
}

fn array_3_to_vec_vec_vec(x: ArrayView3<u32>) -> Vec<Vec<Vec<u32>>> {
    x.outer_iter().map(|x| array_2_to_vec_vec(x)).collect()
}

#[pymethods]
impl CachedAffixDrawer {
    #[new]
    fn new(
        weights_cumulative: PyReadonlyArray2<u32>,
        prefixes_cumulative: PyReadonlyArray2<u32>,
        suffixes_cumulative: PyReadonlyArray2<u32>,
        group_diff_prefix_cumulative: PyReadonlyArray3<u32>,
        group_diff_suffix_cumulative: PyReadonlyArray3<u32>,
        prefix_q: PyReadonlyArray1<bool>,
        suffix_q: PyReadonlyArray1<bool>,
    ) -> Self {
        CachedAffixDrawer {
            weights_cumulative: array_2_to_vec_vec(weights_cumulative.as_array()),
            prefixes_cumulative: array_2_to_vec_vec(prefixes_cumulative.as_array()),
            suffixes_cumulative: array_2_to_vec_vec(suffixes_cumulative.as_array()),
            group_diff_prefix_cumulative: array_3_to_vec_vec_vec(
                group_diff_prefix_cumulative.as_array(),
            ),
            group_diff_suffix_cumulative: array_3_to_vec_vec_vec(
                group_diff_suffix_cumulative.as_array(),
            ),
            prefix_q: prefix_q.as_array().to_owned(),
            suffix_q: suffix_q.as_array().to_owned(),
        }
    }

    fn rust_print(&mut self) -> PyResult<()> {
        println!("{:?}", self.weights_cumulative);
        println!("{:?}", self.suffixes_cumulative);
        println!("{:?}", self.prefixes_cumulative);
        println!("{:?}", self.group_diff_prefix_cumulative);
        println!("{:?}", self.group_diff_suffix_cumulative);
        Ok(())
    }
}
