# --- LOAD BALANCER (INGRESSO) ---
# Gestisce il traffico in entrata e lo distribuisce ai target
resource "aws_lb" "app_alb" {
  name               = "myapp-load-balancer"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
  enable_deletion_protection = false

  tags = { Name = "Public ALB" }
}

resource "aws_lb_target_group" "app_tg" {
  name        = "myapp-target-group"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "instance"

  # Health Check "rilassato" per LocalStack
  # Accettiamo anche 404 (Not Found) come stato "sano" perché le istanze
  # partiranno senza un file index.html.
  health_check {
    path                = "/"
    matcher             = "200-499"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    timeout             = 5
    interval            = 10
  }
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

# --- ARCHITETTURA SCALABILE (ASG + LAUNCH TEMPLATE) ---

resource "aws_launch_template" "app_lt" {
  name_prefix   = "myapp-launch-template"
  image_id      = "ami-df5de72bdb3b" # AMI Ubuntu 22.04 in LocalStack
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  
  tag_specifications {
    resource_type = "instance"
    tags = { Name = "ASG-Instance" }
  }
}

resource "aws_autoscaling_group" "app_asg" {
  name                = "myapp-asg"
  vpc_zone_identifier = [aws_subnet.private_1.id, aws_subnet.private_2.id]
  
  # Configuriamo l'ASG per provare a lanciare 2 istanze
  desired_capacity    = 2
  max_size            = 3
  min_size            = 1
  
  # Importante per LocalStack: usa il check EC2 (status macchina)
  # invece del check ELB (risposta HTTP) per evitare che l'ASG termini
  # le istanze vuote che non rispondono ancora sulla porta 80.
  health_check_type   = "EC2"

  target_group_arns   = [aws_lb_target_group.app_tg.arn]

  launch_template {
    id      = aws_launch_template.app_lt.id
    version = "$Latest"
  }

  tag {
    key                 = "Name"
    value               = "ASG-Worker-Container"
    propagate_at_launch = true
  }
}

# --- MONITORAGGIO E SCALING ---

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "cpu-utilization-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = "60"
  statistic           = "Average"
  threshold           = "70"

  dimensions = {
    AutoScalingGroupName = aws_autoscaling_group.app_asg.name
  }

  alarm_description = "Scala verso l'alto se la CPU > 70%"
  alarm_actions     = [aws_autoscaling_policy.scale_up.arn]
}

resource "aws_autoscaling_policy" "scale_up" {
  name                   = "scale-up-policy"
  scaling_adjustment     = 1
  adjustment_type        = "ChangeInCapacity"
  cooldown               = 300
  autoscaling_group_name = aws_autoscaling_group.app_asg.name
}

# Questa risorsa forza Terraform a creare un container EC2 specifico.
# Serve per garantire un ambiente di debug immediato se l'ASG tarda a partire.

resource "aws_instance" "manual_debug_node" {
  ami           = "ami-df5de72bdb3b"
  instance_type = "m5.large"

  # Invece di aws_subnet.public_1 (Custom), usiamo la Default
  subnet_id = data.aws_subnets.localstack_default.ids[0]

  # usiamo il Default Global SG
  vpc_security_group_ids = [data.aws_security_group.localstack_default_sg.id]
  # Aspettiamo che la regola 8000 sia scritta
  depends_on = [aws_security_group_rule.debug_ingress_8000]

  user_data = <<-EOF
              #!/bin/bash
              echo "Server on Default VPC (Hybrid Mode)" > index.html
              python3 -m http.server 8000 &
              EOF

  tags = {
    Name = "MANUAL-DEBUG-NODE" 
  }
}

# Colleghiamo manualmente questo nodo al Load Balancer
# Così se l'ASG fallisce, il traffico API finirà comunque qui.
# resource "aws_lb_target_group_attachment" "manual_attach" {
#   target_group_arn = aws_lb_target_group.app_tg.arn
#   target_id        = aws_instance.manual_debug_node.id
#   port             = 80
# }

# --- OUTPUTS ---

output "alb_dns_name" {
  description = "DNS del Load Balancer"
  value       = aws_lb.app_alb.dns_name
}

# output "debug_instance_id" {
#   description = "ID dell'istanza manuale per il debug con docker exec"
#   value       = aws_instance.manual_debug_node.id
# }

/*
Iniziamo dalla sezione di Load Balancing, che gestisce l'ingresso del traffico. La risorsa aws_lb crea
un Application Load Balancer. Questo dispositivo virtuale viene posizionato nelle subnet
pubbliche (definite in network.tf) e protetto dal Security Group alb_sg (definito in security.tf),
fungendo da unico punto di contatto per il mondo esterno. Per sapere dove inoltrare le richieste,
definiamo un aws_lb_target_group. Questo gruppo logico rappresenta l'insieme dei nostri server backend;
include un meccanismo vitale chiamato Health Check che interroga periodicamente le istanze
(cercando un codice 200 OK sulla root /) per assicurarsi che siano sane prima di inviare loro traffico.
Il collegamento tra il mondo esterno e il Target Group avviene tramite l'aws_lb_listener,
che resta in ascolto sulla porta 80 e applica un'azione di "forward" (inoltro) verso il gruppo di destinazione.

Passiamo poi alla sezione Compute & Autoscaling, che gestisce i server veri e propri nelle subnet private.
Invece di creare singoli server manualmente, definiamo un "modello" con aws_launch_template.
Questo template specifica le caratteristiche immutabili di ogni server: l'immagine di base (AMI),
la taglia (t2.micro), il Security Group (ec2_sg).

L'orchestratore di tutto questo è l'aws_autoscaling_group (ASG). Configurato per operare nelle subnet private,
questo componente utilizza il Launch Template per garantire che ci sia sempre il numero desiderato di
istanze attive (nella nostra configurazione, partiamo da 2). L'ASG è integrato direttamente con il
Target Group del Load Balancer: appena una nuova istanza viene lanciata e supera i controlli di salute,
viene automaticamente registrata per ricevere traffico, senza intervento manuale.

Infine, implementiamo il Pattern Scale Out attraverso aws_cloudwatch_metric_alarm e aws_autoscaling_policy.
Configurando un allarme su CloudWatch, monitoriamo la metrica CPUUtilization dell'intero gruppo.
Se il carico medio supera il 70% per due periodi consecutivi, l'allarme scatta e attiva la policy di scaling,
che ordina all'ASG di aggiungere una nuova unità (scaling_adjustment = 1). Questo rende l'architettura
elastica e capace di adattarsi autonomamente ai picchi di traffico.

Gli outputs finali ci restituiscono il nome DNS del Load Balancer, che rappresenta l'endpoint effettivo
a cui il frontend (o i client API) dovranno inviare le richieste, e il nome del gruppo di scaling.
*/