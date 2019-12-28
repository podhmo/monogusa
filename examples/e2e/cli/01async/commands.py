import asyncio
import logging

logger = logging.getLogger(__name__)


async def hello(*, debug: bool = False):
    logger.info("start")
    await asyncio.gather(_run("xxx", 3, debug=debug), _run("yyy", 3, debug=debug))
    logger.info("end")


async def _run(message: str, n: int, debug: bool) -> None:
    for i in range(n):
        print(i, message, debug)
        await asyncio.sleep(0.1)
