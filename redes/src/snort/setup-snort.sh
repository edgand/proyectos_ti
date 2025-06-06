#!/bin/bash
# Script para instalar y configurar Snort IDS

# Variables
SNORT_VERSION="3"  # Opciones: 2 o 3
HOME_NET="192.168.0.0/24"  # Ajustar a la red local
RULES_URL="https://www.snort.org/downloads/community/snort3-community-rules.tar.gz"
LOG_DIR="/var/log/snort"
RULES_DIR="/etc/snort/rules"
CONFIG_DIR="/etc/snort"

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
print_message "Iniciando instalación de Snort $SNORT_VERSION"
print_message "Este script instalará:"
echo "  - Snort IDS"
echo "  - Dependencias necesarias"
echo "  - Reglas de comunidad"
echo ""
echo "Red local configurada: $HOME_NET"
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
apt-get install -y build-essential libpcap-dev libpcre3-dev libnet1-dev zlib1g-dev luajit hwloc libdnet-dev libdumbnet-dev bison flex liblzma-dev openssl libssl-dev pkg-config libhwloc-dev cmake cpputest libsqlite3-dev uuid-dev libcmocka-dev libnetfilter-queue-dev libmnl-dev autotools-dev libluajit-5.1-dev libunwind-dev
check_status "Dependencias instaladas" "Error al instalar dependencias"

if [ "$SNORT_VERSION" == "2" ]; then
    # Instalar Snort 2
    print_message "Instalando Snort 2..."
    apt-get install -y snort
    check_status "Snort 2 instalado" "Error al instalar Snort 2"
    
    # Configurar Snort 2
    print_message "Configurando Snort 2..."
    
    # Hacer backup del archivo de configuración original
    cp /etc/snort/snort.conf /etc/snort/snort.conf.bak
    
    # Configurar la red local
    sed -i "s/ipvar HOME_NET any/ipvar HOME_NET $HOME_NET/g" /etc/snort/snort.conf
    
    # Descargar reglas de comunidad
    print_message "Descargando reglas de comunidad..."
    mkdir -p /etc/snort/rules/community
    cd /etc/snort/rules/community
    wget https://www.snort.org/downloads/community/community-rules.tar.gz -O community-rules.tar.gz
    tar -xzf community-rules.tar.gz
    rm community-rules.tar.gz
    
    # Incluir reglas de comunidad en la configuración
    echo "include \$RULE_PATH/community/community.rules" >> /etc/snort/snort.conf
    
    # Crear directorios de logs
    mkdir -p /var/log/snort
    chmod -R 5775 /var/log/snort
    
    # Verificar configuración
    print_message "Verificando configuración de Snort..."
    snort -T -c /etc/snort/snort.conf
    check_status "Configuración de Snort verificada" "Error en la configuración de Snort"
    
else
    # Instalar Snort 3
    print_message "Instalando Snort 3..."
    
    # Crear directorio temporal
    mkdir -p /tmp/snort_src
    cd /tmp/snort_src
    
    # Instalar libdaq
    print_message "Instalando libdaq..."
    git clone https://github.com/snort3/libdaq.git
    cd libdaq
    ./bootstrap
    ./configure
    make
    make install
    check_status "libdaq instalado" "Error al instalar libdaq"
    
    # Actualizar cache de bibliotecas compartidas
    ldconfig
    
    # Instalar Snort 3
    cd /tmp/snort_src
    print_message "Descargando Snort 3..."
    git clone https://github.com/snort3/snort3.git
    cd snort3
    
    print_message "Compilando Snort 3..."
    ./configure_cmake.sh --prefix=/usr/local --enable-tcmalloc
    cd build
    make
    make install
    check_status "Snort 3 instalado" "Error al instalar Snort 3"
    
    # Actualizar cache de bibliotecas compartidas
    ldconfig
    
    # Crear directorios de configuración
    print_message "Creando directorios de configuración..."
    mkdir -p $CONFIG_DIR/rules
    mkdir -p $LOG_DIR
    chmod -R 5775 $LOG_DIR
    
    # Descargar reglas de comunidad
    print_message "Descargando reglas de comunidad..."
    cd $RULES_DIR
    wget $RULES_URL -O snort3-community-rules.tar.gz
    tar -xzf snort3-community-rules.tar.gz
    rm snort3-community-rules.tar.gz
    
    # Crear archivo de configuración básico
    print_message "Creando archivo de configuración básico..."
    cat > $CONFIG_DIR/snort.lua << EOF
