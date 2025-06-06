# Guía de Preparación para la Certificación CEH (Certified Ethical Hacker)

## Introducción

La certificación CEH (Certified Ethical Hacker) es una credencial reconocida internacionalmente que demuestra competencia en hacking ético y seguridad de la información. Otorgada por EC-Council, esta certificación valida la capacidad para identificar vulnerabilidades en sistemas y redes utilizando las mismas técnicas y herramientas que los hackers maliciosos, pero de manera legal y ética.

Esta guía proporciona un enfoque estructurado para prepararse para el examen CEH, incluyendo información sobre los dominios del examen, recursos recomendados, estrategias de estudio y consejos para el día del examen.

## Información General sobre la Certificación CEH

### Descripción y Valor

La certificación CEH está diseñada para profesionales de seguridad que:
- Necesitan entender cómo proteger sistemas contra ataques
- Quieren aprender metodologías, herramientas y técnicas de hacking
- Buscan mejorar las defensas de seguridad mediante la comprensión de las tácticas ofensivas
- Desean avanzar en carreras de seguridad ofensiva o pruebas de penetración

### Requisitos de Elegibilidad

Para obtener la certificación CEH, los candidatos deben:
1. Aprobar el examen CEH
2. Cumplir con uno de los siguientes requisitos:
   - Completar un curso de formación oficial de CEH a través de un centro de formación acreditado por EC-Council
   - Tener al menos 2 años de experiencia en seguridad de la información y solicitar una exención de formación (requiere aprobación de EC-Council)

### Formato del Examen

- 125 preguntas de opción múltiple
- Duración: 4 horas
- Puntuación de aprobación: 70%
- El examen se ofrece en centros de prueba autorizados y en formato de supervisión remota

## Dominios del Examen CEH

El examen CEH v11 (la versión más reciente) cubre los siguientes dominios principales:

### 1. Fundamentos de Hacking Ético (6%)

**Temas clave:**
- Elementos del hacking ético
- Tipos de hacking
- Fases de hacking
- Aspectos legales y éticos
- Tipos de evaluaciones de seguridad

**Conceptos fundamentales:**
- Diferencia entre hacking ético y malicioso
- Metodologías de pruebas de penetración
- Alcance y autorización
- Acuerdos de confidencialidad y no divulgación

### 2. Footprinting y Reconocimiento (9%)

**Temas clave:**
- Técnicas de footprinting
- Herramientas de footprinting
- Contramedidas de footprinting
- Footprinting a través de motores de búsqueda
- Footprinting usando redes sociales

**Conceptos fundamentales:**
- OSINT (Inteligencia de fuentes abiertas)
- Whois, DNS, registros de dominio
- Google dorks y búsqueda avanzada
- Herramientas como Maltego, Shodan, Recon-ng

### 3. Escaneo de Redes (9%)

**Temas clave:**
- Técnicas de escaneo de redes
- Escaneo de puertos y servicios
- Escaneo de vulnerabilidades
- Evasión de IDS/IPS/Firewall
- Banner grabbing

**Conceptos fundamentales:**
- Tipos de escaneo (TCP, SYN, XMAS, etc.)
- Herramientas como Nmap, Nessus, OpenVAS
- Análisis de respuestas y fingerprinting
- Técnicas de evasión

### 4. Enumeración (7%)

**Temas clave:**
- Técnicas de enumeración
- Enumeración de NetBIOS, SNMP, LDAP
- Enumeración de servicios y usuarios
- Contramedidas de enumeración

**Conceptos fundamentales:**
- Extracción de información de servicios
- Herramientas como Enum4linux, SNMPwalk
- Enumeración de recursos compartidos
- Enumeración de usuarios y grupos

### 5. Vulnerabilidades del Sistema (7%)

**Temas clave:**
- Tipos de vulnerabilidades
- Gestión de vulnerabilidades
- Herramientas de evaluación de vulnerabilidades
- Bases de datos de vulnerabilidades
- Explotación de vulnerabilidades comunes

**Conceptos fundamentales:**
- CVE, CVSS, CWE
- Ciclo de vida de gestión de vulnerabilidades
- Herramientas como Nessus, Qualys, OpenVAS
- Análisis de informes de vulnerabilidades

### 6. Malware (6%)

**Temas clave:**
- Tipos de malware
- Análisis de malware
- Vectores de infección
- Contramedidas contra malware
- Tendencias en malware

**Conceptos fundamentales:**
- Virus, gusanos, troyanos, ransomware
- Técnicas de persistencia
- Análisis estático y dinámico
- Sandboxing y entornos aislados

### 7. Sniffing (6%)

**Temas clave:**
- Conceptos de sniffing
- Ataques de sniffing
- Sniffing de protocolos
- Herramientas de sniffing
- Contramedidas contra sniffing

