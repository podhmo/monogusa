import sys
import argparse
from monogusa.cli import run
from magicalimport import import_module


def main() -> None:
    import logging

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("file")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--logging", dest="loglevel", choices=list(logging._nameToLevel.keys())
    )
    if "-" in sys.argv:
        i = sys.argv.index("-")
        raw_args, rest = sys.argv[1:i], sys.argv[i + 1 :]
        args = parser.parse_args(raw_args)
    else:
        args, rest = parser.parse_known_args()
    m = import_module(args.file)
    run(m, filename=args.file, args=rest, debug=args.debug, loglevel=args.loglevel)


if __name__ == "__main__":
    main()
