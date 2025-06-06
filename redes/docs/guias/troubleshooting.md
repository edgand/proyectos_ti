# Guía de Solución de Problemas: Redes, Telecomunicaciones y Herramientas de Monitoreo

Esta guía proporciona procedimientos estructurados para diagnosticar y resolver problemas comunes en sistemas de monitoreo de redes y telecomunicaciones. Está diseñada para ayudar a los administradores de red y personal de soporte a identificar y solucionar problemas de manera eficiente.

## Índice

1. [Metodología de Troubleshooting](#metodología-de-troubleshooting)
2. [Problemas de Conectividad de Red](#problemas-de-conectividad-de-red)
3. [Problemas de Rendimiento de Red](#problemas-de-rendimiento-de-red)
4. [Problemas con Herramientas de Monitoreo](#problemas-con-herramientas-de-monitoreo)
5. [Problemas de Alertas y Notificaciones](#problemas-de-alertas-y-notificaciones)
6. [Problemas de Seguridad y Detección de Intrusiones](#problemas-de-seguridad-y-detección-de-intrusiones)
7. [Problemas de Almacenamiento y Base de Datos](#problemas-de-almacenamiento-y-base-de-datos)
8. [Problemas de Visualización y Dashboards](#problemas-de-visualización-y-dashboards)
9. [Herramientas de Diagnóstico](#herramientas-de-diagnóstico)
10. [Escenarios Comunes de Troubleshooting](#escenarios-comunes-de-troubleshooting)

## Metodología de Troubleshooting

### Enfoque Estructurado

1. **Identificar el problema**
   - Recopilar información sobre síntomas
   - Determinar alcance (usuarios afectados, servicios impactados)
   - Establecer línea temporal (cuándo comenzó, cambios recientes)

2. **Aislar el problema**
   - Determinar componentes afectados
   - Verificar conectividad y dependencias
   - Reducir el alcance del problema

3. **Diagnosticar la causa raíz**
   - Analizar logs y alertas
   - Realizar pruebas específicas
   - Correlacionar eventos

4. **Implementar solución**
   - Aplicar correcciones temporales si es necesario
   - Implementar solución permanente
   - Documentar acciones realizadas

5. **Verificar resolución**
   - Confirmar que el problema está resuelto
   - Verificar que no hay efectos secundarios
   - Monitorear para prevenir recurrencia

6. **Documentar y comunicar**
   - Registrar problema y solución
   - Actualizar documentación si es necesario
   - Comunicar a partes interesadas

### Herramientas Esenciales

- **Herramientas de red**: ping, traceroute, nslookup, dig, nmap, tcpdump, wireshark
- **Herramientas de sistema**: top, htop, iostat, vmstat, df, du, journalctl, systemctl
- **Herramientas de monitoreo**: CLI de Prometheus, Grafana, Elasticsearch, Snort

### Recopilación de Información

- **Preguntas clave**:
  - ¿Cuándo comenzó el problema?
  - ¿Qué cambios se realizaron recientemente?
  - ¿Quién está afectado?
  - ¿El problema es constante o intermitente?
  - ¿Hay patrones temporales o de carga?

- **Información a recopilar**:
  - Logs de sistema y aplicaciones
  - Alertas activas y recientes
  - Métricas de rendimiento
  - Configuraciones relevantes
  - Capturas de pantalla de errores

## Problemas de Conectividad de Red

### Dispositivo No Responde a Ping

#### Síntomas
- No hay respuesta a ping
- Dispositivo aparece como "DOWN" en sistema de monitoreo
- No se puede acceder a servicios del dispositivo

#### Diagnóstico
1. **Verificar conectividad física**
   ```bash
   # Verificar estado de interfaz local
   ip link show
   
   # Verificar tabla ARP
   arp -a
   ```

2. **Verificar conectividad de red**
   ```bash
   # Ping al gateway
   ping -c 4 $(ip route | grep default | awk '{print $3}')
   
   # Traceroute al dispositivo
   traceroute <ip_dispositivo>
   ```

3. **Verificar firewall y ACLs**
   ```bash
   # Verificar reglas de firewall local
   sudo iptables -L
   
   # Escanear puertos (si está permitido)
   nmap -p 22,80,443 <ip_dispositivo>
   ```

#### Soluciones
1. **Problemas físicos**
   - Verificar cables y conexiones
   - Verificar estado de puertos en switches
   - Reiniciar interfaces de red

2. **Problemas de configuración**
   - Verificar configuración IP (dirección, máscara, gateway)
   - Verificar configuración DNS
   - Verificar reglas de firewall

3. **Problemas de dispositivo**
   - Reiniciar dispositivo si es posible
   - Verificar logs del dispositivo
   - Verificar estado de servicios

### Pérdida de Paquetes

#### Síntomas
- Ping muestra pérdida de paquetes
- Conexiones lentas o intermitentes
- Aplicaciones se desconectan aleatoriamente

#### Diagnóstico
1. **Medir pérdida de paquetes**
   ```bash
   # Ping extendido para medir pérdida
   ping -c 100 <ip_destino>
   
   # Prueba MTR para análisis detallado
   mtr -n <ip_destino>
   ```

2. **Verificar interfaces**
   ```bash
   # Verificar errores en interfaces
   ip -s link show
   
   # Verificar drops en interfaces
   ifconfig | grep -E "RX|TX"
   ```

3. **Analizar tráfico**
   ```bash
   # Capturar tráfico para análisis
   tcpdump -i <interfaz> host <ip_destino> -w captura.pcap
   ```

#### Soluciones
1. **Problemas físicos**
   - Verificar calidad de cables y conexiones
   - Verificar si hay interferencias electromagnéticas
   - Reemplazar equipos de red defectuosos

2. **Problemas de congestión**
   - Implementar QoS para priorizar tráfico crítico
   - Aumentar ancho de banda si es necesario
   - Optimizar rutas de red

3. **Problemas de configuración**
   - Ajustar MTU para evitar fragmentación
   - Verificar duplex mismatch
   - Optimizar buffers de red

### Problemas de DNS

#### Síntomas
- Resolución de nombres lenta o fallida
- Errores "Host not found" o similares
- Ping funciona con IP pero no con nombre

#### Diagnóstico
1. **Verificar configuración DNS**
   ```bash
   # Verificar servidores DNS configurados
   cat /etc/resolv.conf
   
   # Verificar resolución de nombres
   nslookup <nombre_host>
   dig <nombre_host>
   ```

2. **Verificar conectividad a servidores DNS**
   ```bash
   # Ping a servidores DNS
   ping -c 4 <ip_servidor_dns>
   
   # Verificar puerto DNS
   nc -zv <ip_servidor_dns> 53
   ```

3. **Verificar caché DNS**
   ```bash
   # Limpiar caché DNS (según sistema)
   sudo systemd-resolve --flush-caches
   ```

#### Soluciones
1. **Problemas de configuración**
   - Corregir entradas en /etc/resolv.conf
   - Verificar orden de búsqueda de dominios
   - Configurar servidores DNS alternativos

2. **Problemas de servidor DNS**
   - Reiniciar servicio DNS si es local
   - Verificar registros DNS en servidor autoritativo
   - Implementar DNS redundante

3. **Problemas de caché**
   - Limpiar caché DNS local
   - Verificar TTL de registros DNS
   - Implementar servidor DNS local para caching

## Problemas de Rendimiento de Red

### Latencia Alta

#### Síntomas
- Tiempos de respuesta elevados
- Aplicaciones lentas
- Valores de ping elevados

#### Diagnóstico
1. **Medir latencia**
   ```bash
   # Ping para medir latencia
   ping -c 20 <ip_destino>
   
   # Análisis detallado con MTR
   mtr -n -c 100 <ip_destino>
   ```

2. **Identificar cuellos de botella**
   ```bash
   # Verificar uso de interfaces
   iftop -i <interfaz>
   
   # Analizar rutas
   traceroute -n <ip_destino>
   ```

3. **Verificar saturación**
   ```bash
   # Verificar carga de red
   netstat -s | grep -E "segments retransmited|failed connection"
   ```

#### Soluciones
1. **Optimización de rutas**
   - Verificar y optimizar rutas de red
   - Implementar rutas estáticas para tráfico crítico
   - Considerar uso de SD-WAN para optimización

2. **Reducción de congestión**
   - Implementar QoS
   - Aumentar ancho de banda
   - Distribuir carga entre múltiples enlaces

3. **Optimización de aplicaciones**
   - Implementar caching
   - Optimizar protocolos de aplicación
   - Reducir chattiness de aplicaciones

### Ancho de Banda Insuficiente

#### Síntomas
- Transferencias de archivos lentas
- Streaming con buffering frecuente
- Saturación de enlaces

#### Diagnóstico
1. **Medir uso de ancho de banda**
   ```bash
   # Monitorear uso de ancho de banda
   iftop -i <interfaz>
   
   # Análisis detallado
   nethogs <interfaz>
   ```

2. **Identificar consumidores principales**
   ```bash
   # Ver conexiones activas y uso
   ss -tunapl
   
   # Analizar flujos de red
   nfdump -R /var/lib/netflow/nfcapd.* -s ip/bytes -n 10
   ```

3. **Verificar capacidad de enlaces**
   ```bash
   # Verificar velocidad de interfaces
   ethtool <interfaz>
   ```

#### Soluciones
1. **Gestión de ancho de banda**
   - Implementar traffic shaping
   - Configurar límites de ancho de banda por servicio
   - Programar transferencias grandes en horarios de baja demanda

2. **Optimización de infraestructura**
   - Aumentar capacidad de enlaces críticos
   - Implementar enlaces redundantes
   - Utilizar tecnologías de compresión WAN

3. **Políticas de uso**
   - Implementar políticas de uso aceptable
   - Bloquear o limitar tráfico no esencial
   - Priorizar aplicaciones críticas

### Problemas de Enrutamiento

#### Síntomas
- Rutas subóptimas
- Pérdida de conectividad intermitente
- Asimetría en rutas de ida y vuelta

#### Diagnóstico
1. **Analizar tablas de enrutamiento**
   ```bash
   # Verificar tabla de rutas
   ip route
   
   # Verificar ruta específica
   ip route get <ip_destino>
   ```

2. **Verificar protocolos de enrutamiento**
   ```bash
   # Verificar estado de BGP (si aplica)
   sudo vtysh -c "show ip bgp summary"
   
   # Verificar estado de OSPF (si aplica)
   sudo vtysh -c "show ip ospf neighbor"
   ```

3. **Analizar rutas de ida y vuelta**
   ```bash
   # Traceroute de ida
   traceroute -n <ip_destino>
   
   # Solicitar traceroute de vuelta (si es posible)
   ```

#### Soluciones
1. **Corrección de configuración**
   - Verificar y corregir configuración de protocolos de enrutamiento
   - Ajustar métricas y preferencias de rutas
   - Corregir filtros de rutas

2. **Optimización de rutas**
   - Implementar rutas estáticas para casos críticos
   - Ajustar timers de protocolos de enrutamiento
   - Implementar route-maps para control de tráfico

3. **Redundancia y failover**
   - Implementar múltiples rutas
   - Configurar ECMP (Equal-Cost Multi-Path)
   - Implementar fast failover

## Problemas con Herramientas de Monitoreo

### Prometheus No Recopila Métricas

#### Síntomas
- Gráficos vacíos en Grafana
- Errores "no data" en consultas
- Targets en estado "down" en Prometheus

#### Diagnóstico
1. **Verificar estado de Prometheus**
   ```bash
   # Verificar estado del servicio
   sudo systemctl status prometheus
   
   # Verificar logs
   sudo journalctl -u prometheus --since "1 hour ago"
   ```

2. **Verificar conectividad a targets**
   ```bash
   # Verificar accesibilidad de endpoint
   curl -s http://<ip_target>:<puerto>/metrics | head
   
   # Verificar conectividad de red
   ping -c 4 <ip_target>
   ```

3. **Verificar configuración**
   ```bash
   # Validar configuración
   promtool check config /etc/prometheus/prometheus.yml
   
   # Verificar targets en UI
   curl -s http://localhost:9090/api/v1/targets | jq
   ```

#### Soluciones
1. **Problemas de servicio**
   - Reiniciar servicio de Prometheus
   - Verificar permisos de archivos y directorios
   - Verificar límites de recursos (memoria, file descriptors)

2. **Problemas de configuración**
   - Corregir errores en prometheus.yml
   - Verificar job_name y static_configs
   - Ajustar scrape_interval si es necesario

3. **Problemas de exporters**
   - Reiniciar servicios de exporters
   - Verificar configuración de exporters
   - Verificar permisos y accesibilidad

### Node Exporter No Funciona

#### Síntomas
- No hay métricas de host en Prometheus
- Target de node_exporter en estado "down"
- No se puede acceder al endpoint /metrics

#### Diagnóstico
1. **Verificar estado del servicio**
   ```bash
   # Verificar estado
   sudo systemctl status node_exporter
   
   # Verificar logs
   sudo journalctl -u node_exporter --since "1 hour ago"
   ```

2. **Verificar accesibilidad**
   ```bash
   # Verificar endpoint localmente
   curl -s http://localhost:9100/metrics | head
   
   # Verificar puerto
   ss -tulpn | grep 9100
   ```

3. **Verificar permisos**
   ```bash
   # Verificar usuario y permisos
   ps aux | grep node_exporter
   
   # Verificar permisos de archivos
   ls -la /usr/local/bin/node_exporter
   ```

#### Soluciones
1. **Problemas de servicio**
   - Reiniciar node_exporter
   - Verificar configuración de systemd
   - Verificar permisos de ejecución

2. **Problemas de red**
   - Verificar reglas de firewall
   - Verificar configuración de red
   - Verificar binding de interfaz

3. **Problemas de configuración**
   - Verificar flags de inicio
   - Verificar collectors habilitados
   - Ajustar opciones según necesidad

### Grafana No Muestra Datos

#### Síntomas
- Paneles vacíos o con error "No data"
- Mensajes de error en consultas
- Gráficos incompletos

#### Diagnóstico
1. **Verificar datasource**
   ```bash
   # Probar conexión a Prometheus
   curl -s http://localhost:9090/api/v1/query?query=up | jq
   
   # Verificar configuración de datasource en Grafana
   curl -s -u admin:admin http://localhost:3000/api/datasources
   ```

2. **Verificar consultas**
   ```bash
   # Probar consulta directamente en Prometheus
   curl -s "http://localhost:9090/api/v1/query?query=node_memory_MemTotal_bytes" | jq
   ```

3. **Verificar permisos y roles**
   ```bash
   # Verificar permisos de usuario en Grafana
   curl -s -u admin:admin http://localhost:3000/api/org/users
   ```

#### Soluciones
1. **Problemas de datasource**
   - Verificar URL y credenciales del datasource
   - Probar conexión desde Grafana UI
   - Reiniciar Grafana y Prometheus

2. **Problemas de consultas**
   - Corregir sintaxis de consultas PromQL
   - Verificar nombres de métricas
   - Ajustar rangos de tiempo

3. **Problemas de permisos**
   - Verificar permisos de usuario
   - Verificar permisos de dashboard
   - Verificar configuración de anonymous access

### Alertas No Se Disparan

#### Síntomas
- Condiciones de alerta se cumplen pero no hay notificaciones
- Alertas en estado "pending" pero nunca "firing"
- No hay registro de alertas enviadas

#### Diagnóstico
1. **Verificar reglas de alerta**
   ```bash
   # Validar reglas
   promtool check rules /etc/prometheus/rules/*.yml
   
   # Verificar estado de reglas
   curl -s http://localhost:9090/api/v1/rules | jq
   ```

2. **Verificar AlertManager**
   ```bash
   # Verificar estado del servicio
   sudo systemctl status alertmanager
   
   # Verificar configuración
   amtool check-config /etc/alertmanager/alertmanager.yml
   
   # Verificar alertas activas
   curl -s http://localhost:9093/api/v1/alerts | jq
   ```

3. **Verificar integración**
   ```bash
   # Verificar configuración de Prometheus
   grep alertmanager /etc/prometheus/prometheus.yml
   
   # Verificar conectividad
   curl -s http://localhost:9093/-/healthy
   ```

#### Soluciones
1. **Problemas de reglas**
   - Corregir sintaxis de reglas
   - Ajustar umbrales y duración
   - Verificar expresiones PromQL

2. **Problemas de AlertManager**
   - Reiniciar AlertManager
   - Corregir configuración de rutas y receptores
   - Verificar configuración de inhibición y silencio

3. **Problemas de integración**
   - Verificar configuración de alertmanagers en Prometheus
   - Verificar conectividad entre Prometheus y AlertManager
   - Verificar configuración de receptores (email, Slack, etc.)

## Problemas de Rendimiento de Red

### Snort No Detecta Amenazas

#### Síntomas
- No hay alertas de seguridad
- Tráfico malicioso no detectado
- Logs de Snort vacíos o mínimos

#### Diagnóstico
1. **Verificar estado de Snort**
   ```bash
   # Verificar proceso
   ps aux | grep snort
   
   # Verificar logs
   sudo tail -f /var/log/snort/alert
   ```

2. **Verificar configuración**
   ```bash
   # Validar configuración
   sudo snort -T -c /etc/snort/snort.conf
   
   # Verificar reglas cargadas
   sudo snort -c /etc/snort/snort.conf --dump-rule-meta
   ```

3. **Verificar captura de tráfico**
   ```bash
   # Verificar interfaz de captura
   sudo snort -c /etc/snort/snort.conf -v
   
   # Verificar tráfico en interfaz
   sudo tcpdump -i <interfaz> -n
   ```

#### Soluciones
1. **Problemas de configuración**
   - Verificar HOME_NET y EXTERNAL_NET
   - Actualizar reglas
   - Habilitar preprocesadores relevantes

2. **Problemas de captura**
   - Verificar modo promiscuo
   - Verificar mirror/span port
   - Verificar posición de sensor en red

3. **Problemas de reglas**
   - Actualizar conjuntos de reglas
   - Ajustar sensibilidad de reglas
   - Añadir reglas personalizadas para amenazas específicas

### Elasticsearch No Indexa Logs

#### Síntomas
- No hay datos nuevos en índices
- Kibana muestra "No results found"
- Filebeat reporta errores de envío

#### Diagnóstico
1. **Verificar estado de Elasticsearch**
   ```bash
   # Verificar salud del cluster
   curl -X GET "localhost:9200/_cluster/health?pretty"
   
   # Verificar índices
   curl -X GET "localhost:9200/_cat/indices?v"
   ```

2. **Verificar Filebeat**
   ```bash
   # Verificar estado
   sudo systemctl status filebeat
   
   # Verificar logs
   sudo journalctl -u filebeat --since "1 hour ago"
   
   # Verificar configuración
   sudo filebeat test config -c /etc/filebeat/filebeat.yml
   ```

3. **Verificar conectividad y permisos**
   ```bash
   # Verificar conectividad
   curl -X GET "localhost:9200"
   
   # Verificar permisos de archivos de log
   ls -la /var/log/snort/
   ```

#### Soluciones
1. **Problemas de Elasticsearch**
   - Verificar espacio en disco
   - Ajustar límites de memoria
   - Verificar políticas de índices

2. **Problemas de Filebeat**
   - Reiniciar servicio
   - Corregir configuración de inputs y outputs
   - Verificar permisos de archivos

3. **Problemas de integración**
   - Verificar credenciales
   - Verificar formato de índices
   - Ajustar pipeline de procesamiento

## Problemas de Almacenamiento y Base de Datos

### Prometheus Se Queda Sin Espacio

#### Síntomas
- Errores de escritura en logs
- Prometheus se reinicia o falla
- Alertas de espacio en disco

#### Diagnóstico
1. **Verificar uso de disco**
   ```bash
   # Verificar espacio total
   df -h /var/lib/prometheus
   
   # Verificar tamaño de TSDB
   du -sh /var/lib/prometheus/
   ```

2. **Verificar configuración de retención**
   ```bash
   # Verificar flags de inicio
   ps aux | grep prometheus
   
   # Verificar configuración
   grep storage.tsdb /etc/systemd/system/prometheus.service
   ```

3. **Verificar métricas de Prometheus**
   ```bash
   # Verificar métricas de almacenamiento
   curl -s http://localhost:9090/api/v1/query?query=prometheus_tsdb_storage_blocks_bytes | jq
   ```

#### Soluciones
1. **Ajustar retención**
   - Reducir período de retención
   - Configurar --storage.tsdb.retention.time
   - Configurar --storage.tsdb.retention.size

2. **Optimizar almacenamiento**
   - Reducir frecuencia de scraping para targets no críticos
   - Filtrar métricas innecesarias
   - Implementar agregación para métricas de alta cardinalidad

3. **Escalar infraestructura**
   - Añadir más espacio en disco
   - Implementar almacenamiento remoto
   - Considerar federación para distribuir carga

### Elasticsearch Con Alto Uso de Recursos

#### Síntomas
- Alto uso de CPU y memoria
- Respuesta lenta de consultas
- Nodos desconectándose del cluster

#### Diagnóstico
1. **Verificar uso de recursos**
   ```bash
   # Verificar uso de memoria
   free -h
   
   # Verificar uso de CPU
   top -b -n 1 | grep java
   ```

2. **Verificar configuración de JVM**
   ```bash
   # Verificar configuración
   cat /etc/elasticsearch/jvm.options
   
   # Verificar uso de heap
   curl -X GET "localhost:9200/_nodes/stats/jvm?pretty"
   ```

3. **Verificar estado del cluster**
   ```bash
   # Verificar salud
   curl -X GET "localhost:9200/_cluster/health?pretty"
   
   # Verificar estadísticas de índices
   curl -X GET "localhost:9200/_stats?pretty"
   ```

#### Soluciones
1. **Optimizar JVM**
   - Ajustar tamaño de heap (50% de RAM disponible, máx 31GB)
   - Configurar garbage collection
   - Ajustar opciones de JVM

2. **Optimizar índices**
   - Implementar políticas de lifecycle
   - Optimizar mappings
   - Consolidar índices pequeños

3. **Escalar cluster**
   - Añadir nodos
   - Distribuir shards
   - Implementar hot-warm architecture

## Problemas de Visualización y Dashboards

### Grafana Lento o No Responde

#### Síntomas
- Carga lenta de dashboards
- Timeout en consultas
- Alta utilización de recursos

#### Diagnóstico
1. **Verificar recursos del sistema**
   ```bash
   # Verificar uso de CPU y memoria
   top -b -n 1 | grep grafana
   
   # Verificar logs
   sudo journalctl -u grafana-server --since "1 hour ago"
   ```

2. **Verificar consultas**
   ```bash
   # Verificar tiempo de respuesta de Prometheus
   time curl -s "http://localhost:9090/api/v1/query?query=up"
   
   # Verificar logs de consultas lentas
   grep "slow queries" /var/log/grafana/grafana.log
   ```

3. **Verificar configuración**
   ```bash
   # Verificar límites de conexiones
   grep max_open_files /etc/systemd/system/grafana-server.service
   
   # Verificar configuración de base de datos
   grep database /etc/grafana/grafana.ini
   ```

#### Soluciones
1. **Optimizar consultas**
   - Simplificar consultas complejas
   - Reducir rango de tiempo en dashboards
   - Aumentar intervalo de refresco

2. **Optimizar recursos**
   - Aumentar límites de memoria
   - Optimizar base de datos de Grafana
   - Implementar caching

3. **Escalar infraestructura**
   - Migrar a servidor más potente
   - Separar base de datos
   - Implementar balanceo de carga

### Kibana No Muestra Logs Correctamente

#### Síntomas
- Campos no aparecen o están mal formateados
- Búsquedas no devuelven resultados esperados
- Visualizaciones incorrectas

#### Diagnóstico
1. **Verificar mappings de índices**
   ```bash
   # Verificar mapping
   curl -X GET "localhost:9200/<nombre_indice>/_mapping?pretty"
   
   # Verificar template
   curl -X GET "localhost:9200/_template/<nombre_template>?pretty"
   ```

2. **Verificar procesamiento de logs**
   ```bash
   # Verificar configuración de Logstash
   cat /etc/logstash/conf.d/*.conf
   
   # Verificar configuración de Filebeat
   cat /etc/filebeat/filebeat.yml
   ```

3. **Verificar datos de ejemplo**
   ```bash
   # Verificar documento de ejemplo
   curl -X GET "localhost:9200/<nombre_indice>/_search?size=1&pretty"
   ```

#### Soluciones
1. **Corregir mappings**
   - Reindexar con mapping correcto
   - Ajustar templates para futuros índices
   - Corregir tipos de datos

2. **Optimizar procesamiento**
   - Ajustar filtros de Logstash
   - Corregir patrones de grok
   - Mejorar enriquecimiento de datos

3. **Ajustar configuración de Kibana**
   - Actualizar index patterns
   - Corregir formatos de campo
   - Ajustar visualizaciones

## Herramientas de Diagnóstico

### Herramientas de Red

| Herramienta | Propósito | Ejemplo de Uso |
|-------------|-----------|----------------|
| ping | Verificar conectividad básica | `ping -c 4 192.168.1.1` |
| traceroute | Analizar ruta de red | `traceroute -n 8.8.8.8` |
| mtr | Combinar ping y traceroute | `mtr -n 8.8.8.8` |
| nmap | Escanear puertos y servicios | `nmap -sS -p 1-1000 192.168.1.1` |
| tcpdump | Capturar y analizar paquetes | `tcpdump -i eth0 host 192.168.1.1` |
| netstat | Mostrar conexiones de red | `netstat -tunapl` |
| ss | Alternativa moderna a netstat | `ss -tunapl` |
| iftop | Monitorear uso de ancho de banda | `iftop -i eth0` |
| iperf | Medir rendimiento de red | `iperf -c servidor -t 30` |

### Herramientas de Sistema

| Herramienta | Propósito | Ejemplo de Uso |
|-------------|-----------|----------------|
| top | Monitorear procesos y recursos | `top` |
| htop | Versión mejorada de top | `htop` |
| iostat | Estadísticas de I/O | `iostat -x 1 10` |
| vmstat | Estadísticas de memoria virtual | `vmstat 1 10` |
| df | Uso de espacio en disco | `df -h` |
| du | Tamaño de directorios | `du -sh /var/log/*` |
| free | Uso de memoria | `free -h` |
| journalctl | Ver logs de systemd | `journalctl -u prometheus` |
| systemctl | Gestionar servicios | `systemctl status grafana-server` |

### Herramientas Específicas de Monitoreo

| Herramienta | Propósito | Ejemplo de Uso |
|-------------|-----------|----------------|
| promtool | Validar configuración de Prometheus | `promtool check config prometheus.yml` |
| amtool | Gestionar AlertManager | `amtool check-config alertmanager.yml` |
| curl | Consultar APIs | `curl -s http://localhost:9090/api/v1/query?query=up` |
| jq | Procesar JSON | `curl -s http://localhost:9090/api/v1/query?query=up \| jq` |
| snort | Analizar tráfico | `snort -T -c /etc/snort/snort.conf` |
| tshark | Versión CLI de Wireshark | `tshark -i eth0 -Y "http"` |

## Escenarios Comunes de Troubleshooting

### Escenario 1: Sistema de Monitoreo No Detecta Dispositivo Caído

#### Descripción
Un dispositivo de red ha fallado, pero el sistema de monitoreo no ha generado alertas.

#### Pasos de Diagnóstico
1. **Verificar estado real del dispositivo**
   ```bash
   ping -c 4 <ip_dispositivo>
   ```

2. **Verificar configuración de monitoreo**
   ```bash
   # Verificar target en Prometheus
   curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.instance=="<ip_dispositivo>:9100")'
   
   # Verificar regla de alerta
   grep -r "<ip_dispositivo>" /etc/prometheus/rules/
   ```

3. **Verificar funcionamiento de alertas**
   ```bash
   # Verificar estado de AlertManager
   curl -s http://localhost:9093/-/healthy
   
   # Verificar configuración de rutas
   grep -A 10 "route:" /etc/alertmanager/alertmanager.yml
   ```

#### Solución
1. Corregir configuración de target en Prometheus
2. Ajustar reglas de alerta para detectar fallos más rápidamente
3. Verificar y corregir configuración de notificaciones en AlertManager
4. Implementar monitoreo redundante para dispositivos críticos

### Escenario 2: Alertas de Alto Uso de CPU Sin Causa Aparente

#### Descripción
El sistema genera alertas de alto uso de CPU en servidores, pero no hay procesos visibles consumiendo recursos.

#### Pasos de Diagnóstico
1. **Verificar uso real de CPU**
   ```bash
   # Ver procesos por uso de CPU
   top -b -n 1 | head -20
   
   # Verificar estadísticas detalladas
   mpstat -P ALL 1 5
   ```

2. **Verificar procesos cortos o intermitentes**
   ```bash
   # Monitorear procesos en tiempo real
   atop
   
   # Verificar si hay procesos que aparecen y desaparecen
   pidstat 1 10
   ```

3. **Verificar carga del sistema**
   ```bash
   # Verificar load average
   uptime
   
   # Verificar procesos en estado D (I/O wait)
   ps aux | awk '$8 ~ /D/'
   ```

#### Solución
1. Identificar procesos causantes (posiblemente cron jobs o tareas programadas)
2. Ajustar umbrales de alerta para considerar picos normales
3. Implementar monitoreo más detallado para identificar causas específicas
4. Optimizar tareas programadas para distribuir carga

### Escenario 3: Pérdida Intermitente de Conectividad

#### Descripción
Los usuarios reportan desconexiones breves pero frecuentes que afectan aplicaciones.

#### Pasos de Diagnóstico
1. **Monitorear conectividad continuamente**
   ```bash
   # Ping continuo con timestamp
   ping -D <ip_gateway> | tee ping_log.txt
   
   # Monitoreo detallado
   mtr -c 100 -i 0.5 <ip_destino>
   ```

2. **Verificar interfaces y errores**
   ```bash
   # Verificar errores en interfaces
   ip -s link show
   
   # Monitorear errores en tiempo real
   watch -n 1 "ip -s link show | grep -A 1 eth0"
   ```

3. **Capturar tráfico durante incidentes**
   ```bash
   # Capturar paquetes con filtro
   tcpdump -i eth0 -w captura.pcap host <ip_destino>
   
   # Analizar capturas
   tshark -r captura.pcap -Y "tcp.analysis.flags"
   ```

#### Solución
1. Identificar patrones temporales (puede estar relacionado con backups u otras tareas programadas)
2. Verificar y reemplazar equipos de red defectuosos
3. Implementar rutas redundantes
4. Ajustar timeouts en aplicaciones para tolerar breves desconexiones

### Escenario 4: Falsos Positivos en IDS

#### Descripción
El sistema Snort genera numerosas alertas que parecen ser falsos positivos.

#### Pasos de Diagnóstico
1. **Analizar patrones de alertas**
   ```bash
   # Contar alertas por tipo
   grep -r "Priority: [0-9]" /var/log/snort/alert | sort | uniq -c | sort -nr
   
   # Identificar fuentes comunes
   grep -r "Classification: " /var/log/snort/alert | sort | uniq -c | sort -nr
   ```

2. **Verificar tráfico relacionado**
   ```bash
   # Capturar tráfico específico
   tcpdump -i eth0 -w captura.pcap host <ip_fuente> and host <ip_destino>
   
   # Analizar con Wireshark/tshark
   tshark -r captura.pcap -Y "<filtro_específico>"
   ```

3. **Revisar reglas que generan alertas**
   ```bash
   # Buscar regla específica
   grep -r "<sid_de_alerta>" /etc/snort/rules/
   ```

#### Solución
1. Ajustar sensibilidad de reglas problemáticas
2. Crear reglas de supresión para tráfico legítimo
3. Actualizar conjuntos de reglas
4. Implementar pre-filtrado de tráfico conocido

### Escenario 5: Degradación Gradual del Rendimiento

#### Descripción
El rendimiento del sistema de monitoreo se ha degradado gradualmente con el tiempo.

#### Pasos de Diagnóstico
1. **Analizar tendencias de recursos**
   ```bash
   # Verificar uso de disco
   df -h
   
   # Verificar crecimiento de directorios
   du -sh --time /var/lib/prometheus/* | sort -hr
   ```

2. **Verificar métricas de rendimiento**
   ```bash
   # Verificar métricas de Prometheus
   curl -s "http://localhost:9090/api/v1/query?query=prometheus_tsdb_head_series"
   
   # Verificar tiempo de consultas
   curl -s "http://localhost:9090/api/v1/query?query=prometheus_http_request_duration_seconds_sum/prometheus_http_request_duration_seconds_count"
   ```

3. **Analizar logs en busca de errores**
   ```bash
   # Buscar errores en logs
   grep -i error /var/log/prometheus/prometheus.log
   
   # Verificar OOM killer
   dmesg | grep -i "out of memory"
   ```

#### Solución
1. Optimizar retención de datos y políticas de almacenamiento
2. Reducir cardinalidad de métricas (menos labels)
3. Optimizar consultas frecuentes
4. Escalar verticalmente (más recursos) u horizontalmente (federación)

## Conclusión

Esta guía de solución de problemas proporciona un marco estructurado para diagnosticar y resolver problemas comunes en sistemas de monitoreo de redes y telecomunicaciones. Recuerde que el troubleshooting efectivo requiere un enfoque sistemático, documentación adecuada y mejora continua de procesos.

Para problemas complejos o recurrentes, considere:

1. Implementar monitoreo proactivo para detectar problemas antes de que afecten a los usuarios
2. Documentar todos los incidentes y soluciones en una base de conocimientos
3. Realizar análisis de causa raíz para problemas significativos
4. Revisar y actualizar procedimientos de troubleshooting regularmente

## Referencias

1. Prometheus Troubleshooting: https://prometheus.io/docs/prometheus/latest/querying/troubleshooting/
2. Grafana Troubleshooting: https://grafana.com/docs/grafana/latest/troubleshooting/
3. Elasticsearch Troubleshooting: https://www.elastic.co/guide/en/elasticsearch/reference/current/troubleshooting.html
4. Snort Troubleshooting: https://www.snort.org/faq
5. Linux Network Troubleshooting: https://www.redhat.com/sysadmin/beginners-guide-network-troubleshooting-linux