-- Snort 3 Configuration
-- Basic configuration file

-- Home network definition
HOME_NET = '$HOME_NET'
EXTERNAL_NET = '!$HOME_NET'

-- Path variables
RULE_PATH = '$RULES_DIR'

-- Configure inspection
detection = {
    pcre_match_limit = 3500,
    pcre_match_limit_recursion = 3500,
}

-- Configure logging
alert_csv = {
    file = true,
    fields = 'timestamp,msg,proto,src,srcport,dst,dstport',
    limit = 10,
}

-- Include rules
ips = {
    include = RULE_PATH .. '/snort3-community-rules/snort3-community.rules',
    variables = {
        nets = {
            HOME_NET = HOME_NET,
            EXTERNAL_NET = EXTERNAL_NET,
        },
        ports = {
            HTTP_PORTS = '80',
            SSH_PORTS = '22',
        },
    },
}
EOF
    
    # Verificar configuración
    print_message "Verificando configuración de Snort 3..."
    snort -c $CONFIG_DIR/snort.lua --warn-all
    check_status "Configuración de Snort 3 verificada" "Error en la configuración de Snort 3"
fi

# Crear script de inicio
print_message "Creando script de inicio..."
cat > /usr/local/bin/start-snort.sh << EOF
#!/bin/bash
# Script para iniciar Snort IDS

INTERFACE=\$1

if [ -z "\$INTERFACE" ]; then
    echo "Error: Debe especificar una interfaz de red"
    echo "Uso: \$0 <interfaz>"
    exit 1
fi

# Verificar que la interfaz existe
if ! ip link show \$INTERFACE &> /dev/null; then
    echo "Error: La interfaz \$INTERFACE no existe"
    echo "Interfaces disponibles:"
    ip -o link show | awk -F': ' '{print \$2}'
    exit 1
fi

echo "Iniciando Snort en la interfaz \$INTERFACE..."
EOF

if [ "$SNORT_VERSION" == "2" ]; then
    cat >> /usr/local/bin/start-snort.sh << EOF
snort -A console -q -u snort -g snort -c /etc/snort/snort.conf -i \$INTERFACE
EOF
else
    cat >> /usr/local/bin/start-snort.sh << EOF
snort -c $CONFIG_DIR/snort.lua -i \$INTERFACE -l $LOG_DIR -D
EOF
fi

chmod +x /usr/local/bin/start-snort.sh

# Crear script para detener Snort
print_message "Creando script para detener Snort..."
cat > /usr/local/bin/stop-snort.sh << EOF
#!/bin/bash
# Script para detener Snort IDS

echo "Deteniendo Snort..."
pkill -f snort
echo "Snort detenido"
EOF

chmod +x /usr/local/bin/stop-snort.sh

# Crear script para ver alertas
print_message "Creando script para ver alertas..."
cat > /usr/local/bin/view-alerts.sh << EOF
#!/bin/bash
# Script para ver alertas de Snort

echo "Mostrando últimas alertas de Snort..."
if [ "$SNORT_VERSION" == "2" ]; then
    tail -f /var/log/snort/alert
else
    find $LOG_DIR -name "*.txt" | xargs tail -f
fi
EOF

chmod +x /usr/local/bin/view-alerts.sh

# Mostrar información final
print_message "Instalación de Snort $SNORT_VERSION completada con éxito"
echo ""
echo "Para iniciar Snort:"
echo "  sudo /usr/local/bin/start-snort.sh <interfaz>"
echo ""
echo "Para detener Snort:"
echo "  sudo /usr/local/bin/stop-snort.sh"
echo ""
echo "Para ver alertas:"
echo "  sudo /usr/local/bin/view-alerts.sh"
echo ""
echo "Directorio de logs: $LOG_DIR"
echo "Directorio de reglas: $RULES_DIR"
echo ""

exit 0

