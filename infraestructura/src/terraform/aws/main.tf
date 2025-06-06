# Configuración del proveedor AWS
provider "aws" {
  region = var.aws_region
}

# Módulo para crear una VPC
module "vpc" {
  source = "../modules/vpc"
  
  vpc_name       = var.vpc_name
  vpc_cidr       = var.vpc_cidr
  azs            = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs
  
  enable_nat_gateway = var.enable_nat_gateway
  single_nat_gateway = var.single_nat_gateway
  
  tags = var.tags
}

# Grupo de seguridad para instancias EC2
resource "aws_security_group" "app_sg" {
  name        = "${var.environment}-app-sg"
  description = "Security group for application servers"
  vpc_id      = module.vpc.vpc_id
  
  # Regla de entrada para SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }
  
  # Regla de entrada para HTTP
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }
  
  # Regla de entrada para HTTPS
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS access"
  }
  
  # Regla de salida para todo el tráfico
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-app-sg"
    }
  )
}

# Instancia EC2 para aplicación
resource "aws_instance" "app_server" {
  count         = var.app_instance_count
  
  ami           = var.app_instance_ami
  instance_type = var.app_instance_type
  subnet_id     = module.vpc.public_subnets[count.index % length(module.vpc.public_subnets)]
  
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  key_name               = var.key_name
  
  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.app_instance_volume_size
    delete_on_termination = true
    encrypted             = true
  }
  
  user_data = <<-EOF
              #!/bin/bash
              echo "Hello from Terraform!"
              apt-get update -y
              apt-get install -y nginx
              echo "<h1>Deployed via Terraform</h1>" > /var/www/html/index.html
              systemctl enable nginx
              systemctl start nginx
              EOF
  
  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-app-server-${count.index + 1}"
    }
  )
}

# Balanceador de carga para aplicación
resource "aws_lb" "app_lb" {
  name               = "${var.environment}-app-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.app_sg.id]
  subnets            = module.vpc.public_subnets
  
  enable_deletion_protection = false
  
  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-app-lb"
    }
  )
}

# Grupo objetivo para el balanceador de carga
resource "aws_lb_target_group" "app_tg" {
  name     = "${var.environment}-app-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id
  
  health_check {
    enabled             = true
    interval            = 30
    path                = "/"
    port                = "traffic-port"
    healthy_threshold   = 3
    unhealthy_threshold = 3
    timeout             = 5
    protocol            = "HTTP"
    matcher             = "200"
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-app-tg"
    }
  )
}

# Adjuntar instancias al grupo objetivo
resource "aws_lb_target_group_attachment" "app_tg_attachment" {
  count            = var.app_instance_count
  target_group_arn = aws_lb_target_group.app_tg.arn
  target_id        = aws_instance.app_server[count.index].id
  port             = 80
}

# Listener para el balanceador de carga
resource "aws_lb_listener" "app_listener" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = 80
  protocol          = "HTTP"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}

# Bucket S3 para almacenamiento
resource "aws_s3_bucket" "app_storage" {
  bucket = "${var.environment}-${var.app_storage_bucket_name}"
  
  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-${var.app_storage_bucket_name}"
    }
  )
}

# Configuración de cifrado para el bucket S3
resource "aws_s3_bucket_server_side_encryption_configuration" "app_storage_encryption" {
  bucket = aws_s3_bucket.app_storage.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configuración de versioning para el bucket S3
resource "aws_s3_bucket_versioning" "app_storage_versioning" {
  bucket = aws_s3_bucket.app_storage.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Configuración de bloqueo público para el bucket S3
resource "aws_s3_bucket_public_access_block" "app_storage_public_access" {
  bucket = aws_s3_bucket.app_storage.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Tabla DynamoDB para bloqueo de estado de Terraform
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "${var.environment}-terraform-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-terraform-locks"
    }
  )
}

# Bucket S3 para almacenar el estado de Terraform
resource "aws_s3_bucket" "terraform_state" {
  bucket = "${var.environment}-terraform-state-${var.aws_account_id}"
  
  tags = merge(
    var.tags,
    {
      Name = "${var.environment}-terraform-state-${var.aws_account_id}"
    }
  )
}

# Configuración de cifrado para el bucket de estado de Terraform
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state_encryption" {
  bucket = aws_s3_bucket.terraform_state.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Configuración de versioning para el bucket de estado de Terraform
resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
  bucket = aws_s3_bucket.terraform_state.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

# Configuración de bloqueo público para el bucket de estado de Terraform
resource "aws_s3_bucket_public_access_block" "terraform_state_public_access" {
  bucket = aws_s3_bucket.terraform_state.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

