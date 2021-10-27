import asyncio
import time
from collections import namedtuple

import ftx
import telebot
from binance import AsyncClient, exceptions


async def get_binance_orderbook(results, config, client=None):
    if client is None:
        client = AsyncClient()
    while True:
        try:
            # что то я тут передавал аргумент limit, но он не работал
            depth = await client.get_order_book(symbol=config['ticker'].replace('/', ''), limit=1)
            res = {'asks': depth['asks'][0], 'bids': depth['bids'][0]}
            print('binance', res)
            results.append(Result([res, time.time()], 'binance'))
        except exceptions.BinanceAPIException as ex:
            print(ex)
            break
        except Exception as ex:
            print('Some not expected error:', ex)
            break
        # наверняка стоят ограничения на кол-во запросов в минуту, поэтому буду делать запросы раз в секунду
        await asyncio.sleep(1)


async def get_ftx_orderbook(results, config, client=None):
    if client is None:
        client = ftx.FtxClient()
    while True:
        try:
            result = client.get_orderbook(config['ticker'], 1)
            result = {'asks': result['asks'][0], 'bids': result['bids'][0]}
            print('ftx', result)
            results.append(Result([result, time.time()], 'ftx'))
            await asyncio.sleep(1)
        except Exception as ex:
            print(ex)

Result = namedtuple('Result', 'result, name')


def compare_results(result_a: Result, result_b: Result, config, is_recursive=True):
    answer = float(result_a.result[0]['asks'][0]) - \
        float((result_b.result[0]['bids'][0]))
    diff = abs(result_a.result[1] - result_b.result[1])
    print(
        f'Спрос в {result_a.name} больше чем предложение в {result_b.name}? {answer > 0}, разница во времени {diff}')
    token = config['telegram_token']
    bot = telebot.TeleBot(token)

    telegram_id = config['telegram_id']
    if answer > 0:
        bot.send_message(telegram_id, f'Разница в цене: {answer}')
    if is_recursive:
        compare_results(result_b, result_a, config, is_recursive=False)


async def calculate(binance_results, ftx_results, config):
    try:
        while True:
            if binance_results and ftx_results:
                compare_results(binance_results.popleft(),
                                ftx_results.popleft(), config)
            await asyncio.sleep(1)
    except Exception as ex:
        print('Some not expected error:', ex)
