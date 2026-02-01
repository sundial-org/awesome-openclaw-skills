#!/usr/bin/env python3
"""
Database query tool with SSH tunnel support.
Manages SSH connections and executes queries against configured databases.
"""

import json
import subprocess
import sys
import os
import signal
import time
import argparse
from typing import Dict, List, Optional, Tuple

# Global to track SSH processes
SSH_PROCESSES = {}

CONFIG_PATH = os.path.expanduser("~/.config/clawdbot/db-config.json")


def load_config(config_path: str = CONFIG_PATH) -> Dict:
    """Load database configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found at {config_path}")
        print(f"Expected format:")
        print(json.dumps({
            "databases": [
                {
                    "name": "name",
                    "host": "localhost",
                    "port": 3306,
                    "database": "db_name",
                    "user": "user",
                    "password": "password",
                    "ssh_tunnel": {
                        "enabled": True,
                        "ssh_host": "remote.example.com",
                        "ssh_user": "user",
                        "ssh_port": 22,
                        "local_port": 3307
                    }
                }
            ]
        }, indent=2))
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}")
        sys.exit(1)


def find_database(config: Dict, description: str) -> Optional[Dict]:
    """Find a database by description (name field)."""
    for db in config.get('databases', []):
        if description.lower() in db.get('name', '').lower():
            return db
    return None


def start_ssh_tunnel(tunnel_config: Dict) -> Optional[subprocess.Popen]:
    """Start SSH tunnel and return the process."""
    ssh_host = tunnel_config.get('ssh_host')
    ssh_user = tunnel_config.get('ssh_user')
    ssh_port = tunnel_config.get('ssh_port', 22)
    ssh_password = tunnel_config.get('ssh_password')
    local_port = tunnel_config.get('local_port')
    remote_host = tunnel_config.get('remote_host', 'localhost')
    remote_port = tunnel_config.get('remote_port', 3306)

    if not all([ssh_host, ssh_user, local_port]):
        print("Error: Incomplete SSH tunnel configuration")
        return None

    # Build SSH command
    ssh_cmd = [
        'ssh',
        '-N',  # No remote command
        '-L', f'{local_port}:{remote_host}:{remote_port}',
        '-p', str(ssh_port),
        '-o', 'ServerAliveInterval=60',
        '-o', 'ServerAliveCountMax=3',
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'UserKnownHostsFile=/dev/null',
        f'{ssh_user}@{ssh_host}'
    ]

    # Use sshpass if password is provided
    if ssh_password:
        ssh_cmd = ['sshpass', '-p', ssh_password] + ssh_cmd

    try:
        process = subprocess.Popen(
            ssh_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait briefly for SSH to establish
        time.sleep(1)

        # Check if process is still running
        if process.poll() is not None:
            _, stderr = process.communicate()
            print(f"Error: SSH tunnel failed: {stderr.decode()}")
            return None

        print(f"✓ SSH tunnel established: localhost:{local_port} -> {remote_host}:{remote_port} via {ssh_host}")
        return process

    except Exception as e:
        print(f"Error starting SSH tunnel: {e}")
        return None


def stop_ssh_tunnel(process: subprocess.Popen) -> bool:
    """Stop SSH tunnel process."""
    try:
        process.terminate()
        process.wait(timeout=5)
        print("✓ SSH tunnel closed")
        return True
    except Exception as e:
        try:
            process.kill()
            process.wait(timeout=2)
            print("✓ SSH tunnel killed")
            return True
        except Exception as e2:
            print(f"Error stopping SSH tunnel: {e2}")
            return False


def execute_mysql_query(host: str, port: int, database: str, user: str, password: str, query: str) -> bool:
    """Execute MySQL query using mysql command-line client."""
    mysql_cmd = [
        'mysql',
        '-h', host,
        '-P', str(port),
        '-u', user,
        f'-p{password}',
        database,
        '-e', query
    ]

    try:
        result = subprocess.run(
            mysql_cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing query: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: mysql client not found. Please install mysql-client.")
        return False


def list_databases(config: Dict):
    """List all configured databases."""
    print("\nConfigured databases:")
    print("-" * 60)
    for i, db in enumerate(config.get('databases', []), 1):
        name = db.get('name', 'Unnamed')
        host = db.get('host', 'N/A')
        db_name = db.get('database', 'N/A')
        ssh = ' (via SSH)' if db.get('ssh_tunnel', {}).get('enabled') else ''
        print(f"{i}. {name}{ssh}")
        print(f"   Host: {host} | Database: {db_name}")
    print("-" * 60)


def query_database(description: str, query: str, config_path: str = None):
    """Query a database by description."""
    config = load_config(config_path or CONFIG_PATH)
    db = find_database(config, description)

    if not db:
        print(f"Error: Database '{description}' not found")
        list_databases(config)
        sys.exit(1)

    print(f"\nQuerying database: {db.get('name')}")

    ssh_process = None
    tunnel_config = db.get('ssh_tunnel', {})

    # Start SSH tunnel if needed
    if tunnel_config.get('enabled'):
        ssh_process = start_ssh_tunnel(tunnel_config)
        if not ssh_process:
            sys.exit(1)

    try:
        # Determine connection parameters
        if ssh_process:
            host = '127.0.0.1'  # Use 127.0.0.1 instead of localhost to force TCP
            port = tunnel_config.get('local_port')
        else:
            host = db.get('host')
            port = db.get('port', 3306)

        # Execute query
        success = execute_mysql_query(
            host=host,
            port=port,
            database=db.get('database'),
            user=db.get('user'),
            password=db.get('password'),
            query=query
        )

    finally:
        # Always close SSH tunnel if we started one
        if ssh_process:
            stop_ssh_tunnel(ssh_process)


def cleanup():
    """Cleanup any running SSH tunnels."""
    if SSH_PROCESSES:
        print("\nCleaning up SSH tunnels...")
        for desc, process in list(SSH_PROCESSES.items()):
            stop_ssh_tunnel(process)
        SSH_PROCESSES.clear()


def main():
    parser = argparse.ArgumentParser(description='Query databases with SSH tunnel support')
    parser.add_argument('--list', action='store_true', help='List all configured databases')
    parser.add_argument('--query', type=str, help='SQL query to execute')
    parser.add_argument('--database', type=str, help='Database description/name')
    parser.add_argument('--config', type=str, help='Path to config file')

    args = parser.parse_args()

    # Set up cleanup on exit
    import atexit
    atexit.register(cleanup)

    # List databases
    if args.list:
        config = load_config(args.config or CONFIG_PATH)
        list_databases(config)
        sys.exit(0)

    # Query database
    if args.database and args.query:
        query_database(args.database, args.query, args.config)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
