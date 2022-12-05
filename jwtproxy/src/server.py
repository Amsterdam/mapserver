#!/usr/bin/env python

import logging
from os import environ as env

import argparse
from aiohttp import ClientSession, web
from jwcrypto.jwt import JWT, JWKSet
from yarl import URL


logger = logging.getLogger("aiohttp.server.jwtproxy")

CHUNK_SIZE = 1024

async def get_jwk():
    # https://login.microsoftonline.com/{tenant}/discovery/v2.0/keys
    if env.get("JWKS_URI"):
        pass


    return JWKSet.from_json(open(env.get("JWKS_PATH")).read())

async def handle(req):
    path = req.match_info["path"]
    target_url = URL("".join([env["PROXY_URL"].rstrip("/"), "/", path.lstrip("/")]))

    logger.info("Proxy-URL: \n%s", target_url)
    logger.debug("Request params: \n %s", req.rel_url.query)
    logger.debug("Request headers: \n %s", req.headers)

    try:
        auth = req.headers["Authorization"]
    except KeyError:
        # TODO: Redirect to AAD /oauth/v2.0/authorize
        raise web.HTTPForbidden(reason="No JWT present in Authorization header")

    bearer = "bearer "
    if not auth[:len(bearer)].lower() == bearer:
        raise web.HTTPForbidden(reason="Authorization header format is 'Bearer <token>'")

    token = auth[len(bearer):]
    j = JWT()

    try:
        j.deserialize(token, key=get_jwk())
    except Exception as e:
        logger.warning(e)
        raise web.HTTPForbidden(reason="Invalid token")
    
    logger.debug("Token: %s", repr(j))

    async with ClientSession() as session:
        async with session.request(
            req.method, target_url, headers=req.headers, params=req.rel_url.query
        ) as resp:
            logger.info("Response status from mapserver: %s", resp.status)
            logger.debug("Headers from mapserver: \n %s", resp.headers)
            logger.debug("Params from mapserver: \n %s", req.rel_url.query)

            server_resp = web.StreamResponse(headers=resp.headers, status=resp.status)

            if resp.headers.get("Transfer-Encoding", None) == "chunked":
                server_resp.enable_chunked_encoding()
            if resp.headers.get("Content-Encoding") == "gzip":
                server_resp.enable_compression()

            await server_resp.prepare(req)
            async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                await server_resp.write(chunk)
            await server_resp.write_eof()
            return server_resp

parser = argparse.ArgumentParser(description="jwt-proxy server")
parser.add_argument('--path')
parser.add_argument('--port', default=8080, type=int)


async def main(*argv):
    logging.basicConfig(level=env.get("LOG_LEVEL", logging.INFO))

    app = web.Application()
    app.router.add_route("OPTIONS", "/{path:.*?}", handle)
    app.router.add_route("GET", "/{path:.*?}", handle)
    app.router.add_route("POST", "/{path:.*?}", handle)
    return app


if __name__ == "__main__":
    args = parser.parse_args()
    web.run_app(main(), host="0.0.0.0", path=args.path)