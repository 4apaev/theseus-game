"""build the container-ship."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import toybulk

toybulk.build('container-ship')
