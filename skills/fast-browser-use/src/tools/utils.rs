/// Normalize an incomplete URL by adding missing protocol and handling common patterns
pub fn normalize_url(url: &str) -> String {
    let trimmed = url.trim();

    // If already has a protocol, return as-is
    if trimmed.starts_with("http://")
        || trimmed.starts_with("https://")
        || trimmed.starts_with("file://")
        || trimmed.starts_with("data:")
        || trimmed.starts_with("about:")
        || trimmed.starts_with("chrome://")
        || trimmed.starts_with("chrome-extension://")
    {
        return trimmed.to_string();
    }

    // Relative path - return as-is
    if trimmed.starts_with('/') || trimmed.starts_with("./") || trimmed.starts_with("../") {
        return trimmed.to_string();
    }

    // localhost special case - use http by default
    if trimmed.starts_with("localhost") || trimmed.starts_with("127.0.0.1") {
        return format!("http://{}", trimmed);
    }

    // Check if it looks like a domain (contains dot or is a known TLD)
    if trimmed.contains('.') {
        // Looks like a domain - add https://
        return format!("https://{}", trimmed);
    }

    // Single word - assume it's a domain name, add www. prefix and https://
    // This handles cases like "google" -> "https://www.google.com"
    format!("https://www.{}.com", trimmed)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_normalize_url_complete() {
        assert_eq!(normalize_url("https://example.com"), "https://example.com");
        assert_eq!(normalize_url("http://example.com"), "http://example.com");
        assert_eq!(normalize_url("https://example.com/path"), "https://example.com/path");
    }

    #[test]
    fn test_normalize_url_missing_protocol() {
        assert_eq!(normalize_url("example.com"), "https://example.com");
        assert_eq!(normalize_url("example.com/path"), "https://example.com/path");
        assert_eq!(normalize_url("sub.example.com"), "https://sub.example.com");
    }

    #[test]
    fn test_normalize_url_partial_domain() {
        assert_eq!(normalize_url("google"), "https://www.google.com");
        assert_eq!(normalize_url("github"), "https://www.github.com");
        assert_eq!(normalize_url("amazon"), "https://www.amazon.com");
    }

    #[test]
    fn test_normalize_url_localhost() {
        assert_eq!(normalize_url("localhost"), "http://localhost");
        assert_eq!(normalize_url("localhost:3000"), "http://localhost:3000");
        assert_eq!(normalize_url("127.0.0.1"), "http://127.0.0.1");
        assert_eq!(normalize_url("127.0.0.1:8080"), "http://127.0.0.1:8080");
    }

    #[test]
    fn test_normalize_url_special_protocols() {
        assert_eq!(normalize_url("about:blank"), "about:blank");
        assert_eq!(normalize_url("file:///path/to/file"), "file:///path/to/file");
        assert_eq!(normalize_url("data:text/html,<h1>Test</h1>"), "data:text/html,<h1>Test</h1>");
        assert_eq!(normalize_url("chrome://settings"), "chrome://settings");
    }

    #[test]
    fn test_normalize_url_relative_paths() {
        assert_eq!(normalize_url("/path"), "/path");
        assert_eq!(normalize_url("/path/to/page"), "/path/to/page");
        assert_eq!(normalize_url("./relative"), "./relative");
        assert_eq!(normalize_url("../parent"), "../parent");
    }

    #[test]
    fn test_normalize_url_whitespace() {
        assert_eq!(normalize_url("  example.com  "), "https://example.com");
        assert_eq!(normalize_url("  https://example.com  "), "https://example.com");
    }
}
