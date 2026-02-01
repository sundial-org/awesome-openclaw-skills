#!/usr/bin/env python3
"""
Nest Device Access API client.
Supports credentials from 1Password or environment variables.
"""

import argparse
import json
import os
import subprocess
import sys

import requests

def get_credentials():
    """
    Retrieve Nest API credentials from 1Password or environment variables.
    
    1Password config (optional):
      - NEST_OP_VAULT: vault name (default: "Alfred")
      - NEST_OP_ITEM: item name (default: "Nest Device Access API")
      - OP_SERVICE_ACCOUNT_TOKEN or OP_TOKEN_*: 1Password token
    
    Environment variables (fallback):
      - NEST_PROJECT_ID
      - NEST_CLIENT_ID
      - NEST_CLIENT_SECRET
      - NEST_REFRESH_TOKEN
    """
    # Try 1Password first
    op_token = None
    for key in os.environ:
        if key.startswith('OP_TOKEN_') or key == 'OP_SERVICE_ACCOUNT_TOKEN':
            op_token = os.environ[key]
            break
    
    if op_token:
        vault = os.environ.get('NEST_OP_VAULT', 'Alfred')
        item = os.environ.get('NEST_OP_ITEM', 'Nest Device Access API')
        
        # Find op binary
        op_path = None
        for path in [os.path.expanduser('~/.local/bin/op'), '/usr/local/bin/op', 'op']:
            try:
                subprocess.run([path, '--version'], capture_output=True, check=True)
                op_path = path
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        if op_path:
            try:
                result = subprocess.run(
                    [op_path, 'item', 'get', item, '--vault', vault, '--format', 'json'],
                    capture_output=True, text=True,
                    env={**os.environ, 'OP_SERVICE_ACCOUNT_TOKEN': op_token}
                )
                if result.returncode == 0:
                    item_data = json.loads(result.stdout)
                    return {f['label']: f.get('value', '') for f in item_data['fields']}
            except Exception:
                pass  # Fall through to env vars
    
    # Fall back to environment variables
    required = ['NEST_PROJECT_ID', 'NEST_CLIENT_ID', 'NEST_CLIENT_SECRET', 'NEST_REFRESH_TOKEN']
    missing = [k for k in required if not os.environ.get(k)]
    
    if missing:
        raise RuntimeError(
            f"Missing credentials. Set environment variables: {', '.join(missing)}\n"
            "Or configure 1Password with OP_SERVICE_ACCOUNT_TOKEN"
        )
    
    return {
        'project_id': os.environ['NEST_PROJECT_ID'],
        'client_id': os.environ['NEST_CLIENT_ID'],
        'client_secret': os.environ['NEST_CLIENT_SECRET'],
        'refresh_token': os.environ['NEST_REFRESH_TOKEN'],
    }

def get_access_token(creds):
    """Get a fresh access token using the refresh token."""
    response = requests.post('https://oauth2.googleapis.com/token', data={
        'client_id': creds['client_id'],
        'client_secret': creds['client_secret'],
        'refresh_token': creds['refresh_token'],
        'grant_type': 'refresh_token'
    })
    response.raise_for_status()
    return response.json()['access_token']

