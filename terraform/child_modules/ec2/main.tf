# --- child_modules/ec2/main.tf

data "aws_vpc" "default" {
  filter {
    name    = "tag:Name"
    values  = ["vpc-name"]
  }
}

data "aws_subnets" "default" {
  filter {
    name    = "tag:Name"
    values  = ["*private-*"]
  }
}

data "aws_kms_key" "ec2" {
  key_id = "alias/${var.environment}-ec2-key"
}

module "private-ami" {
  source = "../ami"
  distro = "ubuntu"
}

resource "aws_iam_role" "ec2-role" {
  name                = "${var.environment}-${var.name}-ec2-role"
  assume_role_policy  = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role        = aws_iam_role.ec2-role.name
  policy_arn  = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_role_policy_attachment" "cloudwatch" {
  role       = aws_iam_role.ec2-role.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "EC2-${var.environment}-${var.name}-profile"
  role = aws_iam_role.ec2-role.name
}

resource "aws_instance" "ec2" {
  count                 = var.instance_count
  ami                   = module.private-ami.ami_id
  instance_type         = var.instance_type
  ebs_optimized         = true
  iam_instance_profile  = aws_iam_instance_profile.ec2_profile.name
  key_name              = "${var.environment}-devops-or-sysadmin-key"
  security_groups       = [var.security_group_id]
  subnet_id             = element(data.aws_subnets.default.ids, count.index)
  tags                  = merge(var.tags, {
    Name                = format("${var.name}%03d%s", count.index + 1, substr(lower(var.environment), 0, 1))
    Environment         = title(var.environment)
    OS                  = module.private-ami.ami_name
  })
  root_block_device {
    delete_on_termination = lower(var.environment) == "prod" ? false : true
    encrypted             = true
    kms_key_id            = data.aws_kms_key.ec2.id
    volume_size           = var.root_volume
    volume_type           = "gp3"
    tags                  = {
      name = format("${var.name}%03d%s_root_volume", count.index + 1, substr(lower(var.environment), 0, 1))
    }
  }

}
