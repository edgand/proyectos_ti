#!/bin/bash
# Script para analizar el rendimiento de la red

# Variables
INTERFACE=$1
DURATION=$2
OUTPUT_DIR="$(dirname "$0")/reports"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
REPORT_FILE="${OUTPUT_DIR}/network-performance-${TIMESTAMP}.txt"

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 <interfaz> [duración_en_segundos]"
    echo ""
    echo "Ejemplos:"
    echo "  $0 eth0            # Analiza el rendimiento de la interfaz eth0"
    echo "  $0 eth0 60         # Analiza el rendimiento durante 60 segundos"
    echo ""
    echo "Este script recopila información sobre el rendimiento de la red utilizando"
    echo "varias herramientas como iperf, ping, traceroute, etc."
    exit 1
}

# Verificar argumentos
if [ -z "$INTERFACE" ]; then
    show_help
fi

# Si no se especifica duración, usar 30 segundos
if [ -z "$DURATION" ]; then
    DURATION=30
fi

# Crear directorio de reportes si no existe
mkdir -p "$OUTPUT_DIR"

# Verificar que las herramientas necesarias están instaladas
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "Advertencia: $1 no está instalado. Algunas pruebas se omitirán."
        return 1
    fi
    return 0
}

# Verificar herramientas
TOOLS_MISSING=0
for tool in ip ifconfig ping traceroute mtr netstat ss iperf3; do
    if ! check_tool $tool; then
        TOOLS_MISSING=1
    fi
done

# Verificar que la interfaz existe
if ! ip link show "$INTERFACE" &> /dev/null; then
    echo "Error: La interfaz $INTERFACE no existe"
    echo "Interfaces disponibles:"
    ip -o link show | awk -F': ' '{print $2}'
    exit 1
fi

# Iniciar reporte
echo "Iniciando análisis de rendimiento de red:"
echo "  Interfaz: $INTERFACE"
echo "  Duración: $DURATION segundos"
echo "  Archivo de reporte: $REPORT_FILE"
echo ""

# Función para añadir una sección al reporte
add_section() {
    echo "" >> "$REPORT_FILE"
    echo "===== $1 =====" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
}

# Iniciar el archivo de reporte
echo "REPORTE DE RENDIMIENTO DE RED" > "$REPORT_FILE"
echo "Fecha: $(date)" >> "$REPORT_FILE"
echo "Interfaz: $INTERFACE" >> "$REPORT_FILE"
echo "Duración: $DURATION segundos" >> "$REPORT_FILE"
echo "Host: $(hostname)" >> "$REPORT_FILE"

# Información del sistema
add_section "INFORMACIÓN DEL SISTEMA"
echo "Sistema operativo: $(uname -a)" >> "$REPORT_FILE"
echo "CPU: $(grep "model name" /proc/cpuinfo | head -1 | cut -d: -f2 | sed 's/^[ \t]*//')" >> "$REPORT_FILE"
echo "Memoria: $(free -h | grep Mem | awk '{print $2}')" >> "$REPORT_FILE"

# Información de la interfaz
add_section "INFORMACIÓN DE LA INTERFAZ"
if command -v ifconfig &> /dev/null; then
    ifconfig "$INTERFACE" >> "$REPORT_FILE"
else
    ip addr show "$INTERFACE" >> "$REPORT_FILE"
fi

# Estadísticas de la interfaz
add_section "ESTADÍSTICAS DE LA INTERFAZ"
if [ -f "/sys/class/net/$INTERFACE/statistics/rx_bytes" ]; then
    RX_BYTES_START=$(cat /sys/class/net/$INTERFACE/statistics/rx_bytes)
    TX_BYTES_START=$(cat /sys/class/net/$INTERFACE/statistics/tx_bytes)
    RX_PACKETS_START=$(cat /sys/class/net/$INTERFACE/statistics/rx_packets)
    TX_PACKETS_START=$(cat /sys/class/net/$INTERFACE/statistics/tx_packets)
    RX_ERRORS_START=$(cat /sys/class/net/$INTERFACE/statistics/rx_errors)
    TX_ERRORS_START=$(cat /sys/class/net/$INTERFACE/statistics/tx_errors)
    
    echo "Esperando $DURATION segundos para recopilar estadísticas..."
    sleep $DURATION
    
    RX_BYTES_END=$(cat /sys/class/net/$INTERFACE/statistics/rx_bytes)
    TX_BYTES_END=$(cat /sys/class/net/$INTERFACE/statistics/tx_bytes)
    RX_PACKETS_END=$(cat /sys/class/net/$INTERFACE/statistics/rx_packets)
    TX_PACKETS_END=$(cat /sys/class/net/$INTERFACE/statistics/tx_packets)
    RX_ERRORS_END=$(cat /sys/class/net/$INTERFACE/statistics/rx_errors)
    TX_ERRORS_END=$(cat /sys/class/net/$INTERFACE/statistics/tx_errors)
    
    RX_BYTES_DIFF=$((RX_BYTES_END - RX_BYTES_START))
    TX_BYTES_DIFF=$((TX_BYTES_END - TX_BYTES_START))
    RX_PACKETS_DIFF=$((RX_PACKETS_END - RX_PACKETS_START))
    TX_PACKETS_DIFF=$((TX_PACKETS_END - TX_PACKETS_START))
    RX_ERRORS_DIFF=$((RX_ERRORS_END - RX_ERRORS_START))
    TX_ERRORS_DIFF=$((TX_ERRORS_END - TX_ERRORS_START))
    
    RX_SPEED=$(echo "scale=2; $RX_BYTES_DIFF / $DURATION / 1024" | bc)
    TX_SPEED=$(echo "scale=2; $TX_BYTES_DIFF / $DURATION / 1024" | bc)
    
    echo "Bytes recibidos: $RX_BYTES_DIFF bytes ($RX_SPEED KB/s)" >> "$REPORT_FILE"
    echo "Bytes transmitidos: $TX_BYTES_DIFF bytes ($TX_SPEED KB/s)" >> "$REPORT_FILE"
    echo "Paquetes recibidos: $RX_PACKETS_DIFF" >> "$REPORT_FILE"
    echo "Paquetes transmitidos: $TX_PACKETS_DIFF" >> "$REPORT_FILE"
    echo "Errores de recepción: $RX_ERRORS_DIFF" >> "$REPORT_FILE"
    echo "Errores de transmisión: $TX_ERRORS_DIFF" >> "$REPORT_FILE"
