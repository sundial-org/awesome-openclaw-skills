use crate::{error::Result, tools::{Tool, ToolContext, ToolResult}};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, schemars::JsonSchema)]
pub struct GetCookiesParams {
    /// Optional list of URLs to filter cookies by
    pub urls: Option<Vec<String>>,
}

#[derive(Debug, Serialize, Deserialize, schemars::JsonSchema)]
pub struct CookieParam {
    pub name: String,
    pub value: String,
    pub domain: Option<String>,
    pub path: Option<String>,
    pub secure: Option<bool>,
    pub http_only: Option<bool>,
    pub same_site: Option<String>,
    pub expires: Option<f64>,
    pub url: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, schemars::JsonSchema)]
pub struct SetCookiesParams {
    pub cookies: Vec<CookieParam>,
}

#[derive(Default)]
pub struct GetCookiesTool;

impl Tool for GetCookiesTool {
    type Params = GetCookiesParams;

    fn name(&self) -> &str {
        "get_cookies"
    }

    fn execute_typed(&self, _params: Self::Params, context: &mut ToolContext) -> Result<ToolResult> {
        let cookies = context.session.get_cookies()?;
        Ok(ToolResult::success_with(cookies))
    }
}

#[derive(Default)]
pub struct SetCookiesTool;

impl Tool for SetCookiesTool {
    type Params = SetCookiesParams;

    fn name(&self) -> &str {
        "set_cookies"
    }

    fn execute_typed(&self, params: Self::Params, context: &mut ToolContext) -> Result<ToolResult> {
        context.session.set_cookies(params.cookies)?;
        Ok(ToolResult::success(None))
    }
}
