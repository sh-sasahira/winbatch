use pyo3::prelude::*;
use umya_spreadsheet::{reader, Spreadsheet, Worksheet};

#[pyclass]
pub struct Book {
    #[pyo3(get, set)]
    pub path: String,
    value: Spreadsheet
}

#[pymethods]
impl Book {
    #[new]
    pub fn new(path: String) -> Self {
        let _path = std::path::Path::new(&path);
        let book = reader::xlsx::read(_path).unwrap();
        Book { path, value: book }
    }

    pub fn __repr__(&self) -> String {
        format!("<Book path='{}'>", self.path)
    }

    pub fn get_value(&self, sheet: String, address: String) -> String {
        let worksheet = self.get_sheet_by_name(&sheet);
        return match worksheet {
            Some(ws) => ws.get_value(address),
            None => "Sheet not found".to_string(),
        }
    }
}

impl Book {
    pub fn get_sheet_by_name(&self, name: &String) -> Option<&Worksheet> {
        self.value.get_sheet_by_name(name)
    }

    pub fn get_sheet_by_index(&self, index: &usize) -> Option<&Worksheet> {
        self.value.get_sheet(index)
    }
}