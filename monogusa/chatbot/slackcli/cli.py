from types import ModuleType
from .runtime import Driver


def run_bot(
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
