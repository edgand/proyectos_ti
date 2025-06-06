#!/bin/bash
# Script de monitoreo de infraestructura

# Variables
LOG_DIR="/var/log/infrastructure-monitoring"
LOG_FILE="${LOG_DIR}/monitoring-$(date +%Y-%m-%d).log"
ALERT_EMAIL="admin@example.com"
THRESHOLD_CPU=80
THRESHOLD_MEMORY=80
THRESHOLD_DISK=90
THRESHOLD_LOAD=5

# Crear directorio de logs si no existe
mkdir -p ${LOG_DIR}

# Función para registrar mensajes
log_message() {
    echo "[$(date +"%Y-%m-%d %H:%M:%S")] $1" >> ${LOG_FILE}
    echo "$1"
}

# Función para enviar alertas
send_alert() {
    local subject="$1"
    local message="$2"
    echo "${message}" | mail -s "${subject}" ${ALERT_EMAIL}
    log_message "Alerta enviada: ${subject}"
}

# Iniciar monitoreo
log_message "Iniciando monitoreo de infraestructura..."

# Verificar uso de CPU
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}' | cut -d. -f1)
log_message "Uso de CPU: ${CPU_USAGE}%"

if [ ${CPU_USAGE} -gt ${THRESHOLD_CPU} ]; then
    send_alert "Alerta: Alto uso de CPU" "El uso de CPU ha alcanzado ${CPU_USAGE}%, superando el umbral de ${THRESHOLD_CPU}%."
fi

# Verificar uso de memoria
MEMORY_TOTAL=$(free -m | awk '/^Mem:/ {print $2}')
MEMORY_USED=$(free -m | awk '/^Mem:/ {print $3}')
MEMORY_USAGE=$((MEMORY_USED * 100 / MEMORY_TOTAL))
log_message "Uso de memoria: ${MEMORY_USAGE}% (${MEMORY_USED}MB de ${MEMORY_TOTAL}MB)"

if [ ${MEMORY_USAGE} -gt ${THRESHOLD_MEMORY} ]; then
    send_alert "Alerta: Alto uso de memoria" "El uso de memoria ha alcanzado ${MEMORY_USAGE}%, superando el umbral de ${THRESHOLD_MEMORY}%."
fi

# Verificar uso de disco
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d% -f1)
log_message "Uso de disco: ${DISK_USAGE}%"

if [ ${DISK_USAGE} -gt ${THRESHOLD_DISK} ]; then
    send_alert "Alerta: Alto uso de disco" "El uso de disco ha alcanzado ${DISK_USAGE}%, superando el umbral de ${THRESHOLD_DISK}%."
fi

# Verificar carga del sistema
SYSTEM_LOAD=$(uptime | awk -F'load average:' '{ print $2 }' | cut -d, -f1 | tr -d ' ')
SYSTEM_LOAD_INT=${SYSTEM_LOAD%.*}
log_message "Carga del sistema: ${SYSTEM_LOAD}"

if [ ${SYSTEM_LOAD_INT} -gt ${THRESHOLD_LOAD} ]; then
    send_alert "Alerta: Alta carga del sistema" "La carga del sistema ha alcanzado ${SYSTEM_LOAD}, superando el umbral de ${THRESHOLD_LOAD}."
fi

# Verificar servicios críticos
check_service() {
    local service_name="$1"
    systemctl is-active --quiet ${service_name}
    if [ $? -ne 0 ]; then
        send_alert "Alerta: Servicio inactivo" "El servicio ${service_name} no está en ejecución."
        log_message "Servicio ${service_name} inactivo"
    else
        log_message "Servicio ${service_name} activo"
    fi
}

# Lista de servicios críticos a verificar
CRITICAL_SERVICES=("nginx" "mysql" "ssh" "prometheus" "grafana-server")

for service in "${CRITICAL_SERVICES[@]}"; do
    check_service ${service}
done

# Verificar conectividad de red
check_connectivity() {
    local host="$1"
    ping -c 1 ${host} > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        send_alert "Alerta: Problema de conectividad" "No se puede alcanzar el host ${host}."
        log_message "No se puede alcanzar el host ${host}"
    else
        log_message "Conectividad con ${host} correcta"
    fi
}

# Lista de hosts a verificar
HOSTS_TO_CHECK=("8.8.8.8" "1.1.1.1" "gateway.local")

for host in "${HOSTS_TO_CHECK[@]}"; do
    check_connectivity ${host}
done

# Verificar puertos críticos
check_port() {
    local host="$1"
    local port="$2"
    local service_name="$3"
    nc -z -w 2 ${host} ${port} > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        send_alert "Alerta: Puerto cerrado" "El puerto ${port} (${service_name}) en ${host} no está accesible."
        log_message "Puerto ${port} (${service_name}) en ${host} no está accesible"
    else
        log_message "Puerto ${port} (${service_name}) en ${host} accesible"
    fi
}

# Lista de puertos críticos a verificar
declare -A PORTS_TO_CHECK
PORTS_TO_CHECK["localhost:80"]="HTTP"
PORTS_TO_CHECK["localhost:443"]="HTTPS"
PORTS_TO_CHECK["localhost:3306"]="MySQL"
PORTS_TO_CHECK["localhost:22"]="SSH"
PORTS_TO_CHECK["localhost:9090"]="Prometheus"
PORTS_TO_CHECK["localhost:3000"]="Grafana"

for port_spec in "${!PORTS_TO_CHECK[@]}"; do
    host=$(echo ${port_spec} | cut -d: -f1)
    port=$(echo ${port_spec} | cut -d: -f2)
    service_name=${PORTS_TO_CHECK[${port_spec}]}
    check_port ${host} ${port} ${service_name}
done

# Verificar logs en busca de errores
check_logs_for_errors() {
    local log_file="$1"
    local error_count=$(grep -i "error\|critical\|fail" ${log_file} | wc -l)
    if [ ${error_count} -gt 0 ]; then
        send_alert "Alerta: Errores en logs" "Se encontraron ${error_count} errores en ${log_file}."
        log_message "Se encontraron ${error_count} errores en ${log_file}"
    else
        log_message "No se encontraron errores en ${log_file}"
    fi
}

# Lista de archivos de log a verificar
LOG_FILES_TO_CHECK=("/var/log/syslog" "/var/log/nginx/error.log" "/var/log/mysql/error.log")

for log_file in "${LOG_FILES_TO_CHECK[@]}"; do
    if [ -f ${log_file} ]; then
        check_logs_for_errors ${log_file}
    else
        log_message "Archivo de log ${log_file} no encontrado"
    fi
done

log_message "Monitoreo de infraestructura completado"

exit 0

