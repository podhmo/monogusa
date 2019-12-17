import argparse
from monogusa.cli import run
from magicalimport import import_module


def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("file")
    args, rest = parser.parse_known_args()
    m = import_module(args.file)
    run(m, filename=args.file, args=rest)


if __name__ == "__main__":
    main()
