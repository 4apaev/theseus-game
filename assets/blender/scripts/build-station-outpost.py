"""build the painted outpost station."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paintedstations import build

build('outpost')
