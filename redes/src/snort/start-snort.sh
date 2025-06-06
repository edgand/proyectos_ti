#!/bin/bash
# Script para iniciar Snort IDS en modo de detección

# Variables
INTERFACE=$1
CONFIG_FILE="/etc/snort/snort.conf"
CONFIG_FILE_SNORT3="/etc/snort/snort.lua"
LOG_DIR="/var/log/snort"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
LOG_FILE="${LOG_DIR}/snort-${TIMESTAMP}.log"
ALERT_FILE="${LOG_DIR}/alert-${TIMESTAMP}.log"
SNORT_USER="snort"
SNORT_GROUP="snort"

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

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 <interfaz> [opciones]"
    echo ""
    echo "Opciones:"
    echo "  -h, --help        Mostrar esta ayuda"
    echo "  -v, --verbose     Modo verboso"
    echo "  -d, --daemon      Ejecutar como demonio"
    echo "  -s, --snort3      Usar Snort 3 (por defecto se usa Snort 2 si está disponible)"
    echo "  -c, --config      Especificar archivo de configuración"
    echo "  -l, --log-dir     Especificar directorio de logs"
    echo ""
    echo "Ejemplos:"
    echo "  $0 eth0           # Iniciar Snort en la interfaz eth0"
    echo "  $0 eth0 -v        # Iniciar Snort en modo verboso"
    echo "  $0 eth0 -d        # Iniciar Snort como demonio"
    echo "  $0 eth0 -s        # Iniciar Snort 3"
    echo ""
    exit 0
}

# Verificar si se está ejecutando como root
if [ "$EUID" -ne 0 ]; then
    print_error "Este script debe ejecutarse como root o con sudo"
    exit 1
fi

# Verificar argumentos
if [ -z "$INTERFACE" ] || [ "$INTERFACE" == "-h" ] || [ "$INTERFACE" == "--help" ]; then
    show_help
fi

# Procesar opciones
VERBOSE=0
DAEMON=0
USE_SNORT3=0
CUSTOM_CONFIG=""
CUSTOM_LOG_DIR=""

shift
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -h|--help)
            show_help
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        -d|--daemon)
            DAEMON=1
            shift
            ;;
        -s|--snort3)
            USE_SNORT3=1
            shift
            ;;
        -c|--config)
            CUSTOM_CONFIG="$2"
            shift
            shift
            ;;
        -l|--log-dir)
            CUSTOM_LOG_DIR="$2"
            shift
            shift
            ;;
        *)
            print_error "Opción desconocida: $1"
            show_help
            ;;
    esac
done

# Verificar que la interfaz existe
if ! ip link show "$INTERFACE" &> /dev/null; then
    print_error "La interfaz $INTERFACE no existe"
    echo "Interfaces disponibles:"
    ip -o link show | awk -F': ' '{print $2}'
    exit 1
fi

# Verificar si Snort está instalado
if [ $USE_SNORT3 -eq 1 ]; then
    if ! command -v snort -V | grep -q "Version 3"; then
        print_error "Snort 3 no está instalado o no está en el PATH"
        exit 1
    fi
    
    # Usar configuración personalizada o la predeterminada
    if [ -n "$CUSTOM_CONFIG" ]; then
        CONFIG_FILE_SNORT3="$CUSTOM_CONFIG"
    fi
    
    # Verificar que el archivo de configuración existe
    if [ ! -f "$CONFIG_FILE_SNORT3" ]; then
        print_error "El archivo de configuración $CONFIG_FILE_SNORT3 no existe"
        exit 1
    fi
    
    # Usar directorio de logs personalizado o el predeterminado
    if [ -n "$CUSTOM_LOG_DIR" ]; then
        LOG_DIR="$CUSTOM_LOG_DIR"
    fi
    
    # Crear directorio de logs si no existe
    mkdir -p "$LOG_DIR"
    chmod -R 5775 "$LOG_DIR"
    
    # Construir comando de Snort 3
    SNORT_CMD="snort -c $CONFIG_FILE_SNORT3 -i $INTERFACE -l $LOG_DIR"
    
    if [ $VERBOSE -eq 1 ]; then
        SNORT_CMD="$SNORT_CMD -v"
    fi
    
    if [ $DAEMON -eq 1 ]; then
        SNORT_CMD="$SNORT_CMD -D"
        print_message "Iniciando Snort 3 como demonio en la interfaz $INTERFACE..."
    else
        print_message "Iniciando Snort 3 en la interfaz $INTERFACE..."
    fi
    
else
    if ! command -v snort &> /dev/null; then
        print_error "Snort no está instalado o no está en el PATH"
        exit 1
    fi
    
    # Usar configuración personalizada o la predeterminada
    if [ -n "$CUSTOM_CONFIG" ]; then
        CONFIG_FILE="$CUSTOM_CONFIG"
    fi
    
    # Verificar que el archivo de configuración existe
    if [ ! -f "$CONFIG_FILE" ]; then
        print_error "El archivo de configuración $CONFIG_FILE no existe"
        exit 1
    fi
    
    # Usar directorio de logs personalizado o el predeterminado
    if [ -n "$CUSTOM_LOG_DIR" ]; then
        LOG_DIR="$CUSTOM_LOG_DIR"
    fi
    
    # Crear directorio de logs si no existe
    mkdir -p "$LOG_DIR"
    chmod -R 5775 "$LOG_DIR"
    
    # Construir comando de Snort 2
    SNORT_CMD="snort -c $CONFIG_FILE -i $INTERFACE -l $LOG_DIR"
    
    if [ $VERBOSE -eq 1 ]; then
        SNORT_CMD="$SNORT_CMD -v"
    else
        SNORT_CMD="$SNORT_CMD -q"
    fi
    
    # Añadir opciones de usuario y grupo
    if getent passwd $SNORT_USER > /dev/null 2>&1; then
        SNORT_CMD="$SNORT_CMD -u $SNORT_USER -g $SNORT_GROUP"
    fi
    
    if [ $DAEMON -eq 1 ]; then
        SNORT_CMD="$SNORT_CMD -D"
        print_message "Iniciando Snort 2 como demonio en la interfaz $INTERFACE..."
    else
        SNORT_CMD="$SNORT_CMD -A console"
        print_message "Iniciando Snort 2 en la interfaz $INTERFACE..."
    fi
fi

# Mostrar comando
if [ $VERBOSE -eq 1 ]; then
    print_message "Ejecutando: $SNORT_CMD"
fi

# Ejecutar Snort
eval $SNORT_CMD

# Verificar si se inició correctamente
if [ $? -eq 0 ]; then
    if [ $DAEMON -eq 1 ]; then
        print_message "Snort iniciado correctamente como demonio"
        echo "Para ver el estado: ps aux | grep snort"
        echo "Para detener: pkill -f snort"
        echo "Logs en: $LOG_DIR"
    else
        print_message "Snort iniciado correctamente"
        echo "Presione Ctrl+C para detener"
    fi
else
    print_error "Error al iniciar Snort"
    exit 1
fi

exit 0

