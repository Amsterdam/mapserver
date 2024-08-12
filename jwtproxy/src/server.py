#!/usr/bin/env python

import argparse
import asyncio
import json
import logging
from logging.config import dictConfig
from os import environ as env
import re

from aiohttp import ClientSession, ClientTimeout, DummyCookieJar, TCPConnector, web
from jwcrypto.jwt import JWT, JWKSet
from yarl import URL


LOG_LEVEL = env.get("LOG_LEVEL", "INFO")
CHUNK_SIZE = 1024
CONN_POOL_SIZE = 100
AZURE_APPLICATIONINSIGHTS_CONNSTRING = env.get("AZURE_APPLICATIONINSIGHTS_CONNSTRING")
PRIVATE_MAPS = env.get("PRIVATE_MAPS", "blackspots brandkranen handelsregister hr")
_map_paths = "|".join(f"maps/{m}" for m in PRIVATE_MAPS.split())
PRIVATE_MAPS_RE_PATTERN = re.compile(f"^({_map_paths})(/|$)")


base_log_fmt = {
    "time": "%(asctime)s",
    "name": "%(name)s",
    "level": "%(levelname)s",
    "message": "%(message)s",
}
log_fmt = base_log_fmt.copy()
audit_log_fmt = {"audit": True}
audit_log_fmt.update(log_fmt)
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
            "level": LOG_LEVEL,
        },
        "appinsights": {
            "class": "opencensus.ext.azure.log_exporter.AzureLogHandler",
            "connection_string": AZURE_APPLICATIONINSIGHTS_CONNSTRING,
            "formatter": "json-audit",
            "level": "DEBUG",
        },
        "appinsightsaccess": {
            "class": "opencensus.ext.azure.log_exporter.AzureLogHandler",
            "connection_string": AZURE_APPLICATIONINSIGHTS_CONNSTRING,
            "formatter": "json",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "jwtproxy.applogs": {
            "propagate": False,
            "handlers": ["console"],
            "level": LOG_LEVEL,
        },
        "jwtproxy.auditlogs": {
            "propagate": False,
            "handlers": ["appinsights"],
            "level": "DEBUG",  # Send everything
        },
        "jwtproxy.accesslogs": {
            "propagate": False,
            "handlers": ["appinsightsaccess"],
            "level": "DEBUG",  # Send everything
        },
    },
}

if not AZURE_APPLICATIONINSIGHTS_CONNSTRING:
    log_cfg["handlers"].pop("appinsights")
    log_cfg["handlers"].pop("appinsightsaccess")
    log_cfg["loggers"]["jwtproxy.auditlogs"]["handlers"] = [
        "console",
    ]
    log_cfg["loggers"]["jwtproxy.accesslogs"]["handlers"] = [
        "console",
    ]
dictConfig(log_cfg)

app_logger = logging.getLogger("jwtproxy.applogs")
audit_logger = logging.getLogger("jwtproxy.auditlogs")
access_logger = logging.getLogger("jwtproxy.accesslogs")

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


async def check_protection(path):
    app_logger.debug("Checking protection for `%s`", path)
    if PRIVATE_MAPS_RE_PATTERN.match(path) is not None:
        raise web.HTTPForbidden(reason=f"Accessing `{path}` without a JWT token is not allowed.")


async def handle(req: web.Request):
    path = req.match_info["path"]
    token = await fetch_token(req)
    proxy_url = env["PRIVATE_PROXY_URL"]
    if token is None:
        await check_protection(path)
        proxy_url = env["PUBLIC_PROXY_URL"]
    target_url = URL("".join([proxy_url.rstrip("/"), "/", path.lstrip("/")]))

    app_logger.debug("Proxy-URL: \n%s", target_url)
    app_logger.debug("Request params: \n %s", req.rel_url.query)
    app_logger.debug("Request headers: \n %s", req.headers)
    

    if token is not None:
        await audit(req, token)

    body = None
    if req.can_read_body:
        body = await req.text()
        app_logger.debug("Request body: \n %s", body)

    async with SessionManager.session().request(
        req.method, target_url, headers=req.headers, params=req.rel_url.query, data=body
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


async def health(req: web.Request):
    return web.Response(text="Status OK")


parser = argparse.ArgumentParser(description="jwt-proxy server")
parser.add_argument("--path")
parser.add_argument("--port", default=8080, type=int)


async def main(*argv):
    app = web.Application()
    app.router.add_route("GET", "/status/health", health)
    app.router.add_route("OPTIONS", "/{path:.*?}", handle)
    app.router.add_route("GET", "/{path:.*?}", handle)
    app.router.add_route("POST", "/{path:.*?}", handle)

    app.on_shutdown.append(on_shutdown)
    return app


if __name__ == "__main__":
    args = parser.parse_args()

    # support listening on unix domain sockets and ports
    if args.path:
        web.run_app(main(), host="0.0.0.0", path=args.path, access_log=access_logger)
    else:
        web.run_app(main(), host="0.0.0.0", port=args.port, access_log=access_logger)
