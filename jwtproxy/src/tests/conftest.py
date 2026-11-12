import os

import aiointercept
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
    os.environ["TEST_JWKS"] = "test_jwk.json"
    for name in (
        "OAUTH_KEYCLOAK_CLAIMS",
        "OAUTH_KEYCLOAK_URL",
        "OAUTH_ENTRA_CLAIMS",
        "OAUTH_ENTRA_URL",
    ):
        os.environ.pop(name, None)


@pytest.fixture
async def mock_upstream():
    async with aiointercept.aiointercept(mock_external_urls=True) as m:
        yield m
