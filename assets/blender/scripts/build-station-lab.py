"""build the painted lab station."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paintedstations import build

build('lab')
