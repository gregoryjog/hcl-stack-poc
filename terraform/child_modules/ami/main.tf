# --- child_modules/ami/main.tf


# Match the passed parameter with the appropriate glob string for available images.

locals {
  current_distros = {
    "rhel"    = "rhel-cis-hardened-*"
    "ubuntu"  = "ubuntu-cis-hardened-*"
    "amazon"  = "Amazon Linux 2023"
  }
  distro_match    = lookup(local.current_distros, lower(var.distro))
}

data "aws_ami" "target_ami" {
  owners = ["self"]
  most_recent = true

  filter {
    name = "name"
    values = [local.distro_match]
    }

  filter {
    name    = "state"
    values  = ["available"]
  }

}
