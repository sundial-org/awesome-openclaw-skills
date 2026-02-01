#!/bin/bash
# Search ÖBB stations/stops by name
# Usage: ./search-station.sh <name>
#
# Returns: Station name, ID, and coordinates

QUERY="${1:-}"

if [ -z "$QUERY" ]; then
    echo "Usage: $0 <station-name>"
    echo "Example: $0 'Wien Hbf'"
    exit 1
fi

curl -s -X POST "https://fahrplan.oebb.at/bin/mgate.exe" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"1","ver":"1.67","lang":"deu",
    "auth":{"type":"AID","aid":"OWDL4fE4ixNiPBBm"},
    "client":{"id":"OEBB","type":"WEB","name":"webapp","l":"vs_webapp"},
    "formatted":false,
    "svcReqL":[{
      "req":{"input":{"field":"S","loc":{"name":"'"$QUERY"'","type":"ALL"},"maxLoc":10}},
      "meth":"LocMatch"
    }]
  }' | jq -r '
    .svcResL[0].res.match.locL[] |
    select(.type == "S") |
    {
      name: .name,
      id: .extId,
      lid: .lid,
      lat: ((.crd.y // 0) / 1000000),
      lon: ((.crd.x // 0) / 1000000)
    }
  '
