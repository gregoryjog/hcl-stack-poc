# --- child_modules/ec2/main.tf



resource "aws_instance" "default" {
  ami           = ""
  instance_type = ""
}

#locals {
#  patch_weeks = ["first", "second", "third", "fourth"]
#  patch_days = ["sunday", "monday", "tuesday", "wednesday", "thursday"]
#  patch_hours = ["22", "23"]
#  name_seed = tostring(parseint(var.server_name, 10))
#  neg_i1 = tonumber(substr(local.name_seed, -1, 1))
#  neg_i2 = tonumber(substr(local.name_seed, -2, 1))
#  neg_i3 = tonumber(substr(local.name_seed, -3, 1))
#  patch_value = "${element(local.patch_weeks, local.neg_i1)}-${element(local.patch_days, local.neg_i2)}-${element(local.patch_hours, local.neg_i3)}"
#}
#
#variable "server_name" {
#  type = "string"
#  value = "noname"
#}