**Conceptos fundamentales:**
- Modo promiscuo
- ARP poisoning
- MITM (Man-in-the-Middle)
- Herramientas como Wireshark, Tcpdump

### 8. Ingeniería Social (6%)

**Temas clave:**
- Tipos de ingeniería social
- Ataques de phishing
- Contramedidas contra ingeniería social
- Factores humanos en seguridad
- Concienciación en seguridad

**Conceptos fundamentales:**
- Pretexting, baiting, quid pro quo
- Spear phishing, whaling
- Herramientas como SET (Social Engineering Toolkit)
- Indicadores de compromiso en ataques de ingeniería social

### 9. Denegación de Servicio (6%)

**Temas clave:**
- Ataques DoS y DDoS
- Técnicas de amplificación
- Botnets
- Herramientas de DoS
- Mitigación de DoS

**Conceptos fundamentales:**
- SYN flood, UDP flood, HTTP flood
- Amplificación DNS/NTP
- Ataques de capa de aplicación
- Servicios de mitigación DDoS

### 10. Hijacking de Sesiones (6%)

**Temas clave:**
- Secuestro de sesión
- Ataques de cookie
- Secuestro de TCP/IP
- Contramedidas contra hijacking
- Ataques de clickjacking

**Conceptos fundamentales:**
- Session fixation
- Cross-site request forgery (CSRF)
- Herramientas como Burp Suite, OWASP ZAP
- Protección de sesiones

### 11. Evasión de IDS, Firewalls y Honeypots (6%)

**Temas clave:**
- Tipos de IDS/IPS
- Técnicas de evasión de firewall
- Técnicas de evasión de IDS/IPS
- Honeypots y honeynets
- Contramedidas contra evasión

**Conceptos fundamentales:**
- Fragmentación de paquetes
- Ofuscación de tráfico
- Túneles y proxies
- Herramientas como Nmap, Metasploit

### 12. Hacking de Servidores Web y Aplicaciones (8%)

**Temas clave:**
- Vulnerabilidades web comunes
- Ataques a servidores web
- Ataques a aplicaciones web
- Metodologías de pruebas de seguridad web
- Contramedidas para aplicaciones web

**Conceptos fundamentales:**
- OWASP Top 10
- Herramientas como Burp Suite, OWASP ZAP
- Configuraciones incorrectas de servidores
- Defensas como WAF, CSP

### 13. SQL Injection (7%)

**Temas clave:**
- Tipos de SQL Injection
- Técnicas de explotación de SQLi
- Blind SQL Injection
- Herramientas de SQLi
- Prevención de SQLi

**Conceptos fundamentales:**
- Error-based, Union-based, Boolean-based SQLi
- Herramientas como SQLmap
- Consultas parametrizadas
- ORM y prevención de SQLi

### 14. Hacking de Redes Inalámbricas (6%)

**Temas clave:**
- Tipos de redes inalámbricas
- Vulnerabilidades en WiFi
- Ataques a redes inalámbricas
- Herramientas de hacking inalámbrico
- Seguridad inalámbrica

**Conceptos fundamentales:**
- WEP, WPA, WPA2, WPA3
- Ataques de handshake
- Rogue AP y Evil Twin
- Herramientas como Aircrack-ng, Wifite

### 15. Hacking de Plataformas Móviles (5%)

**Temas clave:**
- Vulnerabilidades en plataformas móviles
- Ataques a dispositivos móviles
- Seguridad en Android e iOS
- Análisis de aplicaciones móviles
- BYOD y seguridad móvil

**Conceptos fundamentales:**
- Jailbreaking y rooting
- Análisis estático y dinámico de apps
- Herramientas como MobSF, Drozer
- Vectores de ataque móviles

### 16. IoT y OT Hacking (5%)

**Temas clave:**
- Arquitectura de IoT
- Vulnerabilidades en dispositivos IoT
- Ataques a sistemas IoT
- Seguridad en sistemas de control industrial
- Contramedidas para IoT y OT

**Conceptos fundamentales:**
- Protocolos IoT (MQTT, CoAP, etc.)
- Sistemas SCADA y ICS
- Herramientas de análisis de IoT
- Segmentación de red para IoT

### 17. Computación en la Nube (5%)

**Temas clave:**
- Modelos de servicio en la nube
- Vulnerabilidades en entornos cloud
- Ataques a infraestructuras cloud
- Seguridad en contenedores
- Mejores prácticas de seguridad en la nube

**Conceptos fundamentales:**
- Configuraciones incorrectas en la nube
- Seguridad en AWS, Azure, GCP
- Contenedores y orquestación
- DevSecOps

## Plan de Estudio Recomendado

