// YAML rendering utilities for ARIA snapshots
// Based on Playwright's yaml.ts and renderAriaTree logic

/// Check if a YAML string needs quotes
pub fn yaml_string_needs_quotes(s: &str) -> bool {
    if s.is_empty() {
        return true;
    }

    // Leading or trailing whitespace
    if s.starts_with(char::is_whitespace) || s.ends_with(char::is_whitespace) {
        return true;
    }

    // Control characters
    if s.chars().any(|c| c.is_control()) {
        return true;
    }

    // Starts with '-'
    if s.starts_with('-') {
        return true;
    }

    // Contains ':' or '\n' followed by space or at end
    if s.contains(":\n") || s.contains(": ") || s.ends_with(':') {
        return true;
    }

    // Contains '#' preceded by space (comment indicator)
    if s.contains(" #") {
        return true;
    }

    // Line breaks
    if s.contains('\n') || s.contains('\r') {
        return true;
    }

    // Indicator characters
    if s.starts_with(['&', '*', ',', '?', '!', '>', '|', '@', '"', '\'', '#', '%']) {
        return true;
    }

    // Contains quotes or backslashes (need escaping)
    if s.contains('"') || s.contains('\\') || s.contains('\'') {
        return true;
    }

    // Special characters
    if s.chars().any(|c| matches!(c, '{' | '}' | '`')) {
        return true;
    }

    // Starts with '['
    if s.starts_with('[') {
        return true;
    }

    // YAML boolean/null values
    let lower = s.to_lowercase();
    if matches!(lower.as_str(), "y" | "n" | "yes" | "no" | "true" | "false" | "on" | "off" | "null") {
        return true;
    }

    // Numeric values
    if s.parse::<f64>().is_ok() {
        return true;
    }

    false
}

/// Escape a YAML key if needed (uses single quotes)
pub fn yaml_escape_key_if_needed(s: &str) -> String {
    if !yaml_string_needs_quotes(s) {
        return s.to_string();
    }

    // Use single quotes and escape single quotes by doubling them
    format!("'{}'", s.replace('\'', "''"))
}

/// Escape a YAML value if needed (uses double quotes)
pub fn yaml_escape_value_if_needed(s: &str) -> String {
    if !yaml_string_needs_quotes(s) {
        return s.to_string();
    }

    // Use double quotes and escape special characters
    let mut result = String::from('"');

    for ch in s.chars() {
        match ch {
            '\\' => result.push_str("\\\\"),
            '"' => result.push_str("\\\""),
            '\x08' => result.push_str("\\b"),
            '\x0C' => result.push_str("\\f"),
            '\n' => result.push_str("\\n"),
            '\r' => result.push_str("\\r"),
            '\t' => result.push_str("\\t"),
            c if c.is_control() => {
                // Escape control characters as \xNN
                result.push_str(&format!("\\x{:02x}", c as u32));
            }
            c => result.push(c),
        }
    }

    result.push('"');
    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_yaml_string_needs_quotes() {
        assert!(yaml_string_needs_quotes("")); // empty
        assert!(yaml_string_needs_quotes(" text")); // leading space
        assert!(yaml_string_needs_quotes("text ")); // trailing space
        assert!(yaml_string_needs_quotes("-text")); // starts with dash
        assert!(yaml_string_needs_quotes("foo: bar")); // contains colon-space
        assert!(yaml_string_needs_quotes("foo #bar")); // contains space-hash
        assert!(yaml_string_needs_quotes("true")); // boolean
        assert!(yaml_string_needs_quotes("123")); // number
        assert!(yaml_string_needs_quotes("[array]")); // starts with bracket

        assert!(!yaml_string_needs_quotes("simple"));
        assert!(!yaml_string_needs_quotes("hello-world"));
        assert!(!yaml_string_needs_quotes("foo_bar"));
    }

    #[test]
    fn test_yaml_escape_key_if_needed() {
        assert_eq!(yaml_escape_key_if_needed("simple"), "simple");
        assert_eq!(yaml_escape_key_if_needed("it's"), "'it''s'");
        assert_eq!(yaml_escape_key_if_needed("-start"), "'-start'");
    }

    #[test]
    fn test_yaml_escape_value_if_needed() {
        assert_eq!(yaml_escape_value_if_needed("simple"), "simple");
        assert_eq!(yaml_escape_value_if_needed("hello\nworld"), "\"hello\\nworld\"");
        assert_eq!(yaml_escape_value_if_needed("quote\"here"), "\"quote\\\"here\"");
        assert_eq!(yaml_escape_value_if_needed("back\\slash"), "\"back\\\\slash\"");
    }
}
