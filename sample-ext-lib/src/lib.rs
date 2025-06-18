mod sample_ext_lib {
    pub mod book;
}

use pyo3::prelude::*;
use umya_spreadsheet::reader;

use crate::sample_ext_lib::book::Book;

#[pyfunction]
fn hello_from_bin() -> String {
    "Hello from sample-ext-lib!".to_string()
}

#[pyfunction]
fn read_file(path: String, sheet: String, address: String) -> String {
    let path = std::path::Path::new(&path);
    let book = reader::xlsx::read(path).unwrap();
    book.get_sheet_by_name(&sheet.as_str()).unwrap().get_value(address)
}

/// A Python module implemented in Rust. The name of this function must match
/// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
/// import the module.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(hello_from_bin, m)?)?;
    m.add_function(wrap_pyfunction!(read_file, m)?)?;
    m.add_class::<Book>()?;
    Ok(())
}
