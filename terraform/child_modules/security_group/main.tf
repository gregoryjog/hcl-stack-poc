# --- child_modules/security_group/main.tf

# This child module is to simplify the process of SG creation, assuming you don't plan on having incredibly complex SGs.


# This fetches the default private subnets for each VPC, assuming they have the name "private" in them.

data "aws_vpc" "default" {
  filter {
    name    = "tag:Name"
    values  = ["your-vpc-name"]
  }
}

locals {
  private_subnets = flatten([ for i in data.aws_vpc.default.cidr_block_associations[*].cidr_block : slice(cidrsubnets(i, 2, 2, 2, 2), 1, 4) ])
}

# This separates the ports list and creates a new object for each one.

locals {
  list_map = [for i in var.rules : {for port in i.ports: format("%s_%s", i.description, port) => {
    port = port
    protocol = i.protocol
    source = i.source
    description = i.description
  }}]

  # This gets rid of the list/tuple convention and replaces it with nested objects.
  map_extract = merge(flatten([local.list_map])...)
}

# Main group creation

resource "aws_security_group" "default" {
  name = var.name
  description = var.description
  vpc_id = data.aws_vpc.default.id
  tags = merge(var.tags, {
  Environment = var.env
})

}

# Sets the default egress rule for the group

resource "aws_security_group_rule" "egress_default" {
  count = var.allow_all_outbound == true ? 1 : 0
  type = "egress"
  from_port = 0
  to_port = 0
  protocol = "-1"
  cidr_blocks = ["0.0.0.0/0"]
  description = "All egress traffic"
  security_group_id = aws_security_group.default.id
}

resource "aws_security_group_rule" "rules" {
  for_each  = length(var.rules) != 0 ? local.map_extract : {}
  type      = "ingress"
  from_port = lookup(each.value, "port" ) == "-1" ? "-1" : (
  length(regexall("[[:digit:]-]", lookup(each.value, "port"))) == 0
  ) ? lookup(each.value, "port") : (
  element(split("-", lookup(each.value, "port")), 0))
  to_port = lookup(each.value, "port" ) == "-1" ? "-1" : (
  length(regexall("[[:digit:]-]", lookup(each.value, "port"))) == 0
  ) ? lookup(each.value, "port") : (
  element(split("-", lookup(each.value, "port")), 1))

  protocol    = lookup(each.value, "protocol")
  cidr_blocks = contains(lookup(each.value, "source"), "default") == true ? local.private_subnets :
  lookup(each.value, "source")
  description       = lookup(each.value, "description")
  security_group_id = aws_security_group.default.id
}
