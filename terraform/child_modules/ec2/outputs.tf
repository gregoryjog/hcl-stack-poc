# --- child_modules/ec2/outputs.tf

output "private_ip" {
  value = aws_instance.ec2[*].private_ip
}