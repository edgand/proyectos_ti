# Outputs para el módulo de VPC

output "vpc_id" {
  description = "ID de la VPC creada"
  value       = aws_vpc.this.id
}

output "vpc_cidr_block" {
  description = "CIDR block de la VPC"
  value       = aws_vpc.this.cidr_block
}

output "private_subnets" {
  description = "Lista de IDs de subredes privadas"
  value       = aws_subnet.private[*].id
}

output "public_subnets" {
  description = "Lista de IDs de subredes públicas"
  value       = aws_subnet.public[*].id
}

output "private_subnet_cidrs" {
  description = "Lista de CIDR blocks de subredes privadas"
  value       = aws_subnet.private[*].cidr_block
}

output "public_subnet_cidrs" {
  description = "Lista de CIDR blocks de subredes públicas"
  value       = aws_subnet.public[*].cidr_block
}

output "nat_public_ips" {
  description = "Lista de IPs públicas de los NAT Gateways"
  value       = aws_eip.nat[*].public_ip
}

output "public_route_table_id" {
  description = "ID de la tabla de rutas pública"
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "Lista de IDs de tablas de rutas privadas"
  value       = aws_route_table.private[*].id
}

output "nat_gateway_ids" {
  description = "Lista de IDs de NAT Gateways"
  value       = aws_nat_gateway.this[*].id
}

output "internet_gateway_id" {
  description = "ID del Internet Gateway"
  value       = aws_internet_gateway.this.id
}

