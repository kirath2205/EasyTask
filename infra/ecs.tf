resource "aws_ecs_task_definition" "app" {
  family                   = "easytask"
  network_mode             = "awsvpc"
  requires_compatibilities = ["EC2"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.task_exec.arn

  container_definitions = jsonencode([
    {
      name  = "django"
      image = aws_ecr_repository.app.repository_url
      essential = true
      cpu    = 128
      memory = 512
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
        }
      ]
      environment = [
        { name = "DB_HOST", value = aws_db_instance.postgres.address },
        { name = "DB_PORT", value = tostring(aws_db_instance.postgres.port) },
        { name = "DB_NAME", value = var.db_name },
        { name = "DB_USER", value = var.db_username },
        { name = "DB_PASSWORD", value = var.db_password },
        { name = "CELERY_BROKER_URL", value = aws_sqs_queue.celery.url }
      ]
    },
    {
      name      = "celery"
      image     = aws_ecr_repository.app.repository_url
      essential = false
      cpu    = 128
      memory = 512
      command   = ["celery", "-A", "EasyTask", "worker", "--loglevel=info"]
      environment = [
        { name = "DB_HOST", value = aws_db_instance.postgres.endpoint },
        { name = "DB_PORT", value = tostring(aws_db_instance.postgres.port) },
        { name = "DB_NAME", value = var.db_name },
        { name = "DB_USER", value = var.db_username },
        { name = "DB_PASSWORD", value = var.db_password },
        { name = "CELERY_BROKER_URL", value = aws_sqs_queue.celery.url }
      ]
    }
  ])
}

resource "aws_ecs_service" "app" {
  name            = "easytask"
  cluster         = aws_ecs_cluster.app.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "EC2"

  network_configuration {
    subnets         = module.vpc.private_subnets
    security_groups = [aws_security_group.ecs.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "django"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]
}
