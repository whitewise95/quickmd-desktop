import sys
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "_worker":
        from quickmd.engine import worker

        raise SystemExit(worker(Path(sys.argv[2]), Path(sys.argv[3])))
    from quickmd.cli import main

    raise SystemExit(main())
