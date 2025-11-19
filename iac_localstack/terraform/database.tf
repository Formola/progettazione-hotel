resource "aws_s3_bucket" "media_bucket" {
  bucket = "${var.project_name}-media-assets-${var.environment}"
  force_destroy = true # Utile in dev per cancellare bucket non vuoti
}


# Subnet Group per RDS
# resource "aws_db_subnet_group" "default" {
#   name       = "${var.project_name}-db-subnet-group"
#   subnet_ids = [aws_subnet.private.id, aws_subnet.public.id]
# }

# # Istanza RDS (Postgres)
# # NOTA: In LocalStack Free questo è un placeholder API.
# # L'app dovrà connettersi a localhost:5432 (il container Docker reale).
# resource "aws_db_instance" "default" {
#   identifier             = "${var.project_name}-db"
#   allocated_storage      = 20
#   db_name                = var.db_name
#   engine                 = "postgres"
#   engine_version         = "15.3"
#   instance_class         = "db.t3.micro"
#   username               = "appuser"
#   password               = "apppassword"
#   skip_final_snapshot    = true
#   vpc_security_group_ids = [aws_security_group.db_sg.id]
#   db_subnet_group_name   = aws_db_subnet_group.default.name
# }