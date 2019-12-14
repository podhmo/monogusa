import argparse
from magicalimport import import_module
from monogusa.cli.runtime import Driver


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("file")
    args, rest = parser.parse_known_args()
    m = import_module(args.file)
    Driver(prog=args.file).run(rest, module=m)


if __name__ == "__main__":
    main()
