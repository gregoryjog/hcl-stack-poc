# --- child_modules/security_group/variables.tf

variable "name" {
  type        = string
  description = "Security Group Name"
}

variable "description" {
  type        = string
  description = "Security Group Description"
}

variable "env" {
  type        = string
  description = "Environment"
}

variable "tags" {
  type        = map(string)
  description = "Tags to add to the Security Group."
}

variable "allow_all_outbound" {
  type        = bool
  description = "Allow -1 on Egress"
  default     = true
}

variable "rules" {
  type        = map(any)
  description = "A Map to Simplify Desired SG Rules. See comment below below for formatting."
}


/*
The default input for the rules variable will look something like this:
  some_rule = {
        ports       = "8000-9000"
        description = "These ports are for xyz"
        protcol     = "tcp"
        source      = ["10.0.0.0/8", "192.168.1.1/32"]
*\