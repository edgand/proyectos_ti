# Variables para la configuración de AWS

variable "aws_region" {
  description = "Región de AWS donde se desplegarán los recursos"
  type        = string
  default     = "us-east-1"
}

variable "aws_account_id" {
  description = "ID de la cuenta de AWS"
  type        = string
  default     = "123456789012"
}

variable "environment" {
  description = "Entorno de despliegue (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "vpc_name" {
  description = "Nombre de la VPC"
  type        = string
  default     = "main-vpc"
}

variable "vpc_cidr" {
  description = "CIDR block para la VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Lista de zonas de disponibilidad"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "private_subnet_cidrs" {
  description = "Lista de CIDR blocks para subredes privadas"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "Lista de CIDR blocks para subredes públicas"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
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

variable "app_instance_count" {
  description = "Número de instancias EC2 para la aplicación"
  type        = number
  default     = 2
}

variable "app_instance_ami" {
  description = "AMI para instancias EC2 de la aplicación"
  type        = string
  default     = "ami-0c55b159cbfafe1f0" # Ubuntu 20.04 LTS (ejemplo)
}

variable "app_instance_type" {
  description = "Tipo de instancia EC2 para la aplicación"
  type        = string
  default     = "t3.micro"
}

variable "app_instance_volume_size" {
  description = "Tamaño del volumen raíz para instancias EC2 de la aplicación (en GB)"
  type        = number
  default     = 20
}

variable "key_name" {
  description = "Nombre del par de claves SSH para acceder a las instancias EC2"
  type        = string
  default     = "app-key-pair"
}

variable "app_storage_bucket_name" {
  description = "Nombre del bucket S3 para almacenamiento de la aplicación"
  type        = string
  default     = "app-storage"
}

variable "tags" {
  description = "Tags comunes para todos los recursos"
  type        = map(string)
  default     = {
    Project     = "InfrastructureManagement"
    ManagedBy   = "Terraform"
    Environment = "Development"
    Owner       = "InfraTeam"
  }
}

