output "alb_url" {
  value = aws_lb.app.dns_name
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.endpoint
}

output "sqs_queue_url" {
  value = aws_sqs_queue.celery.url
}
output "ecr_repository_url" { value = aws_ecr_repository.app.repository_url }
