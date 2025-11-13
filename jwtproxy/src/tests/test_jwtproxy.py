import pytest
from aioresponses import aioresponses

from ..jwt_keygen import generate_jwt
from ..server import PRIVATE_MAPS

from .conftest import PRIVATE_PROXY_URL, PUBLIC_PROXY_URL

PRIVATE_MAPS_PATHS = [f"maps/{m}" for m in PRIVATE_MAPS.split(" ")]


async def test_health(client):
    resp = await client.get('/status/health')
    assert resp.status == 200


async def test_public_map_without_token_options(client, mock_upstream):
    """
    Test to make sure a OPTIONS request without a token to a private map results
    in a call to the upstream public server.
    """
    mock_upstream.options(f"{PUBLIC_PROXY_URL}/maps/luchtfoto", status=200)
    resp = await client.options("maps/luchtfoto")
    assert resp.status == 200


async def test_public_map_without_token_get(client, mock_upstream):
    """
    Test to make sure a GET request without a token to a private map results
    in a call to the upstream public server.
    """
    mock_upstream.get(f"{PUBLIC_PROXY_URL}/maps/luchtfoto", status=200)
    resp = await client.get("maps/luchtfoto")
    assert resp.status == 200


async def test_public_map_without_token_post(client, mock_upstream):
    """
    Test to make sure a POST request without a token to a private map results
    in a call to the upstream public server.
    """
    mock_upstream.post(f"{PUBLIC_PROXY_URL}/maps/luchtfoto", status=200)
    resp = await client.post("maps/luchtfoto")
    assert resp.status == 200


@pytest.mark.parametrize("private_path", PRIVATE_MAPS_PATHS)
async def test_private_map_without_token_options(client, mock_upstream, private_path):
    """
    Test to make sure an OPTIONS request without a token to a private map results
    in a call to the upstream public server.
    """
    mock_upstream.options(f"{PUBLIC_PROXY_URL}/{private_path}", status=200)
    resp = await client.options(private_path)
    assert resp.status == 200


@pytest.mark.parametrize("private_path", PRIVATE_MAPS_PATHS)
async def test_private_map_without_token_get(client, private_path):
    """
    Test to make sure a GET request without token to a private map results in a 403.
    """
    resp = await client.get(private_path)
    assert resp.status == 403
    assert await resp.text() == f"403: Accessing `{private_path}` without a JWT token is not allowed."


@pytest.mark.parametrize("private_path", PRIVATE_MAPS_PATHS)
async def test_private_map_without_token_post(client, private_path):
    """
    Test to make sure a POST request without token to a private map results in a 403.
    """
    resp = await client.post(private_path)
    assert resp.status == 403
    assert await resp.text() == f"403: Accessing `{private_path}` without a JWT token is not allowed."


@pytest.mark.parametrize("private_path", PRIVATE_MAPS_PATHS)
async def test_private_map_with_valid_token_get(client, mock_upstream, private_path):
    """
    Test to make sure a GET request with a valid token to a private map results
    in a call to the upstream private server.
    """
    mock_upstream.get(f"{PRIVATE_PROXY_URL}/{private_path}", status=200)

    token = generate_jwt(["fp_mdw"], exp=3600)

    resp = await client.get(private_path, headers={"Authorization": f"Bearer {token}"})
    assert resp.status == 200


@pytest.mark.parametrize("private_path", PRIVATE_MAPS_PATHS)
async def test_private_map_with_valid_token_post(client, mock_upstream, private_path):
    """
    Test to make sure a POST request with a valid token to a private map results
    in a call to the upstream private server.
    """
    mock_upstream.post(f"{PRIVATE_PROXY_URL}/{private_path}", status=200)

    token = generate_jwt(["fp_mdw"], exp=3600)

    resp = await client.post(private_path, headers={"Authorization": f"Bearer {token}"})
    assert resp.status == 200


@pytest.mark.parametrize("private_path", PRIVATE_MAPS_PATHS)
async def test_private_map_with_invalid_scope_get(client, private_path):
    """
    Test to make sure a GET request with an invalid scope to a private map results
    in a 403 response.
    """
    token = generate_jwt(["invalid_scope"], exp=3600)

    resp = await client.get(private_path, headers={"Authorization": f"Bearer {token}"})
    assert resp.status == 403
    assert await resp.text() == "403: Insufficient access privilege"


@pytest.mark.parametrize("private_path", PRIVATE_MAPS_PATHS)
async def test_private_map_with_invalid_scope_post(client, private_path):
    """
    Test to make sure a POST request with an invalid scope to a private map results
    in a 403 response.
    """
    token = generate_jwt(["invalid_scope"], exp=3600)

    resp = await client.post(private_path, headers={"Authorization": f"Bearer {token}"})
    assert resp.status == 403
    assert await resp.text() == "403: Insufficient access privilege"


@pytest.mark.parametrize("private_path", PRIVATE_MAPS_PATHS)
async def test_private_map_with_valid_token_post(client, private_path):
    """
    Test to make sure a POST request with an expired token to a private map results
    in a 401 response.
    """
    token = generate_jwt(["fp_mdw"], exp=-3600)

    resp = await client.post(private_path, headers={"Authorization": f"Bearer {token}"})
    assert resp.status == 401
    assert await resp.text() == "401: Token expired"


@pytest.mark.parametrize("private_path", PRIVATE_MAPS_PATHS)
async def test_private_map_with_invalid_token_post(client, private_path):
    """
    Test to make sure a POST request with an invalid token to a private map results
    in a 401 response.
    """
    resp = await client.post(private_path, headers={"Authorization": f"Bearer invalid.token"})
    assert resp.status == 401
    assert await resp.text() == "401: Invalid token"
