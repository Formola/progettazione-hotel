

# --- API GATEWAY HTTP (V2) ---

resource "aws_apigatewayv2_api" "main_api" {
  name          = "myapp-http-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers = ["content-type", "authorization"]
    max_age       = 300
  }
}

# --- AUTHORIZER ---

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

# --- INTEGRAZIONE (Fix Path Mapping) ---

resource "aws_apigatewayv2_integration" "backend_integration" {
  api_id           = aws_apigatewayv2_api.main_api.id
  integration_type = "HTTP_PROXY"
  
  payload_format_version = "1.0" 
  integration_method     = "ANY" 
  
  integration_uri = "http://backend:8000"

  request_parameters = {
    "overwrite:path" = "$request.path"
    
    "append:header.x-user-cognito-sub" = "$context.authorizer.claims.sub"
    "append:header.x-user-email"       = "$context.authorizer.claims.username"
    "append:header.x-user-role"        = "$context.authorizer.claims['cognito:groups']"
  }
}

# --- ROTTE ---

# OPTIONS (CORS) e flyweight per ogni rotta
resource "aws_apigatewayv2_route" "options_route" {
  api_id    = aws_apigatewayv2_api.main_api.id
  route_key = "OPTIONS /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.backend_integration.id}"
  authorization_type = "NONE"
}

resource "aws_apigatewayv2_route" "public_search_no_slash" {
  api_id    = aws_apigatewayv2_api.main_api.id
  route_key = "GET /api/search" 
  target    = "integrations/${aws_apigatewayv2_integration.backend_integration.id}"
  authorization_type = "NONE"
}

# RICERCA PUBBLICA - Con sub-paths
resource "aws_apigatewayv2_route" "public_search_subpaths" {
  api_id    = aws_apigatewayv2_api.main_api.id
  route_key = "GET /api/search/{proxy+}" 
  target    = "integrations/${aws_apigatewayv2_integration.backend_integration.id}"
  authorization_type = "NONE"
}

# DEFAULT (Tutto il resto PROTETTO)
resource "aws_apigatewayv2_route" "default_route" {
  api_id    = aws_apigatewayv2_api.main_api.id
  route_key = "ANY /{proxy+}" 

  target = "integrations/${aws_apigatewayv2_integration.backend_integration.id}"

  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.jwt_auth.id
}

# --- STAGE ---

resource "aws_apigatewayv2_stage" "default_stage" {
  api_id      = aws_apigatewayv2_api.main_api.id
  name        = "$default"
  auto_deploy = true
}

output "api_gateway_endpoint" {
  value = aws_apigatewayv2_api.main_api.api_endpoint
}


