# --- root/app_server/main.tf

variable "environment" {}

variable "instance_type" {}

module "security_group" {
  source      = "../../child_modules/security_group"
  description = "Security group for SomeAppServer"
  env         = var.environment
  name        = "${var.environment}-SomeAppServer-SG"
  rules = [
    {
      ports       = "22"
      protocol    = "tcp"
      description = "Default SSH"
      source      = "10.0.0.0/8"
    }
  ]
  tags = {
    Environment = var.environment
  }
}

module "ec2" {
  source = "../../child_modules/ec2"
  environment       = var.environment
  name              = "SomeAppServer"
  security_group_id = module.security_group.security_group_id
  instance_count    = 3
  os                = "rhel"
  tags              = {
    owner           = "gregory"
  }
}