#!/usr/bin/env python3
import sys
import json
import re

def parse_sessions(output):
    lines = output.strip().split('\n')
    if not lines:
        return []
    
    # The first line is the header
    header = lines[0]
    
    # Find column indices based on header positions
    # Header format: ID    Description    Repo    Last active    Status
    cols = ["ID", "Description", "Repo", "Last active", "Status"]
    indices = []
    for col in cols:
        indices.append(header.find(col))
    
    indices.append(len(header) + 50) # Sentinel

    sessions = []
    for line in lines[1:]:
        if not line.strip():
            continue
        
        session = {}
        for i in range(len(cols)):
            start = indices[i]
            end = indices[i+1]
            # Handle the fact that ID starts before its header label in some cases
            if cols[i] == "ID":
                # Look for a long digit string at the start of the line
                match = re.search(r'(\d+)', line[:indices[1]])
                if match:
                    val = match.group(1)
                else:
                    val = line[start:end].strip()
            else:
                val = line[start:end].strip()
            
            session[cols[i].lower().replace(" ", "_")] = val
        
        sessions.append(session)
    
    return sessions

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    
    print(json.dumps(parse_sessions(content), indent=2))