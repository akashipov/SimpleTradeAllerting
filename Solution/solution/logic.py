import asyncio
import logging
import time
from collections import namedtuple
from typing import Deque, Dict, Optional

import ftx
import telebot
from binance import AsyncClient, exceptions

logging.basicConfig(filename="log_file.log", filemode="w", level=logging.INFO)
log = logging.getLogger(__file__)

Result = namedtuple("Result", "result, name")


async def get_binance_orderbook(
    results: Deque[Result], config: Dict, client: Optional[AsyncClient] = None
) -> None:
    """
    Получаем результаты orderbook от binance биржы/платформы.

    :param results - очередь с состояними стаканов по позиции (Binance биржа/платформа)
    :param config - словарик с конфигами
    :param client - передаем конкретный асинхронный binance клиент, если хотим
    """
    if client is None:
        client = AsyncClient()
    while True:
        try:
            # что то я тут передавал аргумент limit, но он не работал
            depth = await client.get_order_book(
                symbol=config["ticker"].replace("/", ""), limit=1
            )
            res = {"asks": depth["asks"][0], "bids": depth["bids"][0]}
            results.append(Result([res, time.time()], "binance"))
            log.info("binance appended")
        except exceptions.BinanceAPIException as ex:
            log.error(ex)
            break
        except Exception as ex:
            log.critical("Some not expected error:", ex)
            break
        # наверняка стоят ограничения на кол-во запросов в минуту, поэтому буду делать запросы раз в секунду
        await asyncio.sleep(1)


async def get_ftx_orderbook(
    results: Deque[Result], config: Dict, client: Optional[ftx.FtxClient] = None
) -> None:
    """
    Получаем результаты orderbook от ftx биржы/платформы.

    :param results - очередь с состояними стаканов по позиции (ftx биржа/платформа)
    :param config - словарик с конфигами
    :param client - передаем конкретный ftx клиент, если хотим
    """
    if client is None:
        client = ftx.FtxClient()
    while True:
        try:
            result = client.get_orderbook(config["ticker"], 1)
            result = {"asks": result["asks"][0], "bids": result["bids"][0]}
            results.append(Result([result, time.time()], "ftx"))
            log.info("ftx appended")
            await asyncio.sleep(1)
        except Exception as ex:
            log.error(ex)


def compare_results(
    result_a: Result, result_b: Result, config: Dict, is_recursive: bool = True
) -> None:
    """
    Обработка полученных результатов от двух бирж. А именно смотрим на разницу и если она удовлетворяет нашим условиям,
    то присылаем уведомление в телеграмм чат.

    :param result_a - стакан в конкретный момент времени от биржы а
    :param result_b - стакан в конкретный момент времени от биржы б
    :param config - словарик с конфигами
    :param is_recursive - передаем параметр, который говорит нам о том хотим ли мы вызвать
    рекурсивно переставляя местами слагаемые
    """
    answer = float(result_a.result[0]["asks"][0]) - float(
        result_b.result[0]["bids"][0]
    )
    diff = abs(result_a.result[1] - result_b.result[1])
    token = config["telegram_token"]
    bot = telebot.TeleBot(token)

    telegram_id = config["telegram_id"]
    if (
        answer > config["diff_size_for_send"]
    ):  # считывается порог разницы для уведомления
        bot.send_message(
            telegram_id,
            f"Разница в цене: {answer}.\n"
            f'Предложение в {result_b.name} - {float(result_b.result[0]["bids"][0])},'
            f' спрос в {result_a.name} - {float(result_a.result[0]["asks"][0])}.\n'
            f"Разница во времени запросов - {diff}\n",
        )
    if is_recursive:
        compare_results(result_b, result_a, config, is_recursive=False)


async def calculate(
    binance_results: Deque[Result], ftx_results: Deque[Result], config: Dict
) -> None:
    """
    Извлечение результатов от двух бирж и передача в обработчик.

    :param ftx_results - очередь с состояними стаканов по позиции (ftx биржа/платформа)
    :param binance_results - очередь с состояними стаканов по позиции (binance биржа/платформа)
    :param config - словарик с конфигами
    """
    try:
        while True:
            if binance_results and ftx_results:
                compare_results(
                    binance_results.popleft(), ftx_results.popleft(), config
                )
                log.info("\nresults processed\n")
            await asyncio.sleep(1)
    except Exception as ex:
        log.error("Some not expected error:", ex)
