#!/bin/bash
# Get current service disruptions and alerts
# Usage: ./disruptions.sh [max-results]
#
# Example: ./disruptions.sh 20

MAX="${1:-20}"

curl -s -X POST "https://fahrplan.oebb.at/bin/mgate.exe" \
  -H "Content-Type: application/json" \
  -d '{
    "id":"1","ver":"1.67","lang":"deu",
    "auth":{"type":"AID","aid":"OWDL4fE4ixNiPBBm"},
    "client":{"id":"OEBB","type":"WEB","name":"webapp","l":"vs_webapp"},
    "formatted":false,
    "svcReqL":[{
      "req":{
        "himFltrL":[{"type":"PROD","mode":"INC","value":"255"}],
        "maxNum":'"$MAX"'
      },
      "meth":"HimSearch"
    }]
  }' | jq '
    .svcResL[0].res.msgL[] | {
      id: .hid,
      title: .head,
      text: (.text | gsub("<[^>]*>"; "")),
      priority: .prio,
      startDate: .sDate,
      endDate: .eDate,
      active: .act
    }
  '
