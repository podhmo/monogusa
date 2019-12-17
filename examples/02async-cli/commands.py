import asyncio


async def hello(*, debug: bool = False):
    await asyncio.gather(_run("xxx", 3, debug=debug), _run("yyy", 3, debug=debug))


async def _run(message: str, n: int, debug: bool) -> None:
    for i in range(n):
        print(i, message, debug)
        await asyncio.sleep(0.1)
