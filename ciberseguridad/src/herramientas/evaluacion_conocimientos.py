#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Herramienta de Evaluación de Conocimientos para Certificaciones de Ciberseguridad

Esta herramienta permite a los usuarios evaluar su nivel de conocimiento en diferentes
dominios de las certificaciones de ciberseguridad más populares (CISSP, CISM, CEH, ITIL).
Proporciona evaluaciones de diagnóstico, pruebas por dominio y exámenes completos de simulación.

Uso:
    python evaluacion_conocimientos.py --certificacion [cissp|cism|ceh|itil] --modo [diagnostico|dominio|completo]
    
Opciones adicionales:
    --dominio NOMBRE_DOMINIO  Especifica el dominio para evaluar (solo en modo dominio)
    --tiempo MINUTOS          Establece un límite de tiempo para la evaluación (por defecto: sin límite)
    --preguntas NUM           Número de preguntas a incluir (por defecto: varía según el modo)
    --salida ARCHIVO          Archivo para guardar los resultados (por defecto: resultados_evaluacion.json)
"""

import argparse
import json
import os
import random
import sys
import time
import datetime
from collections import defaultdict

# Definición de certificaciones y sus dominios
CERTIFICACIONES = {
    "cissp": {
        "nombre": "Certified Information Systems Security Professional",
        "dominios": {
            "seguridad_riesgos": "Seguridad y Gestión de Riesgos",
            "seguridad_activos": "Seguridad de Activos",
            "arquitectura_seguridad": "Arquitectura e Ingeniería de Seguridad",
            "seguridad_comunicaciones": "Seguridad de Comunicaciones y Redes",
            "gestion_identidad": "Gestión de Identidad y Acceso",
            "evaluacion_seguridad": "Evaluación y Pruebas de Seguridad",
            "operaciones_seguridad": "Operaciones de Seguridad",
            "seguridad_desarrollo": "Seguridad en el Desarrollo de Software"
        },
        "pesos": {
            "seguridad_riesgos": 15,
            "seguridad_activos": 10,
            "arquitectura_seguridad": 13,
            "seguridad_comunicaciones": 13,
            "gestion_identidad": 13,
            "evaluacion_seguridad": 12,
            "operaciones_seguridad": 13,
            "seguridad_desarrollo": 11
        },
        "tiempo_examen": 180,  # minutos
        "num_preguntas_examen": 125,
        "puntuacion_aprobacion": 700  # en escala de 1000
    },
    "cism": {
        "nombre": "Certified Information Security Manager",
        "dominios": {
            "gobierno_seguridad": "Gobierno de la Seguridad de la Información",
            "gestion_riesgos": "Gestión de Riesgos de la Información",
            "programa_seguridad": "Desarrollo y Gestión del Programa de Seguridad",
            "gestion_incidentes": "Gestión de Incidentes de Seguridad"
        },
        "pesos": {
            "gobierno_seguridad": 24,
            "gestion_riesgos": 30,
            "programa_seguridad": 27,
            "gestion_incidentes": 19
        },
        "tiempo_examen": 240,  # minutos
        "num_preguntas_examen": 150,
        "puntuacion_aprobacion": 450  # en escala de 800
    },
    "ceh": {
        "nombre": "Certified Ethical Hacker",
        "dominios": {
            "fundamentos": "Fundamentos de Hacking Ético",
            "footprinting": "Footprinting y Reconocimiento",
            "escaneo_redes": "Escaneo de Redes",
            "enumeracion": "Enumeración",
            "vulnerabilidades": "Vulnerabilidades del Sistema",
            "malware": "Malware",
            "sniffing": "Sniffing",
            "ingenieria_social": "Ingeniería Social",
            "denegacion_servicio": "Denegación de Servicio",
            "hijacking": "Hijacking de Sesiones",
            "evasion": "Evasión de IDS, Firewalls y Honeypots",
            "hacking_web": "Hacking de Servidores Web y Aplicaciones",
            "sql_injection": "SQL Injection",
            "hacking_wireless": "Hacking de Redes Inalámbricas",
            "hacking_mobile": "Hacking de Plataformas Móviles",
            "iot_ot": "IoT y OT Hacking",
            "cloud": "Computación en la Nube"
        },
        "pesos": {
            "fundamentos": 6,
            "footprinting": 9,
            "escaneo_redes": 9,
            "enumeracion": 7,
            "vulnerabilidades": 7,
            "malware": 6,
            "sniffing": 6,
            "ingenieria_social": 6,
            "denegacion_servicio": 6,
            "hijacking": 6,
            "evasion": 6,
            "hacking_web": 8,
            "sql_injection": 7,
            "hacking_wireless": 6,
            "hacking_mobile": 5,
            "iot_ot": 5,
            "cloud": 5
        },
        "tiempo_examen": 240,  # minutos
        "num_preguntas_examen": 125,
        "puntuacion_aprobacion": 70  # porcentaje
    },
    "itil": {
        "nombre": "Information Technology Infrastructure Library",
        "dominios": {
            "conceptos_clave": "Conceptos Clave de ITIL",
            "cuatro_dimensiones": "Las Cuatro Dimensiones de la Gestión de Servicios",
            "sistema_valor": "El Sistema de Valor del Servicio ITIL",
            "practicas_gestion": "Prácticas de Gestión de ITIL",
            "mejora_continua": "Mejora Continua"
        },
        "pesos": {
            "conceptos_clave": 20,
            "cuatro_dimensiones": 20,
            "sistema_valor": 20,
            "practicas_gestion": 30,
            "mejora_continua": 10
        },
        "tiempo_examen": 60,  # minutos
        "num_preguntas_examen": 40,
        "puntuacion_aprobacion": 65  # porcentaje
    }
}

# Base de preguntas de ejemplo (en un entorno real, esto sería una base de datos mucho más grande)
# Formato: {certificacion: {dominio: [lista de preguntas]}}
PREGUNTAS = {
    "cissp": {
        "seguridad_riesgos": [
            {
                "pregunta": "¿Cuál de los siguientes NO es un componente de la tríada CIA?",
                "opciones": [
                    "Confidencialidad",
                    "Integridad",
                    "Autenticación",
                    "Disponibilidad"
                ],
                "respuesta": 2,
                "explicacion": "La tríada CIA consiste en Confidencialidad, Integridad y Disponibilidad. La Autenticación es un control de seguridad, no un componente de la tríada CIA."
            },
            {
                "pregunta": "¿Cuál es el propósito principal de un BIA (Análisis de Impacto al Negocio)?",
                "opciones": [
                    "Identificar amenazas y vulnerabilidades",
                    "Determinar el ROI de los controles de seguridad",
                    "Identificar procesos críticos y el impacto de su interrupción",
                    "Establecer políticas de seguridad"
                ],
                "respuesta": 2,
                "explicacion": "El propósito principal de un BIA es identificar los procesos críticos del negocio y determinar el impacto que tendría su interrupción, lo que ayuda a establecer prioridades para la recuperación."
            },
            {
                "pregunta": "¿Qué tipo de control es un extintor de incendios?",
                "opciones": [
                    "Preventivo",
                    "Detectivo",
                    "Correctivo",
                    "Disuasivo"
                ],
                "respuesta": 2,
                "explicacion": "Un extintor de incendios es un control correctivo porque se utiliza para mitigar o corregir el daño después de que un incidente (incendio) ha ocurrido."
            }
        ],
        "seguridad_activos": [
            {
                "pregunta": "¿Cuál de las siguientes NO es una categoría común de clasificación de datos?",
                "opciones": [
                    "Público",
                    "Confidencial",
                    "Restringido",
                    "Ejecutivo"
                ],
                "respuesta": 3,
                "explicacion": "'Ejecutivo' no es una categoría estándar de clasificación de datos. Las categorías comunes incluyen Público, Interno, Confidencial y Restringido."
            },
            {
                "pregunta": "¿Qué método de sanitización de datos garantiza que los datos no puedan ser recuperados incluso con técnicas forenses avanzadas?",
                "opciones": [
                    "Formateo estándar",
                    "Borrado seguro (múltiples pasadas)",
                    "Destrucción física",
                    "Cifrado"
                ],
                "respuesta": 2,
                "explicacion": "La destrucción física del medio de almacenamiento es el único método que garantiza que los datos no puedan ser recuperados incluso con técnicas forenses avanzadas."
            }
        ],
        # Más dominios y preguntas...
    },
    "cism": {
        "gobierno_seguridad": [
            {
                "pregunta": "¿Cuál es el propósito principal del gobierno de seguridad de la información?",
                "opciones": [
                    "Implementar controles técnicos",
                    "Alinear la seguridad con los objetivos de negocio",
                    "Gestionar incidentes de seguridad",
                    "Desarrollar políticas de seguridad"
                ],
                "respuesta": 1,
                "explicacion": "El propósito principal del gobierno de seguridad de la información es alinear las actividades de seguridad con los objetivos estratégicos del negocio, asegurando que la seguridad apoye y habilite las metas organizacionales."
            }
        ],
        # Más dominios y preguntas...
    },
    # Más certificaciones...
}

class EvaluacionConocimientos:
    def __init__(self, certificacion, modo, dominio=None, tiempo=None, num_preguntas=None, archivo_salida="resultados_evaluacion.json"):
        """
        Inicializa la evaluación de conocimientos.
        
        Args:
            certificacion: Nombre de la certificación (cissp, cism, ceh, itil)
            modo: Tipo de evaluación (diagnostico, dominio, completo)
            dominio: Dominio específico a evaluar (solo para modo dominio)
            tiempo: Límite de tiempo en minutos
            num_preguntas: Número de preguntas a incluir
            archivo_salida: Archivo para guardar los resultados
        """
        if certificacion not in CERTIFICACIONES:
            print(f"Error: Certificación '{certificacion}' no reconocida.")
            print(f"Certificaciones disponibles: {', '.join(CERTIFICACIONES.keys())}")
            sys.exit(1)
            
        self.certificacion = certificacion
        self.modo = modo
        self.dominio = dominio
        self.tiempo = tiempo
        self.archivo_salida = archivo_salida
        
        # Configurar número de preguntas según el modo
        if num_preguntas is not None:
            self.num_preguntas = num_preguntas
        else:
            if modo == "diagnostico":
                self.num_preguntas = 20
            elif modo == "dominio":
                self.num_preguntas = 10
            else:  # completo
                self.num_preguntas = CERTIFICACIONES[certificacion]["num_preguntas_examen"]
        
        # Validar modo y dominio
        if modo == "dominio" and dominio is None:
            print("Error: Debe especificar un dominio para el modo 'dominio'.")
            print(f"Dominios disponibles para {certificacion}:")
            for key, value in CERTIFICACIONES[certificacion]["dominios"].items():
                print(f"  - {key}: {value}")
            sys.exit(1)
            
        if modo == "dominio" and dominio not in CERTIFICACIONES[certificacion]["dominios"]:
            print(f"Error: Dominio '{dominio}' no reconocido para la certificación {certificacion}.")
            print(f"Dominios disponibles:")
            for key, value in CERTIFICACIONES[certificacion]["dominios"].items():
                print(f"  - {key}: {value}")
            sys.exit(1)
            
        # Cargar preguntas
        self.cargar_preguntas()
        
    def cargar_preguntas(self):
        """Carga las preguntas para la evaluación según el modo y dominio seleccionados."""
        self.preguntas_seleccionadas = []
        
        # En un entorno real, aquí se cargarían las preguntas desde una base de datos
        # Para este ejemplo, usamos las preguntas predefinidas
        
        if self.modo == "diagnostico":
            # Seleccionar preguntas de todos los dominios de forma proporcional a sus pesos
            preguntas_por_dominio = {}
            for dominio, peso in CERTIFICACIONES[self.certificacion]["pesos"].items():
                num_preguntas_dominio = max(1, int(self.num_preguntas * peso / 100))
                preguntas_disponibles = PREGUNTAS.get(self.certificacion, {}).get(dominio, [])
                
                if preguntas_disponibles:
                    preguntas_por_dominio[dominio] = random.sample(
                        preguntas_disponibles, 
                        min(num_preguntas_dominio, len(preguntas_disponibles))
                    )
                
            # Aplanar la lista de preguntas
            for dominio, preguntas in preguntas_por_dominio.items():
                for pregunta in preguntas:
                    pregunta_con_meta = pregunta.copy()
                    pregunta_con_meta["dominio"] = dominio
                    self.preguntas_seleccionadas.append(pregunta_con_meta)
                    
            # Ajustar al número deseado de preguntas
            if len(self.preguntas_seleccionadas) > self.num_preguntas:
                self.preguntas_seleccionadas = random.sample(self.preguntas_seleccionadas, self.num_preguntas)
                
        elif self.modo == "dominio":
            # Seleccionar preguntas de un dominio específico
            preguntas_disponibles = PREGUNTAS.get(self.certificacion, {}).get(self.dominio, [])
            
            if not preguntas_disponibles:
                print(f"Error: No hay preguntas disponibles para el dominio '{self.dominio}'.")
                sys.exit(1)
                
            self.preguntas_seleccionadas = random.sample(
                preguntas_disponibles,
                min(self.num_preguntas, len(preguntas_disponibles))
            )
            
            # Añadir metadatos del dominio
            for pregunta in self.preguntas_seleccionadas:
                pregunta["dominio"] = self.dominio
                
        else:  # completo
            # Seleccionar preguntas de todos los dominios según los pesos del examen real
            preguntas_por_dominio = {}
            for dominio, peso in CERTIFICACIONES[self.certificacion]["pesos"].items():
                num_preguntas_dominio = max(1, int(self.num_preguntas * peso / 100))
                preguntas_disponibles = PREGUNTAS.get(self.certificacion, {}).get(dominio, [])
                
                if preguntas_disponibles:
                    # Si no hay suficientes preguntas, usar todas las disponibles
                    if len(preguntas_disponibles) < num_preguntas_dominio:
                        preguntas_por_dominio[dominio] = preguntas_disponibles
                    else:
                        preguntas_por_dominio[dominio] = random.sample(
                            preguntas_disponibles, 
                            num_preguntas_dominio
                        )
            
            # Aplanar la lista de preguntas
            for dominio, preguntas in preguntas_por_dominio.items():
                for pregunta in preguntas:
                    pregunta_con_meta = pregunta.copy()
                    pregunta_con_meta["dominio"] = dominio
                    self.preguntas_seleccionadas.append(pregunta_con_meta)
        
        # Mezclar las preguntas
        random.shuffle(self.preguntas_seleccionadas)
        
    def ejecutar_evaluacion(self):
        """Ejecuta la evaluación interactiva."""
        print("\n" + "="*80)
        print(f"EVALUACIÓN DE CONOCIMIENTOS: {CERTIFICACIONES[self.certificacion]['nombre']}")
        print("="*80)
        
        if self.modo == "diagnostico":
            print("Modo: Diagnóstico - Evaluación rápida de conocimientos en todos los dominios")
        elif self.modo == "dominio":
            dominio_nombre = CERTIFICACIONES[self.certificacion]["dominios"][self.dominio]
            print(f"Modo: Evaluación de dominio - {dominio_nombre}")
        else:  # completo
            print("Modo: Examen completo - Simulación de examen de certificación")
            
        print(f"Número de preguntas: {len(self.preguntas_seleccionadas)}")
        
        if self.tiempo:
            print(f"Tiempo límite: {self.tiempo} minutos")
            tiempo_fin = time.time() + (self.tiempo * 60)
        else:
            tiempo_fin = None
            print("Tiempo límite: Sin límite")
            
        print("\nPresione Enter para comenzar la evaluación...")
        input()
        
        # Iniciar evaluación
        tiempo_inicio = time.time()
        respuestas = []
        
        for i, pregunta in enumerate(self.preguntas_seleccionadas):
            # Verificar tiempo límite
            if tiempo_fin and time.time() > tiempo_fin:
                print("\n¡Tiempo agotado!")
                break
                
            # Mostrar tiempo restante si hay límite
            if tiempo_fin:
                tiempo_restante = int(tiempo_fin - time.time())
                minutos = tiempo_restante // 60
                segundos = tiempo_restante % 60
                print(f"\nTiempo restante: {minutos:02d}:{segundos:02d}")
                
            # Mostrar pregunta
            print(f"\nPregunta {i+1} de {len(self.preguntas_seleccionadas)}")
            if self.modo != "dominio":
                dominio_nombre = CERTIFICACIONES[self.certificacion]["dominios"][pregunta["dominio"]]
                print(f"Dominio: {dominio_nombre}")
                
            print(f"\n{pregunta['pregunta']}")
            
            # Mostrar opciones
            for j, opcion in enumerate(pregunta["opciones"]):
                print(f"{j+1}. {opcion}")
                
            # Obtener respuesta
            while True:
                try:
                    respuesta_usuario = input("\nSeleccione una opción (1-4): ")
                    respuesta_usuario = int(respuesta_usuario)
                    if 1 <= respuesta_usuario <= len(pregunta["opciones"]):
                        break
                    else:
                        print(f"Por favor, ingrese un número entre 1 y {len(pregunta['opciones'])}.")
                except ValueError:
                    print("Por favor, ingrese un número válido.")
            
            # Registrar respuesta (ajustando índice)
            correcta = (respuesta_usuario - 1) == pregunta["respuesta"]
            respuestas.append({
                "pregunta_id": i,
                "dominio": pregunta["dominio"],
                "respuesta_usuario": respuesta_usuario - 1,
                "respuesta_correcta": pregunta["respuesta"],
                "correcta": correcta
            })
            
            # Mostrar resultado inmediato
            if correcta:
                print("\n✓ ¡Correcto!")
            else:
                print(f"\n✗ Incorrecto. La respuesta correcta es: {pregunta['opciones'][pregunta['respuesta']]}")
                
            print(f"Explicación: {pregunta['explicacion']}")
            
            # Pausa entre preguntas
            if i < len(self.preguntas_seleccionadas) - 1:
                input("\nPresione Enter para continuar...")
                
        # Finalizar evaluación
        tiempo_fin_real = time.time()
        duracion = tiempo_fin_real - tiempo_inicio
        
        # Calcular resultados
        self.calcular_resultados(respuestas, duracion)
        
    def calcular_resultados(self, respuestas, duracion):
        """Calcula y muestra los resultados de la evaluación."""
        # Estadísticas generales
        total_preguntas = len(respuestas)
        correctas = sum(1 for r in respuestas if r["correcta"])
        porcentaje = (correctas / total_preguntas * 100) if total_preguntas > 0 else 0
        
        # Estadísticas por dominio
        resultados_dominio = defaultdict(lambda: {"total": 0, "correctas": 0})
        for respuesta in respuestas:
            dominio = respuesta["dominio"]
            resultados_dominio[dominio]["total"] += 1
            if respuesta["correcta"]:
                resultados_dominio[dominio]["correctas"] += 1
                
        # Convertir duración a formato legible
        duracion_str = str(datetime.timedelta(seconds=int(duracion)))
        
        # Determinar si aprobó (solo para modo completo)
        aprobo = None
        if self.modo == "completo":
            if self.certificacion == "cissp":
                # CISSP usa escala de 1000 puntos
                puntuacion_escala = int(porcentaje * 10)
                aprobo = puntuacion_escala >= CERTIFICACIONES[self.certificacion]["puntuacion_aprobacion"]
            else:
                # Otras certificaciones usan porcentaje
                aprobo = porcentaje >= CERTIFICACIONES[self.certificacion]["puntuacion_aprobacion"]
        
        # Mostrar resultados
        print("\n" + "="*80)
        print("RESULTADOS DE LA EVALUACIÓN")
        print("="*80)
        print(f"Certificación: {CERTIFICACIONES[self.certificacion]['nombre']}")
        print(f"Modo: {self.modo}")
        print(f"Preguntas respondidas: {total_preguntas}")
        print(f"Respuestas correctas: {correctas}")
        print(f"Porcentaje de acierto: {porcentaje:.2f}%")
        print(f"Tiempo utilizado: {duracion_str}")
        
        if aprobo is not None:
            print(f"Resultado: {'APROBADO' if aprobo else 'NO APROBADO'}")
            
        # Mostrar resultados por dominio
        print("\nResultados por dominio:")
        for dominio, resultado in resultados_dominio.items():
            dominio_nombre = CERTIFICACIONES[self.certificacion]["dominios"][dominio]
            porcentaje_dominio = (resultado["correctas"] / resultado["total"] * 100) if resultado["total"] > 0 else 0
            print(f"- {dominio_nombre}: {resultado['correctas']}/{resultado['total']} ({porcentaje_dominio:.2f}%)")
            
        # Recomendaciones
        print("\nRecomendaciones:")
        if porcentaje >= 80:
            print("- Excelente nivel de conocimiento. Continúe repasando los temas para mantener su preparación.")
        elif porcentaje >= 70:
            print("- Buen nivel de conocimiento. Enfóquese en los dominios con menor puntuación.")
        elif porcentaje >= 60:
            print("- Nivel de conocimiento aceptable. Se recomienda profundizar en los dominios con menor puntuación.")
        else:
            print("- Se recomienda reforzar los conocimientos en todos los dominios, especialmente en aquellos con menor puntuación.")
            
        # Identificar dominios débiles
        dominios_debiles = []
        for dominio, resultado in resultados_dominio.items():
            porcentaje_dominio = (resultado["correctas"] / resultado["total"] * 100) if resultado["total"] > 0 else 0
            if porcentaje_dominio < 60:
                dominios_debiles.append(CERTIFICACIONES[self.certificacion]["dominios"][dominio])
                
        if dominios_debiles:
            print("- Dominios que requieren más atención:")
            for dominio in dominios_debiles:
                print(f"  * {dominio}")
                
        # Guardar resultados
        self.guardar_resultados({
            "certificacion": self.certificacion,
            "modo": self.modo,
            "fecha": datetime.datetime.now().isoformat(),
            "total_preguntas": total_preguntas,
            "correctas": correctas,
            "porcentaje": porcentaje,
            "duracion": duracion,
            "resultados_dominio": {
                dominio: {
                    "total": resultado["total"],
                    "correctas": resultado["correctas"],
                    "porcentaje": (resultado["correctas"] / resultado["total"] * 100) if resultado["total"] > 0 else 0
                }
                for dominio, resultado in resultados_dominio.items()
            },
            "aprobo": aprobo,
            "respuestas_detalladas": respuestas
        })
        
    def guardar_resultados(self, resultados):
        """Guarda los resultados de la evaluación en un archivo JSON."""
        try:
            with open(self.archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)
            print(f"\nResultados guardados en: {self.archivo_salida}")
        except Exception as e:
            print(f"\nError al guardar resultados: {e}")
            
def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Herramienta de Evaluación de Conocimientos para Certificaciones de Ciberseguridad')
    parser.add_argument('--certificacion', required=True, choices=['cissp', 'cism', 'ceh', 'itil'],
                        help='Certificación a evaluar')
    parser.add_argument('--modo', required=True, choices=['diagnostico', 'dominio', 'completo'],
                        help='Modo de evaluación')
    parser.add_argument('--dominio', help='Dominio específico a evaluar (solo para modo dominio)')
    parser.add_argument('--tiempo', type=int, help='Límite de tiempo en minutos')
    parser.add_argument('--preguntas', type=int, help='Número de preguntas a incluir')
    parser.add_argument('--salida', default='resultados_evaluacion.json',
                        help='Archivo para guardar los resultados')
    
    args = parser.parse_args()
    
    # Crear y ejecutar la evaluación
    evaluacion = EvaluacionConocimientos(
        certificacion=args.certificacion,
        modo=args.modo,
        dominio=args.dominio,
        tiempo=args.tiempo,
        num_preguntas=args.preguntas,
        archivo_salida=args.salida
    )
    
    evaluacion.ejecutar_evaluacion()
    
if __name__ == "__main__":
    main()

