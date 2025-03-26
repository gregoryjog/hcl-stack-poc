# ubuntu-cis.pkr.hcl
packer {
  required_plugins {
    amazon = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/amazon"
    }
  }
}

source "amazon-ebs" "ubuntu" {
  ami_name      = "ubuntu-cis-hardened-${formatdate("YYYYMMDD-hhmmss", timestamp())}"
  instance_type = "t2.micro"
  region        = "us-west-2"

  source_ami_filter {
    filters = {
      name                = "ubuntu/images/*ubuntu-jammy-22.04-amd64-server-*"
      root-device-type    = "ebs"
      virtualization-type = "hvm"
    }
    most_recent = true
    owners      = ["self"]
  }

  ssh_username = "ubuntu"

  tags = {
    Name        = "ubuntu-cis-hardened"
    Builder     = "Packer"
    Owner       = "DevOps"
  }
}

build {
  sources = ["source.amazon-ebs.ubuntu"]

  provisioner "shell" {
    inline = [
      "sudo apt-get update",
      "sudo apt-get upgrade -y",
      "sudo apt-get autoremove -y"
    ]
  }

  # CIS hardening script
  provisioner "shell" {
    script = "scripts/cis-hardening.sh"
  }
}
