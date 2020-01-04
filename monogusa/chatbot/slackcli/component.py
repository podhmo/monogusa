import typing as t
import typing_extensions as tx
import os
import pathlib
import monogusa


@monogusa.component
def api_token(
    *, dotenv_path: t.Optional[str] = None, envvar="SLACKCLI_API_TOKEN"
) -> str:
    """load api token"""
    import dotenv

    dotenv_path = dotenv_path or str(pathlib.Path.cwd() / ".env")
    dotenv.load_dotenv(verbose=True, dotenv_path=dotenv_path)
    return os.environ[envvar]


class APIClient(tx.Protocol):
    # TODO: more methods
    def upload_file(self, channel: str, fname: str, fpath: str, comment: str) -> None:
        ...

    def send_message(
        self,
        channel: str,
        message: str,
        attachments: t.Optional[t.Any] = None,
        as_user: bool = True,
        thread_ts: t.Optional[t.Any] = None,
    ):
        ...


@monogusa.component
def api_client(
    api_token: str,
    *,
    timeout: t.Optional[int] = None,
    bot_icon: t.Optional[str] = None,
    bot_emoji: t.Optional[str] = None,
    connect: bool = True
) -> APIClient:
    from slackbot.slackclient import SlackClient

    return SlackClient(
        api_token,
        timeout=timeout,
        bot_icon=bot_icon,
        bot_emoji=bot_emoji,
        connect=connect,
    )
