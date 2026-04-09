package memcortex.authz

default allow := false

allow if {
  input.action == "read"
}

allow if {
  input.principal_id == "local.operator"
}
