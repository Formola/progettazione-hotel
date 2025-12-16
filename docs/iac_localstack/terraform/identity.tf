# --- COGNITO (IDENTITY PROVIDER) ---

# User Pool
# È il database degli utenti. Qui finiscono le registrazioni.
resource "aws_cognito_user_pool" "main_pool" {
  name = "myapp-user-pool"

  # Policy password: chiediamo un minimo di sicurezza
  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_uppercase = true
  }

  # Gli utenti possono registrarsi con la loro email
  # lo commentiamo altrimenti l'user dovrebbe ricevere un email di verifica con un codice
  # auto_verified_attributes = ["email"]
  
  tags = {
    Name = "Main User Pool"
  }
}

# User Pool Client
# È "l'app" che ha il permesso di parlare con Cognito (es. app frontend).
resource "aws_cognito_user_pool_client" "web_client" {
  name = "myapp-web-client"

  user_pool_id = aws_cognito_user_pool.main_pool.id

  # Non generiamo un client secret perché le app frontend (SPA)
  # non possono conservarlo in modo sicuro.
  generate_secret = false

  # Flussi di autenticazione permessi (SRP è più sicuro per il web)
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH"
  ]
}

# User Pool Domain (Opzionale ma utile)
# Crea un dominio hosted per la pagina di login di Cognito (es. myapp.auth.us-east-1...)
resource "aws_cognito_user_pool_domain" "main_domain" {
  domain       = "myapp-auth-domain-local"
  user_pool_id = aws_cognito_user_pool.main_pool.id
}

# --- OUTPUTS ---

output "cognito_user_pool_id" {
  description = "L'ID del User Pool (da mettere nel frontend)"
  value       = aws_cognito_user_pool.main_pool.id
}

output "cognito_client_id" {
  description = "L'ID del Client App (da mettere nel frontend)"
  value       = aws_cognito_user_pool_client.web_client.id
}

output "cognito_issuer_url" {
  description = "L'URL dell'Issuer per configurare l'Authorizer"
  value       = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.main_pool.id}"
}

/*
Creiamo un aws_cognito_user_pool.
Abbiamo abilitato auto_verified_attributes = ["email"].
Il componente cruciale è lo aws_cognito_user_pool_client.
Nota l'impostazione generate_secret = false: questo è fondamentale per le applicazioni
web moderne (React/Vue/Angular) che girano nel browser e non possono nascondere un segreto.
Abilitiamo il protocollo SRP (ALLOW_USER_SRP_AUTH) che è lo standard sicuro per non inviare mai
la password in chiaro sulla rete durante il login.
*/