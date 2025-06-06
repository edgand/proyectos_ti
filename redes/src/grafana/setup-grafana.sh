#!/bin/bash
# Script para instalar y configurar Grafana con Prometheus para monitoreo de red

# Variables
GRAFANA_VERSION="9.5.2"
PROMETHEUS_VERSION="2.43.0"
NODE_EXPORTER_VERSION="1.5.0"
PROMETHEUS_PORT="9090"
GRAFANA_PORT="3000"
NODE_EXPORTER_PORT="9100"
DATA_DIR="/var/lib/monitoring"
CONFIG_DIR="/etc/monitoring"
DASHBOARD_DIR="/tmp/dashboards"

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
print_message "Iniciando instalación de Grafana y Prometheus"
print_message "Este script instalará:"
echo "  - Grafana $GRAFANA_VERSION"
echo "  - Prometheus $PROMETHEUS_VERSION"
echo "  - Node Exporter $NODE_EXPORTER_VERSION"
echo ""
echo "Puertos:"
echo "  - Grafana: $GRAFANA_PORT"
echo "  - Prometheus: $PROMETHEUS_PORT"
echo "  - Node Exporter: $NODE_EXPORTER_PORT"
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
apt-get install -y wget curl gnupg2 apt-transport-https software-properties-common adduser libfontconfig1
check_status "Dependencias instaladas" "Error al instalar dependencias"

# Crear directorios
print_message "Creando directorios..."
mkdir -p $DATA_DIR/{grafana,prometheus,node_exporter}
mkdir -p $CONFIG_DIR/{grafana,prometheus,node_exporter}
mkdir -p $DASHBOARD_DIR
check_status "Directorios creados" "Error al crear directorios"

# Instalar Grafana
print_message "Instalando Grafana..."
wget -q -O - https://packages.grafana.com/gpg.key | apt-key add -
add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
apt-get update
apt-get install -y grafana
check_status "Grafana instalado" "Error al instalar Grafana"

# Configurar Grafana
print_message "Configurando Grafana..."
cat > /etc/grafana/grafana.ini << EOF
[server]
http_port = $GRAFANA_PORT
domain = localhost
root_url = %(protocol)s://%(domain)s:%(http_port)s/
serve_from_sub_path = false

[security]
admin_user = admin
admin_password = admin
disable_gravatar = true

[users]
allow_sign_up = false
auto_assign_org = true
auto_assign_org_role = Editor

[auth.anonymous]
enabled = false

[dashboards]
default_home_dashboard_path = /var/lib/grafana/dashboards/network-overview.json
EOF

# Crear directorio para dashboards
mkdir -p /var/lib/grafana/dashboards

# Instalar Prometheus
print_message "Instalando Prometheus..."
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v$PROMETHEUS_VERSION/prometheus-$PROMETHEUS_VERSION.linux-amd64.tar.gz
tar xzf prometheus-$PROMETHEUS_VERSION.linux-amd64.tar.gz
cp prometheus-$PROMETHEUS_VERSION.linux-amd64/prometheus /usr/local/bin/
cp prometheus-$PROMETHEUS_VERSION.linux-amd64/promtool /usr/local/bin/
cp -r prometheus-$PROMETHEUS_VERSION.linux-amd64/consoles /etc/prometheus
cp -r prometheus-$PROMETHEUS_VERSION.linux-amd64/console_libraries /etc/prometheus
rm -rf prometheus-$PROMETHEUS_VERSION.linux-amd64 prometheus-$PROMETHEUS_VERSION.linux-amd64.tar.gz
check_status "Prometheus instalado" "Error al instalar Prometheus"

# Crear usuario para Prometheus
useradd --no-create-home --shell /bin/false prometheus
mkdir -p /var/lib/prometheus
chown prometheus:prometheus /var/lib/prometheus
chown prometheus:prometheus /usr/local/bin/prometheus
chown prometheus:prometheus /usr/local/bin/promtool
chown -R prometheus:prometheus /etc/prometheus

