import argparse
import os
from magicalimport import import_module
from monogusa.cli.runtime import Driver


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("file")
    args, rest = parser.parse_known_args()
    m = import_module(args.file)

    debug = bool(os.environ.get("DEBUG"))
    if os.environ.get("LOGGING"):
        import logging

        logging.basicConfig(level=getattr(logging, os.environ.get("LOGGING").upper()))
    Driver(prog=args.file).run(rest, module=m, debug=debug)


if __name__ == "__main__":
    main()
