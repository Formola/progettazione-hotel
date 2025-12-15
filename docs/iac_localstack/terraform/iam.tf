/* ------------------------------------------------------------------------
   Gestione dei permessi (Identity and Access Management).
   Qui definiamo i ruoli che i nostri server (EC2) possono "indossare"
   per acquisire automaticamente i permessi di scrittura su S3 o accesso al DB.
   ------------------------------------------------------------------------
*/

# https://anuradhawick.medium.com/understanding-aws-cognito-and-iam-roles-af2dfefef996

/* 
   Questo blocco crea un'identità vuota chiamata "hotel_backend_role".
   La "assume_role_policy" è fondamentale: definisce CHI ha il diritto di indossare questo ruolo.
   In questo caso, stiamo dicendo: "Solo il servizio EC2 (ec2.amazonaws.com) può assumere questo ruolo".
   Un utente umano o un servizio diverso (es. Lambda) non potrà usarlo.
*/
resource "aws_iam_role" "backend_role" {
  name = "hotel_backend_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })

  tags = {
    Name = "HotelBackendRole"
  }
}

/* POLICY
   Questo blocco definisce COSA può fare chi possiede il ruolo.
   Invece di dare accesso "AdministratorAccess" (pericoloso), diamo solo i permessi S3 necessari.
      
   Actions:
   - PutObject: Caricare file
   - GetObject: Leggere file
   - ListBucket: Vedere l'elenco dei file
   - DeleteObject: Cancellare file
*/
resource "aws_iam_policy" "s3_backend_policy" {
  name        = "hotel_s3_access_policy"
  description = "Policy che permette lettura e scrittura sul bucket dell'hotel"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowS3Access"
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        /* Qui limitiamo l'accesso SOLO al nostro bucket specifico.
           Mettiamo due righe: una per il bucket stesso (list) e una per il contenuto (/*)
        */
        Resource = [
          aws_s3_bucket.media_bucket.arn,
          "${aws_s3_bucket.media_bucket.arn}/*"
        ]
      }
    ]
  })
}

/* L'ATTACHMENT
   Questo blocco unisce il Ruolo (punto 1) alla Policy (punto 2).
   Senza questo, il ruolo esisterebbe ma non avrebbe alcun permesso effettivo.
*/
resource "aws_iam_role_policy_attachment" "attach_s3_to_role" {
  role       = aws_iam_role.backend_role.name
  policy_arn = aws_iam_policy.s3_backend_policy.arn
}

/* 4. L'INSTANCE PROFILE 
   Questo è un concetto specifico di AWS per le EC2.
   Una macchina virtuale EC2 non può "toccare" direttamente un IAM Role.
   Ha bisogno di un "Profilo Istanza" che faccia da wrapper (contenitore) per il ruolo.
   Sarà questo nome ("hotel_backend_profile") che passeremo alla configurazione della EC2.
*/
resource "aws_iam_instance_profile" "backend_profile" {
  name = "hotel_backend_profile"
  role = aws_iam_role.backend_role.name
}