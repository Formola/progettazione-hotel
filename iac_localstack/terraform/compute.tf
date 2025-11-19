# compute.tf

# 1. Launch Template (FUNZIONA IN FREE - È il "BluePrint" del server)
resource "aws_launch_template" "app_lt" {
  name_prefix   = "${var.project_name}-lt-"
  image_id      = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  network_interfaces {
    associate_public_ip_address = true
    security_groups             = [aws_security_group.ec2_sg.id]
  }

  user_data = base64encode("#!/bin/bash\necho 'Hello from LocalStack' > index.html")
}

# --- SEZIONE SCALE OUT (SOLO PRO / AWS REALE) ---
# Queste risorse (ALB, Target Group, ASG) richiedono LocalStack Pro.
# Le commentiamo per far passare il deploy in locale, ma sono pronte per AWS.

/*
resource "aws_lb_target_group" "app_tg" {
  name     = "${var.project_name}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
  target_type = "instance"
}

resource "aws_lb" "app_alb" {
  name               = "${var.project_name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public.id]
}

resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.app_alb.arn
  port              = "80"
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}

resource "aws_autoscaling_group" "app_asg" {
  name                = "${var.project_name}-asg"
  desired_capacity    = 1
  max_size            = 3
  min_size            = 1
  vpc_zone_identifier = [aws_subnet.private.id]
  target_group_arns   = [aws_lb_target_group.app_tg.arn]
  launch_template {
    id      = aws_launch_template.app_lt.id
    version = "$Latest"
  }
}
*/

# --- ALTERNATIVA PER TEST LOCALE (FREE TIER) ---
# Creiamo una singola istanza manualmente per provare che la rete e i Security Group funzionano.
resource "aws_instance" "test_instance" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.public.id # La mettiamo nella pubblica per testare facile
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]

  tags = {
    Name = "Test-Instance-LocalStack"
  }
}

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "${var.project_name}-cpu-high"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "60"
  statistic           = "Average"
  threshold           = "80"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  # Colleghiamo all'istanza singola invece che all'ASG
  dimensions = {
    InstanceId = aws_instance.test_instance.id
  }
}

# notifications.tf

resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts-topic"
}

resource "aws_sns_topic_subscription" "email_sub" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.admin_email
}