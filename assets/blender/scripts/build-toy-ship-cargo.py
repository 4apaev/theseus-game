"""build the cargo hull and module ports."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toyships

toyships.build('cargo')
