# type: ignore
def test_create_parser():
    from . import _commands as module
    from monogusa.cli.runtime import create_parser

    parser = create_parser(module)
    got = parser.format_help()

    want = """\
usage: pytest [-h] {hello,bye} ...

optional arguments:
  -h, --help   show this help message and exit

subcommands:
  {hello,bye}
    hello      hello world, example
    bye        byebye, example
"""

    assert got == want
