"""build the dry-dock."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toylagrange

toylagrange.build('dry-dock')
