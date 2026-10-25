"""build the repair-tender."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toyutility

toyutility.build('repair-tender')
