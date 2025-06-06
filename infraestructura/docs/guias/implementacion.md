# Guía de Implementación: Gestión de Infraestructura Tecnológica

Esta guía proporciona instrucciones detalladas para implementar la solución de gestión de infraestructura tecnológica en entornos on-premise y en la nube.

## Índice

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación de Herramientas](#instalación-de-herramientas)
3. [Configuración Inicial](#configuración-inicial)
4. [Despliegue de Infraestructura](#despliegue-de-infraestructura)
5. [Configuración de Servidores](#configuración-de-servidores)
6. [Configuración de Monitoreo](#configuración-de-monitoreo)
7. [Verificación y Pruebas](#verificación-y-pruebas)
8. [Mantenimiento y Operaciones](#mantenimiento-y-operaciones)
9. [Solución de Problemas](#solución-de-problemas)
10. [Referencias](#referencias)

## Requisitos Previos

### Credenciales y Accesos

Antes de comenzar, asegúrese de tener:

- Credenciales de AWS, Azure o GCP con permisos adecuados
- Claves SSH para acceso a servidores
- Permisos de administrador en sistemas on-premise

### Conocimientos Recomendados

- Conceptos básicos de redes y sistemas operativos
- Familiaridad con línea de comandos Linux
- Conocimientos básicos de Terraform y Ansible
- Comprensión de conceptos de nube (VPC, subredes, grupos de seguridad, etc.)

## Instalación de Herramientas

### Terraform

```bash
# En Ubuntu/Debian
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform

# Verificar instalación
terraform --version
```

### Ansible

```bash
# En Ubuntu/Debian
sudo apt-get update
sudo apt-get install ansible

# Verificar instalación
ansible --version
```

### AWS CLI (para despliegues en AWS)

```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configurar credenciales
aws configure
```

### Otras Herramientas

```bash
# Herramientas adicionales
sudo apt-get install git python3-pip jq

# Dependencias de Python
pip3 install boto3 netaddr
```

## Configuración Inicial

### Clonar el Repositorio

```bash
git clone https://github.com/usuario/gestion-infraestructura.git
cd gestion-infraestructura
```

### Configurar Variables de Entorno

Cree archivos de variables para cada entorno:

```bash
mkdir -p src/terraform/aws/environments/{development,staging,production}
cp src/terraform/aws/environments/example/terraform.tfvars src/terraform/aws/environments/development/terraform.tfvars
```

Edite el archivo `terraform.tfvars` con los valores adecuados para su entorno:

```hcl
aws_region = "us-east-1"
aws_account_id = "123456789012"
environment = "development"
vpc_name = "dev-vpc"
vpc_cidr = "10.0.0.0/16"
availability_zones = ["us-east-1a", "us-east-1b", "us-east-1c"]
private_subnet_cidrs = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
public_subnet_cidrs = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
app_instance_count = 2
app_instance_type = "t3.micro"
```

### Configurar Backend de Terraform

Cree un archivo de configuración de backend para cada entorno:

```bash
cat > src/terraform/aws/environments/development/backend.tfvars << EOF
bucket = "my-terraform-state-bucket"
key = "development/terraform.tfstate"
region = "us-east-1"
dynamodb_table = "terraform-locks"
encrypt = true
EOF
```

## Despliegue de Infraestructura

### Inicializar Terraform

```bash
cd src/terraform/aws
terraform init -backend-config=environments/development/backend.tfvars
```

### Validar Configuración

```bash
terraform validate
```

### Crear Plan de Despliegue

```bash
terraform plan -var-file=environments/development/terraform.tfvars -out=tfplan
```

### Aplicar Plan de Despliegue

```bash
terraform apply tfplan
```

### Verificar Recursos Creados

```bash
terraform output
```

## Configuración de Servidores

### Generar Inventario de Ansible

```bash
cd ../../
python3 scripts/generate_ansible_inventory.py src/terraform/aws/terraform_output.json src/ansible/inventories/development/hosts
```

### Ejecutar Playbook de Ansible

```bash
cd src/ansible
ansible-playbook -i inventories/development/hosts playbooks/configure-webservers.yml
```

### Verificar Configuración

```bash
ansible -i inventories/development/hosts webservers -m ping
```

## Configuración de Monitoreo

### Instalar Prometheus y Grafana

```bash
ansible-playbook -i inventories/development/hosts playbooks/install-monitoring.yml
```

### Configurar Alertas

Edite el archivo `src/ansible/templates/prometheus/alerts.yml.j2` para configurar las alertas según sus necesidades.

### Verificar Monitoreo

Acceda a la interfaz web de Grafana en `http://<ip-servidor-monitoreo>:3000` con las credenciales predeterminadas (admin/admin).

## Verificación y Pruebas

### Verificar Conectividad

```bash
ansible -i inventories/development/hosts all -m shell -a "ping -c 4 google.com"
```

### Verificar Servicios

```bash
ansible -i inventories/development/hosts webservers -m shell -a "systemctl status nginx"
```

### Pruebas de Carga

Utilice herramientas como Apache Benchmark o JMeter para realizar pruebas de carga:

```bash
ab -n 1000 -c 50 http://<ip-balanceador-carga>/
```

## Mantenimiento y Operaciones

### Actualizar Infraestructura

Para actualizar la infraestructura después de cambios en el código:

```bash
cd src/terraform/aws
terraform plan -var-file=environments/development/terraform.tfvars -out=tfplan
terraform apply tfplan
```

### Actualizar Configuración de Servidores

```bash
cd src/ansible
ansible-playbook -i inventories/development/hosts playbooks/configure-webservers.yml
```

### Respaldos

Los respaldos se configuran automáticamente y se ejecutan diariamente a las 3:00 AM. Los archivos de respaldo se almacenan en `/var/backups/webapp/`.

### Rotación de Logs

Los logs se rotan automáticamente utilizando logrotate. La configuración se encuentra en `/etc/logrotate.d/nginx`.

## Solución de Problemas

### Problemas Comunes

#### Error de Conexión SSH

```
UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh", "unreachable": true}
```

**Solución**: Verifique que las claves SSH estén correctamente configuradas y que los grupos de seguridad permitan el tráfico SSH.

#### Error de Permisos

```
"msg": "Permission denied"
```

**Solución**: Verifique que el usuario de Ansible tenga permisos sudo en los servidores.

#### Error de Terraform

```
Error: Error creating VPC: VpcLimitExceeded: The maximum number of VPCs has been reached.
```

**Solución**: Elimine VPCs no utilizadas o solicite un aumento de límite a AWS.

### Herramientas de Diagnóstico

- **Logs de Terraform**: Se encuentran en el directorio `.terraform/` y en la salida de la consola.
- **Logs de Ansible**: Utilice la opción `-v` para aumentar la verbosidad (`-v`, `-vv`, `-vvv`).
- **Logs del Sistema**: Revise `/var/log/syslog` y `/var/log/nginx/error.log` para problemas específicos.

## Referencias

1. [Documentación de Terraform](https://www.terraform.io/docs)
2. [Documentación de Ansible](https://docs.ansible.com)
3. [Documentación de AWS](https://docs.aws.amazon.com)
4. [Mejores Prácticas de Infraestructura como Código](https://www.hashicorp.com/resources/what-is-infrastructure-as-code)
5. [Guía de Seguridad para AWS](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)

