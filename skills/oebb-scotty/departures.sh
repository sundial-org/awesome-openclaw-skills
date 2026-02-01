#!/bin/bash
# Get departures from an ÖBB station
# Usage: ./departures.sh <station-name> [date] [time] [max-results]
#
# Date format: YYYYMMDD (default: today)
# Time format: HHMM (default: now)
# Example: ./departures.sh "Wien Hbf" 20260109 0800 20

STATION="${1:-}"
DATE="${2:-$(date +%Y%m%d)}"
TIME="${3:-$(date +%H%M)}00"
MAX="${4:-20}"

if [ -z "$STATION" ]; then
    echo "Usage: $0 <station-name> [date] [time] [max-results]"
    echo "Example: $0 'Wien Hbf' 20260109 0800 20"
    exit 1
fi

# Ensure time has seconds
if [ ${#TIME} -eq 4 ]; then
    TIME="${TIME}00"
fi

# First, resolve station name to LID
STATION_LID=$(curl -s -X POST "https://fahrplan.oebb.at/bin/mgate.exe" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"1","ver":"1.67","lang":"deu",
    "auth":{"type":"AID","aid":"OWDL4fE4ixNiPBBm"},
    "client":{"id":"OEBB","type":"WEB","name":"webapp","l":"vs_webapp"},
    "formatted":false,
    "svcReqL":[{
      "req":{"input":{"field":"S","loc":{"name":"'"$STATION"'","type":"S"},"maxLoc":1}},
      "meth":"LocMatch"
    }]
  }' | jq -r '.svcResL[0].res.match.locL[0].lid // empty')

if [ -z "$STATION_LID" ]; then
    echo "Error: Could not find station: $STATION"
    exit 1
fi

# Get departures
curl -s -X POST "https://fahrplan.oebb.at/bin/mgate.exe" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"1","ver":"1.67","lang":"deu",
    "auth":{"type":"AID","aid":"OWDL4fE4ixNiPBBm"},
    "client":{"id":"OEBB","type":"WEB","name":"webapp","l":"vs_webapp"},
    "formatted":false,
    "svcReqL":[{
      "req":{
        "stbLoc":{"lid":"'"$STATION_LID"'","type":"S"},
        "date":"'"$DATE"'",
        "time":"'"$TIME"'",
        "type":"DEP",
        "maxJny":'"$MAX"'
      },
      "meth":"StationBoard"
    }]
  }' | jq '
    .svcResL[0].res as $res |
    {
      station: ($res.common.locL[0].name),
      date: "'"$DATE"'",
      departures: [
        $res.jnyL[] | {
          time: (.stbStop.dTimeS | "\(.[0:2]):\(.[2:4])"),
          timeReal: (if .stbStop.dTimeR then (.stbStop.dTimeR | "\(.[0:2]):\(.[2:4])") else null end),
          delay: (if .stbStop.dTimeR and .stbStop.dTimeS then
            (((.stbStop.dTimeR[0:2] | tonumber) * 60 + (.stbStop.dTimeR[2:4] | tonumber)) -
             ((.stbStop.dTimeS[0:2] | tonumber) * 60 + (.stbStop.dTimeS[2:4] | tonumber)))
          else null end),
          platform: .stbStop.dPltfS.txt,
          train: ($res.common.prodL[.prodX].name // ""),
          category: ($res.common.prodL[.prodX].prodCtx.catOutL // ""),
          direction: .dirTxt,
          cancelled: (.stbStop.dCncl // false)
        }
      ]
    }
  '
