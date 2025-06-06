# Outputs para la configuración de AWS

output "vpc_id" {
  description = "ID de la VPC creada"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block de la VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "Lista de IDs de subredes privadas"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "Lista de IDs de subredes públicas"
  value       = module.vpc.public_subnets
}

output "nat_public_ips" {
  description = "Lista de IPs públicas de los NAT Gateways"
  value       = module.vpc.nat_public_ips
}

output "app_security_group_id" {
  description = "ID del grupo de seguridad para la aplicación"
  value       = aws_security_group.app_sg.id
}

output "app_instance_ids" {
  description = "Lista de IDs de instancias EC2 de la aplicación"
  value       = aws_instance.app_server[*].id
}

output "app_instance_public_ips" {
  description = "Lista de IPs públicas de instancias EC2 de la aplicación"
  value       = aws_instance.app_server[*].public_ip
}

output "app_instance_private_ips" {
  description = "Lista de IPs privadas de instancias EC2 de la aplicación"
  value       = aws_instance.app_server[*].private_ip
}

output "app_lb_dns_name" {
  description = "DNS name del balanceador de carga de la aplicación"
  value       = aws_lb.app_lb.dns_name
}

output "app_lb_zone_id" {
  description = "Zone ID del balanceador de carga de la aplicación"
  value       = aws_lb.app_lb.zone_id
}

output "app_storage_bucket_id" {
  description = "ID del bucket S3 para almacenamiento de la aplicación"
  value       = aws_s3_bucket.app_storage.id
}

output "app_storage_bucket_arn" {
  description = "ARN del bucket S3 para almacenamiento de la aplicación"
  value       = aws_s3_bucket.app_storage.arn
}

output "terraform_state_bucket_id" {
  description = "ID del bucket S3 para el estado de Terraform"
  value       = aws_s3_bucket.terraform_state.id
}

output "terraform_locks_table_name" {
  description = "Nombre de la tabla DynamoDB para bloqueos de Terraform"
  value       = aws_dynamodb_table.terraform_locks.name
}

output "terraform_locks_table_arn" {
  description = "ARN de la tabla DynamoDB para bloqueos de Terraform"
  value       = aws_dynamodb_table.terraform_locks.arn
}

