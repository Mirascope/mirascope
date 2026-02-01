"""Allow running with `python -m mirascope.cli`."""

from mirascope.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
