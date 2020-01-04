import typing as t
import handofcats
from monogusa.chatbot.slackcli import cli
from monogusa.chatbot.slackcli import runtime


@handofcats.as_command  # type: ignore
def run(
    target_module: str,
    *,
    token: t.Optional[str] = None,
    name: str = "app",
    command_prefix: str = "$",
    debug: bool = True,
) -> None:
    import logging
    from magicalimport import import_module

    logging.basicConfig(level=logging.DEBUG)
    module = import_module(target_module, cwd=True)

    token = token or runtime.api_token()
    cli.run_bot(
        token, module=module, name=name, command_prefix=command_prefix, debug=debug
    )
