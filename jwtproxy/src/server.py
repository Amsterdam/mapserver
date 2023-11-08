#!/usr/bin/env python

import argparse
import asyncio
import logging
from logging.config import dictConfig
import json
from os import environ as env

from aiohttp import ClientSession, ClientTimeout, DummyCookieJar, TCPConnector, web
from jwcrypto.jwt import JWT, JWKSet
from yarl import URL

app_logger = logging.getLogger("jwtproxy.applogs")
audit_logger = logging.getLogger("jwtproxy.auditlogs")

CHUNK_SIZE = 1024
CONN_POOL_SIZE = 100
AZURE_APPLICATIONINSIGHTS_CONNSTRING = env.get("AZURE_APPLICATIONINSIGHTS_CONNSTRING")


async def fetch_token(req: web.Request):
    """Fetch the token from the request.

    We want to do this in a separate functions,
    because on missing token, we return None
    so the caller can redirect to another server/endpoint
    for that scenario.
    """
    try:
        auth = req.headers.get("Authorization")
        if auth is not None:
            bearer = "bearer "
            if not auth[: len(bearer)].lower() == bearer:
                raise web.HTTPForbidden(reason="Authorization header format is 'Bearer <token>'")
            token = auth[len(bearer) :]
        else:
            token = req.query["access_token"]
    except KeyError:
        app_logger.debug("No JWT present in Authorization header or `access_token` query string.")
        return None
    else:
        return token


async def audit(req: web.Request, token: str):
    # Note that this function only supports token formats issued by
    # the iam KeyCloak server.

    j = JWT()
    jwks = await get_jwk()

    try:
        j.deserialize(token, key=jwks)
    except Exception as e:
        app_logger.warning(e)
        raise web.HTTPForbidden(reason="Invalid token")

    claims = json.loads(j.claims)
    try:
        assert "fp_mdw" in claims["realm_access"]["roles"]
    except (KeyError, AssertionError):
        audit_logger.info(
            "Access to %s (%s) denied for subject %s (username: %s)",
            req.url,
            req.method,
            claims.get("email"),
            claims.get("preferred_username"),
        )
        raise web.HTTPUnauthorized(reason="Insufficient access privilege")

    audit_logger.info(
        "Access to %s (%s) granted to subject %s (username: %s)",
        req.url,
        req.method,
        claims.get("email"),
        claims.get("preferred_username"),
    )


class SessionManager:
    _session = None

    @classmethod
    def session(cls):
        if cls._session is None:
            # We're not reading any payloads so we don't need to decompress.
            # Also, we don't want to process any cookies
            # (cookies are shared between session requests)
            cls._session = ClientSession(
                auto_decompress=False,
                cookie_jar=DummyCookieJar(),
                connector=TCPConnector(limit=CONN_POOL_SIZE),
            )
            app_logger.debug("created new client Session")
        return cls._session

    @classmethod
    async def close(cls):
        session = cls._session
        if session is not None and not session.closed:
            await session.close()
            cls._session = None
            app_logger.debug("successfully closed session")
        app_logger.debug("no session to close")


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
                skip_auto_headers=["Accept-Encoding"],  # we dont need a compressed jwks
            ) as resp:
                payload = await resp.text()
        else:
            payload = open(env.get("JWKS_PATH")).read()
        cached_jwk = JWKSet.from_json(payload)
        return cached_jwk


async def handle(req: web.Request):
    path = req.match_info["path"]
    token = await fetch_token(req)
    proxy_url = env["PRIVATE_PROXY_URL"]
    if token is None:
        proxy_url = env["PUBLIC_PROXY_URL"]
    target_url = URL("".join([proxy_url.rstrip("/"), "/", path.lstrip("/")]))

    app_logger.debug("Proxy-URL: \n%s", target_url)
    app_logger.debug("Request params: \n %s", req.rel_url.query)
    app_logger.debug("Request headers: \n %s", req.headers)

    if token is not None:
        await audit(req, token)

    async with SessionManager.session().request(
        req.method, target_url, headers=req.headers, params=req.rel_url.query
    ) as resp:
        app_logger.debug("Response status from upstream: %s", resp.status)
        app_logger.debug("Headers from upstream: \n %s", resp.headers)
        app_logger.debug("Params from upstream: \n %s", req.rel_url.query)

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

base_log_fmt = {
    "time": "%(asctime)s",
    "name": "%(name)s",
    "level": "%(levelname)s",
    "message": "%(message)s",
}
log_fmt = base_log_fmt.copy()

audit_log_fmt = {"audit": True}
audit_log_fmt.update(log_fmt)


async def main(*argv):
    level = env.get("LOG_LEVEL", logging.INFO)

    log_cfg = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {"format": json.dumps(log_fmt)},
            "json-audit": {"format": json.dumps(audit_log_fmt)},
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "level": level,
            },
            "appinsights": {
                "class": "opencensus.ext.azure.log_exporter.AzureLogHandler",
                "connection_string": AZURE_APPLICATIONINSIGHTS_CONNSTRING,
                "formatter": "json-audit",
                "level": "DEBUG",
            },
        },
        "loggers": {
            "jwtproxy.applogs": {
                "propagate": False,
                "handlers": ["console"],
                "level": level,
            },
            "jwtproxy.auditlogs": {
                "propagate": False,
                "handlers": ["appinsights"],
                "level": "DEBUG",  # Send everything
            },
        },
    }

    if not AZURE_APPLICATIONINSIGHTS_CONNSTRING:
        log_cfg["handlers"].pop("appinsights")
        log_cfg["loggers"]["jwtproxy.auditlogs"]["handlers"] = [
            "console",
        ]
    dictConfig(log_cfg)

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
