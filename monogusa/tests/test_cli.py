# type: ignore
import pytest


def test_create_parser() -> None:
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


def test_driver():
    import contextlib
    from io import StringIO
    from . import _commands as module
    from monogusa.cli.runtime import Driver

    driver = Driver()
    with contextlib.redirect_stdout(StringIO()) as o:
        driver.run(["hello", "--name", "foo"], module=module)

    want = "Hello foo"
    assert o.getvalue().strip() == want.strip()


@pytest.mark.asyncio
async def test_async_driver():
    from . import _commands_async as module
    from monogusa.cli.runtime import AsyncDriver

    o = module.OUTPUT
    module.cleaup()

    driver = AsyncDriver()
    await driver.run(["hello"], module=module)
    want = "hello\nend"
    assert o.getvalue().strip() == want.strip()
