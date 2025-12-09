# compute.tf---------------------------------------------------------

resource "aws_key_pair" "deployer" {
  key_name   = "deployer-key"
  public_key = file("${path.module}/local-key.pub")
}

resource "aws_security_group" "alb_sg" {
  name        = "${var.project_name}-alb-sg-v3"
  description = "Allow HTTP inbound traffic on 8081"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 8081 
    to_port     = 8081
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "ec2_sg" {
  name        = "${var.project_name}-ec2-sg-v3"
  description = "Allow traffic from ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 80    
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }


  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


resource "aws_instance" "test_instance" {
  ami           = "ami-df5de72bdb3b"
  instance_type = "m5.large"
  subnet_id     = aws_subnet.public.id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  key_name               = aws_key_pair.deployer.key_name

  user_data = <<-EOF
              #!/bin/bash
              apt-get update
              apt-get install -y nginx
              echo "<h1>ALB sulla porta 8081!</h1>" > /var/www/html/index.html
              service nginx start
              EOF

  tags = {
    Name = "Test-Instance-LocalStack"
  }
}


resource "aws_lb" "test_alb" {
  name               = "test-alb-final" # <--- NUOVO NOME per reset
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id] # <--- Usa la SG corretta con la 8081
  subnets            = [aws_subnet.public.id, aws_subnet.private.id]
}

resource "aws_lb_target_group" "test_tg" {
  name     = "test-tg-final"
  port     = 80      # <--- Il target è l'EC2, che ascolta sulla 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

resource "aws_lb_target_group_attachment" "test_attach" {
  target_group_arn = aws_lb_target_group.test_tg.arn
  target_id        = aws_instance.test_instance.id
  port             = 80
}

resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.test_alb.arn
  port              = "8081" # <--- ASCOLTA QUI
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.test_tg.arn
  }
}

output "alb_dns" {
  value = aws_lb.test_alb.dns_name
}