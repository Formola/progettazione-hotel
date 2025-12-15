# Security Group per il Load Balancer (Livello Pubblico)
# Deve accettare traffico da chiunque su internet.
resource "aws_security_group" "alb_sg" {
  name        = "alb-security-group"
  description = "Permette traffico HTTP/HTTPS pubblico verso il Load Balancer"
  vpc_id      = aws_vpc.main.id # Associa al VPC principale

  # Ingress: Regole per il traffico in ENTRATA
  # Apriamo la porta 80 (HTTP) a tutto il mondo (0.0.0.0/0)
  ingress {
    description = "HTTP from Internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Apriamo la porta 443 (HTTPS) a tutto il mondo
  ingress {
    description = "HTTPS from Internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Da ovunque
  }

  # Egress: Regole per il traffico in USCITA
  # Il LB deve poter parlare con chiunque (principalmente le istanze EC2)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # -1 significa "tutti i protocolli"
    cidr_blocks = ["0.0.0.0/0"] # Verso ovunque
  }

  tags = {
    Name = "alb-sg"
  }
}

# Security Group per le Istanze EC2 (Livello Applicativo)
# Le istanze non parlano con internet, ma SOLO col Load Balancer.
resource "aws_security_group" "ec2_sg" {
  name        = "ec2-security-group"
  description = "Permette traffico solo dal Load Balancer"
  vpc_id      = aws_vpc.main.id # Associa al VPC principale

  # Ingress: Accetta connessioni sulla porta 8000 da TUTTI (per debug con LocalStack)
  # non funziona, non apre la porta e localstack quindi non la mappa sull'host
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Deve essere 0.0.0.0/0 per il mapping
  }

  # Ingress: Accetta connessioni sulla porta 80 SOLO se provengono
  # dal Security Group del Load Balancer (alb_sg).
  ingress {
    description     = "HTTP from ALB only"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id] # Solo dal SG dell'ALB
  }

  # Opzionale: SSH per debug (solo dalla rete locale o VPN)
  ingress {
    description = "SSH from internal network"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"] # Solo dall'interno della VPC
  }

  # Egress: Le istanze devono poter uscire (es. per scaricare update o parlare con S3/RDS)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] # Verso ovunque
  }

  tags = {
    Name = "ec2-backend-sg"
  }
}

# Security Group per il Database (Livello Dati)
# Il DB è il componente più critico. Nessuno entra qui tranne il Backend.
resource "aws_security_group" "db_sg" {
  name        = "rds-security-group"
  description = "Permette traffico PostgreSQL solo dalle EC2"
  vpc_id      = aws_vpc.main.id # Associa al VPC principale

  # Ingress: Porta 5432 (standard Postgres) aperta SOLO
  # per il Security Group delle EC2 (ec2_sg).
  ingress {
    description     = "PostgreSQL from Backend EC2"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_sg.id] # Solo dal SG delle EC2
  }

  tags = {
    Name = "rds-sg"
  }
}



# default per ec2 
# Currently, LocalStack only supports the default security group.
# You can add rules to the security group using the AuthorizeSecurityGroupIngress API.
# NON creiamo un nuovo gruppo per il debug, usiamo il Default del VPC.
# LocalStack preferisce questo per il port mapping automatico.
# Non usiamo blocchi ingress/egress qui dentro.
# --- AGGIUNTA PER IL DEBUG ---
# Apriamo la porta 8000 sul gruppo default del VPC default
resource "aws_security_group_rule" "debug_ingress_8000" {
  type              = "ingress"
  from_port         = 8000
  to_port           = 8000
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  
  # Usiamo l'ID del gruppo default letto in network.tf
    security_group_id = data.aws_security_group.localstack_default_sg.id
}

# Apriamo anche SSH per sicurezza
resource "aws_security_group_rule" "debug_ingress_ssh" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
    security_group_id = data.aws_security_group.localstack_default_sg.id
}

# --- OUTPUTS ---
# Questi valori verranno stampati alla fine del comando 'terraform apply'
# e potranno essere usati da altri moduli o script esterni.

output "security_group_alb_id" {
  description = "ID del Security Group del Load Balancer"
  value       = aws_security_group.alb_sg.id
}

output "security_group_ec2_id" {
  description = "ID del Security Group delle istanze Backend"
  value       = aws_security_group.ec2_sg.id
}

output "security_group_db_id" {
  description = "ID del Security Group del Database RDS"
  value       = aws_security_group.db_sg.id
}


/*
In questo modulo di sicurezza stiamo definendo tre risorse fondamentali di tipo aws_security_group, che agiscono
come firewall virtuali stateful per controllare il traffico in entrata e in uscita verso le risorse AWS.
Ogni gruppo è associato alla VPC creata precedentemente tramite il parametro vpc_id per garantire che le
regole siano applicate all'interno del nostro recinto di rete isolato.

Il primo componente è il Security Group per l'Application Load Balancer (alb_sg). La sua funzione è gestire
il traffico pubblico, pertanto le regole di ingresso (ingress) sono configurate per accettare connessioni
da qualsiasi indirizzo IP (0.0.0.0/0) sulle porte standard del web, ovvero la porta 80 per HTTP e la 443 per HTTPS.
Questo permette agli utenti di tutto il mondo di raggiungere il punto di ingresso dell'applicazione.
Le regole di uscita (egress) sono impostate su -1 (tutti i protocolli) verso ovunque, poiché il Load Balancer
deve avere la libertà di inoltrare le richieste verso le istanze backend o di comunicare con altri servizi
AWS senza blocchi.

Il secondo componente è il Security Group per le istanze EC2 di Backend (ec2_sg), che implementa un
livello di sicurezza più stringente. Qui non usiamo indirizzi IP generici per le regole di ingresso web,
ma utilizziamo il parametro security_groups. Questo crea un riferimento diretto al gruppo del Load Balancer,
stabilendo una regola che dice esplicitamente "accetta traffico sulla porta 80 solo se proviene da una risorsa
che possiede il Security Group dell'ALB". Questo impedisce a chiunque di aggirare il Load Balancer e
contattare direttamente i server. Abbiamo aggiunto anche una regola per SSH (porta 22) limitata al CIDR
della VPC per eventuali operazioni di debug interno. L'uscita è lasciata aperta per permettere alle istanze
di scaricare pacchetti o connettersi a S3 e RDS.

Il terzo componente è il Security Group per il Database (db_sg), che rappresenta il livello più profondo e protetto.
La regola di ingresso sulla porta 5432, tipica di PostgreSQL, è vincolata esclusivamente al Security Group delle
istanze EC2 (ec2_sg) tramite il parametro security_groups. Questo assicura che né il Load Balancer né alcun
utente esterno possano tentare una connessione diretta al database. Solo il codice che gira sui server
applicativi backend ha il permesso di scambiare dati con RDS.

Infine, la sezione outputs espone gli ID univoci (aws_security_group.*.id) dei tre gruppi appena creati.
Questi output sono essenziali perché, quando andremo a creare le istanze EC2 e il database RDS nei prossimi file,
dovremo indicare a Terraform quali Security Group assegnare loro.
*/