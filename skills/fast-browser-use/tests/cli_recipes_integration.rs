use std::process::Command;
use std::path::PathBuf;
use std::fs;

// Helper to get the path to the binary
fn bin_path() -> PathBuf {
    let mut path = std::env::current_dir().unwrap();
    path.push("target");
    path.push("debug");
    path.push("fast-browser-use");
    path
}

#[test]
fn test_recipe_1_navigate_human_emulation() {
    let output = Command::new(bin_path())
        .arg("navigate")
        .arg("--url")
        .arg("https://example.com")
        .arg("--human-emulation")
        .arg("--wait-for-selector")
        .arg("h1")
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success(), "Command failed: {}", String::from_utf8_lossy(&output.stderr));
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(stderr.contains("Engaging human emulation"));
    assert!(stderr.contains("Waiting for selector: h1"));
}

#[test]
fn test_recipe_2_snapshot() {
    let output_file = "test_e2e_state.json";
    
    // Clean up if exists
    if std::path::Path::new(output_file).exists() {
        let _ = std::fs::remove_file(output_file);
    }

    let output = Command::new(bin_path())
        .arg("snapshot")
        .arg("--url")
        .arg("https://example.com")
        .arg("--include-styles")
        .arg("--output")
        .arg(output_file)
        .output()
        .expect("Failed to execute command");

    assert!(output.status.success(), "Command failed: {}", String::from_utf8_lossy(&output.stderr));
    
    assert!(std::path::Path::new(output_file).exists());
    let content = fs::read_to_string(output_file).unwrap();
    // Check for some expected content in the snapshot
    assert!(content.contains("Example Domain") || content.contains("example.com"));
    
    // Clean up
    let _ = std::fs::remove_file(output_file);
}

#[test]
fn test_recipe_3_login_flow() {
    let session_file = "test_e2e_auth.json";
    
    // Clean up
    if std::path::Path::new(session_file).exists() {
        let _ = std::fs::remove_file(session_file);
    }

    // Step 1: Login (simulated with echo)
    // We use a pipe to send newline to stdin
    let mut child = Command::new(bin_path())
        .arg("login")
        .arg("--url")
        .arg("https://example.com")
        .arg("--save-session")
        .arg(session_file)
        .stdin(std::process::Stdio::piped())
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .expect("Failed to spawn process");

    {
        let stdin = child.stdin.as_mut().expect("Failed to open stdin");
        use std::io::Write;
        stdin.write_all(b"\n").expect("Failed to write to stdin");
    }

    let output = child.wait_with_output().expect("Failed to read stdout");
    
    assert!(output.status.success(), "Login command failed: {}", String::from_utf8_lossy(&output.stderr));
    assert!(std::path::Path::new(session_file).exists(), "Session file was not created");

    // Step 2: Reuse session
    let output_nav = Command::new(bin_path())
        .arg("navigate")
        .arg("--url")
        .arg("https://example.com")
        .arg("--load-session")
        .arg(session_file)
        .output()
        .expect("Failed to execute navigate command");

    assert!(output_nav.status.success(), "Navigate with session failed: {}", String::from_utf8_lossy(&output_nav.stderr));
    let stderr_nav = String::from_utf8_lossy(&output_nav.stderr);
    assert!(stderr_nav.contains("Loading session from"));

    // Clean up
    let _ = std::fs::remove_file(session_file);
}
