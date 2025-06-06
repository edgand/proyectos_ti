#!/bin/bash
# Script para automatizar el despliegue de infraestructura

# Variables
TERRAFORM_DIR="../src/terraform/aws"
ANSIBLE_DIR="../src/ansible"
ENVIRONMENT=$1
LOG_FILE="deploy-$(date +%Y-%m-%d-%H-%M-%S).log"

# Función para registrar mensajes
log_message() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" | tee -a ${LOG_FILE}
}

# Verificar que se proporcionó un entorno
if [ -z "${ENVIRONMENT}" ]; then
    log_message "Error: Debe especificar un entorno (development, staging, production)"
    echo "Uso: $0 <environment>"
    exit 1
fi

# Verificar que el entorno es válido
if [[ "${ENVIRONMENT}" != "development" && "${ENVIRONMENT}" != "staging" && "${ENVIRONMENT}" != "production" ]]; then
    log_message "Error: El entorno debe ser development, staging o production"
    echo "Uso: $0 <environment>"
    exit 1
fi

log_message "Iniciando despliegue de infraestructura para el entorno ${ENVIRONMENT}..."

# Verificar que Terraform está instalado
if ! command -v terraform &> /dev/null; then
    log_message "Error: Terraform no está instalado"
    exit 1
fi

# Verificar que Ansible está instalado
if ! command -v ansible-playbook &> /dev/null; then
    log_message "Error: Ansible no está instalado"
    exit 1
fi

# Crear directorio de variables de entorno si no existe
mkdir -p ${TERRAFORM_DIR}/environments/${ENVIRONMENT}

# Copiar archivo de variables de entorno si no existe
if [ ! -f "${TERRAFORM_DIR}/environments/${ENVIRONMENT}/terraform.tfvars" ]; then
    log_message "Creando archivo de variables para el entorno ${ENVIRONMENT}..."
    cp ${TERRAFORM_DIR}/environments/example/terraform.tfvars ${TERRAFORM_DIR}/environments/${ENVIRONMENT}/terraform.tfvars
    log_message "Por favor, edite el archivo ${TERRAFORM_DIR}/environments/${ENVIRONMENT}/terraform.tfvars con los valores adecuados"
    exit 1
fi

# Inicializar Terraform
log_message "Inicializando Terraform..."
cd ${TERRAFORM_DIR}
terraform init -backend-config=environments/${ENVIRONMENT}/backend.tfvars

if [ $? -ne 0 ]; then
    log_message "Error: No se pudo inicializar Terraform"
    exit 1
fi

# Validar configuración de Terraform
log_message "Validando configuración de Terraform..."
terraform validate

if [ $? -ne 0 ]; then
    log_message "Error: La configuración de Terraform no es válida"
    exit 1
fi

# Crear plan de Terraform
log_message "Creando plan de Terraform..."
terraform plan -var-file=environments/${ENVIRONMENT}/terraform.tfvars -out=tfplan

if [ $? -ne 0 ]; then
    log_message "Error: No se pudo crear el plan de Terraform"
    exit 1
fi

# Preguntar al usuario si desea aplicar el plan
read -p "¿Desea aplicar el plan de Terraform? (s/n): " APPLY_PLAN

if [[ "${APPLY_PLAN}" == "s" || "${APPLY_PLAN}" == "S" ]]; then
    # Aplicar plan de Terraform
    log_message "Aplicando plan de Terraform..."
    terraform apply tfplan
    
    if [ $? -ne 0 ]; then
        log_message "Error: No se pudo aplicar el plan de Terraform"
        exit 1
    fi
else
    log_message "Despliegue de infraestructura cancelado por el usuario"
    exit 0
fi

# Obtener información de salida de Terraform
log_message "Obteniendo información de salida de Terraform..."
terraform output -json > terraform_output.json

if [ $? -ne 0 ]; then
    log_message "Error: No se pudo obtener la información de salida de Terraform"
    exit 1
fi

# Generar inventario dinámico para Ansible
log_message "Generando inventario dinámico para Ansible..."
python3 ../scripts/generate_ansible_inventory.py terraform_output.json ${ANSIBLE_DIR}/inventories/${ENVIRONMENT}/hosts

if [ $? -ne 0 ]; then
    log_message "Error: No se pudo generar el inventario dinámico para Ansible"
    exit 1
fi

# Ejecutar playbook de Ansible para configurar servidores
log_message "Ejecutando playbook de Ansible para configurar servidores..."
cd ${ANSIBLE_DIR}
ansible-playbook -i inventories/${ENVIRONMENT}/hosts playbooks/configure-webservers.yml

if [ $? -ne 0 ]; then
    log_message "Error: No se pudo ejecutar el playbook de Ansible"
    exit 1
fi

log_message "Despliegue de infraestructura completado con éxito"

exit 0

