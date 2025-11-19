# resource "aws_cognito_user_pool" "main" {
#   name = "${var.project_name}-user-pool"

#   password_policy {
#     minimum_length    = 8
#     require_lowercase = true
#     require_numbers   = true
#   }
  
#   auto_verified_attributes = ["email"]
# }

# resource "aws_cognito_user_pool_client" "client" {
#   name = "${var.project_name}-app-client"
#   user_pool_id = aws_cognito_user_pool.main.id
#   explicit_auth_flows = ["ADMIN_NO_SRP_AUTH"]
# }