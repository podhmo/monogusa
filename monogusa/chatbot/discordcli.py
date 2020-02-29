import typing as t
from types import ModuleType
from discord.ext import commands
import handofcats
from monogusa.langhelpers import reify
from monogusa.cli import runtime as cli_runtime
from monogusa.chatbot import runtime


# TODO: support MessageEvent


class Driver:
    def __init__(
        self,
        module: ModuleType,
        *,
        name: str = "app",
        command_prefix: str = "$",
        debug: bool = True,
    ) -> None:
        self.name = name
        self.module = module
        self.command_prefix = command_prefix
        self.debug = debug

        self.driver: t.Optional[cli_runtime.AsyncDriver] = None

    @reify
    def parser(self) -> runtime.ExitExceptionParser:
        return runtime.ExitExceptionParser(prog=self.name)

    @reify
    def command_name(self) -> str:
        return f"{self.command_prefix}{self.name}"

    async def run(self, ctx: commands.Context) -> None:
        text = ctx.message.content
        argv = runtime.parse(text, name=self.command_name)

        with runtime.handle() as output_list:
            r: t.Any = None
            if self.driver is None:
                self.driver = cli_runtime.AsyncDriver(parser=self.parser)
                r = await self.driver.run(argv, module=self.module, debug=self.debug)
            else:
                r = await self.driver._run(argv, debug=self.debug)
            if r is not None:
                cli_runtime.default_continuation(r)

        if output_list:
            new_line = "\n"
            await ctx.send(
                f"""\
```
{new_line.join(output_list).strip(new_line)}
```"""
            )


def run(
    token: str,
    *,
    module: ModuleType,
    name: str = "app",
    command_prefix: str = "$",
    debug: bool = True,
) -> None:
    bot = commands.Bot(command_prefix=command_prefix)

    # NOTE: update name for discord.py's command framework
    Driver.run.__name__ = name
    driver = Driver(module, name=name, command_prefix=command_prefix, debug=debug)
    driver.run = bot.command()(driver.run)  # type: ignore

    bot.run(token)


@handofcats.as_command(config=handofcats.Config(ignore_expose=True))  # type: ignore
def main(
    target_module: str,
    *,
    token: t.Optional[str] = None,
    name: str = "app",
    command_prefix: str = "$",
    debug: bool = True,
) -> None:
    import logging
    import os
    import pathlib
    from monogusa.langhelpers import import_module
    import dotenv

    logging.basicConfig(level=logging.DEBUG)
    module = import_module(target_module, cwd=True)
    if token is None:
        dotenv.load_dotenv(verbose=True, dotenv_path=str(pathlib.Path.cwd() / ".env"))
        token = os.environ["DISCORDCLI_API_TOKEN"]
    run(token, module=module, name=name, command_prefix=command_prefix, debug=debug)
