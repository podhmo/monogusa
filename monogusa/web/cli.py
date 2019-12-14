import typing as t
import sys
import os
import argparse

from .types import ASGIApp


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-doc", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--port", type=int, default=None)
    return parser


def run(app: ASGIApp, *, where: t.Optional[str] = None, _depth: int = 1) -> None:
    if where is None:
        frame = sys._getframe(_depth)  # black magic
        _globals = frame.f_globals
        where = _globals["__file__"]

    parser = create_parser()
    args = parser.parse_args()

    if args.show_doc:
        return show_doc(app, debug=args.debug)
    else:
        os.chdir(os.path.dirname(where))
        app_name = os.path.basename(where)[: -len(".py")]
        cmd_args = ["uvicorn", f"{app_name}:app"]
        if args.debug:
            cmd_args.append("--debug")
        if args.port is not None:
            cmd_args.extend(["--port", str(args.port)])
        os.execvp("uvicorn", cmd_args)


def show_doc(app: ASGIApp, *, debug: bool = False) -> None:
    import asyncio
    from async_asgi_testclient import TestClient
    from dictknife import loading

    async def run() -> None:
        async with TestClient(app) as client:
            response = await client.get("/openapi.json")
            loading.dumpfile(response.json())

    asyncio.run(run(), debug=debug)
