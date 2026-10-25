"""build the ore-carrier."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toybulk

toybulk.build('ore-carrier')
