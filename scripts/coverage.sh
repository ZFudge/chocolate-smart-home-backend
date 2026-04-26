#!/bin/bash

function checkPluginCoverage() {
    PLUGIN_NAME=$1
    echo "CHECKING TEST COVERAGE FOR \"$PLUGIN_NAME\" PLUGIN"
    PLUGIN_DIRECTORY="src/plugins/device_plugins/$PLUGIN_NAME"

    pytest --cov=$PLUGIN_DIRECTORY \
    --cov-report=term-missing \
    $PLUGIN_DIRECTORY/tests/
}