### Fase 1: Planificación y Evaluación (1-2 semanas)

1. **Evaluación de conocimientos**
   - Realizar una evaluación diagnóstica para identificar áreas de fortaleza y debilidad
   - Revisar los requisitos de elegibilidad y confirmar que se cumplen

2. **Preparación del entorno de laboratorio**
   - Configurar una máquina virtual con Kali Linux
   - Instalar máquinas virtuales vulnerables para práctica (como Metasploitable, DVWA, etc.)
   - Configurar entornos de prueba aislados

3. **Planificación del estudio**
   - Establecer un calendario de estudio realista
   - Adquirir los materiales de estudio recomendados
   - Identificar grupos de estudio o mentores

### Fase 2: Estudio de Fundamentos (4-6 semanas)

1. **Estudio del material básico**
   - Leer el CEH Official Courseware o libros recomendados
   - Estudiar cada dominio en profundidad
   - Tomar notas detalladas y crear resúmenes

2. **Comprensión de conceptos clave**
   - Centrarse en la comprensión de los conceptos fundamentales
   - Familiarizarse con las herramientas principales
   - Crear tarjetas de memoria para comandos y herramientas importantes

### Fase 3: Práctica Práctica (4-6 semanas)

1. **Laboratorios prácticos**
   - Realizar laboratorios para cada dominio del examen
   - Practicar con herramientas reales en entornos controlados
   - Documentar procedimientos y resultados

2. **Escenarios de hacking ético**
   - Completar escenarios de hacking ético de principio a fin
   - Practicar la metodología completa de pruebas de penetración
   - Participar en CTFs (Capture The Flag) y plataformas como HackTheBox, TryHackMe

### Fase 4: Práctica y Revisión (2-4 semanas)

1. **Exámenes de práctica**
   - Realizar múltiples exámenes de práctica completos
   - Analizar los resultados para identificar áreas de mejora
   - Practicar la gestión del tiempo durante los exámenes

2. **Revisión final**
   - Repasar todos los dominios, con énfasis en áreas débiles
   - Revisar notas y resúmenes
   - Consolidar el conocimiento con mapas mentales o diagramas

### Fase 5: Preparación Final (1 semana)

1. **Revisión rápida**
   - Repasar conceptos clave y áreas problemáticas
   - Revisar comandos y herramientas importantes

2. **Preparación logística**
   - Confirmar los detalles del examen (ubicación, hora, requisitos)
   - Preparar documentos necesarios
   - Planificar el viaje y alojamiento si es necesario

## Recursos Recomendados

### Materiales Oficiales de EC-Council

- **CEH Official Courseware**: El material oficial del curso CEH
- **CEH Certified Ethical Hacker Practice Exams**: Exámenes de práctica oficiales
- **iLabs**: Plataforma de laboratorios prácticos de EC-Council

### Libros Recomendados

- **CEH Certified Ethical Hacker All-in-One Exam Guide** por Matt Walker
- **CEH v11 Certified Ethical Hacker Study Guide** por Ric Messier
- **Hands-On Ethical Hacking and Network Defense** por Michael T. Simpson et al.

### Plataformas de Práctica

- **TryHackMe**: Plataforma con laboratorios guiados y desafíos
- **HackTheBox**: Plataforma con máquinas vulnerables para practicar hacking ético
- **VulnHub**: Colección de máquinas virtuales vulnerables para practicar
- **PortSwigger Web Security Academy**: Para practicar vulnerabilidades web

### Cursos Online

- **Udemy**: Cursos de CEH de instructores como Nathan House
- **Pluralsight**: Cursos de preparación para CEH
- **INE (eLearnSecurity)**: Cursos de seguridad ofensiva y hacking ético

### Herramientas Esenciales

- **Kali Linux**: Distribución Linux con herramientas de seguridad preinstaladas
- **Metasploit Framework**: Framework de explotación
- **Nmap**: Escáner de puertos y herramienta de descubrimiento de red
- **Wireshark**: Analizador de protocolos de red
- **Burp Suite**: Herramienta para pruebas de seguridad en aplicaciones web
- **John the Ripper / Hashcat**: Herramientas de cracking de contraseñas
- **Aircrack-ng**: Suite para auditoría de redes inalámbricas

## Estrategias para el Examen

### Preparación Mental

- Mantener una actitud positiva y confiada
- Practicar técnicas de reducción de estrés
- Asegurar un descanso adecuado antes del examen

### Durante el Examen

- Leer cada pregunta cuidadosamente, identificando palabras clave
- Eliminar opciones obviamente incorrectas
- Gestionar el tiempo (aproximadamente 1.9 minutos por pregunta)
- Marcar preguntas difíciles para revisión posterior
- Responder todas las preguntas (no hay penalización por respuestas incorrectas)

