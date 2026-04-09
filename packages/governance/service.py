import httpx

from packages.core.auth import PrincipalContext
from packages.core.models.contracts import PolicyDecision
from packages.core.settings import settings
from packages.storage.db import SessionLocal
from packages.storage.repositories import metrics_summary as repo_metrics_summary
from packages.storage.repositories import list_policy_decisions as repo_list_policy_decisions
from packages.storage.repositories import store_policy_decision


class GovernanceService:
    ROLE_PERMISSIONS = {
        "admin": {
            "read_memory",
            "write_memory",
            "modify_memory",
            "approve_changes",
            "delete_memory",
            "manage_policies",
            "execute_maintenance",
            "view_sensitive_data",
        },
        "operator": {
            "read_memory",
            "write_memory",
            "modify_memory",
            "approve_changes",
            "execute_maintenance",
            "view_sensitive_data",
        },
        "agent": {"read_memory", "write_memory", "modify_memory"},
        "reader": {"read_memory"},
    }

    def authorize(
        self,
        principal: PrincipalContext,
        permission: str,
        resource: str,
    ) -> dict[str, object]:
        allow, policy_source = self._opa_decision(
            principal=principal,
            action=permission,
            resource=resource,
        )
        if allow is None:
            allow = self._role_matrix_decision(principal.roles, permission)
            policy_source = "role_matrix"

        with SessionLocal() as session:
            stored = store_policy_decision(
                session,
                principal_id=principal.principal_id,
                resource=resource,
                action=permission,
                workspace_id=principal.workspace_id,
                namespace=principal.namespace,
                allow=allow,
                policy_source=policy_source,
            )
        return stored

    def evaluate(
        self,
        principal_id: str,
        resource: str,
        action: str,
        workspace_id: str,
        namespace: str,
    ) -> dict[str, object]:
        principal = PrincipalContext(
            principal_id=principal_id,
            roles=["reader"],
            request_id="policy-eval",
            workspace_id=workspace_id,
            namespace=namespace,
            auth_source="evaluation",
        )
        allow, policy_source = self._opa_decision(principal=principal, action=action, resource=resource)
        if allow is None:
            allow = action == "read" or principal_id == "local.operator"
            policy_source = "infra/opa/policy.rego:fallback"
        decision = PolicyDecision(
            principal_id=principal_id,
            resource=resource,
            action=action,
            workspace_id=workspace_id,
            namespace=namespace,
            allow=allow,
            policy_source=policy_source,
        )
        payload = decision.model_dump()
        with SessionLocal() as session:
            stored = store_policy_decision(session, **payload)
        payload["decision_id"] = stored["decision_id"]
        return payload

    def metrics_summary(self) -> dict[str, object]:
        with SessionLocal() as session:
            summary = repo_metrics_summary(session)
        summary["api_requests"] = 0
        return summary

    def list_policy_decisions(self, workspace_id: str, namespace: str, limit: int = 10) -> list[dict[str, object]]:
        with SessionLocal() as session:
            return repo_list_policy_decisions(session, workspace_id, namespace, limit)

    def _role_matrix_decision(self, roles: list[str], permission: str) -> bool:
        permissions = set()
        for role in roles:
            permissions.update(self.ROLE_PERMISSIONS.get(role, set()))
        return permission in permissions

    def _opa_decision(
        self,
        principal: PrincipalContext,
        action: str,
        resource: str,
    ) -> tuple[bool | None, str]:
        if not settings.enable_opa_authorization:
            return None, "opa_disabled"

        payload = {
            "input": {
                "principal_id": principal.principal_id,
                "principal_type": principal.principal_type.value,
                "roles": principal.roles,
                "workspace_id": principal.workspace_id,
                "namespace": principal.namespace,
                "resource": resource,
                "action": action,
                "permission": action,
            }
        }
        url = f"{settings.opa_url.rstrip('/')}/v1/data/{settings.opa_policy_package}/allow"
        try:
            with httpx.Client(timeout=settings.opa_timeout_seconds) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
            result = response.json().get("result")
            if isinstance(result, bool):
                return result, f"opa:{settings.opa_policy_package}"
        except Exception:
            return None, "opa_unavailable"
        return None, "opa_invalid_response"
