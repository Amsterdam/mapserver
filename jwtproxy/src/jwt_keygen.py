#!/usr/bin/env python
import argparse
import json
import pathlib
import sys
import time
import uuid

from jwcrypto.jwk import JWK
from jwcrypto.jwt import JWT

"""
Utitility script for generating JSON web keys and JSON web tokens
which can be used when testing. JWTs can contain private
claims which are scopes as used in the authorization mechanism of
amsterdam-schema.

The key used by the development configuration of the jwtproxy is stored in
./test_jwk.json.
"""

parser = argparse.ArgumentParser()
parser.add_argument(
    "scopes", nargs="*", help="Scopes added to the JWT as private claims"
)
parser.add_argument(
    "--exp", default=None, type=int, help="Number of seconds to expiration"
)

JWK_PATH = pathlib.Path(__file__).parent / "test_jwk.json"


def generate_jwk():
    return JWK.generate(
        kty="EC", crv="P-256", kid=str(uuid.uuid4()), key_ops=["verify", "sign"]
    )


def generate_jwt(scopes, exp):
    """Generate a JWT, signed using the first key stored at test_jwk.json.
    If there is no JWKSet at this location, generate it and write it to
    the file as a JWKSet"""
    if JWK_PATH.exists():
        key = JWK(**json.load(open(JWK_PATH))["keys"][0])
        if "d" not in key:
            raise ValueError("The configured JWK does not contain a private key")
    else:
        with open(JWK_PATH, "w+") as fp:
            key = generate_jwk()
            json.dump({"keys": [key]}, fp, indent=2, sort_keys=True)

    scopes = list(set(scopes))
    now = int(time.time())
    claims = {
        "iat": now,
        "realm_access": {
            "roles": scopes
        },
        "sub": "test@tester.nl",
    }
    if exp is not None:
        claims["exp"] = now + exp

    token = JWT(header={"alg": "ES256", "kid": key.kid, "kty": "EC"}, claims=claims)
    token.make_signed_token(key)

    return token.serialize()


if __name__ == "__main__":
    args = parser.parse_args()
    token = generate_jwt(args.scopes, args.exp)
    sys.stdout.write(token)
    sys.stdout.write("\n")
