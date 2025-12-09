# # SG per Load Balancer (Aperto a tutti sulla 80)
# resource "aws_security_group" "alb_sg" {
#   name        = "${var.project_name}-alb-sg"
#   description = "Allow HTTP inbound traffic"
#   vpc_id      = aws_vpc.main.id

#   ingress {
#     from_port   = 80
#     to_port     = 80
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }

# # SG per EC2 (Accetta traffico SOLO dal Load Balancer)
# resource "aws_security_group" "ec2_sg" {
#   name        = "${var.project_name}-ec2-sg"
#   description = "Allow traffic from ALB"
#   vpc_id      = aws_vpc.main.id

#   ingress {
#     from_port       = 8080
#     to_port         = 8080
#     protocol        = "tcp"
#     security_groups = [aws_security_group.alb_sg.id]
#   }
  
#   # Regola extra per permettere l'accesso SSH (opzionale ma utile)
#   ingress {
#     from_port   = 22
#     to_port     = 22
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }


# resource "aws_security_group_rule" "allow_http_ingress" {
#   type              = "ingress"
#   from_port         = 80
#   to_port           = 80
#   protocol          = "tcp"
#   cidr_blocks       = ["0.0.0.0/0"]
#   security_group_id = aws_security_group.ec2_sg.id
# }