# --- SEZIONE S3 (FRONTEND & MEDIA) ---

# Bucket S3 per il Frontend (Static Website Hosting)
resource "aws_s3_bucket" "frontend_bucket" {
  bucket = "my-app-frontend-bucket-local"
  
  # Force destroy permette di cancellare il bucket anche se non è vuoto
  # (utile in fase di test/dev con terraform destroy)
  force_destroy = true

  tags = {
    Name = "Frontend Static Hosting"
  }
}

# Configurazione per trasformare il bucket in un sito web
resource "aws_s3_bucket_website_configuration" "frontend_config" {
  bucket = aws_s3_bucket.frontend_bucket.id

  index_document {
    suffix = "index.html"
  }

  error_document {
    key = "index.html" # Per le SPA (React/Vue/Svelte), gli errori 404 devono tornare a index.html
  }
}

# Policy per rendere pubblico il contenuto del bucket Frontend
# Senza questa, il sito non sarebbe visibile al browser.
resource "aws_s3_bucket_policy" "frontend_public_policy" {
  bucket = aws_s3_bucket.frontend_bucket.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*" # Chiunque
        Action    = "s3:GetObject" # Permesso di lettura degli oggetti
        Resource  = "${aws_s3_bucket.frontend_bucket.arn}/*"
      },
    ]
  })
}

# Bucket S3 per i Media (User Uploads)
# Qui finiscono le immagini profilo, i video, ecc. caricati dagli utenti.
# Questo bucket rimane privato di default (l'accesso sarà gestito via codice o presigned URLs).
resource "aws_s3_bucket" "media_bucket" {
  bucket = "my-app-media-assets-local"
  force_destroy = true

  tags = {
    Name = "User Media Storage"
  }
}

# --- SEZIONE DATABASE (RDS) ---

# Subnet Group per RDS
# RDS deve sapere in quali subnet può creare le sue interfacce di rete.
# Gli passiamo le Subnet Private create in network.tf per tenerlo isolato.
resource "aws_db_subnet_group" "db_subnet_group" {
  name       = "main-db-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]

  tags = {
    Name = "My DB Subnet Group"
  }
}

# Istanza Database RDS (PostgreSQL)
resource "aws_db_instance" "postgres" {
  identifier        = "myapp-postgres-db"
  engine            = "postgres"
  engine_version    = "13"         
  instance_class    = "db.t3.micro" # Free tier friendly
  allocated_storage = 20           # 20 GB

  db_name  = "myappdb"
  username = "dbadmin"
  password = "password" # In prod si usa AWS Secrets Manager!!

  # Networking & Sicurezza
  db_subnet_group_name   = aws_db_subnet_group.db_subnet_group.name
  vpc_security_group_ids = [aws_security_group.db_sg.id]
  
  # Importante: Non vogliamo che sia accessibile da internet
  publicly_accessible    = false
  
  # Skip final snapshot serve per distruggere il DB velocemente senza fare backup
  # (Utile solo in dev/localstack)
  skip_final_snapshot    = true

  tags = {
    Name = "Primary Database"
  }
}

# --- OUTPUTS ---

output "s3_frontend_endpoint" {
  description = "L'URL pubblico del sito web statico ospitato su S3"
  value       = aws_s3_bucket_website_configuration.frontend_config.website_endpoint
}

output "s3_frontend_bucket_name" {
  description = "Il nome del bucket S3 del frontend"
  value       = aws_s3_bucket.frontend_bucket.id
}

output "s3_media_bucket_name" {
  description = "Il nome del bucket S3 per i media"
  value       = aws_s3_bucket.media_bucket.id
}

output "rds_endpoint" {
  description = "L'indirizzo di connessione al database (host:port)"
  value       = aws_db_instance.postgres.endpoint
}

output "rds_db_name" {
  description = "Il nome del database creato"
  value       = aws_db_instance.postgres.db_name
}

## POPOLAMENTO DB

# --- POPOLAMENTO SCHEMA DB (Via psql locale) ---

# --- POPOLAMENTO SCHEMA DB (Via psql locale) ---

resource "null_resource" "db_setup" {
  
  # Trigger: riesegui se cambia il file SQL o l'ID del database
  triggers = {
    schema_hash = filemd5("${path.module}/schema.sql")
    db_instance = aws_db_instance.postgres.id 
  }

  # Dipendenza esplicita: aspetta che RDS sia pronto
  depends_on = [aws_db_instance.postgres] 

  provisioner "local-exec" {
    environment = {
      PGPASSWORD = aws_db_instance.postgres.password 
    }

    command = "sleep 5 && psql -h localhost -p 4510 -U ${aws_db_instance.postgres.username} -d ${aws_db_instance.postgres.db_name} -f ${path.module}/schema.sql"
  }
}
/*
Per la parte di Frontend, implementiamo il Direct Hosting Pattern utilizzando aws_s3_bucket per creare
un contenitore chiamato frontend_bucket. A differenza di un normale spazio di archiviazione, questo bucket
viene "attivato" come server web tramite la risorsa aws_s3_bucket_website_configuration.
Qui definiamo l'index_document (la home page) e l'error_document. Notiamo che entrambi puntano a index.html:
questo è un trucco standard per le Single Page Application (SPA) moderne. Poiché il routing è gestito dal
browser (lato client), se un utente ricarica la pagina su un percorso come /profilo, S3 non troverebbe il
file profilo.html e darebbe errore; reindirizzando l'errore a index.html, permettiamo al framework JS di
caricarsi e mostrare la pagina corretta. Per rendere il sito accessibile agli utenti, applichiamo una
aws_s3_bucket_policy che concede il permesso s3:GetObject a chiunque (Principal = "*"), rendendo di fatto
pubblici i file in lettura.

Per i file caricati dagli utenti (immagini, documenti), creiamo un secondo bucket distinto, media_bucket.
A differenza del primo, questo non ha configurazioni di sito web né policy pubbliche aperte a tutti di default.
È un contenitore "passivo" che verrà utilizzato dal backend per leggere e scrivere file (Object Storage puro),
mantenendo i dati degli utenti separati dal codice dell'applicazione.

Spostandoci sul Database, configuriamo l'ambiente per i dati strutturati. Prima di creare il database
vero e proprio, dobbiamo definire "dove" può esistere all'interno della nostra rete.
Questo lo facciamo con aws_db_subnet_group, raggruppando le due Subnet Private create precedentemente
nel file network.tf.

Infine, creiamo l'istanza aws_db_instance con motore PostgreSQL. I parametri definiscono 
la potenza della macchina (instance_class), lo spazio su disco (allocated_storage) e le credenziali di
accesso iniziali. Dal punto di vista della sicurezza e della rete, colleghiamo l'istanza al db_subnet_group
appena creato e le assegniamo il vpc_security_group_ids corrispondente al Security Group del
DB definito in security.tf. Il parametro publicly_accessible = false è la garanzia finale che questo database
non avrà un indirizzo IP pubblico, rendendolo raggiungibile esclusivamente dalle applicazioni
che girano dentro la nostra VPC.

Gli outputs finali ci forniscono le coordinate essenziali per collegare i pezzi: l'URL del sito web su S3
per testare il frontend e l'endpoint (indirizzo DNS) del database RDS che dovremo poi inserire nella
configurazione del nostro Backend.
*/