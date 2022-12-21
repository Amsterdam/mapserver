#!/usr/bin/env python

import argparse
import asyncio
import gzip
import logging
from os import environ as env

from aiohttp import (ClientSession, ClientTimeout, DummyCookieJar,
                     TCPConnector, web)
from jwcrypto.jwt import JWT, JWKSet
from yarl import URL

logger = logging.getLogger("aiohttp.server.jwtproxy")

CHUNK_SIZE = 1024
CONN_POOL_SIZE = 100


class SessionManager:
    _session = None

    @classmethod
    def session(cls):
        if cls._session is None:
            # we're not reading any payloads so we don't need to
            # Also, we don't want to process any cookies
            # (cookies are shared between session requests)
            cls._session = ClientSession(
                auto_decompress=False,
                cookie_jar=DummyCookieJar(),
                connector=TCPConnector(limit=CONN_POOL_SIZE),
            )
            logger.debug("created new client Session")
        return cls._session

    @classmethod
    async def close(cls):
        session = cls._session
        if session is not None and not session.closed:
            await session.close()
            cls._session = None
            logger.debug("successfully closed session")
        logger.debug("no session to close")


async def on_shutdown(app):
    await SessionManager.close()


lock = asyncio.Lock()
cached_jwk = None


async def get_jwk():
    """If we can get the pubkey from a URL, get it from there.
    Otherwise, default to the filesystem."""
    # https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys
    async with lock:
        global cached_jwk
        if cached_jwk is not None:
            return cached_jwk

        url = env.get("JWKS_URL")
        if url:
            async with SessionManager.session().get(
                url,
                timeout=ClientTimeout(sock_connect=3, sock_read=3),
            ) as resp:
                payload = gzip.decompress(await resp.read()).decode()
        else:
            payload = open(env.get("JWKS_PATH")).read()
        cached_jwk = JWKSet.from_json(payload)
        return cached_jwk


async def handle(req):
    path = req.match_info["path"]
    target_url = URL("".join([env["PROXY_URL"].rstrip("/"), "/", path.lstrip("/")]))

    logger.info("Proxy-URL: \n%s", target_url)
    logger.debug("Request params: \n %s", req.rel_url.query)
    logger.debug("Request headers: \n %s", req.headers)

    try:
        auth = req.headers["Authorization"]
    except KeyError:
        raise web.HTTPForbidden(reason="No JWT present in Authorization header")

    bearer = "bearer "
    if not auth[: len(bearer)].lower() == bearer:
        raise web.HTTPForbidden(
            reason="Authorization header format is 'Bearer <token>'"
        )

    token = auth[len(bearer) :]
    j = JWT()
    jwks = await get_jwk()

    try:
        j.deserialize(token, key=jwks)
    except Exception as e:
        logger.warning(e)
        raise web.HTTPForbidden(reason="Invalid token")

    logger.debug("Token: %s", repr(j))

    async with SessionManager.session().request(
        req.method, target_url, headers=req.headers, params=req.rel_url.query
    ) as resp:
        logger.info("Response status from mapserver: %s", resp.status)
        logger.debug("Headers from mapserver: \n %s", resp.headers)
        logger.debug("Params from mapserver: \n %s", req.rel_url.query)

        server_resp = web.StreamResponse(headers=resp.headers, status=resp.status)

        if resp.headers.get("Transfer-Encoding", None) == "chunked":
            server_resp.enable_chunked_encoding()

        await server_resp.prepare(req)
        async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
            await server_resp.write(chunk)
        await server_resp.write_eof()
        return server_resp


parser = argparse.ArgumentParser(description="jwt-proxy server")
parser.add_argument("--path")
parser.add_argument("--port", default=8080, type=int)


async def main(*argv):
    logging.basicConfig(level=env.get("LOG_LEVEL", logging.INFO))

    app = web.Application()
    app.router.add_route("OPTIONS", "/{path:.*?}", handle)
    app.router.add_route("GET", "/{path:.*?}", handle)
    app.router.add_route("POST", "/{path:.*?}", handle)

    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == "__main__":
    args = parser.parse_args()

    # support listening on unix domain sockets and ports
    if args.path:
        web.run_app(main(), host="0.0.0.0", path=args.path)
    else:
        web.run_app(main(), host="0.0.0.0", port=args.port)