### Enfoque de Respuesta

- Recordar que el examen evalúa conocimiento práctico y teórico
- Considerar el contexto de la pregunta (fase de hacking, herramienta específica, etc.)
- Buscar la respuesta más completa y precisa
- Tener en cuenta las mejores prácticas de la industria

## Después del Examen

### Si Aprueba

- Descargar el certificado digital
- Actualizar el perfil profesional (LinkedIn, CV, etc.)
- Considerar certificaciones avanzadas como CEH Practical o ECSA
- Comenzar a planificar actividades de educación continua

### Si No Aprueba

- Revisar el informe de resultados para identificar áreas débiles
- Ajustar el plan de estudio para enfocarse en esas áreas
- Considerar recursos adicionales o diferentes enfoques de estudio
- Programar el siguiente intento (después del período de espera requerido)

## Mantenimiento de la Certificación

- La certificación CEH es válida por 3 años
- Para renovar, se requieren 120 créditos ECE (EC-Council Continuing Education)
- Los créditos se pueden obtener a través de:
  - Educación continua
  - Conferencias y eventos
  - Publicaciones y contribuciones
  - Certificaciones adicionales
- Pagar la tarifa de renovación

## Consideraciones Éticas y Legales

- **Siempre obtener autorización por escrito** antes de realizar cualquier prueba de penetración
- Respetar el alcance definido en los acuerdos
- Mantener la confidencialidad de la información obtenida
- Reportar vulnerabilidades de manera responsable
- Conocer las leyes locales e internacionales sobre hacking y seguridad informática

## Conclusión

La certificación CEH es una credencial valiosa que demuestra competencia en hacking ético y seguridad ofensiva. Con una preparación adecuada, un plan de estudio estructurado y mucha práctica práctica, los candidatos pueden aumentar significativamente sus posibilidades de éxito en el examen.

Recuerde que el verdadero valor de la certificación CEH no está solo en aprobar el examen, sino en adquirir habilidades prácticas que puedan aplicarse en el mundo real para mejorar la seguridad de los sistemas y redes.

¡Buena suerte en su preparación y examen CEH!

---

## Apéndice: Comandos y Herramientas Esenciales

### Nmap
```bash
# Escaneo básico
nmap 192.168.1.1

# Escaneo de puertos específicos
nmap -p 80,443,8080 192.168.1.1

# Escaneo sigiloso (SYN scan)
nmap -sS 192.168.1.1

# Detección de versiones de servicios
nmap -sV 192.168.1.1

# Escaneo completo con scripts
nmap -sC -sV -O -p- 192.168.1.1
```

### Metasploit
```bash
# Iniciar Metasploit
msfconsole

# Buscar exploits
search apache

# Usar un exploit
use exploit/multi/http/apache_struts2_content_type_ognl

# Configurar opciones
set RHOSTS 192.168.1.1
set RPORT 8080

# Ejecutar exploit
exploit
```

### Hydra
```bash
# Ataque de fuerza bruta SSH
hydra -l admin -P wordlist.txt ssh://192.168.1.1

# Ataque de fuerza bruta formulario web
hydra -l admin -P wordlist.txt 192.168.1.1 http-post-form "/login:username=^USER^&password=^PASS^:F=Login failed"
```

### John the Ripper
```bash
# Cracking de hash
john --format=md5 hash.txt

# Cracking con wordlist
john --wordlist=wordlist.txt hash.txt
```

### Aircrack-ng
```bash
# Poner interfaz en modo monitor
airmon-ng start wlan0

# Capturar tráfico
airodump-ng wlan0mon

# Capturar handshake
airodump-ng -c 1 --bssid 00:11:22:33:44:55 -w capture wlan0mon

# Cracking de WPA/WPA2
aircrack-ng -w wordlist.txt capture-01.cap
```

### Wireshark Filtros Útiles
```
# Filtrar por IP
ip.addr == 192.168.1.1

# Filtrar por protocolo
http or dns

# Filtrar por puerto
tcp.port == 80

# Filtrar por contenido
http contains "password"
```

### SQLmap
```bash
# Prueba básica de inyección SQL
sqlmap -u "http://example.com/page.php?id=1"

# Prueba con autenticación
sqlmap -u "http://example.com/page.php?id=1" --cookie="PHPSESSID=1234"

# Extracción de bases de datos
sqlmap -u "http://example.com/page.php?id=1" --dbs

# Extracción de tablas
sqlmap -u "http://example.com/page.php?id=1" -D database_name --tables
```

### Burp Suite
- Interceptar solicitudes HTTP/HTTPS
- Analizar y modificar parámetros
- Realizar ataques de fuerza bruta
- Escanear vulnerabilidades web
- Realizar pruebas de seguridad en aplicaciones web

