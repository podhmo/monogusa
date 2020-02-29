import sys
import argparse
from monogusa.cli import run
from monogusa.cli import runtime
from monogusa.langhelpers import import_module


def main() -> None:
    from handofcats.customize import logging_setup

    parser = argparse.ArgumentParser(
        prog="monogusa.cli", add_help=False, formatter_class=runtime._HelpFormatter,
    )
    parser.add_argument("file")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--ignore-only", action="store_true")
    parser.add_argument("--cont", default=None)

    activate_logging = logging_setup(parser, debug=False)

    if "-" in sys.argv:
        i = sys.argv.index("-")
        raw_args, rest = sys.argv[1:i], sys.argv[i + 1 :]
        args = parser.parse_args(raw_args)
    else:
        args, rest = parser.parse_known_args()
    activate_logging(vars(args).copy())

    m = import_module(args.file, cwd=True)

    retval = run(
        m,
        filename=args.file,
        args=rest,
        debug=args.debug,
        ignore_only=args.ignore_only,
    )

    if retval is None:
        return

    if args.cont is None:
        cont = runtime.default_continuation
    else:
        from magicalimport import import_symbol

        cont = import_symbol(args.cont)
    cont(retval)


if __name__ == "__main__":
    main()
