use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ConsoleLog {
    pub type_: String,
    pub text: String,
    pub timestamp: f64,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct NetworkError {
    pub url: String,
    pub error_text: String,
    pub method: String,
    pub timestamp: f64,
}
