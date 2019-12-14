import asyncio


async def hello():
    print("start hello")
    await asyncio.sleep(0.5)
    print("end  hello")
