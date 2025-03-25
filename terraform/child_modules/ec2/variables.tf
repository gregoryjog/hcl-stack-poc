# --- child_modules/ec2/variables.tf

variable "name" {
  type        = string
  description = "Name of instance/server."
}

variable "environment" {
  type        = string
  description = "Environment of resource."
}

variable "instance_count" {
  type        = number
  description = "Number of instances to create."
  default     = 1
}

variable "tags" {
  type        = map(string)
  description = "Tags to pass through to created resources."
  default     = {}
}

variable "security_group_id" {
  type        = string
  description = "Security Group ID to assign to instance."
}

variable "os" {
  type        = string
  description = "Operating system to install."
  default     = "ubuntu"
}

variable "root_volume" {
  type        = number
  description = "Size of root volume (in GiB)"
  default     = 100
}

variable "instance_type" {
  type        = string
  description = "Instance type to use."
  default     = "m5a.large"
}

