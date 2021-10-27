import asyncio
from collections import deque

from solution.config.config import load_config
from solution.logic import calculate, get_binance_orderbook, get_ftx_orderbook


async def main():
    binance_results = deque(maxlen=1)
    ftx_results = deque(maxlen=1)
    tasks = []
    config = load_config()
    tasks.append(asyncio.create_task(
        get_ftx_orderbook(ftx_results, config=config)))
    tasks.append(asyncio.create_task(
        get_binance_orderbook(binance_results, config=config)))
    tasks.append(asyncio.create_task(
        calculate(binance_results, ftx_results, config=config)))
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
