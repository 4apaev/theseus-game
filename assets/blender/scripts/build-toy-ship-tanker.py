"""build the toy tanker for external review."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from toytraffic import build

build('tanker')
