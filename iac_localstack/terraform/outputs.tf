
output "vpc_id" {
  value = aws_vpc.main.id
}

output "s3_bucket_name" {
  value = aws_s3_bucket.media_bucket.id
}

output "sns_topic_arn" {
  value = aws_sns_topic.alerts.arn
}


output "test_instance_id" {
  description = "ID dell'istanza di test creata su LocalStack"
  value       = aws_instance.test_instance.id
}

output "real_db_connection" {
  value = "postgres://appuser:apppassword@localhost:5432/appdb"
}

output "api_base_url" {
  description = "URL Base del Gateway"
  value       = "http://localhost:4566/restapis/${aws_api_gateway_rest_api.main.id}/dev/_user_request_/api"
}