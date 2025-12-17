variable aws_region {
  type        = string
  default     = "us-east-1"
  description = "description"
}

variable "db_password" {
  description = "Password del database (LocalStack)"
  type        = string
  default     = "test"  # tflocal init hooks di localstack non passa un file .tfvars, quindi usiamo un default
}
