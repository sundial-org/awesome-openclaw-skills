#!/usr/bin/env python3
import subprocess
import sys
import os
import json
import argparse

def run_command(cmd, shell=True, capture=True):
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=capture, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {cmd}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return None

def get_session_info(session_id):
    """Use parse_sessions.py to get session information robustly."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    parse_script = os.path.join(script_dir, "parse_sessions.py")
    
    list_output = run_command("jules remote list --session")
    if not list_output:
        return None
    
    # Use parse_sessions.py to parse the output
    try:
        result = subprocess.run(
            ["python3", parse_script],
            input=list_output,
            capture_output=True,
            text=True,
            check=True
        )
        sessions = json.loads(result.stdout)
        
        # Find the session with matching ID
        for session in sessions:
            if session.get("id") == session_id:
                return session
        
        return None
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error parsing session list: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Jules CLI Wrapper for Automated Workflows")
    parser.add_argument("task", help="The task description")
    parser.add_argument("--repo", help="Repository to work on (format: username/repo)")
    parser.add_argument("--no-wait", action="store_true", help="Don't wait for session to complete")
    
    args = parser.parse_args()

    # Environment Check
    if "HOME" not in os.environ:
        print("Warning: HOME environment variable is not set. Jules might not find its credentials.")
        # Try to set it to current user's home if we can
        import getpass
        os.environ["HOME"] = f"/home/{getpass.getuser()}"
        print(f"Set HOME to {os.environ['HOME']}")

    creds_path = os.path.expanduser("~/.jules/cache/oauth_creds.json")
    if not os.path.exists(creds_path):
        print(f"Error: Jules credentials not found at {creds_path}. Please run 'jules login' first.")
        sys.exit(1)

    # 1. Create Session
    new_cmd = f'jules remote new --session "{args.task}"'
    if args.repo:
        new_cmd += f" --repo {args.repo}"
    
    print(f"Creating Jules session: {new_cmd}")
    # Run with /dev/null to avoid TTY issues
    output = run_command(f"{new_cmd} < /dev/null")
    if not output:
        sys.exit(1)

    # Get the first session from the list (most recently created)
    session_info = get_session_info(None)
    if not session_info:
        print("Could not retrieve session information from jules remote list")
        sys.exit(1)
    
    # If we didn't get a specific ID from parsing, use the first (most recent) session
    # that matches our task description
    session_id = session_info.get("id")
    if not session_id:
        print("Could not parse Session ID from session list")
        sys.exit(1)
    
    print(f"Session created with ID: {session_id}")

    if args.no_wait:
        print(f"Session {session_id} is running. URL: https://jules.google.com/session/{session_id}")
        return

    # 2. Wait for Session
    script_dir = os.path.dirname(os.path.realpath(__file__))
    wait_script = os.path.join(script_dir, "wait_for_session.sh")
    print(f"Waiting for session {session_id} to complete...")
    
    # Use the wait_for_session.sh script to avoid code duplication
    wait_result = run_command(f"bash {wait_script} {session_id}")
    if wait_result is None:
        sys.exit(1)

    # 3. Pull and Apply
    print(f"Pulling and applying changes for session {session_id}...")
    pull_output = run_command(f"jules remote pull --session {session_id} --apply < /dev/null")
    if pull_output is None:
        sys.exit(1)
    print("Changes applied successfully.")
    print(f"Session complete! URL: https://jules.google.com/session/{session_id}")

if __name__ == "__main__":
    main()
