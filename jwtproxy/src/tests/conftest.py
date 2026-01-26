import os

import aioresponses
import pytest

from ..server import main

PRIVATE_PROXY_URL = "http://private_proxy"
PUBLIC_PROXY_URL = "http://public_proxy"


@pytest.fixture
async def server(aiohttp_server):
    app = await main()
    return await aiohttp_server(app)


@pytest.fixture
async def client(aiohttp_client):
    app = await main()
    return await aiohttp_client(app)


@pytest.fixture(scope="session", autouse=True)
def set_env():
    os.environ["PRIVATE_PROXY_URL"] = PRIVATE_PROXY_URL
    os.environ["PUBLIC_PROXY_URL"] = PUBLIC_PROXY_URL
    os.environ["JWKS_PATH"] = "test_jwk.json"


@pytest.fixture
def mock_upstream():
    with aioresponses.aioresponses(passthrough_unmatched=True) as m:
        yield m
