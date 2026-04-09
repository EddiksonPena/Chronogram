from collections.abc import Callable

from fastapi import Depends, Header, HTTPException, status

from packages.core.auth import PrincipalContext
from packages.core.auth_service import AuthService
from packages.governance.service import GovernanceService


def get_principal(
    authorization: str | None = Header(default=None),
    x_principal_id: str | None = Header(default=None),
    x_principal_type: str | None = Header(default=None),
    x_principal_roles: str | None = Header(default=None),
    x_request_id: str | None = Header(default=None),
    x_workspace_id: str | None = Header(default=None),
    x_namespace: str | None = Header(default=None),
) -> PrincipalContext:
    return AuthService().resolve_principal(
        authorization=authorization,
        x_principal_id=x_principal_id,
        x_principal_type=x_principal_type,
        x_principal_roles=x_principal_roles,
        x_request_id=x_request_id,
        x_workspace_id=x_workspace_id,
        x_namespace=x_namespace,
    )

def require_permission(permission: str, resource_getter: Callable[[PrincipalContext], str]):
    def dependency(principal: PrincipalContext = Depends(get_principal)) -> PrincipalContext:
        allowed = GovernanceService().authorize(
            principal=principal,
            permission=permission,
            resource=resource_getter(principal),
        )
        if not allowed["allow"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Policy denied action")
        return principal

    return dependency
