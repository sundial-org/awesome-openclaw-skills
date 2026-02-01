
import asyncio
import hashlib
import json
import time
from datetime import datetime
import networkx as nx

try:
    from aioblescan import aioblescan as aiobs
except ImportError:
    print("aioblescan not available. BLE scanning may not function.")

SALT = "anima2026"

def hash_mac(mac: str) -> str:
    salted = (mac + SALT).encode("utf-8")
    return hashlib.sha256(salted).hexdigest()

def store_to_dag(mac_hashes):
    G = nx.DiGraph()
    timestamp = datetime.utcnow().isoformat()
    for h in mac_hashes:
        G.add_node(h, timestamp=timestamp)
    nx.write_gpickle(G, "anima_dag.gpickle")
    print(f"Stored {len(mac_hashes)} nodes to anima_dag.gpickle")

async def main():
    mac_hashes = set()

    def callback(data):
        ev = aiobs.HCI_Event()
        ev.decode(data)
        mac = ev.retrieve("peer")
        if mac:
            mac_str = str(mac[0].val)
            h = hash_mac(mac_str)
            mac_hashes.add(h)
            print(f"Detected MAC: {mac_str} → Hash: {h}")

    event_loop = asyncio.get_event_loop()
    socket = aiobs.create_bt_socket(0)
    fac = event_loop._create_connection_transport(socket, aiobs.BLEScanRequester, None, None)
    transport, protocol = await fac
    protocol.process = callback
    await protocol.send_scan_request()
    print("Scanning for 10 seconds...")
    await asyncio.sleep(10)
    await protocol.stop_scan_request()
    store_to_dag(mac_hashes)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Scan aborted.")
