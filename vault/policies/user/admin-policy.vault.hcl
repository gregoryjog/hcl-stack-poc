# admin-policy.vault.hcl


path "aws/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}


path "aws/creds/*" {
  capabilities = ["create", "read", "update"]
}


path "aws/roles/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}


path "sys/mounts/aws" {
  capabilities = ["create", "update", "delete"]
}


path "sys/mounts" {
  capabilities = ["read", "list"]
}


path "auth/token/lookup-self" {
  capabilities = ["read"]
}


path "auth/token/create" {
  capabilities = ["create", "update"]
}