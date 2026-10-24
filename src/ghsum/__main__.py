"""Allow `python -m ghsum owner/repo`."""

import sys

from ghsum.cli import main

sys.exit(main())
