"""build the gas-station."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toylagrange

toylagrange.build('gas-station')
