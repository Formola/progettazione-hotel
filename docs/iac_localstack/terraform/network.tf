# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  
  tags = {
    Name = "main-vpc"
  }
}

# Recuperiamo le zone di disponibilità disponibili
data "aws_availability_zones" "available" {
  state = "available"
}

# Subnet Pubbliche (Per Load Balancer)
resource "aws_subnet" "public_1" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-1"
    Type = "Public"
  }
}

resource "aws_subnet" "public_2" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = {
    Name = "public-subnet-2"
    Type = "Public"
  }
}

# Subnet Private (Per EC2 Backend e RDS)
resource "aws_subnet" "private_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name = "private-subnet-1"
    Type = "Private"
  }
}

resource "aws_subnet" "private_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = data.aws_availability_zones.available.names[1]

  tags = {
    Name = "private-subnet-2"
    Type = "Private"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "main-igw"
  }
}

# Routing Pubblico
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }

  tags = {
    Name = "public-route-table"
  }
}

# Associazioni delle Route Table Pubbliche
resource "aws_route_table_association" "public_1" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}

# Routing Privato
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id
  # Nota: Senza NAT Gateway, queste subnet non escono su internet.
  
  tags = {
    Name = "private-route-table"
  }
}

resource "aws_route_table_association" "private_1" {
  subnet_id      = aws_subnet.private_1.id
  route_table_id = aws_route_table.private.id
}

resource "aws_route_table_association" "private_2" {
  subnet_id      = aws_subnet.private_2.id
  route_table_id = aws_route_table.private.id
}

# Route 53 DNS Zone Privata
resource "aws_route53_zone" "private" {
  name = "myapp.local"

  vpc {
    vpc_id = aws_vpc.main.id
  }
  
  tags = {
    Name = "private-dns-zone"
  }
}

# test ec2
# --- AGGIUNTA PER IL DEBUG ---
# Recuperiamo i dati del VPC di Default (quello che usa la CLI)

# In LocalStack, networking features like subnets and VPCs are not emulated.
# LocalStack provides a default security group that manages the exposed ports for the EC2 instance.
# While users can create additional security groups, LocalStack focuses on the default security group.
data "aws_vpc" "localstack_default" {
  default = true
}

# Recuperiamo le subnet del VPC di Default
data "aws_subnets" "localstack_default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.localstack_default.id]
  }
}

# Cerchiamo esplicitamente il Security Group che si chiama "default"
# all'interno del VPC di Default.
data "aws_security_group" "localstack_default_sg" {
  vpc_id = data.aws_vpc.localstack_default.id
  name   = "default"
}

# --- OUTPUTS ---

output "vpc_id" {
  description = "L'ID della Virtual Private Cloud creata"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Lista degli ID delle Subnet Pubbliche"
  value       = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

output "private_subnet_ids" {
  description = "Lista degli ID delle Subnet Private"
  value       = [aws_subnet.private_1.id, aws_subnet.private_2.id]
}

output "private_dns_zone_id" {
  description = "L'ID della Hosted Zone privata di Route53"
  value       = aws_route53_zone.private.zone_id
}

/*
Questo file getta le fondamenta dell'intera infrastruttura definendo la topologia di rete.
Iniziamo con la risorsa aws_vpc, che crea il Virtual Private Cloud isolato. Qui impostiamo il blocco CIDR
su 10.0.0.0/16, che ci fornisce un ampio spazio di indirizzi IP privati. I parametri enable_dns_support e 
enable_dns_hostnames sono impostati su true perché sono essenziali per il funzionamento interno dei servizi AWS e
per permettere alle istanze di risolversi a vicenda tramite nome host invece che tramite IP, facilitando la gestione 
del cluster.

Successivamente, strutturiamo la rete in sottoreti utilizzando aws_subnet e data.aws_availability_zones.
Per garantire ridondanza e alta disponibilità, creiamo due subnet pubbliche e due subnet private distribuite
su diverse Availability Zones (AZ). Le subnet pubbliche hanno il flag map_public_ip_on_launch attivo, il che
significa che ogni risorsa lanciata qui riceverà automaticamente un IP pubblico, rendendole ideali per ospitare
il Load Balancer. Le subnet private, al contrario, sono progettate per ospitare le risorse sensibili come le
istanze EC2 di backend e il database RDS, che non devono essere direttamente esposte a internet.

Per connettere la nostra rete al mondo esterno, implementiamo un aws_internet_gateway e lo attacchiamo alla VPC.
Tuttavia, creare il gateway non basta: dobbiamo istruire la rete su come usarlo. Questo avviene tramite
la aws_route_table pubblica, dove definiamo una rotta che invia tutto il traffico destinato all'esterno (0.0.0.0/0)
verso l'Internet Gateway. Associando questa tabella solo alle subnet pubbliche, creiamo una separazione netta:
le subnet pubbliche possono "uscire" su internet, mentre quelle private rimangono isolate, aumentando drasticamente
la sicurezza.

Infine, configuriamo la risoluzione dei nomi con aws_route53_zone. Creiamo una "Hosted Zone" privata
chiamata myapp.local e la associamo alla nostra VPC. Questo componente agisce come un server DNS interno:
ci permetterà, nelle fasi successive, di creare record DNS personalizzati (come db.myapp.local o api.myapp.local)
che funzionano solo all'interno della nostra rete privata. Questo è fondamentale per permettere ai microservizi
di parlarsi in modo affidabile senza dipendere da indirizzi IP che potrebbero cambiare con l'autoscaling.

Gli outputs finali espongono gli ID della VPC, delle liste di subnet e della zona DNS. Questi valori sono
cruciali perché verranno "consumati" dai file Terraform successivi: ad esempio, il file del database
avrà bisogno degli ID delle subnet private per sapere dove posizionare le istanze RDS, e il Load Balancer
avrà bisogno degli ID delle subnet pubbliche per sapere dove mettersi in ascolto.
*/