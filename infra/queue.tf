resource "aws_sqs_queue" "celery" {
  name = "easytask-celery"
}