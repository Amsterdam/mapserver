# Refactor OAuth claims environment handling

## Agreed scope

- Read provider configuration from `OAUTH_KEYCLOAK_CLAIMS`, `OAUTH_KEYCLOAK_URL`,
  `OAUTH_ENTRA_CLAIMS`, and `OAUTH_ENTRA_URL`.
- Parse claims environment values in the existing comma-separated `key=value`
  format into dictionaries.
- Represent each cached provider as a dict containing its `check_claims` and
  JWKSet, then pass both to JWCrypto's `JWT` validator. Use `jwks_url` only
  while loading the keyset.
- Include `exp: None` in each check-claims dictionary so expiration is required
  and validated; keep the local `TEST_JWKS` fallback compatible.
- Isolate tests from inherited OAuth provider variables so they use the local
  `TEST_JWKS` fixture.
- Keep `TEST_JWKS` out of Compose and deployment configuration; use OAuth
  provider variables for local development and deployments.
- Keep role authorization unchanged.
- Leave missing-`iss` handling explicit: direct lookup raises `KeyError`.
- Keep the implementation minimal and preserve local `TEST_JWKS` fallback.
- Limit test changes to the environment fixture; do not change behavior tests.

## Verification

- Run Python syntax validation and Compose configuration validation.
- Run the proxy test suite after the fixture change.
