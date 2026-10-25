"""build the military, industrial and research hulls."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toyships

for kind in ('military', 'industrial', 'research'):
    toyships.build(kind)