class NestClient:
    """Client for the Nest Smart Device Management API."""
    
    BASE_URL = 'https://smartdevicemanagement.googleapis.com/v1'
    
    def __init__(self, creds=None):
        """
        Initialize the client.
        
        Args:
            creds: Optional dict with project_id, client_id, client_secret, refresh_token.
                   If not provided, credentials are loaded from 1Password or env vars.
        """
        self.creds = creds or get_credentials()
        self.project_id = self.creds['project_id']
        self.access_token = get_access_token(self.creds)
        self.headers = {'Authorization': f'Bearer {self.access_token}'}
    
    def _request(self, method, path, **kwargs):
        url = f"{self.BASE_URL}/enterprises/{self.project_id}{path}"
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response.json() if response.text else {}
    
    def list_devices(self):
        """List all devices."""
        return self._request('GET', '/devices').get('devices', [])
    
    def get_device(self, device_id):
        """Get a specific device by ID."""
        return self._request('GET', f'/devices/{device_id}')
    
    def execute_command(self, device_id, command, params=None):
        """Execute a command on a device."""
        body = {'command': command, 'params': params or {}}
        return self._request('POST', f'/devices/{device_id}:executeCommand', json=body)
    
    # ─── Thermostat ────────────────────────────────────────────────────────────
    
    def set_thermostat_mode(self, device_id, mode):
        """Set thermostat mode: HEAT, COOL, HEATCOOL, OFF."""
        return self.execute_command(
            device_id, 
            'sdm.devices.commands.ThermostatMode.SetMode', 
            {'mode': mode}
        )
    
    def set_heat_temperature(self, device_id, temp_celsius):
        """Set heat setpoint in Celsius."""
        return self.execute_command(
            device_id,
            'sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat',
            {'heatCelsius': temp_celsius}
        )
    
    def set_cool_temperature(self, device_id, temp_celsius):
        """Set cool setpoint in Celsius."""
        return self.execute_command(
            device_id,
            'sdm.devices.commands.ThermostatTemperatureSetpoint.SetCool',
            {'coolCelsius': temp_celsius}
        )
    
    def set_heat_cool_temperature(self, device_id, heat_celsius, cool_celsius):
        """Set both heat and cool setpoints for HEATCOOL mode."""
        return self.execute_command(
            device_id,
            'sdm.devices.commands.ThermostatTemperatureSetpoint.SetRange',
            {'heatCelsius': heat_celsius, 'coolCelsius': cool_celsius}
        )
    
    def set_eco_mode(self, device_id, mode):
        """Set eco mode: MANUAL_ECO or OFF."""
        return self.execute_command(
            device_id,
            'sdm.devices.commands.ThermostatEco.SetMode',
            {'mode': mode}
        )
    
    # ─── Camera ────────────────────────────────────────────────────────────────
    
    def generate_stream(self, device_id):
        """Generate a live stream URL for a camera (RTSP)."""
        return self.execute_command(
            device_id,
            'sdm.devices.commands.CameraLiveStream.GenerateRtspStream'
        )
    
    def generate_webrtc_stream(self, device_id, offer_sdp):
        """Generate a WebRTC stream for a camera."""
        return self.execute_command(
            device_id,
            'sdm.devices.commands.CameraLiveStream.GenerateWebRtcStream',
            {'offerSdp': offer_sdp}
        )
    
    def extend_stream(self, device_id, stream_token):
        """Extend an active RTSP stream."""
        return self.execute_command(
            device_id,
            'sdm.devices.commands.CameraLiveStream.ExtendRtspStream',
            {'streamExtensionToken': stream_token}
        )
    
    def stop_stream(self, device_id, stream_token):
        """Stop an active stream."""
        return self.execute_command(
            device_id,
            'sdm.devices.commands.CameraLiveStream.StopRtspStream',
            {'streamExtensionToken': stream_token}
        )


