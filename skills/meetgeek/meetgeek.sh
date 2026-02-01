#!/bin/bash
# Wrapper for meetgeek-cli that ensures correct node version
source ~/.nvm/nvm.sh && nvm use 22 > /dev/null 2>&1
exec meetgeek "$@"
