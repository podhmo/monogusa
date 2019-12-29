import typing as t
from types import ModuleType
from slackbot.dispatcher import Message
import handofcats
from monogusa.langhelpers import reify
from monogusa.cli import runtime as cli_runtime
from monogusa.chatbot import runtime


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

        self.driver: t.Optional[cli_runtime.Driver] = None

    @reify
    def parser(self) -> runtime.ExitExceptionParser:
        return runtime.ExitExceptionParser(prog=self.name)

    @reify
    def command_name(self) -> str:
        return f"{self.command_prefix}{self.name}"

    def run(self, message: Message) -> None:
        text = message.body["text"]
        argv = runtime.parse(text, name=self.command_name)

        with runtime.handle() as output_list:
            if self.driver is None:
                self.driver = cli_runtime.Driver(parser=self.parser)
                self.driver.run(argv, module=self.module, debug=self.debug)
            else:
                self.driver._run(argv, debug=self.debug)

        if output_list:
            new_line = "\n"
            message.reply(
                f"""\
```
{new_line.join(output_list).strip(new_line)}
```""",
                in_thread=True,
            )


def run(
    token: str,
    *,
    module: ModuleType,
    name: str = "app",
    command_prefix: str = "$",
    debug: bool = True,
) -> None:
    from slackbot.bot import Bot, listen_to, settings

    driver = Driver(module, name=name, command_prefix=command_prefix, debug=debug)
    driver.run = listen_to(fr"^ *\{driver.command_name}")(driver.run)  # type: ignore

    # NOTE: update API_TOKEN, because slackbot.settings running import time
    settings.API_TOKEN = token
    if len(settings.PLUGINS) == 1 and settings.PLUGINS[0] == "slackbot.plugins":
        settings.PLUGINS = []

    bot = Bot()
    bot.run()


@handofcats.as_command  # type: ignore
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
    from magicalimport import import_module
    import dotenv

    logging.basicConfig(level=logging.DEBUG)
    module = import_module(target_module, cwd=True)

    if token is None:
        dotenv.load_dotenv(verbose=True, dotenv_path=str(pathlib.Path.cwd() / ".env"))
        token = os.environ["SLACKCLI_API_TOKEN"]
    run(token, module=module, name=name, command_prefix=command_prefix, debug=debug)
