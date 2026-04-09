package memcortex.authz

default allow := false

allow if {
  input.action == "read"
}

allow if {
  input.principal_id == "local.operator"
}

role_permissions := {
  "admin": {
    "read_memory",
    "write_memory",
    "modify_memory",
    "approve_changes",
    "delete_memory",
    "manage_policies",
    "execute_maintenance",
    "view_sensitive_data",
    "read",
    "write",
  },
  "operator": {
    "read_memory",
    "write_memory",
    "modify_memory",
    "approve_changes",
    "execute_maintenance",
    "view_sensitive_data",
    "read",
    "write",
  },
  "agent": {"read_memory", "write_memory", "modify_memory", "read", "write"},
  "reader": {"read_memory", "read"},
}

allow if {
  some idx
  role := input.roles[idx]
  role_permissions[role][input.permission]
}
