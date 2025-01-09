import asyncio

async def build_pylon():
    await asyncio.sleep(3)  # 模拟建造需要3秒
    print("Pylon built")

async def main():
    print("Start")
    await build_pylon()
    print("End")

asyncio.run(main())