def format_device(device):
    """Format device info for display."""
    name = device['name'].split('/')[-1]
    device_type = device['type'].split('.')[-1]
    traits = device.get('traits', {})
    
    info = {'id': name, 'type': device_type}
    
    if 'sdm.devices.traits.Info' in traits:
        info['custom_name'] = traits['sdm.devices.traits.Info'].get('customName', '')
    
    if 'sdm.devices.traits.Temperature' in traits:
        temp = traits['sdm.devices.traits.Temperature'].get('ambientTemperatureCelsius')
        if temp:
            info['temperature_c'] = round(temp, 1)
            info['temperature_f'] = round(temp * 9/5 + 32, 1)
    
    if 'sdm.devices.traits.Humidity' in traits:
        info['humidity'] = traits['sdm.devices.traits.Humidity'].get('ambientHumidityPercent')
    
    if 'sdm.devices.traits.ThermostatMode' in traits:
        info['mode'] = traits['sdm.devices.traits.ThermostatMode'].get('mode')
        info['available_modes'] = traits['sdm.devices.traits.ThermostatMode'].get('availableModes', [])
    
    if 'sdm.devices.traits.ThermostatTemperatureSetpoint' in traits:
        setpoint = traits['sdm.devices.traits.ThermostatTemperatureSetpoint']
        if 'heatCelsius' in setpoint:
            info['heat_setpoint_c'] = round(setpoint['heatCelsius'], 1)
        if 'coolCelsius' in setpoint:
            info['cool_setpoint_c'] = round(setpoint['coolCelsius'], 1)
    
    if 'sdm.devices.traits.ThermostatHvac' in traits:
        info['hvac_status'] = traits['sdm.devices.traits.ThermostatHvac'].get('status')
    
    if 'sdm.devices.traits.ThermostatEco' in traits:
        eco = traits['sdm.devices.traits.ThermostatEco']
        info['eco_mode'] = eco.get('mode')
        if 'heatCelsius' in eco:
            info['eco_heat_c'] = eco['heatCelsius']
        if 'coolCelsius' in eco:
            info['eco_cool_c'] = eco['coolCelsius']
    
    if 'sdm.devices.traits.CameraLiveStream' in traits:
        info['live_stream'] = True
        info['stream_protocols'] = traits['sdm.devices.traits.CameraLiveStream'].get('supportedProtocols', [])
    
    if 'sdm.devices.traits.CameraEventImage' in traits:
        info['event_image'] = True
    
    return info


def fahrenheit_to_celsius(f):
    return (f - 32) * 5/9


def main():
    parser = argparse.ArgumentParser(description='Nest Device Access API client')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List devices
    subparsers.add_parser('list', help='List all devices')
    
    # Get device
    get_parser = subparsers.add_parser('get', help='Get device details')
    get_parser.add_argument('device_id', help='Device ID')
    
    # Set temperature
    temp_parser = subparsers.add_parser('set-temp', help='Set thermostat temperature')
    temp_parser.add_argument('device_id', help='Device ID')
    temp_parser.add_argument('temperature', type=float, help='Temperature')
    temp_parser.add_argument('--unit', choices=['c', 'f'], default='c', help='Unit (c/f)')
    temp_parser.add_argument('--type', choices=['heat', 'cool'], default='heat', help='Setpoint type')
    
    # Set mode
    mode_parser = subparsers.add_parser('set-mode', help='Set thermostat mode')
    mode_parser.add_argument('device_id', help='Device ID')
    mode_parser.add_argument('mode', choices=['HEAT', 'COOL', 'HEATCOOL', 'OFF'], help='Mode')
    
    # Set eco
    eco_parser = subparsers.add_parser('set-eco', help='Set eco mode')
    eco_parser.add_argument('device_id', help='Device ID')
    eco_parser.add_argument('mode', choices=['MANUAL_ECO', 'OFF'], help='Eco mode')
    
    # Camera stream
    stream_parser = subparsers.add_parser('stream', help='Generate camera stream URL')
    stream_parser.add_argument('device_id', help='Device ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        client = NestClient()
        
        if args.command == 'list':
            devices = client.list_devices()
            print(json.dumps([format_device(d) for d in devices], indent=2))
        
        elif args.command == 'get':
            device = client.get_device(args.device_id)
            print(json.dumps(format_device(device), indent=2))
        
        elif args.command == 'set-temp':
            temp = args.temperature
            if args.unit == 'f':
                temp = fahrenheit_to_celsius(temp)
            
            if args.type == 'heat':
                client.set_heat_temperature(args.device_id, temp)
            else:
                client.set_cool_temperature(args.device_id, temp)
            print(json.dumps({'success': True, 'setpoint_c': round(temp, 1)}))
        
        elif args.command == 'set-mode':
            client.set_thermostat_mode(args.device_id, args.mode)
            print(json.dumps({'success': True, 'mode': args.mode}))
        
        elif args.command == 'set-eco':
            client.set_eco_mode(args.device_id, args.mode)
            print(json.dumps({'success': True, 'eco_mode': args.mode}))
        
        elif args.command == 'stream':
            result = client.generate_stream(args.device_id)
            print(json.dumps(result, indent=2))
    
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
