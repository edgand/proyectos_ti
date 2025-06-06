#!/bin/bash
# Script para configurar Zabbix Server y Agent

# Variables
ZABBIX_VERSION="6.0"
DB_NAME="zabbix"
DB_USER="zabbix"
DB_PASSWORD="zabbix_password"
ZABBIX_SERVER_IP="127.0.0.1"
TIMEZONE="America/Mexico_City"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Función para mostrar mensajes
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Función para verificar si un comando fue exitoso
check_status() {
    if [ $? -eq 0 ]; then
        print_message "$1"
    else
        print_error "$2"
        exit 1
    fi
}

# Verificar si se está ejecutando como root
if [ "$EUID" -ne 0 ]; then
    print_error "Este script debe ejecutarse como root o con sudo"
    exit 1
fi

# Mostrar información de instalación
print_message "Iniciando instalación de Zabbix $ZABBIX_VERSION"
print_message "Este script instalará:"
echo "  - Zabbix Server"
echo "  - Zabbix Frontend (Apache)"
echo "  - Zabbix Agent"
echo "  - MySQL Server"
echo ""

# Preguntar si desea continuar
read -p "¿Desea continuar con la instalación? (s/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    print_message "Instalación cancelada"
    exit 0
fi

# Actualizar repositorios
print_message "Actualizando repositorios..."
apt-get update
check_status "Repositorios actualizados" "Error al actualizar repositorios"

# Instalar dependencias
print_message "Instalando dependencias..."
apt-get install -y wget gnupg2 software-properties-common
check_status "Dependencias instaladas" "Error al instalar dependencias"

# Añadir repositorio de Zabbix
print_message "Añadiendo repositorio de Zabbix..."
wget https://repo.zabbix.com/zabbix/${ZABBIX_VERSION}/ubuntu/pool/main/z/zabbix-release/zabbix-release_${ZABBIX_VERSION}-1+ubuntu$(lsb_release -rs)_all.deb
check_status "Paquete de repositorio descargado" "Error al descargar paquete de repositorio"

dpkg -i zabbix-release_${ZABBIX_VERSION}-1+ubuntu$(lsb_release -rs)_all.deb
check_status "Repositorio de Zabbix añadido" "Error al añadir repositorio de Zabbix"

apt-get update
check_status "Repositorios actualizados" "Error al actualizar repositorios"

# Instalar MySQL Server
print_message "Instalando MySQL Server..."
apt-get install -y mysql-server
check_status "MySQL Server instalado" "Error al instalar MySQL Server"

# Configurar MySQL para Zabbix
print_message "Configurando MySQL para Zabbix..."
mysql -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8 COLLATE utf8_bin;"
mysql -e "CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';"
mysql -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"
check_status "Base de datos y usuario MySQL creados" "Error al configurar MySQL"

# Instalar Zabbix Server y Frontend
print_message "Instalando Zabbix Server, Frontend y Agent..."
apt-get install -y zabbix-server-mysql zabbix-frontend-php zabbix-apache-conf zabbix-sql-scripts zabbix-agent
check_status "Zabbix instalado" "Error al instalar Zabbix"

# Importar esquema inicial
print_message "Importando esquema inicial a la base de datos..."
zcat /usr/share/doc/zabbix-sql-scripts/mysql/server.sql.gz | mysql -u $DB_USER -p$DB_PASSWORD $DB_NAME
check_status "Esquema inicial importado" "Error al importar esquema inicial"

# Configurar Zabbix Server
print_message "Configurando Zabbix Server..."
sed -i "s/# DBPassword=/DBPassword=$DB_PASSWORD/g" /etc/zabbix/zabbix_server.conf
check_status "Zabbix Server configurado" "Error al configurar Zabbix Server"

# Configurar PHP para Zabbix Frontend
print_message "Configurando PHP para Zabbix Frontend..."
sed -i "s/;date.timezone =/date.timezone = $TIMEZONE/g" /etc/php/*/apache2/php.ini
check_status "PHP configurado" "Error al configurar PHP"

# Configurar Zabbix Agent
print_message "Configurando Zabbix Agent..."
sed -i "s/Server=127.0.0.1/Server=$ZABBIX_SERVER_IP/g" /etc/zabbix/zabbix_agentd.conf
sed -i "s/ServerActive=127.0.0.1/ServerActive=$ZABBIX_SERVER_IP/g" /etc/zabbix/zabbix_agentd.conf
sed -i "s/Hostname=Zabbix server/Hostname=$(hostname)/g" /etc/zabbix/zabbix_agentd.conf
check_status "Zabbix Agent configurado" "Error al configurar Zabbix Agent"

# Reiniciar servicios
print_message "Reiniciando servicios..."
systemctl restart zabbix-server zabbix-agent apache2
systemctl enable zabbix-server zabbix-agent apache2
check_status "Servicios reiniciados y habilitados" "Error al reiniciar servicios"

# Verificar estado de los servicios
print_message "Verificando estado de los servicios..."
systemctl status zabbix-server --no-pager
systemctl status zabbix-agent --no-pager
systemctl status apache2 --no-pager

# Mostrar información de acceso
IP_ADDRESS=$(hostname -I | awk '{print $1}')
print_message "Instalación completada con éxito"
echo ""
echo "Acceda a la interfaz web de Zabbix en: http://$IP_ADDRESS/zabbix"
echo "Credenciales por defecto:"
echo "  Usuario: Admin"
echo "  Contraseña: zabbix"
echo ""
echo "Recuerde cambiar la contraseña después de iniciar sesión"
echo ""
echo "Para añadir hosts a monitorear, vaya a Configuration -> Hosts -> Create host"
echo ""

exit 0

