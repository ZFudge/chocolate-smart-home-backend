#!/bin/sh

echo "Checking if backend is healthy..."
#  Check if the uvicorn process is running
[ $(ps | grep 'uvicorn src.main:app' | wc -l) -ge 1 ] || exit 1

exit 0
