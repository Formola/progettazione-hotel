# --- API GATEWAY (INGRESSO GESTITO) ---

# API Gateway (Tipo HTTP - V2)
resource "aws_apigatewayv2_api" "main_api" {
  name          = "myapp-http-api"
  protocol_type = "HTTP"
  
  tags = {
    Name = "Main API Gateway"
  }
}

# Authorizer
# Collega l'API Gateway a Cognito.
# Se la richiesta non ha un token valido emesso dal nostro User Pool, viene bloccata qui.
resource "aws_apigatewayv2_authorizer" "jwt_auth" {
  api_id           = aws_apigatewayv2_api.main_api.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "cognito-authorizer"

  jwt_configuration {
    audience = [aws_cognito_user_pool_client.web_client.id]
    issuer   = "https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.main_pool.id}"
  }
}

# Integrazione con ALB
# Diciamo all'API Gateway: "Se passi il controllo, gira la richiesta al Load Balancer".
resource "aws_apigatewayv2_integration" "alb_integration" {
  api_id           = aws_apigatewayv2_api.main_api.id
  integration_type = "HTTP_PROXY" # Usiamo Proxy per semplicità verso l'ALB pubblico
  
  # Usiamo il metodo ANY per passare tutto (GET, POST, PUT...)
  integration_method = "ANY" 
  
  # L'URL di destinazione è il DNS del Load Balancer (definito in compute.tf)
  integration_uri    = "http://${aws_lb.app_alb.dns_name}:4566" 
}

# Rotta Default (Catch-all)
# Intercetta TUTTE le chiamate ($default) e applica l'Authorizer.
resource "aws_apigatewayv2_route" "default_route" {
  api_id    = aws_apigatewayv2_api.main_api.id
  route_key = "$default" # Significa "qualsiasi path e metodo"

  target = "integrations/${aws_apigatewayv2_integration.alb_integration.id}"

  # QUI ATTIVIAMO LA PROTEZIONE:
  # authorization_type = "JWT"
  # authorizer_id      = aws_apigatewayv2_authorizer.jwt_auth.id
  
  # Per ora lasciamo "NONE" per facilitarti i test iniziali con curl senza token.
  authorization_type = "NONE" 
}

# Stage (Ambiente)
# Lo stage di default che deploya le modifiche automaticamente.
resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.main_api.id
  name        = "$default"
  auto_deploy = true
}

# --- OUTPUTS ---

output "api_gateway_endpoint" {
  description = "L'URL pubblico finale delle tue API (da usare nel frontend)"
  value       = aws_apigatewayv2_api.main_api.api_endpoint
}


/*
Il flusso che abbiamo costruito è:

Ingresso: L'utente chiama l'URL dell'API Gateway (api_gateway_endpoint).

Authorizer (aws_apigatewayv2_authorizer): Prima di fare qualsiasi cosa, il Gateway controlla
l'header Authorization. Verifica che il token JWT sia stato firmato dal nostro User Pool Cognito (issuer)
e sia destinato alla nostra app (audience). Se il token è falso o scaduto, la richiesta
muore qui con un 401 Unauthorized.

Routing (aws_apigatewayv2_route): Se autorizzato, la rotta $default prende la richiesta.

Integrazione (aws_apigatewayv2_integration): La richiesta viene impacchettata e spedita (HTTP_PROXY)
verso il DNS del tuo Load Balancer (aws_lb.app_alb.dns_name).

Nota importante sull'Authorizer: Nel codice della rotta (default_route),
abbiamo authorization_type = "NONE" (e commentato la parte JWT).
Perché? Perché appena lanci terraform apply vorrai testare se il collegamento "Gateway -> ALB -> EC2"
funziona facendo una semplice chiamata curl. Se attivassimo subito l'auth, dovresti prima registrarti,
confermare l'email, fare login, prendere il token e passarlo nell'header solo per vedere se risponde "Hello World".
Quando sei pronto a blindare tutto, basta decommentare quelle due righe e fare di nuovo terraform apply.

*/