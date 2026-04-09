from packages.core.models.contracts import PolicyDecision


class GovernanceService:
    def evaluate(
        self,
        principal_id: str,
        resource: str,
        action: str,
        workspace_id: str,
        namespace: str,
    ) -> dict[str, object]:
        allow = action == "read" or principal_id == "local.operator"
        decision = PolicyDecision(
            principal_id=principal_id,
            resource=resource,
            action=action,
            workspace_id=workspace_id,
            namespace=namespace,
            allow=allow,
            policy_source="infra/opa/policy.rego",
        )
        return decision.model_dump()

    def metrics_summary(self) -> dict[str, object]:
        return {
            "api_requests": 0,
            "memory_count": 3,
            "capability_count": 2,
            "maintenance_jobs": 0,
            "policy_decisions": 0,
        }
