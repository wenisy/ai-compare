#!/usr/bin/env bash

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "To run 'simulation.py' from this environment, use:"
echo "  source .venv/bin/activate && python simulation.py"
f