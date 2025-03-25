# --- cloud/terraform/config.hcl

locals {
  aws_creds_file  = pathexpand("~/.aws/credentials")
  platform        = get_platform()
  environment     = local.platform == "windows" ? run_cmd("./Get-AWSParam.ps1") : run_cmd("./get_param.sh")
  current_dir     = basename(get_working_dir())

}

remote_state {
  backend = "s3"
  config = {
    bucket  = "somecompany-terraform-backend-${local.environment}"
    key     = "${current_dir}/state/"
    region  = "us-west-2"
    encrypt = true
  }
}

terraform {
  extra_arguments "dynamic_env" {
    commands = [
      "apply",
      "init",
      "plan",
      "state",
      "validate"
    ]
    required_var_files = ["${get_working_dir()/env/${local.environment}.tfvars}"]
  }
}

