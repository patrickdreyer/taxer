#!/bin/bash
set -e
pip install --root-user-action=ignore --upgrade pip
pip install --root-user-action=ignore -r /workspaces/taxer/.devcontainer/pip-requirements.txt
