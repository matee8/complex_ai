#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Make backend/src importable
BASE_DIR = Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Point to settings in backend/src/complex_ai/settings.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "complex_ai.settings")

from django.core.management import execute_from_command_line

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
