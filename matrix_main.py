"""Chain together the intro, rain transition, and main Matrix console.

This launcher intentionally runs each stage in its own fresh Python process so
pygame does not reuse display state between scenes.
"""

import argparse
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Iterable, List


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_script(script_name: str) -> int:
    """Run a single script by spawning a new Python process."""

    script_path = os.path.join(ROOT_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"[MATRIX] Missing script: {script_path}")
        return 1

    cmd = [sys.executable, script_path]
    print(f"[MATRIX] Starting {script_name} -> {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        print(f"[MATRIX] {script_name} interrupted by user.")
        return 1

    if result.returncode != 0:
        print(f"[MATRIX] {script_name} exited with code {result.returncode}.")
    return result.returncode


def build_chain(skip_intro: bool, skip_rain: bool, skip_console: bool) -> List[str]:
    """Return the ordered list of scripts to run, respecting skip flags."""

    order = []
    if not skip_intro:
        order.append("wake_up_neo_intro_backup.py")
    if not skip_rain:
        order.append("matrix_rain_only.py")
    if not skip_console:
        order.append("matrix_console.py")
    return order


def validate_chain(chain: Iterable[str]) -> bool:
    """Ensure every script in the chain exists before running."""

    missing = []
    for script in chain:
        script_path = Path(ROOT_DIR, script)
        if not script_path.exists():
            missing.append(script_path)

    if missing:
        print("[MATRIX] Missing the following scripts:")
        for path in missing:
            print(f"  - {path}")
        return False

    return True


def list_project_files() -> None:
    """Print a quick overview of Python files in the project directory."""

    print("[MATRIX] Project files:")
    for path in sorted(Path(ROOT_DIR).glob("*.py")):
        size = path.stat().st_size
        print(f"  - {path.name} ({size} bytes)")


def chain_scripts(chain: Iterable[str], pause: float) -> int:
    """Run scripts in sequence, pausing between stages when requested."""

    for script in chain:
        code = run_script(script)
        if code != 0:
            print("[MATRIX] Aborting chain due to previous error.")
            return code

        if pause > 0:
            print(f"[MATRIX] Pausing {pause:.1f}s before next stage...")
            time.sleep(pause)

    return 0


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Matrix launcher chain")
    parser.add_argument("--skip-intro", action="store_true", help="Skip wake_up_neo intro")
    parser.add_argument("--skip-rain", action="store_true", help="Skip Matrix rain transition")
    parser.add_argument("--skip-console", action="store_true", help="Skip main console")
    parser.add_argument(
        "--list-files", action="store_true", help="List project Python files before running"
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=0.0,
        metavar="SECONDS",
        help="Seconds to pause between stages (default: 0)",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    chain = build_chain(args.skip_intro, args.skip_rain, args.skip_console)

    if args.list_files:
        list_project_files()

    if not chain:
        print("[MATRIX] Nothing to run: all stages skipped.")
        return 0

    if not validate_chain(chain):
        return 1

    return chain_scripts(chain, args.pause)


if __name__ == "__main__":
    sys.exit(main())
