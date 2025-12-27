terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
  access_key = "test"
  secret_key = "test"

  s3_use_path_style = true
  skip_credentials_validation = true
  skip_metadata_api_check = true
  skip_requesting_account_id = true

  # Mappatura di TUTTI i servizi su LocalStack
  endpoints {
    apigateway     = "http://localhost:4566"
    apigatewayv2   = "http://localhost:4566"
    autoscaling    = "http://localhost:4566"
    cloudwatch     = "http://localhost:4566"
    cognitoidp     = "http://localhost:4566"
    ec2            = "http://localhost:4566"
    elb            = "http://localhost:4566"
    elbv2          = "http://localhost:4566"
    iam            = "http://localhost:4566"
    rds            = "http://localhost:4566"
    route53        = "http://localhost:4566"
    s3             = "http://localhost:4566"
    sns            = "http://localhost:4566"
    sqs            = "http://localhost:4566"
    sts            = "http://localhost:4566"
    cloudfront    = "http://localhost:4566"

  }
}

# endpoints {
#   s3             = "http://s3.localhost.localstack.cloud:4566"
# }

# Note

# If there are any difficulties resolving this DNS
# record, you can utilize http://localhost:4566
# as a fallback option in combination with
# setting s3_use_path_style = true in the provider.
# It’s worth noting that the S3 service endpoint
# differs slightly from the other service endpoints
# due to AWS deprecating path-style based access for
# hosting buckets.

# --- FILE GENERATION ---

resource "local_file" "dotenv" {
  filename = "/config/localstack.env"
  content  = <<EOF
# File generato automaticamente da Terraform dentro LocalStack

# --- CONFIGURAZIONE FRONTEND (Browser -> Localhost) ---
PUBLIC_COGNITO_USER_POOL_ID=${aws_cognito_user_pool.main_pool.id}
PUBLIC_COGNITO_CLIENT_ID=${aws_cognito_user_pool_client.web_client.id}
PUBLIC_COGNITO_ISSUER_URL=https://cognito-idp.${var.aws_region}.amazonaws.com/${aws_cognito_user_pool.main_pool.id}
PUBLIC_AWS_REGION=us-east-1
PUBLIC_COGNITO_ENDPOINT=http://localhost:4566

# --- API GATEWAY (Browser -> Localhost) ---
PUBLIC_API_GATEWAY_ENDPOINT=${aws_apigatewayv2_api.main_api.api_endpoint}

# --- CONFIGURAZIONE BACKEND (Container -> Container) ---
AWS_ENDPOINT_URL=http://localstack:4566
AWS_REGION=us-east-1
COGNITO_USER_POOL_ID=${aws_cognito_user_pool.main_pool.id}
COGNITO_CLIENT_ID=${aws_cognito_user_pool_client.web_client.id}

# --- LOAD BALANCER & API ---
ALB_DNS_NAME=${aws_lb.app_alb.dns_name}
API_GATEWAY_ENDPOINT=${aws_apigatewayv2_api.main_api.api_endpoint}

# --- STORAGE ---
S3_FRONTEND_BUCKET=${aws_s3_bucket.frontend_bucket.id}
S3_FRONTEND_ENDPOINT=${aws_s3_bucket_website_configuration.frontend_config.website_endpoint}
S3_MEDIA_BUCKET=${aws_s3_bucket.media_bucket.id}

# --- RDS DATABASE ---
DB_ENDPOINT=${aws_db_instance.postgres.endpoint}
DB_HOST=localstack
DB_PORT=4510
DB_USER=${aws_db_instance.postgres.username}
DB_PASS=${var.db_password}
DB_NAME=${aws_db_instance.postgres.db_name}

# --- CLOUDFRONT ---
CLOUDFRONT_DOMAIN=${aws_cloudfront_distribution.s3_distribution.domain_name}
CLOUDFRONT_ID=${aws_cloudfront_distribution.s3_distribution.id}
EOF
}
