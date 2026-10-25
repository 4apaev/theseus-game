"""build the gas-carrier freighter."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toyfreighters

toyfreighters.build('gas-carrier')
