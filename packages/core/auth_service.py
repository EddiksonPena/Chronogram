from __future__ import annotations

from collections.abc import Iterable
from functools import lru_cache

import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient

from packages.core.auth import PrincipalContext, PrincipalType
from packages.core.ids import make_id
from packages.core.settings import settings


@lru_cache(maxsize=8)
def _jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url)


class AuthService:
    def resolve_principal(
        self,
        authorization: str | None,
        x_principal_id: str | None,
        x_principal_type: str | None,
        x_principal_roles: str | None,
        x_request_id: str | None,
        x_workspace_id: str | None,
        x_namespace: str | None,
    ) -> PrincipalContext:
        token = self._extract_bearer_token(authorization)
        if token is not None:
            return self._principal_from_token(
                token=token,
                request_id=x_request_id,
                workspace_id=x_workspace_id,
                namespace=x_namespace,
            )

        if x_principal_id is not None:
            return self._principal_from_headers(
                principal_id=x_principal_id,
                principal_type=x_principal_type,
                roles=x_principal_roles,
                request_id=x_request_id,
                workspace_id=x_workspace_id,
                namespace=x_namespace,
            )

        if settings.app_env == "development" or settings.auth_allow_header_fallback:
            return PrincipalContext(
                principal_id="local.operator",
                principal_type=PrincipalType.HUMAN_USER,
                roles=["admin"],
                request_id=x_request_id or make_id("req"),
                workspace_id=x_workspace_id or "default",
                namespace=x_namespace or "project",
                auth_source="development_fallback",
            )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token or principal identity",
        )

    def principal_from_token(
        self,
        token: str,
        request_id: str | None = None,
        workspace_id: str | None = None,
        namespace: str | None = None,
    ) -> PrincipalContext:
        return self._principal_from_token(token, request_id, workspace_id, namespace)

    def _principal_from_headers(
        self,
        principal_id: str,
        principal_type: str | None,
        roles: str | None,
        request_id: str | None,
        workspace_id: str | None,
        namespace: str | None,
    ) -> PrincipalContext:
        resolved_roles = [role.strip() for role in (roles or "reader").split(",") if role.strip()]
        return PrincipalContext(
            principal_id=principal_id,
            principal_type=PrincipalType(principal_type or PrincipalType.HUMAN_USER.value),
            roles=resolved_roles,
            request_id=request_id or make_id("req"),
            workspace_id=workspace_id or "default",
            namespace=namespace or "project",
            auth_source="header",
        )

    def _principal_from_token(
        self,
        token: str,
        request_id: str | None,
        workspace_id: str | None,
        namespace: str | None,
    ) -> PrincipalContext:
        claims = self._decode_token(token)
        principal_id = (
            claims.get("preferred_username")
            or claims.get("email")
            or claims.get("sub")
            or "unknown-principal"
        )
        principal_type = self._principal_type_from_claims(claims)
        roles = self._claims_roles(claims)
        return PrincipalContext(
            principal_id=str(principal_id),
            principal_type=principal_type,
            roles=roles or ["reader"],
            request_id=request_id or str(claims.get("jti") or make_id("req")),
            workspace_id=workspace_id or str(claims.get("workspace_id") or claims.get("workspace") or "default"),
            namespace=namespace or str(claims.get("namespace") or "project"),
            auth_source="bearer",
            token_subject=str(claims.get("sub") or principal_id),
            issuer=str(claims.get("iss") or ""),
        )

    def _decode_token(self, token: str) -> dict[str, object]:
        jwks_url = settings.keycloak_jwks_url or (
            f"{settings.keycloak_url.rstrip('/')}/realms/{settings.keycloak_realm}/protocol/openid-connect/certs"
        )
        try:
            signing_key = _jwks_client(jwks_url).get_signing_key_from_jwt(token)
            options = {
                "verify_signature": True,
                "verify_aud": bool(settings.keycloak_audience),
            }
            kwargs: dict[str, object] = {
                "algorithms": ["RS256", "RS384", "RS512"],
                "options": options,
                "issuer": f"{settings.keycloak_url.rstrip('/')}/realms/{settings.keycloak_realm}",
            }
            if settings.keycloak_audience:
                kwargs["audience"] = settings.keycloak_audience
            return jwt.decode(token, signing_key.key, **kwargs)
        except Exception as exc:  # pragma: no cover - exercised via HTTPException surface
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid bearer token: {exc}",
            ) from exc

    def _extract_bearer_token(self, authorization: str | None) -> str | None:
        if authorization is None:
            return None
        scheme, _, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header must use Bearer scheme",
            )
        return token.strip()

    def _claims_roles(self, claims: dict[str, object]) -> list[str]:
        roles: list[str] = []
        realm_access = claims.get("realm_access")
        if isinstance(realm_access, dict):
            roles.extend(self._coerce_roles(realm_access.get("roles")))

        resource_access = claims.get("resource_access")
        if isinstance(resource_access, dict):
            client_roles = resource_access.get(settings.keycloak_client_id)
            if isinstance(client_roles, dict):
                roles.extend(self._coerce_roles(client_roles.get("roles")))
        return sorted(set(role for role in roles if role))

    def _coerce_roles(self, value: object) -> list[str]:
        if isinstance(value, Iterable) and not isinstance(value, (str, bytes, dict)):
            return [str(item) for item in value]
        return []

    def _principal_type_from_claims(self, claims: dict[str, object]) -> PrincipalType:
        if claims.get("client_id") or claims.get("azp") == settings.keycloak_client_id:
            return PrincipalType.SERVICE_ACCOUNT
        if "agent" in self._claims_roles(claims):
            return PrincipalType.AGENT_IDENTITY
        return PrincipalType.HUMAN_USER
