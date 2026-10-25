"""build the asteroid-barge and its load."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toytowing

toytowing.build('asteroid-barge')