# Configurar Prometheus
print_message "Configurando Prometheus..."
cat > /etc/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
  - static_configs:
    - targets:
      # - alertmanager:9093

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
    - targets: ['localhost:$PROMETHEUS_PORT']

  - job_name: 'node_exporter'
    static_configs:
    - targets: ['localhost:$NODE_EXPORTER_PORT']
EOF

chown prometheus:prometheus /etc/prometheus/prometheus.yml

# Crear servicio systemd para Prometheus
cat > /etc/systemd/system/prometheus.service << EOF
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
    --config.file /etc/prometheus/prometheus.yml \
    --storage.tsdb.path /var/lib/prometheus/ \
    --web.console.templates=/etc/prometheus/consoles \
    --web.console.libraries=/etc/prometheus/console_libraries \
    --web.listen-address=0.0.0.0:$PROMETHEUS_PORT \
    --web.enable-lifecycle

[Install]
WantedBy=multi-user.target
EOF

# Instalar Node Exporter
print_message "Instalando Node Exporter..."
cd /tmp
wget https://github.com/prometheus/node_exporter/releases/download/v$NODE_EXPORTER_VERSION/node_exporter-$NODE_EXPORTER_VERSION.linux-amd64.tar.gz
tar xzf node_exporter-$NODE_EXPORTER_VERSION.linux-amd64.tar.gz
cp node_exporter-$NODE_EXPORTER_VERSION.linux-amd64/node_exporter /usr/local/bin/
rm -rf node_exporter-$NODE_EXPORTER_VERSION.linux-amd64 node_exporter-$NODE_EXPORTER_VERSION.linux-amd64.tar.gz
check_status "Node Exporter instalado" "Error al instalar Node Exporter"

# Crear usuario para Node Exporter
useradd --no-create-home --shell /bin/false node_exporter
chown node_exporter:node_exporter /usr/local/bin/node_exporter

# Crear servicio systemd para Node Exporter
cat > /etc/systemd/system/node_exporter.service << EOF
[Unit]
Description=Node Exporter
Wants=network-online.target
After=network-online.target

[Service]
User=node_exporter
Group=node_exporter
Type=simple
ExecStart=/usr/local/bin/node_exporter \
    --web.listen-address=0.0.0.0:$NODE_EXPORTER_PORT

[Install]
WantedBy=multi-user.target
EOF

# Crear dashboard de ejemplo para monitoreo de red
print_message "Creando dashboard de ejemplo..."
cat > /var/lib/grafana/dashboards/network-overview.json << 'EOF'
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "panels": [
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 2,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.5.5",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "rate(node_network_receive_bytes_total{device!=\"lo\"}[1m])",
          "interval": "",
          "legendFormat": "{{device}} - Receive",
          "refId": "A"
        },
        {
          "expr": "rate(node_network_transmit_bytes_total{device!=\"lo\"}[1m])",
          "interval": "",
          "legendFormat": "{{device}} - Transmit",
          "refId": "B"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Network Traffic",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "bytes",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 4,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.5.5",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "rate(node_network_receive_packets_total{device!=\"lo\"}[1m])",
          "interval": "",
          "legendFormat": "{{device}} - Receive",
          "refId": "A"
        },
        {
          "expr": "rate(node_network_transmit_packets_total{device!=\"lo\"}[1m])",
          "interval": "",
          "legendFormat": "{{device}} - Transmit",
          "refId": "B"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Network Packets",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "pps",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 8
      },
      "hiddenSeries": false,
      "id": 6,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.5.5",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "node_memory_MemTotal_bytes - node_memory_MemFree_bytes - node_memory_Buffers_bytes - node_memory_Cached_bytes",
          "interval": "",
          "legendFormat": "Used",
          "refId": "A"
        },
        {
          "expr": "node_memory_Buffers_bytes + node_memory_Cached_bytes",
          "interval": "",
          "legendFormat": "Buffers/Cache",
          "refId": "B"
        },
        {
          "expr": "node_memory_MemFree_bytes",
          "interval": "",
          "legendFormat": "Free",
          "refId": "C"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Memory Usage",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "bytes",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 8
      },
      "hiddenSeries": false,
      "id": 8,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.5.5",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "rate(node_cpu_seconds_total{mode=\"user\"}[1m])",
          "interval": "",
          "legendFormat": "CPU {{cpu}} - User",
          "refId": "A"
        },
        {
          "expr": "rate(node_cpu_seconds_total{mode=\"system\"}[1m])",
          "interval": "",
          "legendFormat": "CPU {{cpu}} - System",
          "refId": "B"
        },
        {
          "expr": "rate(node_cpu_seconds_total{mode=\"iowait\"}[1m])",
          "interval": "",
          "legendFormat": "CPU {{cpu}} - IO Wait",
          "refId": "C"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "CPU Usage",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "percentunit",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 16
      },
      "hiddenSeries": false,
      "id": 10,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.5.5",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "rate(node_disk_read_bytes_total[1m])",
          "interval": "",
          "legendFormat": "{{device}} - Read",
          "refId": "A"
        },
        {
          "expr": "rate(node_disk_written_bytes_total[1m])",
          "interval": "",
          "legendFormat": "{{device}} - Write",
          "refId": "B"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Disk I/O",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "bytes",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fieldConfig": {
        "defaults": {},
        "overrides": []
      },
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 16
      },
      "hiddenSeries": false,
      "id": 12,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "alertThreshold": true
      },
      "percentage": false,
      "pluginVersion": "7.5.5",
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "node_filesystem_avail_bytes",
          "interval": "",
          "legendFormat": "{{mountpoint}} - Available",
          "refId": "A"
        },
        {
          "expr": "node_filesystem_size_bytes - node_filesystem_avail_bytes",
          "interval": "",
          "legendFormat": "{{mountpoint}} - Used",
          "refId": "B"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Filesystem Usage",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "bytes",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    }
  ],
  "refresh": "5s",
  "schemaVersion": 27,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Network Overview",
  "uid": "network-overview",
  "version": 1
}
EOF

