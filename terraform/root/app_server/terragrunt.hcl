# --- root/app_server/terragrunt.hcl

include "config" {
  path = "${get_path_from_repo_root()}/cloud/terraform/config/config.hcl"
}