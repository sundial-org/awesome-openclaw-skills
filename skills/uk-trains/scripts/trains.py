#!/usr/bin/env python3
"""UK Trains CLI - Query National Rail Darwin API directly via SOAP"""

import sys
import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from urllib.error import URLError, HTTPError

TOKEN = os.environ.get('NATIONAL_RAIL_TOKEN', '')
ENDPOINT = 'https://lite.realtime.nationalrail.co.uk/OpenLDBWS/ldb12.asmx'

# Namespace mappings
NS = {
    'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
    'lt': 'http://thalesgroup.com/RTTI/2012-01-13/ldb/types',
    'lt4': 'http://thalesgroup.com/RTTI/2015-11-27/ldb/types',
    'lt5': 'http://thalesgroup.com/RTTI/2016-02-16/ldb/types',
    'lt7': 'http://thalesgroup.com/RTTI/2017-10-01/ldb/types',
    'lt8': 'http://thalesgroup.com/RTTI/2021-11-01/ldb/types',
    'ldb': 'http://thalesgroup.com/RTTI/2021-11-01/ldb/',
}

def soap_request(action: str, body: str) -> str:
    """Make a SOAP request to the Darwin API."""
    envelope = f'''<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <AccessToken xmlns="http://thalesgroup.com/RTTI/2013-11-28/Token/types">
      <TokenValue>{TOKEN}</TokenValue>
    </AccessToken>
  </soap:Header>
  <soap:Body>
    {body}
  </soap:Body>
</soap:Envelope>'''
    
    req = urllib.request.Request(
        ENDPOINT,
        data=envelope.encode('utf-8'),
        headers={
            'Content-Type': 'text/xml;charset=UTF-8',
            'SOAPAction': action,
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode('utf-8')
    except HTTPError as e:
        print(json.dumps({'error': f'HTTP {e.code}: {e.reason}'}), file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(json.dumps({'error': str(e.reason)}), file=sys.stderr)
        sys.exit(1)

def get_text(elem, path: str, ns=NS) -> str:
    """Get text from an element, trying multiple namespace prefixes."""
    for prefix in ['lt4', 'lt5', 'lt8', 'lt']:
        try:
            full_path = '/'.join(f'{prefix}:{p}' if ':' not in p else p for p in path.split('/'))
            found = elem.find(full_path, ns)
            if found is not None and found.text:
                return found.text.strip()
        except:
            pass
    return ''

def parse_location(loc_elem) -> dict:
    """Parse a location element."""
    return {
        'name': get_text(loc_elem, 'location/locationName') or get_text(loc_elem, 'locationName'),
        'crs': get_text(loc_elem, 'location/crs') or get_text(loc_elem, 'crs'),
        'via': get_text(loc_elem, 'location/via') or get_text(loc_elem, 'via'),
    }

def parse_service(svc) -> dict:
    """Parse a train service element."""
    # Get origin(s)
    origins = []
    for orig in svc.findall('.//lt5:origin/lt4:location', NS) or svc.findall('.//lt4:origin/lt4:location', NS):
        origins.append({
            'name': get_text(orig, 'locationName'),
            'crs': get_text(orig, 'crs'),
        })
    
    # Get destination(s)
    destinations = []
    for dest in svc.findall('.//lt5:destination/lt4:location', NS) or svc.findall('.//lt4:destination/lt4:location', NS):
        destinations.append({
            'name': get_text(dest, 'locationName'),
            'crs': get_text(dest, 'crs'),
            'via': get_text(dest, 'via'),
        })
    
    # Count coaches if formation data exists
    coaches = svc.findall('.//lt7:coach', NS) or svc.findall('.//{http://thalesgroup.com/RTTI/2017-10-01/ldb/types}coach')
    coach_count = len(coaches) if coaches else None
    
    # Also check for explicit length field
    length = get_text(svc, 'length')
    carriages = int(length) if length else coach_count
    
    return {
        'std': get_text(svc, 'std'),  # Scheduled departure
        'etd': get_text(svc, 'etd'),  # Expected departure
        'sta': get_text(svc, 'sta'),  # Scheduled arrival
        'eta': get_text(svc, 'eta'),  # Expected arrival
        'platform': get_text(svc, 'platform'),
        'operator': get_text(svc, 'operator'),
        'operatorCode': get_text(svc, 'operatorCode'),
        'serviceType': get_text(svc, 'serviceType'),
        'serviceID': get_text(svc, 'serviceID'),
        'carriages': carriages,
        'isCancelled': get_text(svc, 'isCancelled') == 'true',
        'cancelReason': get_text(svc, 'cancelReason'),
        'delayReason': get_text(svc, 'delayReason'),
        'origin': origins,
        'destination': destinations,
    }

def get_departures(station: str, rows: int = 10, filter_to: str = None) -> dict:
    """Get departure board for a station."""
    filter_xml = ''
    if filter_to:
        filter_xml = f'<filterCrs>{filter_to.upper()}</filterCrs><filterType>to</filterType>'
    
    body = f'''<GetDepartureBoardRequest xmlns="http://thalesgroup.com/RTTI/2021-11-01/ldb/">
      <numRows>{rows}</numRows>
      <crs>{station.upper()}</crs>
      {filter_xml}
    </GetDepartureBoardRequest>'''
    
    xml_resp = soap_request('http://thalesgroup.com/RTTI/2012-01-13/ldb/GetDepartureBoard', body)
    return parse_board_response(xml_resp)

def get_arrivals(station: str, rows: int = 10, filter_from: str = None) -> dict:
    """Get arrival board for a station."""
    filter_xml = ''
    if filter_from:
        filter_xml = f'<filterCrs>{filter_from.upper()}</filterCrs><filterType>from</filterType>'
    
    body = f'''<GetArrivalBoardRequest xmlns="http://thalesgroup.com/RTTI/2021-11-01/ldb/">
      <numRows>{rows}</numRows>
      <crs>{station.upper()}</crs>
      {filter_xml}
    </GetArrivalBoardRequest>'''
    
    xml_resp = soap_request('http://thalesgroup.com/RTTI/2012-01-13/ldb/GetArrivalBoard', body)
    return parse_board_response(xml_resp)

def parse_board_response(xml_resp: str) -> dict:
    """Parse a departure/arrival board response."""
    root = ET.fromstring(xml_resp)
    
    # Find the result element
    result = root.find('.//ldb:GetStationBoardResult', NS)
    if result is None:
        result = root.find('.//{http://thalesgroup.com/RTTI/2021-11-01/ldb/}GetStationBoardResult')
    
    if result is None:
        # Check for fault
        fault = root.find('.//soap:Fault/faultstring', NS)
        if fault is not None:
            return {'error': fault.text}
        return {'error': 'Could not parse response'}
    
    # Parse messages
    messages = []
    for msg in result.findall('.//lt:message', NS):
        if msg.text:
            messages.append(msg.text.strip())
    
    # Parse services
    services = []
    for svc in result.findall('.//lt8:service', NS):
        services.append(parse_service(svc))
    
    return {
        'generatedAt': get_text(result, 'generatedAt'),
        'locationName': get_text(result, 'locationName'),
        'crs': get_text(result, 'crs'),
        'messages': messages,
        'trainServices': services,
    }

def cmd_departures(args):
    """Handle departures command."""
    station = args[0] if args else None
    if not station:
        print('Usage: trains.py departures <station> [to <dest>] [--rows N]', file=sys.stderr)
        sys.exit(1)
    
    rows = 10
    filter_to = None
    i = 1
    while i < len(args):
        if args[i] == 'to' and i + 1 < len(args):
            filter_to = args[i + 1]
            i += 2
        elif args[i] == '--rows' and i + 1 < len(args):
            rows = int(args[i + 1])
            i += 2
        else:
            i += 1
    
    result = get_departures(station, rows, filter_to)
    print(json.dumps(result, indent=2))

def cmd_arrivals(args):
    """Handle arrivals command."""
    station = args[0] if args else None
    if not station:
        print('Usage: trains.py arrivals <station> [from <origin>] [--rows N]', file=sys.stderr)
        sys.exit(1)
    
    rows = 10
    filter_from = None
    i = 1
    while i < len(args):
        if args[i] == 'from' and i + 1 < len(args):
            filter_from = args[i + 1]
            i += 2
        elif args[i] == '--rows' and i + 1 < len(args):
            rows = int(args[i + 1])
            i += 2
        else:
            i += 1
    
    result = get_arrivals(station, rows, filter_from)
    print(json.dumps(result, indent=2))

def cmd_search(args):
    """Search for stations - uses static CRS code list."""
    query = ' '.join(args).lower() if args else ''
    
    # Common stations (subset - full list would be much larger)
    stations = [
        ('PAD', 'London Paddington'), ('EUS', 'London Euston'), ('KGX', 'London Kings Cross'),
        ('STP', 'London St Pancras International'), ('VIC', 'London Victoria'), ('WAT', 'London Waterloo'),
        ('CHX', 'London Charing Cross'), ('LST', 'London Liverpool Street'), ('FST', 'London Fenchurch Street'),
        ('MYB', 'London Marylebone'), ('BHM', 'Birmingham New Street'), ('BHI', 'Birmingham International'),
        ('MAN', 'Manchester Piccadilly'), ('MCV', 'Manchester Victoria'), ('LDS', 'Leeds'),
        ('EDB', 'Edinburgh Waverley'), ('GLC', 'Glasgow Central'), ('GLQ', 'Glasgow Queen Street'),
        ('BRI', 'Bristol Temple Meads'), ('BPW', 'Bristol Parkway'), ('LIV', 'Liverpool Lime Street'),
        ('NCL', 'Newcastle'), ('SHF', 'Sheffield'), ('NOT', 'Nottingham'), ('CBG', 'Cambridge'),
        ('OXF', 'Oxford'), ('RDG', 'Reading'), ('BTN', 'Brighton'), ('SOU', 'Southampton Central'),
        ('PLY', 'Plymouth'), ('EXD', 'Exeter St Davids'), ('YRK', 'York'), ('PBO', 'Peterborough'),
        ('DID', 'Didcot Parkway'), ('SWI', 'Swindon'), ('CLJ', 'Clapham Junction'), ('CRE', 'Crewe'),
        ('COV', 'Coventry'), ('WVH', 'Wolverhampton'), ('LUT', 'Luton'), ('LTN', 'Luton Airport Parkway'),
        ('STN', 'Stansted Airport'), ('GTW', 'Gatwick Airport'), ('LGW', 'London Gatwick Airport'),
        ('SRA', 'Stratford'), ('HHE', 'Heathrow Airport'), ('GDP', 'Gidea Park'), ('ROM', 'Romford'),
    ]
    
    matches = []
    for crs, name in stations:
        if query in name.lower() or query in crs.lower():
            matches.append({'crsCode': crs, 'stationName': name})
    
    print(json.dumps(matches, indent=2))

def main():
    if not TOKEN:
        print(json.dumps({'error': 'NATIONAL_RAIL_TOKEN not set. Register at https://realtime.nationalrail.co.uk/OpenLDBWSRegistration/'}))
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print('''UK Trains CLI - National Rail Darwin API

Usage: trains.py <command> [args]

Commands:
  departures <station> [to <dest>] [--rows N]   Show departures
  arrivals <station> [from <origin>] [--rows N] Show arrivals
  search <query>                                Search for stations

Examples:
  trains.py departures PAD
  trains.py departures PAD to OXF --rows 5
  trains.py arrivals MAN from EUS
  trains.py search paddington

Environment:
  NATIONAL_RAIL_TOKEN  Your Darwin API token (required)
''', file=sys.stderr)
        sys.exit(1)
    
    cmd = sys.argv[1]
    args = sys.argv[2:]
    
    if cmd == 'departures':
        cmd_departures(args)
    elif cmd == 'arrivals':
        cmd_arrivals(args)
    elif cmd == 'search':
        cmd_search(args)
    else:
        print(f'Unknown command: {cmd}', file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
