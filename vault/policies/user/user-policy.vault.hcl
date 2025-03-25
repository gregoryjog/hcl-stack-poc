# user-policy.vault.hcl

path "aws/creds/terraform-user-role" {
  capabilities = ["read", "create"]
}


path "auth/token/lookup-self" {
  capabilities = ["read"]
}


path "auth/token/create" {
  capabilities = ["create", "update"]
}