import typing as t
from types import ModuleType


def run(
    token: str,
    *,
    module: ModuleType,
    name: str = "app",
    command_prefix: str = "$",
    setup: t.Optional[t.Callable[[str], None]] = None,
    debug: bool = True,
) -> None:
    from slackbot.bot import Bot, listen_to, settings
    from slackbot.dispatcher import Message
    from monogusa.chatbot.slackcli.driver import Driver

    if setup is None:
        from monogusa.chatbot.slackcli import defaultcomponent

        setup = defaultcomponent.setup
    setup(token)

    driver = Driver(module, name=name, command_prefix=command_prefix, debug=debug)
    driver.run = listen_to(fr"^ *\{driver.command_name}")(driver.run)  # type: ignore

    # xxx:
    @listen_to(".")  # type: ignore
    def on_message(m: Message) -> None:
        from monogusa.events import subscribe, MessageEvent

        ev = MessageEvent(raw=m, content=m.body.get("text"))
        subscribe.send(ev)

    # NOTE: update API_TOKEN, because slackbot.settings running import time
    settings.API_TOKEN = token
    if len(settings.PLUGINS) == 1 and settings.PLUGINS[0] == "slackbot.plugins":
        settings.PLUGINS = []

    bot = Bot()
    bot.run()
