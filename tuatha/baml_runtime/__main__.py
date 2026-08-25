"""CLI: python3 -m tuatha.baml_runtime run"""
import asyncio
import sys
from .extractor import run_all_subjects


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        asyncio.run(run_all_subjects())
    else:
        print("  usage: python3 -m tuatha.baml_runtime run")


if __name__ == "__main__":
    main()
