# Variables para el módulo de VPC

variable "vpc_name" {
  description = "Nombre de la VPC"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block para la VPC"
  type        = string
}

variable "azs" {
  description = "Lista de zonas de disponibilidad"
  type        = list(string)
}

variable "private_subnets" {
  description = "Lista de CIDR blocks para subredes privadas"
  type        = list(string)
}

variable "public_subnets" {
  description = "Lista de CIDR blocks para subredes públicas"
  type        = list(string)
}

variable "enable_nat_gateway" {
  description = "Habilitar NAT Gateway para subredes privadas"
  type        = bool
  default     = true
}

variable "single_nat_gateway" {
  description = "Usar un solo NAT Gateway para todas las subredes privadas"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags comunes para todos los recursos"
  type        = map(string)
  default     = {}
}

