"""build the outpost with five docking platforms."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paintedstations import build

build('outpost', docking=True)
