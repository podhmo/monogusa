import typing as t
import handofcats
from monogusa.chatbot.slackcli import run


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
    from magicalimport import import_module
    import dotenv

    logging.basicConfig(level=logging.DEBUG)
    module = import_module(target_module, cwd=True)

    if token is None:
        dotenv.load_dotenv(verbose=True, dotenv_path=str(pathlib.Path.cwd() / ".env"))
        token = os.environ["SLACKCLI_API_TOKEN"]
    run(token, module=module, name=name, command_prefix=command_prefix, debug=debug)
