#!/bin/bash
# Script para capturar tráfico de red utilizando tcpdump

# Variables
INTERFACE=$1
FILTER=$2
DURATION=$3
OUTPUT_DIR="$(dirname "$0")/captures"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
CAPTURE_FILE="${OUTPUT_DIR}/${FILTER}-${TIMESTAMP}.pcap"

# Función para mostrar ayuda
show_help() {
    echo "Uso: $0 <interfaz> <filtro> [duración_en_segundos]"
    echo ""
    echo "Ejemplos:"
    echo "  $0 eth0 http            # Captura tráfico HTTP en la interfaz eth0"
    echo "  $0 eth0 \"port 80\" 60   # Captura tráfico en el puerto 80 durante 60 segundos"
    echo "  $0 eth0 \"host 8.8.8.8\"  # Captura tráfico hacia/desde 8.8.8.8"
    echo ""
    echo "Filtros comunes:"
    echo "  http      - Tráfico HTTP (puerto 80)"
    echo "  https     - Tráfico HTTPS (puerto 443)"
    echo "  dns       - Tráfico DNS (puerto 53)"
    echo "  ssh       - Tráfico SSH (puerto 22)"
    echo "  icmp      - Tráfico ICMP (ping)"
    echo "  arp       - Tráfico ARP"
    echo "  port X    - Tráfico en el puerto X"
    echo "  host X    - Tráfico hacia/desde el host X"
    echo "  net X     - Tráfico hacia/desde la red X"
    echo ""
    echo "Para filtros más complejos, consulte la documentación de tcpdump:"
    echo "  man tcpdump"
    exit 1
}

# Verificar argumentos
if [ -z "$INTERFACE" ] || [ -z "$FILTER" ]; then
    show_help
fi

# Si no se especifica duración, usar 0 (captura indefinida)
if [ -z "$DURATION" ]; then
    DURATION=0
fi

# Crear directorio de capturas si no existe
mkdir -p "$OUTPUT_DIR"

# Convertir filtros comunes a expresiones de tcpdump
case "$FILTER" in
    http)
        FILTER="port 80"
        ;;
    https)
        FILTER="port 443"
        ;;
    dns)
        FILTER="port 53"
        ;;
    ssh)
        FILTER="port 22"
        ;;
    icmp)
        FILTER="icmp"
        ;;
    arp)
        FILTER="arp"
        ;;
esac

# Verificar que tcpdump está instalado
if ! command -v tcpdump &> /dev/null; then
    echo "Error: tcpdump no está instalado"
    echo "Instálelo con: sudo apt-get install tcpdump"
    exit 1
fi

# Verificar que la interfaz existe
if ! ip link show "$INTERFACE" &> /dev/null; then
    echo "Error: La interfaz $INTERFACE no existe"
    echo "Interfaces disponibles:"
    ip -o link show | awk -F': ' '{print $2}'
    exit 1
fi

# Mostrar información de la captura
echo "Iniciando captura de tráfico:"
echo "  Interfaz: $INTERFACE"
echo "  Filtro: $FILTER"
if [ "$DURATION" -gt 0 ]; then
    echo "  Duración: $DURATION segundos"
else
    echo "  Duración: indefinida (presione Ctrl+C para detener)"
fi
echo "  Archivo de salida: $CAPTURE_FILE"
echo ""

# Iniciar captura
if [ "$DURATION" -gt 0 ]; then
    echo "La captura se detendrá automáticamente después de $DURATION segundos..."
    sudo tcpdump -i "$INTERFACE" -w "$CAPTURE_FILE" "$FILTER" -G "$DURATION" -W 1
else
    echo "Presione Ctrl+C para detener la captura..."
    sudo tcpdump -i "$INTERFACE" -w "$CAPTURE_FILE" "$FILTER"
fi

# Verificar si la captura fue exitosa
if [ $? -eq 0 ]; then
    echo ""
    echo "Captura completada con éxito"
    echo "Archivo guardado en: $CAPTURE_FILE"
    echo ""
    echo "Para analizar la captura con Wireshark:"
    echo "  wireshark $CAPTURE_FILE"
    echo ""
    echo "Para analizar la captura con tcpdump:"
    echo "  tcpdump -r $CAPTURE_FILE -n"
    
    # Mostrar estadísticas básicas
    echo ""
    echo "Estadísticas básicas de la captura:"
    echo "--------------------------------"
    echo "Tamaño del archivo: $(du -h "$CAPTURE_FILE" | cut -f1)"
    echo "Número de paquetes: $(tcpdump -r "$CAPTURE_FILE" -n | wc -l)"
    
    # Mostrar los 5 hosts más activos
    echo ""
    echo "Hosts más activos:"
    tcpdump -r "$CAPTURE_FILE" -n -q | awk '{print $3, $5}' | sed 's/\./ /g' | awk '{print $1"."$2"."$3"."$4, $5"."$6"."$7"."$8}' | sort | uniq -c | sort -nr | head -5
else
    echo ""
    echo "Error durante la captura"
    exit 1
fi

exit 0

