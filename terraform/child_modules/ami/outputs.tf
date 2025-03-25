# --- child_modules/ami/outputs.tf

output "ami_id" {
  value = data.aws_ami.target_ami.id
}

