# Guía de Implementación: Redes, Telecomunicaciones y Herramientas de Monitoreo

Esta guía proporciona instrucciones detalladas para implementar la solución de monitoreo y gestión de redes y telecomunicaciones en un entorno empresarial.

## Índice

1. [Requisitos Previos](#requisitos-previos)
2. [Arquitectura de Implementación](#arquitectura-de-implementación)
3. [Instalación de Componentes Principales](#instalación-de-componentes-principales)
4. [Configuración de Monitoreo de Red](#configuración-de-monitoreo-de-red)
5. [Configuración de Análisis de Tráfico](#configuración-de-análisis-de-tráfico)
6. [Configuración de Detección de Intrusiones](#configuración-de-detección-de-intrusiones)
7. [Configuración de Visualización y Alertas](#configuración-de-visualización-y-alertas)
8. [Integración con Infraestructura Existente](#integración-con-infraestructura-existente)
9. [Verificación y Pruebas](#verificación-y-pruebas)
10. [Mantenimiento y Operaciones](#mantenimiento-y-operaciones)

## Requisitos Previos

### Hardware Recomendado

| Componente | Especificaciones Mínimas | Especificaciones Recomendadas |
|------------|--------------------------|-------------------------------|
| Servidor de Monitoreo | 4 cores, 16 GB RAM, 250 GB SSD | 8+ cores, 32+ GB RAM, 500+ GB SSD |
| Colector de Flujos | 2 cores, 8 GB RAM, 100 GB SSD | 4+ cores, 16+ GB RAM, 200+ GB SSD |
| Almacenamiento de PCAP | 2 cores, 8 GB RAM, 1 TB HDD | 4+ cores, 16+ GB RAM, 2+ TB SSD |
| Base de Datos | 4 cores, 32 GB RAM, 500 GB SSD | 8+ cores, 64+ GB RAM, 1+ TB SSD |

### Software Base

- Sistema Operativo: Ubuntu Server 20.04 LTS o superior
- Docker y Docker Compose (opcional para despliegue en contenedores)
- Git para gestión de configuraciones
- Python 3.8 o superior
- Java 11 o superior (para Elasticsearch)

### Accesos y Permisos

- Acceso de administrador a dispositivos de red (switches, routers, firewalls)
- Permisos para configurar SNMP, NetFlow, sFlow o IPFIX en dispositivos de red
- Acceso SSH a servidores para instalación de agentes
- Permisos de firewall para permitir tráfico de monitoreo

## Arquitectura de Implementación

### Diagrama de Red

```
                                  ┌─────────────────┐
                                  │   Internet      │
                                  └────────┬────────┘
                                           │
                                  ┌────────┴────────┐
                                  │    Firewall     │
                                  └────────┬────────┘
                                           │
                 ┌───────────────┬─────────┴─────────┬───────────────┐
                 │               │                   │               │
         ┌───────┴───────┐ ┌─────┴─────┐     ┌───────┴───────┐ ┌─────┴─────┐
         │  Core Switch  │ │ Servidor  │     │  Servidor de  │ │ Servidor  │
         │               │ │ Monitoreo │     │  Colección    │ │   PCAP    │
         └───────┬───────┘ └───────────┘     └───────────────┘ └───────────┘
                 │
    ┌────────────┼────────────┬────────────────────┐
    │            │            │                    │
┌───┴───┐    ┌───┴───┐    ┌───┴───┐            ┌───┴───┐
│ Dist. │    │ Dist. │    │ Dist. │            │ Dist. │
│Switch1│    │Switch2│    │Switch3│            │SwitchN│
└───┬───┘    └───┬───┘    └───┬───┘            └───┬───┘
    │            │            │                    │
┌───┴───┐    ┌───┴───┐    ┌───┴───┐            ┌───┴───┐
│Access │    │Access │    │Access │            │Access │
│Switch1│    │Switch2│    │Switch3│            │SwitchN│
└───┬───┘    └───┬───┘    └───┬───┘            └───┬───┘
    │            │            │                    │
┌───┴───┐    ┌───┴───┐    ┌───┴───┐            ┌───┴───┐
│Clients│    │Clients│    │Clients│            │Clients│
└───────┘    └───────┘    └───────┘            └───────┘
```

### Flujo de Datos

1. **Recolección de Métricas**:
   - Los agentes Node Exporter recopilan métricas de servidores
   - Los dispositivos de red envían traps SNMP y flujos NetFlow
   - El tráfico de red se captura en puntos estratégicos

2. **Procesamiento**:
   - Prometheus recopila y almacena métricas
   - Snort analiza tráfico en busca de amenazas
   - Logstash procesa logs y eventos

3. **Almacenamiento**:
   - Las métricas se almacenan en TSDB de Prometheus
   - Las capturas de paquetes se almacenan en formato PCAP
   - Los logs y eventos se almacenan en Elasticsearch

4. **Visualización y Alertas**:
   - Grafana muestra dashboards con métricas de red
   - Wireshark permite análisis detallado de paquetes
   - Kibana visualiza logs y eventos
   - Alert Manager gestiona notificaciones y escalado

## Instalación de Componentes Principales

### Preparación del Sistema

1. **Actualizar el sistema**:
   ```bash
   sudo apt-get update
   sudo apt-get upgrade -y
   ```

2. **Instalar dependencias comunes**:
   ```bash
   sudo apt-get install -y wget curl gnupg2 apt-transport-https \
   software-properties-common adduser libfontconfig1 build-essential \
   libpcap-dev python3-pip git
   ```

3. **Configurar zonas horarias**:
   ```bash
   sudo timedatectl set-timezone UTC
   ```

### Instalación de Prometheus

1. **Crear usuario y directorios**:
   ```bash
   sudo useradd --no-create-home --shell /bin/false prometheus
   sudo mkdir -p /etc/prometheus /var/lib/prometheus
   ```

2. **Descargar e instalar Prometheus**:
   ```bash
   cd /tmp
   wget https://github.com/prometheus/prometheus/releases/download/v2.43.0/prometheus-2.43.0.linux-amd64.tar.gz
   tar xzf prometheus-2.43.0.linux-amd64.tar.gz
   
   sudo cp prometheus-2.43.0.linux-amd64/prometheus /usr/local/bin/
   sudo cp prometheus-2.43.0.linux-amd64/promtool /usr/local/bin/
   sudo cp -r prometheus-2.43.0.linux-amd64/consoles /etc/prometheus
   sudo cp -r prometheus-2.43.0.linux-amd64/console_libraries /etc/prometheus
   
   sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus
   sudo chown prometheus:prometheus /usr/local/bin/prometheus
   sudo chown prometheus:prometheus /usr/local/bin/promtool
   ```

3. **Configurar Prometheus**:
   ```bash
   sudo nano /etc/prometheus/prometheus.yml
   ```
   
   Contenido básico:
   ```yaml
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
       - targets: ['localhost:9090']
   
     - job_name: 'node_exporter'
       static_configs:
       - targets: ['localhost:9100']
   ```

4. **Crear servicio systemd**:
   ```bash
   sudo nano /etc/systemd/system/prometheus.service
   ```
   
   Contenido:
   ```ini
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
       --web.console.libraries=/etc/prometheus/console_libraries
   
   [Install]
   WantedBy=multi-user.target
   ```

5. **Iniciar Prometheus**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable prometheus
   sudo systemctl start prometheus
   sudo systemctl status prometheus
   ```

### Instalación de Node Exporter

1. **Crear usuario**:
   ```bash
   sudo useradd --no-create-home --shell /bin/false node_exporter
   ```

2. **Descargar e instalar Node Exporter**:
   ```bash
   cd /tmp
   wget https://github.com/prometheus/node_exporter/releases/download/v1.5.0/node_exporter-1.5.0.linux-amd64.tar.gz
   tar xzf node_exporter-1.5.0.linux-amd64.tar.gz
   
   sudo cp node_exporter-1.5.0.linux-amd64/node_exporter /usr/local/bin/
   sudo chown node_exporter:node_exporter /usr/local/bin/node_exporter
   ```

3. **Crear servicio systemd**:
   ```bash
   sudo nano /etc/systemd/system/node_exporter.service
   ```
   
   Contenido:
   ```ini
   [Unit]
   Description=Node Exporter
   Wants=network-online.target
   After=network-online.target
   
   [Service]
   User=node_exporter
   Group=node_exporter
   Type=simple
   ExecStart=/usr/local/bin/node_exporter
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Iniciar Node Exporter**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable node_exporter
   sudo systemctl start node_exporter
   sudo systemctl status node_exporter
   ```

### Instalación de Grafana

1. **Añadir repositorio de Grafana**:
   ```bash
   wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
   sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
   ```

2. **Instalar Grafana**:
   ```bash
   sudo apt-get update
   sudo apt-get install -y grafana
   ```

3. **Configurar Grafana**:
   ```bash
   sudo nano /etc/grafana/grafana.ini
   ```
   
   Modificaciones recomendadas:
   ```ini
   [server]
   http_port = 3000
   domain = localhost
   
   [security]
   admin_user = admin
   admin_password = admin
   
   [users]
   allow_sign_up = false
   ```

4. **Iniciar Grafana**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable grafana-server
   sudo systemctl start grafana-server
   sudo systemctl status grafana-server
   ```

### Instalación de Snort

1. **Instalar dependencias**:
   ```bash
   sudo apt-get install -y build-essential libpcap-dev libpcre3-dev libnet1-dev zlib1g-dev luajit hwloc libdnet-dev libdumbnet-dev bison flex liblzma-dev openssl libssl-dev pkg-config libhwloc-dev cmake cpputest libsqlite3-dev uuid-dev libcmocka-dev libnetfilter-queue-dev libmnl-dev autotools-dev libluajit-5.1-dev libunwind-dev
   ```

2. **Instalar Snort 3 (compilación desde fuente)**:
   ```bash
   cd /tmp
   
   # Instalar libdaq
   git clone https://github.com/snort3/libdaq.git
   cd libdaq
   ./bootstrap
   ./configure
   make
   sudo make install
   
   # Actualizar cache de bibliotecas compartidas
   sudo ldconfig
   
   # Instalar Snort 3
   cd /tmp
   git clone https://github.com/snort3/snort3.git
   cd snort3
   ./configure_cmake.sh --prefix=/usr/local --enable-tcmalloc
   cd build
   make
   sudo make install
   
   # Actualizar cache de bibliotecas compartidas
   sudo ldconfig
   ```

3. **Configurar Snort**:
   ```bash
   sudo mkdir -p /etc/snort/rules
   sudo mkdir -p /var/log/snort
   sudo chmod -R 5775 /var/log/snort
   
   # Descargar reglas de comunidad
   cd /etc/snort/rules
   sudo wget https://www.snort.org/downloads/community/snort3-community-rules.tar.gz
   sudo tar -xzf snort3-community-rules.tar.gz
   sudo rm snort3-community-rules.tar.gz
   ```

4. **Crear configuración básica**:
   ```bash
   sudo nano /etc/snort/snort.lua
   ```
   
   Contenido básico:
   ```lua
   -- Snort 3 Configuration
   
   -- Home network definition
   HOME_NET = '192.168.0.0/24'  -- Ajustar a la red local
   EXTERNAL_NET = '!$HOME_NET'
   
   -- Path variables
   RULE_PATH = '/etc/snort/rules'
   
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
   ```

5. **Verificar configuración**:
   ```bash
   sudo snort -c /etc/snort/snort.lua --warn-all
   ```

### Instalación de Elasticsearch y Kibana

1. **Añadir repositorio de Elastic**:
   ```bash
   wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
   sudo apt-get install apt-transport-https
   echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list
   ```

2. **Instalar Elasticsearch**:
   ```bash
   sudo apt-get update
   sudo apt-get install elasticsearch
   ```

3. **Configurar Elasticsearch**:
   ```bash
   sudo nano /etc/elasticsearch/elasticsearch.yml
   ```
   
   Modificaciones recomendadas:
   ```yaml
   cluster.name: monitoring-cluster
   node.name: node-1
   network.host: 0.0.0.0
   http.port: 9200
   discovery.seed_hosts: ["127.0.0.1"]
   cluster.initial_master_nodes: ["node-1"]
   ```

4. **Iniciar Elasticsearch**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable elasticsearch
   sudo systemctl start elasticsearch
   ```

5. **Instalar Kibana**:
   ```bash
   sudo apt-get install kibana
   ```

6. **Configurar Kibana**:
   ```bash
   sudo nano /etc/kibana/kibana.yml
   ```
   
   Modificaciones recomendadas:
   ```yaml
   server.port: 5601
   server.host: "0.0.0.0"
   elasticsearch.hosts: ["http://localhost:9200"]
   ```

7. **Iniciar Kibana**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable kibana
   sudo systemctl start kibana
   ```

## Configuración de Monitoreo de Red

### Configuración de SNMP en Dispositivos de Red

#### Para Dispositivos Cisco

1. **Configurar SNMP v2c (básico)**:
   ```
   enable
   configure terminal
   snmp-server community public RO
   snmp-server location "Data Center"
   snmp-server contact "Network Team"
   end
   write memory
   ```

2. **Configurar SNMP v3 (recomendado para producción)**:
   ```
   enable
   configure terminal
   snmp-server group SNMP-RO v3 priv read SNMP-RO-VIEW
   snmp-server view SNMP-RO-VIEW iso included
   snmp-server user snmpuser SNMP-RO v3 auth sha authpassword priv aes 128 privpassword
   end
   write memory
   ```

#### Para Dispositivos Juniper

1. **Configurar SNMP v2c**:
   ```
   configure
   set snmp community public authorization read-only
   set snmp location "Data Center"
   set snmp contact "Network Team"
   commit
   exit
   ```

2. **Configurar SNMP v3**:
   ```
   configure
   set snmp v3 usm local-engine user snmpuser authentication-sha authentication-password authpassword
   set snmp v3 usm local-engine user snmpuser privacy-aes128 privacy-password privpassword
   set snmp v3 vacm security-to-group security-model usm security-name snmpuser group SNMP-RO
   set snmp v3 vacm access group SNMP-RO default-context-prefix security-model usm security-level privacy read-view view-all
   set snmp v3 vacm view view-all oid iso include
   commit
   exit
   ```

### Configuración de NetFlow/sFlow

#### Para Dispositivos Cisco (NetFlow)

1. **Configurar NetFlow v9**:
   ```
   enable
   configure terminal
   flow exporter EXPORTER
    destination 192.168.1.100
    source Loopback0
    transport udp 9995
    export-protocol netflow-v9
    template data timeout 60
   exit
   flow monitor MONITOR
    record netflow-v9
    exporter EXPORTER
    cache timeout active 60
   exit
   interface GigabitEthernet0/0
    ip flow monitor MONITOR input
    ip flow monitor MONITOR output
   exit
   end
   write memory
   ```

#### Para Dispositivos Juniper (sFlow)

1. **Configurar sFlow**:
   ```
   configure
   set protocols sflow collector 192.168.1.100 udp-port 6343
   set protocols sflow interfaces ge-0/0/0 polling-interval 20
   set protocols sflow interfaces ge-0/0/0 sample-rate 2000
   set protocols sflow source-ip 192.168.1.1
   commit
   exit
   ```

### Configuración de Prometheus para Monitoreo de Red

1. **Añadir configuración para SNMP Exporter**:
   ```bash
   sudo nano /etc/prometheus/prometheus.yml
   ```
   
   Añadir:
   ```yaml
   scrape_configs:
     # ... configuración existente ...
     
     - job_name: 'snmp'
       static_configs:
         - targets:
           - '192.168.1.1'  # Router
           - '192.168.1.2'  # Switch
           - '192.168.1.3'  # Firewall
       metrics_path: /snmp
       params:
         module: [if_mib]
       relabel_configs:
         - source_labels: [__address__]
           target_label: __param_target
         - source_labels: [__param_target]
           target_label: instance
         - target_label: __address__
           replacement: localhost:9116  # SNMP exporter
   ```

2. **Instalar y configurar SNMP Exporter**:
   ```bash
   cd /tmp
   wget https://github.com/prometheus/snmp_exporter/releases/download/v0.20.0/snmp_exporter-0.20.0.linux-amd64.tar.gz
   tar xzf snmp_exporter-0.20.0.linux-amd64.tar.gz
   sudo cp snmp_exporter-0.20.0.linux-amd64/snmp_exporter /usr/local/bin/
   
   sudo mkdir -p /etc/snmp_exporter
   sudo nano /etc/snmp_exporter/snmp.yml
   # Copiar configuración adecuada para sus dispositivos
   
   sudo nano /etc/systemd/system/snmp_exporter.service
   ```
   
   Contenido del servicio:
   ```ini
   [Unit]
   Description=SNMP Exporter
   Wants=network-online.target
   After=network-online.target
   
   [Service]
   User=prometheus
   Group=prometheus
   Type=simple
   ExecStart=/usr/local/bin/snmp_exporter --config.file=/etc/snmp_exporter/snmp.yml
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Iniciar SNMP Exporter**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable snmp_exporter
   sudo systemctl start snmp_exporter
   ```

## Configuración de Análisis de Tráfico

### Instalación de Wireshark (CLI)

1. **Instalar tshark (Wireshark CLI)**:
   ```bash
   sudo apt-get install -y tshark
   ```

2. **Configurar permisos para captura sin root**:
   ```bash
   sudo usermod -a -G wireshark $USER
   sudo chgrp wireshark /usr/bin/dumpcap
   sudo chmod 750 /usr/bin/dumpcap
   sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap
   ```

### Configuración de Captura de Paquetes

1. **Crear script para captura programada**:
   ```bash
   sudo nano /usr/local/bin/capture-packets.sh
   ```
   
   Contenido:
   ```bash
   #!/bin/bash
   
   INTERFACE=$1
   DURATION=$2
   FILTER=$3
   OUTPUT_DIR="/var/lib/pcap"
   TIMESTAMP=$(date +%Y%m%d-%H%M%S)
   
   mkdir -p $OUTPUT_DIR
   
   tshark -i $INTERFACE -a duration:$DURATION -f "$FILTER" -w $OUTPUT_DIR/capture-$TIMESTAMP.pcap
   ```

2. **Hacer ejecutable el script**:
   ```bash
   sudo chmod +x /usr/local/bin/capture-packets.sh
   ```

3. **Configurar captura programada con cron**:
   ```bash
   sudo crontab -e
   ```
   
   Añadir:
   ```
   # Capturar tráfico HTTP cada hora durante 5 minutos
   0 * * * * /usr/local/bin/capture-packets.sh eth0 300 "port 80" > /dev/null 2>&1
   
   # Capturar tráfico DNS cada 2 horas durante 10 minutos
   0 */2 * * * /usr/local/bin/capture-packets.sh eth0 600 "port 53" > /dev/null 2>&1
   ```

### Configuración de Análisis de Flujos

1. **Instalar nfdump para NetFlow**:
   ```bash
   sudo apt-get install -y nfdump
   ```

2. **Configurar nfcapd para recibir flujos**:
   ```bash
   sudo mkdir -p /var/lib/netflow
   
   sudo nano /etc/systemd/system/nfcapd.service
   ```
   
   Contenido:
   ```ini
   [Unit]
   Description=NetFlow Capture Daemon
   After=network.target
   
   [Service]
   ExecStart=/usr/bin/nfcapd -w -D -l /var/lib/netflow -p 9995 -u nobody -g nogroup
   Restart=on-failure
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Iniciar servicio**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable nfcapd
   sudo systemctl start nfcapd
   ```

4. **Crear script para análisis de flujos**:
   ```bash
   sudo nano /usr/local/bin/analyze-flows.sh
   ```
   
   Contenido:
   ```bash
   #!/bin/bash
   
   DATE=$(date +%Y/%m/%d)
   NETFLOW_DIR="/var/lib/netflow"
   REPORT_DIR="/var/lib/netflow/reports"
   
   mkdir -p $REPORT_DIR
   
   # Top talkers
   nfdump -R $NETFLOW_DIR/nfcapd.* -s ip/bytes -n 10 > $REPORT_DIR/top_talkers_$DATE.txt
   
   # Top protocols
   nfdump -R $NETFLOW_DIR/nfcapd.* -s proto/bytes -n 10 > $REPORT_DIR/top_protocols_$DATE.txt
   
   # Top ports
   nfdump -R $NETFLOW_DIR/nfcapd.* -s port/bytes -n 10 > $REPORT_DIR/top_ports_$DATE.txt
   ```

5. **Hacer ejecutable el script y programarlo**:
   ```bash
   sudo chmod +x /usr/local/bin/analyze-flows.sh
   
   sudo crontab -e
   ```
   
   Añadir:
   ```
   # Analizar flujos diariamente a medianoche
   0 0 * * * /usr/local/bin/analyze-flows.sh > /dev/null 2>&1
   ```

## Configuración de Detección de Intrusiones

### Configuración de Snort IDS

1. **Crear script de inicio para Snort**:
   ```bash
   sudo nano /usr/local/bin/start-snort.sh
   ```
   
   Contenido:
   ```bash
   #!/bin/bash
   
   INTERFACE=$1
   CONFIG_FILE="/etc/snort/snort.lua"
   LOG_DIR="/var/log/snort"
   
   if [ -z "$INTERFACE" ]; then
       echo "Error: Debe especificar una interfaz de red"
       echo "Uso: $0 <interfaz>"
       exit 1
   fi
   
   # Verificar que la interfaz existe
   if ! ip link show "$INTERFACE" &> /dev/null; then
       echo "Error: La interfaz $INTERFACE no existe"
       echo "Interfaces disponibles:"
       ip -o link show | awk -F': ' '{print $2}'
       exit 1
   fi
   
   echo "Iniciando Snort en la interfaz $INTERFACE..."
   snort -c $CONFIG_FILE -i $INTERFACE -l $LOG_DIR -D
   
   if [ $? -eq 0 ]; then
       echo "Snort iniciado correctamente"
       echo "Logs en: $LOG_DIR"
   else
       echo "Error al iniciar Snort"
       exit 1
   fi
   ```

2. **Hacer ejecutable el script**:
   ```bash
   sudo chmod +x /usr/local/bin/start-snort.sh
   ```

3. **Crear servicio systemd para Snort**:
   ```bash
   sudo nano /etc/systemd/system/snort.service
   ```
   
   Contenido:
   ```ini
   [Unit]
   Description=Snort NIDS Daemon
   After=network.target
   
   [Service]
   Type=forking
   ExecStart=/usr/local/bin/start-snort.sh eth0
   ExecStop=/usr/bin/pkill -f snort
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Iniciar servicio**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable snort
   sudo systemctl start snort
   ```

### Integración de Alertas de Snort con Elasticsearch

1. **Instalar Filebeat**:
   ```bash
   wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
   sudo apt-get install filebeat
   ```

2. **Configurar Filebeat para Snort**:
   ```bash
   sudo nano /etc/filebeat/filebeat.yml
   ```
   
   Contenido:
   ```yaml
   filebeat.inputs:
   - type: log
     enabled: true
     paths:
       - /var/log/snort/*.log
     tags: ["snort", "ids"]
   
   output.elasticsearch:
     hosts: ["localhost:9200"]
     index: "snort-%{+yyyy.MM.dd}"
   
   setup.template.name: "snort"
   setup.template.pattern: "snort-*"
   setup.ilm.enabled: false
   ```

3. **Iniciar Filebeat**:
   ```bash
   sudo systemctl enable filebeat
   sudo systemctl start filebeat
   ```

4. **Crear dashboard en Kibana**:
   - Acceder a Kibana en http://localhost:5601
   - Ir a Management > Stack Management > Index Patterns
   - Crear un nuevo index pattern para "snort-*"
   - Ir a Dashboard y crear un nuevo dashboard para visualizar alertas de Snort

## Configuración de Visualización y Alertas

### Configuración de Grafana

1. **Añadir datasource de Prometheus**:
   - Acceder a Grafana en http://localhost:3000
   - Ir a Configuration > Data Sources
   - Añadir Prometheus con URL http://localhost:9090
   - Guardar y probar

2. **Importar dashboards predefinidos**:
   - Ir a Create > Import
   - Importar dashboards populares por ID:
     - 1860 (Node Exporter Full)
     - 11074 (SNMP Statistics)
     - 11176 (Network Traffic)

3. **Crear dashboard personalizado para monitoreo de red**:
   - Crear un nuevo dashboard
   - Añadir paneles para:
     - Tráfico de red por interfaz
     - Errores de red
     - Latencia
     - Disponibilidad de dispositivos

### Configuración de Alert Manager

1. **Instalar Alert Manager**:
   ```bash
   cd /tmp
   wget https://github.com/prometheus/alertmanager/releases/download/v0.25.0/alertmanager-0.25.0.linux-amd64.tar.gz
   tar xzf alertmanager-0.25.0.linux-amd64.tar.gz
   
   sudo cp alertmanager-0.25.0.linux-amd64/alertmanager /usr/local/bin/
   sudo cp alertmanager-0.25.0.linux-amd64/amtool /usr/local/bin/
   
   sudo mkdir -p /etc/alertmanager
   ```

2. **Configurar Alert Manager**:
   ```bash
   sudo nano /etc/alertmanager/alertmanager.yml
   ```
   
   Contenido básico:
   ```yaml
   global:
     resolve_timeout: 5m
     smtp_smarthost: 'smtp.example.org:587'
     smtp_from: 'alertmanager@example.org'
     smtp_auth_username: 'alertmanager'
     smtp_auth_password: 'password'
   
   route:
     group_by: ['alertname', 'instance']
     group_wait: 30s
     group_interval: 5m
     repeat_interval: 4h
     receiver: 'email'
   
   receivers:
   - name: 'email'
     email_configs:
     - to: 'admin@example.org'
   ```

3. **Crear servicio systemd**:
   ```bash
   sudo nano /etc/systemd/system/alertmanager.service
   ```
   
   Contenido:
   ```ini
   [Unit]
   Description=Alertmanager
   Wants=network-online.target
   After=network-online.target
   
   [Service]
   User=prometheus
   Group=prometheus
   Type=simple
   ExecStart=/usr/local/bin/alertmanager \
     --config.file=/etc/alertmanager/alertmanager.yml \
     --storage.path=/var/lib/alertmanager
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Iniciar Alert Manager**:
   ```bash
   sudo mkdir -p /var/lib/alertmanager
   sudo chown prometheus:prometheus /var/lib/alertmanager
   
   sudo systemctl daemon-reload
   sudo systemctl enable alertmanager
   sudo systemctl start alertmanager
   ```

5. **Configurar reglas de alerta en Prometheus**:
   ```bash
   sudo mkdir -p /etc/prometheus/rules
   sudo nano /etc/prometheus/rules/network.rules.yml
   ```
   
   Contenido:
   ```yaml
   groups:
   - name: network
     rules:
     - alert: HighNetworkTraffic
       expr: rate(node_network_receive_bytes_total[5m]) + rate(node_network_transmit_bytes_total[5m]) > 100000000
       for: 5m
       labels:
         severity: warning
       annotations:
         summary: "High network traffic on {{ $labels.instance }}"
         description: "Network traffic is above 100Mbps on {{ $labels.instance }} (current value: {{ $value | humanize }})"
     
     - alert: NetworkInterfaceDown
       expr: node_network_up == 0
       for: 1m
       labels:
         severity: critical
       annotations:
         summary: "Network interface down on {{ $labels.instance }}"
         description: "Network interface {{ $labels.device }} is down on {{ $labels.instance }}"
   ```

6. **Actualizar configuración de Prometheus**:
   ```bash
   sudo nano /etc/prometheus/prometheus.yml
   ```
   
   Añadir:
   ```yaml
   rule_files:
     - "rules/network.rules.yml"
   
   alerting:
     alertmanagers:
     - static_configs:
       - targets:
         - localhost:9093
   ```

7. **Reiniciar Prometheus**:
   ```bash
   sudo systemctl restart prometheus
   ```

## Integración con Infraestructura Existente

### Integración con Active Directory/LDAP

1. **Configurar autenticación LDAP en Grafana**:
   ```bash
   sudo nano /etc/grafana/grafana.ini
   ```
   
   Añadir:
   ```ini
   [auth.ldap]
   enabled = true
   config_file = /etc/grafana/ldap.toml
   allow_sign_up = true
   ```

2. **Configurar LDAP**:
   ```bash
   sudo nano /etc/grafana/ldap.toml
   ```
   
   Contenido básico:
   ```toml
   [[servers]]
   host = "ldap.example.org"
   port = 389
   use_ssl = false
   start_tls = true
   bind_dn = "cn=admin,dc=example,dc=org"
   bind_password = "admin"
   search_filter = "(sAMAccountName=%s)"
   search_base_dns = ["dc=example,dc=org"]
   
   [servers.attributes]
   name = "givenName"
   surname = "sn"
   username = "sAMAccountName"
   member_of = "memberOf"
   email = "mail"
   
   [[servers.group_mappings]]
   group_dn = "cn=admins,dc=example,dc=org"
   org_role = "Admin"
   
   [[servers.group_mappings]]
   group_dn = "cn=users,dc=example,dc=org"
   org_role = "Editor"
   ```

### Integración con Sistema de Tickets

1. **Configurar webhook en Alert Manager**:
   ```bash
   sudo nano /etc/alertmanager/alertmanager.yml
   ```
   
   Añadir:
   ```yaml
   receivers:
   - name: 'ticket-system'
     webhook_configs:
     - url: 'http://ticketing-system.example.org/api/v1/alerts'
       send_resolved: true
       http_config:
         basic_auth:
           username: 'alertmanager'
           password: 'password'
   ```

2. **Actualizar ruta de alertas**:
   ```yaml
   route:
     group_by: ['alertname', 'instance']
     group_wait: 30s
     group_interval: 5m
     repeat_interval: 4h
     receiver: 'ticket-system'
   ```

3. **Reiniciar Alert Manager**:
   ```bash
   sudo systemctl restart alertmanager
   ```

### Integración con CMDB

1. **Crear script para sincronizar inventario**:
   ```bash
   sudo nano /usr/local/bin/sync-cmdb.py
   ```
   
   Contenido básico:
   ```python
   #!/usr/bin/env python3
   
   import requests
   import json
   import subprocess
   import yaml
   
   # Obtener dispositivos de CMDB
   cmdb_url = "http://cmdb.example.org/api/v1/devices"
   cmdb_auth = ("username", "password")
   
   response = requests.get(cmdb_url, auth=cmdb_auth)
   devices = response.json()
   
   # Preparar configuración para Prometheus
   prometheus_config = {
       "global": {
           "scrape_interval": "15s",
           "evaluation_interval": "15s"
       },
       "alerting": {
           "alertmanagers": [
               {
                   "static_configs": [
                       {
                           "targets": ["localhost:9093"]
                       }
                   ]
               }
           ]
       },
       "rule_files": ["rules/network.rules.yml"],
       "scrape_configs": [
           {
               "job_name": "prometheus",
               "static_configs": [
                   {
                       "targets": ["localhost:9090"]
                   }
               ]
           }
       ]
   }
   
   # Añadir dispositivos de CMDB
   snmp_targets = []
   for device in devices:
       if device["type"] == "network":
           snmp_targets.append(device["ip_address"])
   
   if snmp_targets:
       prometheus_config["scrape_configs"].append({
           "job_name": "snmp",
           "static_configs": [
               {
                   "targets": snmp_targets
               }
           ],
           "metrics_path": "/snmp",
           "params": {
               "module": ["if_mib"]
           },
           "relabel_configs": [
               {
                   "source_labels": ["__address__"],
                   "target_label": "__param_target"
               },
               {
                   "source_labels": ["__param_target"],
                   "target_label": "instance"
               },
               {
                   "target_label": "__address__",
                   "replacement": "localhost:9116"
               }
           ]
       })
   
   # Guardar configuración
   with open("/etc/prometheus/prometheus.yml.new", "w") as f:
       yaml.dump(prometheus_config, f, default_flow_style=False)
   
   # Validar configuración
   result = subprocess.run(["promtool", "check", "config", "/etc/prometheus/prometheus.yml.new"], capture_output=True)
   
   if result.returncode == 0:
       subprocess.run(["mv", "/etc/prometheus/prometheus.yml.new", "/etc/prometheus/prometheus.yml"])
       subprocess.run(["systemctl", "reload", "prometheus"])
       print("Configuración actualizada correctamente")
   else:
       print("Error en la configuración:", result.stderr.decode())
   ```

2. **Hacer ejecutable el script y programarlo**:
   ```bash
   sudo chmod +x /usr/local/bin/sync-cmdb.py
   
   sudo crontab -e
   ```
   
   Añadir:
   ```
   # Sincronizar con CMDB diariamente
   0 2 * * * /usr/local/bin/sync-cmdb.py > /var/log/sync-cmdb.log 2>&1
   ```

## Verificación y Pruebas

### Verificación de Componentes

1. **Verificar Prometheus**:
   ```bash
   curl http://localhost:9090/-/healthy
   ```

2. **Verificar Grafana**:
   ```bash
   curl http://localhost:3000/api/health
   ```

3. **Verificar Elasticsearch**:
   ```bash
   curl -X GET "localhost:9200/_cluster/health?pretty"
   ```

4. **Verificar Snort**:
   ```bash
   ps aux | grep snort
   sudo snort -V
   ```

### Pruebas de Monitoreo

1. **Prueba de recopilación de métricas**:
   - Acceder a Prometheus en http://localhost:9090
   - Ir a Status > Targets para verificar que todos los objetivos están UP
   - Ejecutar consulta `up` para verificar disponibilidad de objetivos

2. **Prueba de visualización**:
   - Acceder a Grafana en http://localhost:3000
   - Verificar que los dashboards muestran datos
   - Probar diferentes rangos de tiempo

3. **Prueba de alertas**:
   - Simular una condición de alerta (por ejemplo, alta utilización de CPU)
   - Verificar que la alerta se activa en Prometheus
   - Verificar que Alert Manager recibe y procesa la alerta
   - Verificar que la notificación se envía correctamente

### Pruebas de Seguridad

1. **Prueba de detección de intrusiones**:
   - Generar tráfico sospechoso (por ejemplo, escaneo de puertos)
   - Verificar que Snort detecta y alerta sobre la actividad
   - Verificar que las alertas se registran correctamente

2. **Prueba de captura de paquetes**:
   - Ejecutar una captura manual:
     ```bash
     sudo /usr/local/bin/capture-packets.sh eth0 60 "port 80"
     ```
   - Verificar que el archivo PCAP se crea correctamente
   - Analizar el archivo con tshark:
     ```bash
     tshark -r /var/lib/pcap/capture-*.pcap | head
     ```

## Mantenimiento y Operaciones

### Tareas de Mantenimiento Regulares

1. **Actualización de componentes**:
   ```bash
   # Actualizar sistema
   sudo apt-get update
   sudo apt-get upgrade -y
   
   # Actualizar Prometheus y exporters
   # (Seguir procedimiento de actualización específico)
   
   # Actualizar reglas de Snort
   cd /etc/snort/rules
   sudo wget https://www.snort.org/downloads/community/snort3-community-rules.tar.gz
   sudo tar -xzf snort3-community-rules.tar.gz
   sudo rm snort3-community-rules.tar.gz
   sudo systemctl restart snort
   ```

2. **Rotación de logs**:
   ```bash
   sudo nano /etc/logrotate.d/monitoring
   ```
   
   Contenido:
   ```
   /var/log/prometheus/*.log
   /var/log/grafana/*.log
   /var/log/elasticsearch/*.log
   /var/log/snort/*.log
   {
       daily
       missingok
       rotate 7
       compress
       delaycompress
       notifempty
       create 0640 prometheus prometheus
       sharedscripts
       postrotate
           systemctl reload prometheus grafana-server elasticsearch snort
       endscript
   }
   ```

3. **Respaldo de configuraciones**:
   ```bash
   sudo nano /usr/local/bin/backup-configs.sh
   ```
   
   Contenido:
   ```bash
   #!/bin/bash
   
   BACKUP_DIR="/var/backups/monitoring"
   TIMESTAMP=$(date +%Y%m%d-%H%M%S)
   
   mkdir -p $BACKUP_DIR
   
   # Respaldar configuraciones
   tar -czf $BACKUP_DIR/configs-$TIMESTAMP.tar.gz \
       /etc/prometheus \
       /etc/grafana \
       /etc/snort \
       /etc/alertmanager \
       /etc/elasticsearch \
       /etc/kibana
   
   # Mantener solo los últimos 7 respaldos
   ls -t $BACKUP_DIR/configs-*.tar.gz | tail -n +8 | xargs rm -f
   ```

4. **Hacer ejecutable el script y programarlo**:
   ```bash
   sudo chmod +x /usr/local/bin/backup-configs.sh
   
   sudo crontab -e
   ```
   
   Añadir:
   ```
   # Respaldar configuraciones semanalmente
   0 3 * * 0 /usr/local/bin/backup-configs.sh > /dev/null 2>&1
   ```

### Procedimientos Operativos

1. **Reinicio de servicios**:
   ```bash
   # Reiniciar Prometheus
   sudo systemctl restart prometheus
   
   # Reiniciar Grafana
   sudo systemctl restart grafana-server
   
   # Reiniciar Elasticsearch
   sudo systemctl restart elasticsearch
   
   # Reiniciar Snort
   sudo systemctl restart snort
   ```

2. **Verificación de estado**:
   ```bash
   # Verificar estado de todos los servicios
   sudo systemctl status prometheus grafana-server elasticsearch kibana snort alertmanager
   
   # Verificar uso de disco
   df -h
   
   # Verificar uso de memoria
   free -h
   
   # Verificar carga del sistema
   uptime
   ```

3. **Troubleshooting**:
   ```bash
   # Verificar logs de Prometheus
   sudo journalctl -u prometheus
   
   # Verificar logs de Grafana
   sudo journalctl -u grafana-server
   
   # Verificar logs de Elasticsearch
   sudo journalctl -u elasticsearch
   
   # Verificar logs de Snort
   sudo cat /var/log/snort/alert_fast.txt
   ```

### Documentación

1. **Inventario de dispositivos monitoreados**:
   - Mantener una lista actualizada de todos los dispositivos monitoreados
   - Incluir información como dirección IP, tipo de dispositivo, ubicación, etc.

2. **Diagrama de red**:
   - Mantener un diagrama actualizado de la red
   - Incluir ubicación de sensores, colectores y servidores de monitoreo

3. **Procedimientos de respuesta a incidentes**:
   - Documentar procedimientos para diferentes tipos de alertas
   - Incluir información de contacto para escalamiento

4. **Registro de cambios**:
   - Mantener un registro de todos los cambios realizados en la infraestructura de monitoreo
   - Incluir fecha, descripción del cambio, responsable y resultado

## Referencias

1. Prometheus Documentation: [https://prometheus.io/docs/](https://prometheus.io/docs/)
2. Grafana Documentation: [https://grafana.com/docs/](https://grafana.com/docs/)
3. Snort Documentation: [https://www.snort.org/documents](https://www.snort.org/documents)
4. Elasticsearch Documentation: [https://www.elastic.co/guide/index.html](https://www.elastic.co/guide/index.html)
5. Wireshark Documentation: [https://www.wireshark.org/docs/](https://www.wireshark.org/docs/)
6. NetFlow Documentation: [https://www.cisco.com/c/en/us/products/ios-nx-os-software/netflow-version-9/index.html](https://www.cisco.com/c/en/us/products/ios-nx-os-software/netflow-version-9/index.html)
7. NIST SP 800-137: Information Security Continuous Monitoring: [https://csrc.nist.gov/publications/detail/sp/800-137/final](https://csrc.nist.gov/publications/detail/sp/800-137/final)

