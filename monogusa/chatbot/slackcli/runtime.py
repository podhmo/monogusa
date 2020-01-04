import typing as t
import os
import pathlib


# component
def api_token(
    *, dotenv_path: t.Optional[str] = None, envvar="SLACKCLI_API_TOKEN"
) -> str:
    """load api token"""
    import dotenv

    dotenv_path = dotenv_path or str(pathlib.Path.cwd() / ".env")
    dotenv.load_dotenv(verbose=True, dotenv_path=dotenv_path)
    return os.environ[envvar]
