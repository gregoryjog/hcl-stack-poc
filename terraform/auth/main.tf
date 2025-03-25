#--- terraform/vault.tf
#
provider "vault" {
  address = "http://127.0.0.1:8200"
  # No token specified - VAULT_TOKEN env var will be used
}

data "vault_aws_access_credentials" "creds" {
  backend = "aws"
  role    = "terraform-role"
  region  = "us-west-2"
  type    = "sts"
}

output "debug" {
  value = {
    "session_start" = data.vault_aws_access_credentials.creds.lease_start_time
    "session_duration" = data.vault_aws_access_credentials.creds.lease_duration
  }
}
#
 provider "aws" {
   region     = "us-west-2"
   access_key = data.vault_aws_access_credentials.creds.access_key
   secret_key = data.vault_aws_access_credentials.creds.secret_key
   token      = data.vault_aws_access_credentials.creds.security_token
 }

# output "Debug" {
#   value = env("VAULT_TOKEN")
# }
