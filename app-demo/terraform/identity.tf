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

  auto_verified_attributes = ["email"]

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

  # SECURITY: Prevenzione Enumerazione Utenti
  # Con "ENABLED", Cognito risponde con un errore generico anche se l'user non esiste.
  # Evita che qualcuno provi 1000 email per vedere quali sono registrate.
  prevent_user_existence_errors = "ENABLED"

  # Flussi di autenticazione permessi (SRP è più sicuro per il web)
  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH"
  ]

  # TOKEN VALIDITY
  # Access Token breve (es. 1 ora)
  # Refresh Token lungo (es. 1 giorni) -> Permette all'utente di restare loggato.
  access_token_validity = 60
  id_token_validity     = 60
  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  # refresh token possiamo mettere un mi
  refresh_token_validity = 1

  # Revoca Token
  # Permette di invalidare i token se necessario
  enable_token_revocation = true
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
