#!/usr/bin/env python3
"""
VEO - Modern Video Generation Engine
Main entry point for the VEO system.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from veo.cli.main import app

if __name__ == "__main__":
    app()
