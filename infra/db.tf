resource "aws_db_subnet_group" "rds" {
  name       = "easytask-rds"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_db_instance" "postgres" {
  identifier              = "easytask-postgres"
  engine                  = "postgres"
  engine_version          = "15.12"
  instance_class          = "db.t3.micro"  # Smallest, lowest-cost
  allocated_storage       = 20             # Minimum required
  username                = var.db_username
  password                = var.db_password
  db_name                 = var.db_name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  db_subnet_group_name    = aws_db_subnet_group.rds.name
  publicly_accessible     = false
  skip_final_snapshot     = true
  multi_az                = false
  storage_encrypted       = false
}