else
    echo "No se pueden obtener estadísticas de la interfaz" >> "$REPORT_FILE"
fi

# Prueba de conectividad
add_section "PRUEBA DE CONECTIVIDAD"
if check_tool ping; then
    echo "Ping a Google DNS (8.8.8.8):" >> "$REPORT_FILE"
    ping -c 10 8.8.8.8 >> "$REPORT_FILE" 2>&1
    
    echo "" >> "$REPORT_FILE"
    echo "Ping a Cloudflare DNS (1.1.1.1):" >> "$REPORT_FILE"
    ping -c 10 1.1.1.1 >> "$REPORT_FILE" 2>&1
fi

# Prueba de ruta
add_section "PRUEBA DE RUTA"
if check_tool traceroute; then
    echo "Traceroute a Google DNS (8.8.8.8):" >> "$REPORT_FILE"
    traceroute -n 8.8.8.8 >> "$REPORT_FILE" 2>&1
fi

# Prueba MTR
add_section "PRUEBA MTR"
if check_tool mtr; then
    echo "MTR a Google DNS (8.8.8.8):" >> "$REPORT_FILE"
    mtr -r -c 10 8.8.8.8 >> "$REPORT_FILE" 2>&1
fi

# Conexiones de red
add_section "CONEXIONES DE RED"
if check_tool netstat; then
    echo "Conexiones establecidas:" >> "$REPORT_FILE"
    netstat -tunapl | grep ESTABLISHED >> "$REPORT_FILE" 2>&1
elif check_tool ss; then
    echo "Conexiones establecidas:" >> "$REPORT_FILE"
    ss -tunapl | grep ESTAB >> "$REPORT_FILE" 2>&1
fi

# Prueba de velocidad con iperf
add_section "PRUEBA DE VELOCIDAD (IPERF)"
if check_tool iperf3; then
    echo "Prueba de velocidad con iperf3 (si está disponible un servidor):" >> "$REPORT_FILE"
    echo "Nota: Esta prueba fallará si no hay un servidor iperf disponible." >> "$REPORT_FILE"
    iperf3 -c iperf.he.net -t 5 >> "$REPORT_FILE" 2>&1 || echo "No se pudo conectar a un servidor iperf" >> "$REPORT_FILE"
fi

# Tabla de enrutamiento
add_section "TABLA DE ENRUTAMIENTO"
ip route >> "$REPORT_FILE"

# Resolución DNS
add_section "RESOLUCIÓN DNS"
echo "Configuración DNS:" >> "$REPORT_FILE"
cat /etc/resolv.conf >> "$REPORT_FILE"

echo "" >> "$REPORT_FILE"
echo "Prueba de resolución DNS:" >> "$REPORT_FILE"
if check_tool dig; then
    dig google.com >> "$REPORT_FILE" 2>&1
elif check_tool nslookup; then
    nslookup google.com >> "$REPORT_FILE" 2>&1
else
    echo "No se encontraron herramientas de resolución DNS" >> "$REPORT_FILE"
fi

# Finalizar reporte
add_section "RESUMEN"
echo "Análisis completado el $(date)" >> "$REPORT_FILE"

if [ $TOOLS_MISSING -eq 1 ]; then
    echo "Advertencia: Algunas herramientas no estaban disponibles. El reporte puede estar incompleto." >> "$REPORT_FILE"
    echo "Para obtener un reporte completo, instale las siguientes herramientas:" >> "$REPORT_FILE"
    echo "  sudo apt-get install iproute2 net-tools iputils-ping traceroute mtr-tiny iperf3 dnsutils" >> "$REPORT_FILE"
fi

echo ""
echo "Análisis de rendimiento completado"
echo "Reporte guardado en: $REPORT_FILE"

exit 0

