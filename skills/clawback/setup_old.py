#!/usr/bin/env python3
"""
ClawBack - Congressional Trade Mirror Bot
Setup script for installation and configuration
"""
import os
import sys
import subprocess
import json

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        return False
    print(f"Python {sys.version_info.major}.{sys.version_info.minor} detected - OK")
    return True

def install_requirements():
    """Install required Python packages"""
    print("\nInstalling required packages...")
    
    requirements_file = os.path.join('src', 'requirements.txt')
    
    if not os.path.exists(requirements_file):
        print(f"Error: Requirements file not found at {requirements_file}")
        return False
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print("Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing requirements: {e}")
        return False

def setup_directories():
    """Create necessary directories"""
    print("\nSetting up directories...")
    
    directories = ['logs', 'data', 'config']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory exists: {directory}")
    
    return True

def check_config():
    """Check if configuration file exists"""
    print("\nChecking configuration...")
    
    config_file = os.path.join('config', 'config.json')
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Check for API keys
            if config.get('etrade', {}).get('apiKey'):
                print("Configuration file found with API keys - OK")
            else:
                print("Warning: API keys not found in config.json")
                print("Please add your E*TRADE API keys to config/config.json")
            
            return True
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {config_file}")
            return False
    else:
        print(f"Error: Config file not found at {config_file}")
        print("Please create config/config.json with your API keys")
        return False

def create_example_config():
    """Create example configuration file"""
    print("\nCreating example configuration...")
    
    example_config = {
        "etrade": {
            "environment": "sandbox",
            "apiKey": "YOUR_SANDBOX_API_KEY_HERE",
            "apiSecret": "YOUR_SANDBOX_API_SECRET_HERE",
            "baseUrl": "https://apisb.etrade.com",
            "oauth": {
                "requestTokenUrl": "https://apisb.etrade.com/oauth/request_token",
                "accessTokenUrl": "https://apisb.etrade.com/oauth/access_token",
                "authorizeUrl": "https://us.etrade.com/e/t/etws/authorize"
            }
        },
        "trading": {
            "accountId": "",
            "tradeScalePercentage": 0.01,
            "maxPositionPercentage": 0.05,
            "dailyLossLimit": 0.02,
            "tradeDelayMinutes": 5,
            "marketHoursOnly": True,
            "marketOpen": "09:30",
            "marketClose": "16:00"
        },
        "congress": {
            "dataSource": "official",
            "pollIntervalHours": 24,
            "minimumTradeSize": 10000,
            "tradeTypes": ["purchase", "sale"]
        },
        "logging": {
            "level": "info",
            "file": "logs/trading.log",
            "maxSize": "10MB",
            "maxFiles": 10
        }
    }
    
    config_dir = 'config'
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    example_file = os.path.join(config_dir, 'config.example.json')
    
    with open(example_file, 'w') as f:
        json.dump(example_config, f, indent=2)
    
    print(f"Example configuration created at {example_file}")
    print("Please copy to config.json and add your API keys")
    
    return True

def setup_environment():
    """Setup Python virtual environment"""
    print("\nSetting up Python environment...")
    
    venv_dir = 'venv'
    
    if not os.path.exists(venv_dir):
        try:
            print("Creating virtual environment...")
            subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
            print(f"Virtual environment created at {venv_dir}")
            
            # Determine activation command
            if sys.platform == 'win32':
                activate_cmd = os.path.join(venv_dir, 'Scripts', 'activate')
            else:
                activate_cmd = f"source {os.path.join(venv_dir, 'bin', 'activate')}"
            
            print(f"\nTo activate the virtual environment, run:")
            print(f"  {activate_cmd}")
            
        except subprocess.CalledProcessError as e:
            print(f"Error creating virtual environment: {e}")
            return False
    else:
        print(f"Virtual environment already exists at {venv_dir}")
    
    return True

def main():
    """Main setup function"""
    print("="*60)
    print("ClawBack - Congressional Trade Mirror - Setup")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Ask for setup options
    print("\nSetup options:")
    print("1. Full setup (recommended)")
    print("2. Install requirements only")
    print("3. Create directories only")
    print("4. Create example config only")
    print("5. Setup virtual environment only")
    
    try:
        choice = input("\nSelect option (1-5, default 1): ").strip() or '1'
        
        if choice == '1':
            # Full setup
            setup_directories()
            create_example_config()
            setup_environment()
            install_requirements()
            
            print("\n" + "="*60)
            print("Setup complete!")
            print("\nNext steps:")
            print("1. Edit config/config.json with your E*TRADE API keys")
            print("2. Run: python src/main.py auth (to authenticate)")
            print("3. Run: python src/main.py interactive (for interactive mode)")
            print("="*60)
            
        elif choice == '2':
            install_requirements()
        elif choice == '3':
            setup_directories()
        elif choice == '4':
            create_example_config()
        elif choice == '5':
            setup_environment()
        else:
            print("Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\nSetup cancelled")
        return

if __name__ == "__main__":
    main()