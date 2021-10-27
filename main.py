import asyncio
from collections import deque

from Solution.solution.config import load_config
from Solution.solution.logic import (calculate, get_binance_orderbook,
                                     get_ftx_orderbook)


async def main():
    binance_results = deque()
    ftx_results = deque()
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