# Crear script para configurar datasource de Prometheus en Grafana
print_message "Creando script para configurar datasource..."
cat > /usr/local/bin/configure-grafana-datasource.sh << EOF
#!/bin/bash
# Esperar a que Grafana esté disponible
echo "Esperando a que Grafana esté disponible..."
until curl -s http://localhost:$GRAFANA_PORT/api/health | grep -q "ok"; do
    sleep 1
done

# Crear datasource de Prometheus
echo "Creando datasource de Prometheus..."
curl -X POST -H "Content-Type: application/json" -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://localhost:$PROMETHEUS_PORT",
    "access": "proxy",
    "isDefault": true
}' http://admin:admin@localhost:$GRAFANA_PORT/api/datasources

echo "Datasource creado correctamente"
EOF

chmod +x /usr/local/bin/configure-grafana-datasource.sh

# Reiniciar servicios
print_message "Reiniciando servicios..."
systemctl daemon-reload
systemctl enable grafana-server
systemctl enable prometheus
systemctl enable node_exporter
systemctl restart grafana-server
systemctl restart prometheus
systemctl restart node_exporter
check_status "Servicios reiniciados" "Error al reiniciar servicios"

# Configurar datasource de Prometheus en Grafana
print_message "Configurando datasource de Prometheus en Grafana..."
sleep 10  # Esperar a que Grafana inicie completamente
/usr/local/bin/configure-grafana-datasource.sh
check_status "Datasource configurado" "Error al configurar datasource"

# Mostrar información final
IP_ADDRESS=$(hostname -I | awk '{print $1}')
print_message "Instalación completada con éxito"
echo ""
echo "Acceda a Grafana en: http://$IP_ADDRESS:$GRAFANA_PORT"
echo "Credenciales por defecto:"
echo "  Usuario: admin"
echo "  Contraseña: admin"
echo ""
echo "Acceda a Prometheus en: http://$IP_ADDRESS:$PROMETHEUS_PORT"
echo ""
echo "Node Exporter está disponible en: http://$IP_ADDRESS:$NODE_EXPORTER_PORT/metrics"
echo ""
echo "Se ha creado un dashboard de ejemplo llamado 'Network Overview'"
echo ""
echo "Recuerde cambiar la contraseña de Grafana después de iniciar sesión"
echo ""

exit 0

