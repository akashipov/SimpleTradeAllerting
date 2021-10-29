import asyncio

import pytest
import requests
from binance import AsyncClient, Client
from ftx import FtxClient


@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


def test_response_binance(event_loop):
    client = AsyncClient()
    response = event_loop.run_until_complete(
        client.get_order_book(symbol="BTCUSDT")
    )
    assert "bids" in response
    assert "asks" in response


def test_response_ftx():
    client = FtxClient()
    response = client.get_orderbook("BTC/USDT", 1)
    assert "bids" in response
    assert "asks" in response


def test_response_glm_btc():
    client = FtxClient()
    try:
        client.get_orderbook("GLM/BTC", 1)
        assert False
    except Exception as ex:
        pass

    client = Client()
    try:
        client.get_order_book(symbol="GLMBTC")
    except Exception as ex:
        print(ex)
        assert False
