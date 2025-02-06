#!/bin/sh

set -eu

manifest_version() {
    sed -n -e 's/^.*"version": "\([0-9\.]\+\)".*$/\1/p' custom_components/smartbox/manifest.json
}

module_version() {
    sed -n -e 's/^__version__ = "\([0-9\.]\+\)".*$/\1/p' custom_components/smartbox/__init__.py
}

manifest_smartbox_version() {
    sed -n -e 's/^.*\(smartbox==[0-9\.]\+\(b[0-9]\+\)\?\).*$/\1/p' custom_components/smartbox/manifest.json
}

requirements_smartbox_version() {
    sed -n -e 's/^.*\(smartbox==[0-9\.]\+\(b[0-9]\+\)\?\).*$/\1/p' requirements_common.txt
}

echo Checking manifest and module versions match...
if [ "$(manifest_version)" != "$(module_version)" ]
then
    echo "Manifest version $(manifest_version) does not match module $(module_version)" >&2
    exit 1
fi

echo Checking manifest and requirements smartbox versions match...
if [ "$(manifest_smartbox_version)" != "$(requirements_smartbox_version)" ]
then
    echo "Manifest smartbox version $(manifest_smartbox_version) does not match requirements smartbox version $(requirements_smartbox_version)" >&2
    exit 1
fi

echo Checking black formatting...
black --check .

echo Checking ruff...
ruff check .

echo Checking mypy...
mypy .
