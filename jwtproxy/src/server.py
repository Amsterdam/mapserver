#!/usr/bin/env python

import logging
from os import environ as env

import argparse
import atexit
from aiohttp import ClientSession, web, DummyCookieJar, TCPConnector, ClientTimeout
from jwcrypto.jwt import JWT, JWKSet
from yarl import URL
import gzip


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


async def get_jwk():
    """If we can get the pubkey from a URL, get it from there.
    Otherwise, default to the filesystem."""
    # https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys
    url = env.get("JWKS_URL")
    if url:
        async with SessionManager.session().get(
            url,
            timeout=ClientTimeout(sock_connect=3, sock_read=3),
        ) as resp:
            payload = gzip.decompress(await resp.read()).decode()
    else:
        payload = open(env.get("JWKS_PATH")).read()

    return JWKSet.from_json(payload)


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

    app.on_shutdown.append(SessionManager.close)
    return app


if __name__ == "__main__":
    args = parser.parse_args()
    web.run_app(main(), host="0.0.0.0", path=args.path)
