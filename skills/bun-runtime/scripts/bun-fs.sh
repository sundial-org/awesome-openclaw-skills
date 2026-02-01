#!/usr/bin/env bash

# Bun filesystem operations
# Usage: scripts/bun-fs.sh <action> <path> [data]
# Actions: read, write

ACTION="$1"
FILEPATH="$2"
DATA="$3"

case "$ACTION" in
  read)
    bun -e "
      const file = Bun.file('$FILEPATH');
      if (!file.size) {
        console.log(JSON.stringify({ error: 'File not found or empty: $FILEPATH' }));
        process.exit(1);
      }
      console.log(JSON.stringify({ content: await file.text() }));
    "
    ;;
  write)
    bun -e "
      const path = require('path');
      const fs = require('fs');
      const dir = path.dirname('$FILEPATH');
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
      await Bun.write('$FILEPATH', '$DATA');
      console.log(JSON.stringify({ written: true, path: '$FILEPATH' }));
    "
    ;;
  *)
    echo "{\"error\":\"Invalid action: $ACTION\"}"
    exit 1
    ;;
esac
