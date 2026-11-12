#!/usr/bin/env python

import argparse
import asyncio
import json
import logging
import re
from logging.config import dictConfig
from os import environ as env

from aiohttp import ClientSession, ClientTimeout, DummyCookieJar, TCPConnector, web
from jwcrypto.common import JWException
from jwcrypto.jwt import JWT, JWKSet, JWTExpired, JWTMissingKey
from yarl import URL

LOG_LEVEL = env.get("LOG_LEVEL", "INFO")
CHUNK_SIZE = 1024
CONN_POOL_SIZE = 100
AZURE_APPLICATIONINSIGHTS_CONNSTRING = env.get("AZURE_APPLICATIONINSIGHTS_CONNSTRING")
PRIVATE_MAPS = env.get("PRIVATE_MAPS", "blackspots brandkranen handelsregister hr hr_kvk")
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
    },
    "loggers": {
        "jwtproxy.applogs": {
            "propagate": False,
            "handlers": ["console"],
            "level": LOG_LEVEL,
        },
        "jwtproxy.auditlogs": {
            "propagate": False,
            "handlers": ["console"], # changed below if Azure Connection string is set
            "level": "DEBUG",  # Send everything
        },
        "jwtproxy.accesslogs": {
            "propagate": False,
            "handlers": ["console"], # changed below if Azure Connection string is set
            "level": "DEBUG",  # Send everything
        },
    },
}

if AZURE_APPLICATIONINSIGHTS_CONNSTRING:
    from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
    from opentelemetry.sdk._logs import LoggerProvider
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

    logger_provider = LoggerProvider()
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            AzureMonitorLogExporter(connection_string=AZURE_APPLICATIONINSIGHTS_CONNSTRING)
        )
    )
    log_cfg["handlers"]["appinsights"] = {
        "class": "opentelemetry.sdk._logs.LoggingHandler",
        "logger_provider": logger_provider,
        "formatter": "json-audit",
        "level": "DEBUG",
    }
    log_cfg["handlers"]["appinsightsaccess"] = {
        "class": "opentelemetry.sdk._logs.LoggingHandler",
        "logger_provider": logger_provider,
        "formatter": "json",
        "level": "DEBUG",
    }
    log_cfg["loggers"]["jwtproxy.auditlogs"]["handlers"] = ["appinsights"]
    log_cfg["loggers"]["jwtproxy.accesslogs"]["handlers"] = ["appinsightsaccess"]
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
    # This function now supports tokens issued by both Keycloak and Entra ID

    # First check if the access token is valid
    claims = None
    for provider in await get_jwks():
        try:
            j = JWT(
                jwt=token,
                key=provider["jwks"],
                check_claims=provider["check_claims"],
            )
        except JWTMissingKey:
            continue
        except JWTExpired as e:
            app_logger.warning(e)
            raise web.HTTPUnauthorized(reason="Token expired") from e
        except (JWException, ValueError) as e:
            app_logger.warning(e)
            continue

        candidate_claims = json.loads(j.claims)
        if not isinstance(candidate_claims, dict):
            raise web.HTTPUnauthorized(reason="Invalid token")
        claims = candidate_claims
        break

    if claims is None:
        raise web.HTTPUnauthorized(reason="Invalid token")

    # Then check is the validated access token contains the correct scope
    realm_access = claims.get("realm_access")
    keycloak_roles = realm_access.get("roles") if isinstance(realm_access, dict) else None
    entra_roles = claims.get("roles")
    has_access = (
        isinstance(keycloak_roles, list) and "fp_mdw" in keycloak_roles
    ) or (isinstance(entra_roles, list) and "FP/MDW" in entra_roles)

    # Deny requests if no_access:
    if not has_access:
        audit_logger.info(
            "Access to %s (%s) denied for subject %s (username: %s)",
            req.url,
            req.method,
            claims.get("email"),
            claims.get("preferred_username"),
        )
        raise web.HTTPForbidden(reason="Insufficient access privilege") from None

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
cached_jwks = None

async def get_jwks():
    """Load and cache the configured issuer/JWKS pairs."""
    async with lock:
        global cached_jwks
        if cached_jwks is not None:
            return cached_jwks

        providers = (
            (env.get("OAUTH_KEYCLOAK_CLAIMS"), env.get("OAUTH_KEYCLOAK_URL")),
            (env.get("OAUTH_ENTRA_CLAIMS"), env.get("OAUTH_ENTRA_URL")),
        )
        keysets = []
        for check_claims, url in providers:
            if check_claims is None and url is None:
                continue
            if not check_claims or not url:
                raise RuntimeError("Each provider must have a JWKS_URL and CHECK_CLAIMS var")

            check_claims = dict(item.split("=", 1) for item in check_claims.split(","))
            if not check_claims.get("iss"):
                raise RuntimeError("check_claims must include an issuer (iss)")

            # 
            check_claims["exp"] = None

            async with SessionManager.session().get(
                url,
                timeout=ClientTimeout(sock_connect=3, sock_read=3),
                skip_auto_headers=["Accept-Encoding"],  # we dont need a compressed jwks
            ) as resp:
                resp.raise_for_status()
                provider = {
                    "check_claims": check_claims,
                    "jwks": JWKSet.from_json(await resp.text()),
                }
                keysets.append(provider)

        if not keysets:
            jwks_path = env.get("JWKS_PATH")
            if not jwks_path:
                raise RuntimeError("Configure issuer/JWKS URL pairs or JWKS_PATH")
            with open(jwks_path) as file:
                keysets.append(
                    {
                        "check_claims": {"exp": None},
                        "jwks": JWKSet.from_json(file.read()),
                    }
                )

        cached_jwks = keysets
        return cached_jwks


async def check_protection(path, method):
    app_logger.debug("Checking protection for `%s`", path)
    if PRIVATE_MAPS_RE_PATTERN.match(path) is not None:
        if method == "OPTIONS":
            return web.Response(text="Status OK")
        else:
            raise web.HTTPForbidden(
                reason=f"Accessing `{path}` without a JWT token is not allowed."
            )
    return None


async def handle(req: web.Request):
    path = req.match_info["path"]
    token = await fetch_token(req)
    proxy_url = env["PRIVATE_PROXY_URL"]
    if token is None:
        await check_protection(path, req.method)
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

    upstream_headers = req.headers.copy()
    upstream_headers.pop("Host", None)
    async with SessionManager.session().request(
        req.method, target_url, headers=upstream_headers, params=req.rel_url.query, data=body
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


async def main(*argv) -> web.Application:
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
        web.run_app(main(), host="0.0.0.0", path=args.path, access_log=access_logger)  # noqa: S104
    else:
        web.run_app(main(), host="0.0.0.0", port=args.port, access_log=access_logger)  # noqa: S104
