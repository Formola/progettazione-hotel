variable "aws_region" {
  description = "Regione AWS"
  default     = "us-east-1"
}

variable "project_name" {
  default     = "myapp-scaleout"
}

variable "environment" {
  description = "Ambiente di deploy"
  default     = "local-dev"
}

variable "db_name" {
  description = "db name"
  default     = "appdb"
}

variable "admin_email" {
  description = "admin email"
  default     = "admin@example.com"
}