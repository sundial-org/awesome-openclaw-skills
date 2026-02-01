#!/bin/bash
# Get arrivals at an ÖBB station
# Usage: ./arrivals.sh <station-name> [date] [time] [max-results]
#
# Date format: YYYYMMDD (default: today)
# Time format: HHMM (default: now)
# Example: ./arrivals.sh "Salzburg Hbf" 20260109 0800 20

STATION="${1:-}"
DATE="${2:-$(date +%Y%m%d)}"
TIME="${3:-$(date +%H%M)}00"
MAX="${4:-20}"

if [ -z "$STATION" ]; then
    echo "Usage: $0 <station-name> [date] [time] [max-results]"
    echo "Example: $0 'Salzburg Hbf' 20260109 0800 20"
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

# Get arrivals
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
        "type":"ARR",
        "maxJny":'"$MAX"'
      },
      "meth":"StationBoard"
    }]
  }' | jq '
    .svcResL[0].res as $res |
    {
      station: ($res.common.locL[0].name),
      date: "'"$DATE"'",
      arrivals: [
        $res.jnyL[] | {
          time: (.stbStop.aTimeS | "\(.[0:2]):\(.[2:4])"),
          timeReal: (if .stbStop.aTimeR then (.stbStop.aTimeR | "\(.[0:2]):\(.[2:4])") else null end),
          delay: (if .stbStop.aTimeR and .stbStop.aTimeS then
            (((.stbStop.aTimeR[0:2] | tonumber) * 60 + (.stbStop.aTimeR[2:4] | tonumber)) -
             ((.stbStop.aTimeS[0:2] | tonumber) * 60 + (.stbStop.aTimeS[2:4] | tonumber)))
          else null end),
          platform: .stbStop.aPltfS.txt,
          train: ($res.common.prodL[.prodX].name // ""),
          category: ($res.common.prodL[.prodX].prodCtx.catOutL // ""),
          from: .dirTxt,
          cancelled: (.stbStop.aCncl // false)
        }
      ]
    }
  '
