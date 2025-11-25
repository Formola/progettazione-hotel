# gateway.tf

# 1. API Gateway
resource "aws_api_gateway_rest_api" "main" {
  name        = "${var.project_name}-api"
  description = "API Gateway generico per Backend"
}

# 2. Risorsa base ("/api")
resource "aws_api_gateway_resource" "api" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_rest_api.main.root_resource_id
  path_part   = "api"
}

# 3. Risorsa Proxy ("{proxy+}")
# attura qualsiasi percorso dopo /api/
# /api/auth, /api/users/123, /api/rooms/456
resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  parent_id   = aws_api_gateway_resource.api.id
  path_part   = "{proxy+}"
}

# 4. Metodo ANY
# Accetta qualsiasi metodo HTTP
resource "aws_api_gateway_method" "proxy_any" {
  rest_api_id   = aws_api_gateway_rest_api.main.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"

  request_parameters = {
    "method.request.path.proxy" = true
  }
}

# 5. Integrazione
resource "aws_api_gateway_integration" "integration" {
  rest_api_id = aws_api_gateway_rest_api.main.id
  resource_id = aws_api_gateway_resource.proxy.id
  http_method = aws_api_gateway_method.proxy_any.http_method

  # Configurazione HTTP_PROXY generica
  type                    = "HTTP_PROXY"
  integration_http_method = "ANY"

  uri                     = "http://my-backend-server:4000/api/{proxy}"

  request_parameters = {
    "integration.request.path.proxy" = "method.request.path.proxy"
  }
}

# 6. Deployment
resource "aws_api_gateway_deployment" "deploy" {
  rest_api_id = aws_api_gateway_rest_api.main.id

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.main.body))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [aws_api_gateway_integration.integration]
}

# 7. Stage (Ambiente)
resource "aws_api_gateway_stage" "dev" {
  deployment_id = aws_api_gateway_deployment.deploy.id
  rest_api_id   = aws_api_gateway_rest_api.main.id
  stage_name    = "dev"
}