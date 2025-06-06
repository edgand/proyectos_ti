# Guía de Solución de Problemas: Gestión de Infraestructura Tecnológica

Esta guía proporciona estrategias y soluciones para resolver problemas comunes que pueden surgir durante la implementación y operación de la infraestructura tecnológica.

## Índice

1. [Problemas de Terraform](#problemas-de-terraform)
2. [Problemas de Ansible](#problemas-de-ansible)
3. [Problemas de Conectividad](#problemas-de-conectividad)
4. [Problemas de Servidores Web](#problemas-de-servidores-web)
5. [Problemas de Base de Datos](#problemas-de-base-de-datos)
6. [Problemas de Monitoreo](#problemas-de-monitoreo)
7. [Problemas de Seguridad](#problemas-de-seguridad)
8. [Problemas de Rendimiento](#problemas-de-rendimiento)
9. [Herramientas de Diagnóstico](#herramientas-de-diagnóstico)
10. [Procedimientos de Escalamiento](#procedimientos-de-escalamiento)

## Problemas de Terraform

### Error: No se puede inicializar el backend

**Síntoma**: Error al ejecutar `terraform init`.

```
Error: Failed to get existing workspaces: S3 bucket does not exist.
```

**Posibles Causas**:
- El bucket S3 para el estado no existe
- Credenciales de AWS incorrectas o insuficientes
- Región de AWS incorrecta

**Soluciones**:
1. Verifique que el bucket S3 existe:
   ```bash
   aws s3 ls s3://nombre-del-bucket
   ```

2. Verifique sus credenciales de AWS:
   ```bash
   aws sts get-caller-identity
   ```

3. Cree el bucket S3 si no existe:
   ```bash
   aws s3 mb s3://nombre-del-bucket --region us-east-1
   ```

### Error: No se pueden aplicar cambios

**Síntoma**: Error al ejecutar `terraform apply`.

```
Error: Error creating VPC: VpcLimitExceeded: The maximum number of VPCs has been reached.
```

**Posibles Causas**:
- Límites de servicio alcanzados
- Recursos bloqueados por otra operación
- Permisos insuficientes

**Soluciones**:
1. Verifique los límites de servicio en la consola de AWS
2. Solicite un aumento de límite si es necesario
3. Verifique si hay operaciones pendientes en la consola
4. Verifique los permisos de IAM

### Error: Conflicto de estado

**Síntoma**: El estado de Terraform no coincide con la infraestructura real.

```
Error: Error refreshing state: state data for resource X does not match config
```

**Posibles Causas**:
- Cambios manuales en la infraestructura
- Corrupción del archivo de estado
- Múltiples personas aplicando cambios simultáneamente

**Soluciones**:
1. Importe los recursos existentes al estado:
   ```bash
   terraform import aws_instance.example i-abcd1234
   ```

2. Actualice el estado manualmente:
   ```bash
   terraform state rm aws_instance.example
   terraform import aws_instance.example i-abcd1234
   ```

3. Utilice un backend remoto con bloqueo para evitar cambios simultáneos

## Problemas de Ansible

### Error: Host Inalcanzable

**Síntoma**: Ansible no puede conectarse a los hosts.

```
UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh", "unreachable": true}
```

**Posibles Causas**:
- Problemas de conectividad de red
- Claves SSH incorrectas
- Firewall bloqueando conexiones
- Host apagado o no disponible

**Soluciones**:
1. Verifique la conectividad:
   ```bash
   ping hostname
   ```

2. Verifique que puede conectarse manualmente por SSH:
   ```bash
   ssh -i /path/to/key.pem usuario@hostname
   ```

3. Verifique los grupos de seguridad o reglas de firewall
4. Verifique que el host está en ejecución

### Error: Permisos Denegados

**Síntoma**: Ansible no puede ejecutar comandos con privilegios.

```
"msg": "Missing sudo password"
```

**Posibles Causas**:
- Configuración incorrecta de sudo
- Contraseña de sudo no proporcionada
- Usuario no tiene permisos sudo

**Soluciones**:
1. Configure sudo sin contraseña para el usuario de Ansible:
   ```bash
   echo "ansible ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/ansible
   ```

2. Proporcione la contraseña de sudo:
   ```bash
   ansible-playbook playbook.yml -i inventory --ask-become-pass
   ```

3. Verifique que el usuario tiene permisos sudo:
   ```bash
   sudo -l -U usuario
   ```

### Error: Módulo No Encontrado

**Síntoma**: Ansible no puede encontrar un módulo.

```
"msg": "Could not find the required Python library"
```

**Posibles Causas**:
- Dependencias de Python faltantes
- Versión incorrecta de Python
- Módulo no instalado

**Soluciones**:
1. Instale las dependencias requeridas:
   ```bash
   ansible-playbook playbook.yml -i inventory -e 'ansible_python_interpreter=/usr/bin/python3'
   ```

2. Instale el módulo faltante:
   ```bash
   pip install nombre-del-modulo
   ```

3. Utilice `pip` dentro del playbook:
   ```yaml
   - name: Instalar dependencias
     pip:
       name: nombre-del-modulo
       state: present
   ```

## Problemas de Conectividad

### Error: No se puede acceder a los servidores

**Síntoma**: No se puede acceder a los servidores por SSH o HTTP.

**Posibles Causas**:
- Grupos de seguridad mal configurados
- Problemas de enrutamiento
- Firewall bloqueando conexiones
- Servidor no en ejecución

**Soluciones**:
1. Verifique los grupos de seguridad:
   ```bash
   aws ec2 describe-security-groups --group-ids sg-12345678
   ```

2. Verifique las tablas de enrutamiento:
   ```bash
   aws ec2 describe-route-tables --route-table-ids rtb-12345678
   ```

3. Verifique el estado del servidor:
   ```bash
   aws ec2 describe-instance-status --instance-ids i-12345678
   ```

4. Verifique las reglas de firewall en el servidor:
   ```bash
   sudo iptables -L
   ```

### Error: Problemas de DNS

**Síntoma**: No se pueden resolver nombres de dominio.

**Posibles Causas**:
- Configuración de DNS incorrecta
- Problemas con el proveedor de DNS
- Caché de DNS desactualizada

**Soluciones**:
1. Verifique la configuración de DNS:
   ```bash
   cat /etc/resolv.conf
   ```

2. Pruebe con servidores DNS alternativos:
   ```bash
   dig @8.8.8.8 example.com
   ```

3. Limpie la caché de DNS:
   ```bash
   sudo systemd-resolve --flush-caches
   ```

4. Verifique la configuración de Route 53 (si se utiliza):
   ```bash
   aws route53 list-resource-record-sets --hosted-zone-id Z1234567890
   ```

## Problemas de Servidores Web

### Error: Nginx no inicia

**Síntoma**: El servicio Nginx no puede iniciarse.

```
Job for nginx.service failed because the control process exited with error code.
```

**Posibles Causas**:
- Configuración incorrecta
- Puerto ya en uso
- Permisos insuficientes
- Falta de recursos

**Soluciones**:
1. Verifique la configuración de Nginx:
   ```bash
   sudo nginx -t
   ```

2. Verifique si el puerto está en uso:
   ```bash
   sudo netstat -tulpn | grep 80
   ```

3. Verifique los permisos:
   ```bash
   sudo chown -R www-data:www-data /var/www/html
   ```

4. Verifique los logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

### Error: Certificado SSL inválido

**Síntoma**: Advertencias de certificado SSL en el navegador.

**Posibles Causas**:
- Certificado caducado
- Nombre de dominio incorrecto
- Certificado autofirmado
- Cadena de certificados incompleta

**Soluciones**:
1. Verifique la fecha de caducidad del certificado:
   ```bash
   openssl x509 -in /etc/letsencrypt/live/example.com/cert.pem -noout -dates
   ```

2. Renueve el certificado:
   ```bash
   sudo certbot renew
   ```

3. Verifique la configuración de Nginx:
   ```bash
   sudo nginx -t
   ```

4. Verifique la cadena de certificados:
   ```bash
   openssl verify -CAfile /etc/letsencrypt/live/example.com/chain.pem /etc/letsencrypt/live/example.com/cert.pem
   ```

## Problemas de Base de Datos

### Error: No se puede conectar a la base de datos

**Síntoma**: Las aplicaciones no pueden conectarse a la base de datos.

**Posibles Causas**:
- Servicio de base de datos no en ejecución
- Credenciales incorrectas
- Firewall bloqueando conexiones
- Límite de conexiones alcanzado

**Soluciones**:
1. Verifique el estado del servicio:
   ```bash
   sudo systemctl status mysql
   ```

2. Verifique las credenciales:
   ```bash
   mysql -u usuario -p
   ```

3. Verifique las reglas de firewall:
   ```bash
   sudo iptables -L | grep 3306
   ```

4. Verifique el límite de conexiones:
   ```bash
   mysql -e "SHOW VARIABLES LIKE 'max_connections';"
   ```

### Error: Base de datos llena

**Síntoma**: No se pueden escribir nuevos datos en la base de datos.

**Posibles Causas**:
- Disco lleno
- Cuota de almacenamiento alcanzada
- Tablas corruptas

**Soluciones**:
1. Verifique el espacio en disco:
   ```bash
   df -h
   ```

2. Limpie logs y datos temporales:
   ```bash
   sudo find /var/log -type f -name "*.gz" -delete
   ```

3. Optimice las tablas:
   ```bash
   mysqlcheck --optimize --all-databases
   ```

4. Aumente el tamaño del volumen (en la nube):
   ```bash
   aws ec2 modify-volume --volume-id vol-12345678 --size 100
   ```

## Problemas de Monitoreo

### Error: Prometheus no recopila métricas

**Síntoma**: No hay datos en los dashboards de Grafana.

**Posibles Causas**:
- Exporters no en ejecución
- Configuración incorrecta de scraping
- Problemas de conectividad
- Problemas de autenticación

**Soluciones**:
1. Verifique el estado de los exporters:
   ```bash
   sudo systemctl status node_exporter
   ```

2. Verifique la configuración de Prometheus:
   ```bash
   curl http://localhost:9090/api/v1/targets
   ```

3. Verifique la conectividad:
   ```bash
   curl http://localhost:9100/metrics
   ```

4. Verifique los logs:
   ```bash
   sudo journalctl -u prometheus
   ```

### Error: Alertas no se envían

**Síntoma**: Las alertas no llegan a los destinatarios.

**Posibles Causas**:
- Configuración incorrecta de Alertmanager
- Problemas con el servidor de correo
- Reglas de alerta mal definidas
- Problemas de conectividad

**Soluciones**:
1. Verifique la configuración de Alertmanager:
   ```bash
   curl http://localhost:9093/api/v1/status
   ```

2. Verifique las reglas de alerta:
   ```bash
   curl http://localhost:9090/api/v1/rules
   ```

3. Pruebe el servidor de correo:
   ```bash
   echo "Test" | mail -s "Test Alert" admin@example.com
   ```

4. Verifique los logs:
   ```bash
   sudo journalctl -u alertmanager
   ```

## Problemas de Seguridad

### Error: Acceso no autorizado

**Síntoma**: Detección de intentos de acceso no autorizados en los logs.

**Posibles Causas**:
- Credenciales comprometidas
- Vulnerabilidades de seguridad
- Configuración incorrecta de permisos
- Ataques de fuerza bruta

**Soluciones**:
1. Cambie inmediatamente las credenciales:
   ```bash
   passwd usuario
   ```

2. Verifique los logs de autenticación:
   ```bash
   sudo grep "Failed password" /var/log/auth.log
   ```

3. Configure Fail2Ban:
   ```bash
   sudo apt-get install fail2ban
   ```

4. Limite el acceso SSH:
   ```bash
   sudo vim /etc/ssh/sshd_config
   # Permitir solo usuarios específicos
   AllowUsers usuario1 usuario2
   ```

### Error: Vulnerabilidades detectadas

**Síntoma**: Escaneos de seguridad reportan vulnerabilidades.

**Posibles Causas**:
- Software desactualizado
- Configuraciones inseguras
- Parches de seguridad no aplicados
- Servicios innecesarios en ejecución

**Soluciones**:
1. Actualice el sistema:
   ```bash
   sudo apt-get update && sudo apt-get upgrade
   ```

2. Aplique parches de seguridad:
   ```bash
   sudo apt-get dist-upgrade
   ```

3. Deshabilite servicios innecesarios:
   ```bash
   sudo systemctl disable servicio
   sudo systemctl stop servicio
   ```

4. Implemente recomendaciones de hardening:
   ```bash
   sudo apt-get install lynis
   sudo lynis audit system
   ```

## Problemas de Rendimiento

### Error: Alta carga de CPU

**Síntoma**: Servidores con alta utilización de CPU.

**Posibles Causas**:
- Procesos consumiendo muchos recursos
- Configuración incorrecta de aplicaciones
- Ataques DoS
- Tamaño de instancia insuficiente

**Soluciones**:
1. Identifique los procesos que consumen más CPU:
   ```bash
   top -c
   ```

2. Analice los procesos problemáticos:
   ```bash
   ps aux | grep proceso
   ```

3. Ajuste la configuración de la aplicación:
   ```bash
   # Ejemplo para Nginx: reducir workers
   sudo vim /etc/nginx/nginx.conf
   ```

4. Escale verticalmente (aumente el tamaño de la instancia):
   ```bash
   aws ec2 modify-instance-attribute --instance-id i-12345678 --instance-type t3.large
   ```

### Error: Problemas de memoria

**Síntoma**: Servidores con alta utilización de memoria o swapping.

**Posibles Causas**:
- Fugas de memoria
- Configuración incorrecta de aplicaciones
- Tamaño de instancia insuficiente
- Demasiados procesos en ejecución

**Soluciones**:
1. Identifique los procesos que consumen más memoria:
   ```bash
   ps aux --sort=-%mem | head
   ```

2. Analice el uso de memoria:
   ```bash
   free -m
   ```

3. Ajuste la configuración de la aplicación:
   ```bash
   # Ejemplo para MySQL: reducir buffer pool
   sudo vim /etc/mysql/mysql.conf.d/mysqld.cnf
   ```

4. Aumente el tamaño de la instancia o agregue más memoria:
   ```bash
   aws ec2 modify-instance-attribute --instance-id i-12345678 --instance-type r5.large
   ```

## Herramientas de Diagnóstico

### Herramientas de Sistema

1. **Monitoreo de Recursos**:
   - `top` / `htop`: Monitoreo de CPU y memoria
   - `iostat`: Estadísticas de E/S
   - `vmstat`: Estadísticas de memoria virtual
   - `dstat`: Estadísticas combinadas

2. **Análisis de Red**:
   - `netstat` / `ss`: Conexiones de red
   - `tcpdump`: Captura de paquetes
   - `iftop`: Uso de ancho de banda
   - `mtr`: Diagnóstico de rutas de red

3. **Análisis de Logs**:
   - `journalctl`: Logs del sistema (systemd)
   - `tail` / `grep`: Filtrado de logs
   - `lnav`: Navegador de logs
   - `goaccess`: Análisis de logs de acceso web

### Herramientas de Cloud

1. **AWS**:
   - CloudWatch: Monitoreo y logs
   - CloudTrail: Auditoría de API
   - VPC Flow Logs: Tráfico de red
   - AWS Config: Configuración y cumplimiento

2. **Azure**:
   - Azure Monitor: Monitoreo y logs
   - Network Watcher: Diagnóstico de red
   - Security Center: Seguridad y cumplimiento
   - Resource Graph: Consulta de recursos

3. **Google Cloud**:
   - Cloud Monitoring: Monitoreo y alertas
   - Cloud Logging: Gestión de logs
   - Network Intelligence Center: Diagnóstico de red
   - Security Command Center: Seguridad y cumplimiento

## Procedimientos de Escalamiento

### Niveles de Escalamiento

1. **Nivel 1: Soporte Inicial**
   - Operadores de infraestructura
   - Tiempo de respuesta: 30 minutos
   - Problemas típicos: Reinicio de servicios, problemas de acceso básicos

2. **Nivel 2: Soporte Técnico**
   - Administradores de sistemas
   - Tiempo de respuesta: 2 horas
   - Problemas típicos: Configuración de servicios, problemas de rendimiento

3. **Nivel 3: Soporte Especializado**
   - Ingenieros de infraestructura
   - Tiempo de respuesta: 4 horas
   - Problemas típicos: Problemas complejos de configuración, optimización

4. **Nivel 4: Soporte Avanzado**
   - Arquitectos de soluciones
   - Tiempo de respuesta: 8 horas
   - Problemas típicos: Problemas de arquitectura, decisiones de diseño

### Proceso de Escalamiento

1. **Documentación del Problema**
   - Descripción detallada
   - Pasos para reproducir
   - Logs relevantes
   - Acciones ya tomadas

2. **Notificación**
   - Canales de comunicación: Email, Slack, Sistema de tickets
   - Información de contacto
   - Nivel de urgencia

3. **Seguimiento**
   - Actualización regular del estado
   - Documentación de acciones tomadas
   - Comunicación con stakeholders

4. **Resolución y Cierre**
   - Documentación de la solución
   - Actualización de runbooks
   - Análisis post-mortem para problemas críticos

## Referencias

1. [Terraform Troubleshooting](https://www.terraform.io/docs/extend/debugging.html)
2. [Ansible Troubleshooting](https://docs.ansible.com/ansible/latest/user_guide/playbooks_debugger.html)
3. [AWS Troubleshooting](https://aws.amazon.com/premiumsupport/knowledge-center/)
4. [Linux Performance Analysis](http://www.brendangregg.com/linuxperf.html)
5. [Nginx Troubleshooting](https://www.nginx.com/resources/wiki/start/topics/tutorials/debugging/)
6. [MySQL Troubleshooting](https://dev.mysql.com/doc/refman/8.0/en/problems.html)
7. [Prometheus Troubleshooting](https://prometheus.io/docs/prometheus/latest/querying/basics/)
8. [Security Incident Response](https://csrc.nist.gov/publications/detail/sp/800-61/rev-2/final)

