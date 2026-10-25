"""build orbit controls and sprites."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toyorbit

toyorbit.build()
