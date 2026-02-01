#!/bin/bash
# Search for train connections between two stations
# Usage: ./trip.sh <from-station> <to-station> [date] [time] [num-results]
#
# Date format: YYYYMMDD (default: today)
# Time format: HHMM (default: now)
# Example: ./trip.sh "Wien Hbf" "Salzburg Hbf" 20260109 0800 5

FROM="${1:-}"
TO="${2:-}"
DATE="${3:-$(date +%Y%m%d)}"
TIME="${4:-$(date +%H%M)}00"
NUM="${5:-5}"

if [ -z "$FROM" ] || [ -z "$TO" ]; then
    echo "Usage: $0 <from-station> <to-station> [date] [time] [num-results]"
    echo "Example: $0 'Wien Hbf' 'Salzburg Hbf' 20260109 0800 5"
    exit 1
fi

# Ensure time has seconds
if [ ${#TIME} -eq 4 ]; then
    TIME="${TIME}00"
fi

# First, resolve station names to LIDs
FROM_LID=$(curl -s -X POST "https://fahrplan.oebb.at/bin/mgate.exe" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"1","ver":"1.67","lang":"deu",
    "auth":{"type":"AID","aid":"OWDL4fE4ixNiPBBm"},
    "client":{"id":"OEBB","type":"WEB","name":"webapp","l":"vs_webapp"},
    "formatted":false,
    "svcReqL":[{
      "req":{"input":{"field":"S","loc":{"name":"'"$FROM"'","type":"S"},"maxLoc":1}},
      "meth":"LocMatch"
    }]
  }' | jq -r '.svcResL[0].res.match.locL[0].lid // empty')

TO_LID=$(curl -s -X POST "https://fahrplan.oebb.at/bin/mgate.exe" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"1","ver":"1.67","lang":"deu",
    "auth":{"type":"AID","aid":"OWDL4fE4ixNiPBBm"},
    "client":{"id":"OEBB","type":"WEB","name":"webapp","l":"vs_webapp"},
    "formatted":false,
    "svcReqL":[{
      "req":{"input":{"field":"S","loc":{"name":"'"$TO"'","type":"S"},"maxLoc":1}},
      "meth":"LocMatch"
    }]
  }' | jq -r '.svcResL[0].res.match.locL[0].lid // empty')

if [ -z "$FROM_LID" ]; then
    echo "Error: Could not find station: $FROM"
    exit 1
fi

if [ -z "$TO_LID" ]; then
    echo "Error: Could not find station: $TO"
    exit 1
fi

# Now search for trips
curl -s -X POST "https://fahrplan.oebb.at/bin/mgate.exe" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"1","ver":"1.67","lang":"deu",
    "auth":{"type":"AID","aid":"OWDL4fE4ixNiPBBm"},
    "client":{"id":"OEBB","type":"WEB","name":"webapp","l":"vs_webapp"},
    "formatted":false,
    "svcReqL":[{
      "req":{
        "depLocL":[{"lid":"'"$FROM_LID"'","type":"S"}],
        "arrLocL":[{"lid":"'"$TO_LID"'","type":"S"}],
        "jnyFltrL":[{"type":"PROD","mode":"INC","value":"1023"}],
        "getPolyline":false,
        "getPasslist":true,
        "outDate":"'"$DATE"'",
        "outTime":"'"$TIME"'",
        "outFrwd":true,
        "numF":'"$NUM"'
      },
      "meth":"TripSearch"
    }]
  }' | jq '
    .svcResL[0].res as $res |
    $res.outConL[] | {
      date: .date,
      departure: {
        time: (.dep.dTimeS | "\(.[0:2]):\(.[2:4])"),
        timeReal: (if .dep.dTimeR then (.dep.dTimeR | "\(.[0:2]):\(.[2:4])") else null end),
        platform: .dep.dPltfS.txt,
        station: ($res.common.locL[.dep.locX].name)
      },
      arrival: {
        time: (.arr.aTimeS | "\(.[0:2]):\(.[2:4])"),
        timeReal: (if .arr.aTimeR then (.arr.aTimeR | "\(.[0:2]):\(.[2:4])") else null end),
        platform: .arr.aPltfS.txt,
        station: ($res.common.locL[.arr.locX].name)
      },
      duration: (.dur | "\(.[0:2])h \(.[2:4])m"),
      changes: .chg,
      legs: [.secL[] | select(.type == "JNY") | {
        train: ($res.common.prodL[.jny.prodX].name // "Train"),
        category: ($res.common.prodL[.jny.prodX].prodCtx.catOutL // ""),
        direction: .jny.dirTxt,
        departure: {
          time: (.dep.dTimeS | "\(.[0:2]):\(.[2:4])"),
          station: ($res.common.locL[.dep.locX].name),
          platform: .dep.dPltfS.txt
        },
        arrival: {
          time: (.arr.aTimeS | "\(.[0:2]):\(.[2:4])"),
          station: ($res.common.locL[.arr.locX].name),
          platform: .arr.aPltfS.txt
        }
      }]
    }
  '
