#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Herramienta de Generación de Plan de Estudio para Certificaciones de Ciberseguridad

Esta herramienta genera un plan de estudio personalizado para prepararse para certificaciones
de ciberseguridad (CISSP, CISM, CEH, ITIL) basado en la experiencia del usuario, el tiempo
disponible y otros factores.

Uso:
    python plan_estudio.py --certificacion [cissp|cism|ceh|itil] --experiencia AÑOS --horas_semanales HORAS
    
Opciones adicionales:
    --fecha_examen YYYY-MM-DD  Fecha objetivo para el examen
    --areas_debiles dom1,dom2   Áreas en las que el usuario necesita enfocarse más
    --formato [markdown|html|pdf]  Formato de salida del plan
    --salida ARCHIVO           Archivo para guardar el plan de estudio
"""

import argparse
import json
import os
import sys
import datetime
import calendar
import math
from collections import defaultdict

# Importar definiciones de certificaciones
try:
    from evaluacion_conocimientos import CERTIFICACIONES
except ImportError:
    # Si no se puede importar, definir aquí las certificaciones
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

# Recursos recomendados por certificación
RECURSOS = {
    "cissp": {
        "libros": [
            {
                "titulo": "Official (ISC)² CISSP CBK",
                "autor": "(ISC)²",
                "descripcion": "La guía oficial que cubre todos los dominios del CISSP.",
                "nivel": "Avanzado",
                "url": "https://www.isc2.org/Training/Self-Study-Resources"
            },
            {
                "titulo": "CISSP All-in-One Exam Guide",
                "autor": "Shon Harris y Fernando Maymí",
                "descripcion": "Una guía completa y detallada que cubre todos los dominios.",
                "nivel": "Intermedio",
                "url": "https://www.amazon.com/CISSP-All-One-Guide-Eighth/dp/1260142655"
            },
            {
                "titulo": "CISSP Study Guide",
                "autor": "Eric Conrad, Seth Misenar y Joshua Feldman",
                "descripcion": "Un enfoque conciso pero completo para la preparación del examen.",
                "nivel": "Intermedio",
                "url": "https://www.amazon.com/CISSP-Study-Guide-Eric-Conrad/dp/0128024372"
            },
            {
                "titulo": "11th Hour CISSP",
                "autor": "Eric Conrad",
                "descripcion": "Excelente para repaso final antes del examen.",
                "nivel": "Avanzado",
                "url": "https://www.amazon.com/11th-Hour-CISSP-Study-Guide/dp/0128112484"
            }
        ],
        "cursos": [
            {
                "titulo": "Curso Oficial (ISC)² CISSP",
                "proveedor": "(ISC)²",
                "descripcion": "Curso oficial de preparación para el examen CISSP.",
                "duracion": "40 horas",
                "formato": "Presencial/Virtual",
                "url": "https://www.isc2.org/Training/Classroom-Based"
            },
            {
                "titulo": "CISSP Certification Training",
                "proveedor": "Cybrary",
                "descripcion": "Curso gratuito con videos detallados que cubren todos los dominios.",
                "duracion": "20 horas",
                "formato": "Virtual",
                "url": "https://www.cybrary.it/course/cissp/"
            },
            {
                "titulo": "CISSP Certification Prep",
                "proveedor": "Pluralsight",
                "descripcion": "Serie de cursos que cubren todos los dominios del CISSP.",
                "duracion": "25 horas",
                "formato": "Virtual",
                "url": "https://www.pluralsight.com/paths/cissp"
            }
        ],
        "practica": [
            {
                "titulo": "CISSP Official (ISC)² Practice Tests",
                "autor": "Mike Chapple y David Seidl",
                "descripcion": "Preguntas de práctica oficiales de (ISC)².",
                "cantidad": "1300 preguntas",
                "url": "https://www.amazon.com/CISSP-Official-Practice-Tests-Chapple/dp/1119787637"
            },
            {
                "titulo": "Boson CISSP Practice Exams",
                "proveedor": "Boson",
                "descripcion": "Simuladores de examen de alta calidad con explicaciones detalladas.",
                "cantidad": "750 preguntas",
                "url": "https://www.boson.com/practice-exam/cissp-isc2-practice-exam"
            },
            {
                "titulo": "CCCure CISSP",
                "proveedor": "CCCure",
                "descripcion": "Base de datos extensa de preguntas de práctica.",
                "cantidad": "3000+ preguntas",
                "url": "https://cccure.education/index.php/cccure-free-it-security-certifications-practice-questions"
            }
        ],
        "herramientas": [
            {
                "titulo": "MindMaps for CISSP",
                "autor": "Clement Dupuis",
                "descripcion": "Mapas mentales que cubren todos los dominios del CISSP.",
                "url": "https://www.studynotesandtheory.com/single-post/Free-CISSP-Mind-Maps"
            },
            {
                "titulo": "Sunflower CISSP",
                "autor": "Comunidad",
                "descripcion": "Resumen gratuito y popular de los dominios CISSP.",
                "url": "https://www.sunflower-cissp.com/"
            },
            {
                "titulo": "CISSP Flashcards",
                "proveedor": "Quizlet",
                "descripcion": "Tarjetas de memoria para repasar conceptos clave.",
                "url": "https://quizlet.com/subject/cissp/"
            }
        ]
    },
    "cism": {
        "libros": [
            {
                "titulo": "CISM Review Manual",
                "autor": "ISACA",
                "descripcion": "Manual oficial de revisión para el examen CISM.",
                "nivel": "Avanzado",
                "url": "https://www.isaca.org/bookstore/certification-related-products/crmcism"
            },
            {
                "titulo": "CISM Certified Information Security Manager All-in-One Exam Guide",
                "autor": "Peter Gregory",
                "descripcion": "Guía completa que cubre todos los dominios del CISM.",
                "nivel": "Intermedio",
                "url": "https://www.amazon.com/Certified-Information-Security-Manager-All-One/dp/1260458806"
            },
            {
                "titulo": "CISM Certified Information Security Manager Practice Exams",
                "autor": "Peter Gregory",
                "descripcion": "Libro de práctica con preguntas de examen y explicaciones detalladas.",
                "nivel": "Avanzado",
                "url": "https://www.amazon.com/CISM-Certified-Information-Security-Manager/dp/1260456234"
            }
        ],
        "cursos": [
            {
                "titulo": "CISM Certification Training",
                "proveedor": "ISACA",
                "descripcion": "Curso oficial de preparación para el examen CISM.",
                "duracion": "32 horas",
                "formato": "Presencial/Virtual",
                "url": "https://www.isaca.org/training-and-events/training/course-descriptions/cism-certification-preparation-course"
            },
            {
                "titulo": "CISM - Certified Information Security Manager",
                "proveedor": "Udemy",
                "descripcion": "Curso completo que cubre todos los dominios del CISM.",
                "duracion": "15 horas",
                "formato": "Virtual",
                "url": "https://www.udemy.com/course/cism-certification/"
            }
        ],
        "practica": [
            {
                "titulo": "CISM Review Questions, Answers & Explanations Database",
                "proveedor": "ISACA",
                "descripcion": "Base de datos oficial de preguntas de práctica.",
                "cantidad": "1000+ preguntas",
                "url": "https://www.isaca.org/bookstore/certification-related-products/cismqae"
            },
            {
                "titulo": "CISM Practice Tests",
                "proveedor": "Udemy",
                "descripcion": "Exámenes de práctica con explicaciones detalladas.",
                "cantidad": "500 preguntas",
                "url": "https://www.udemy.com/course/cism-practice-tests/"
            }
        ],
        "herramientas": [
            {
                "titulo": "CISM Flashcards",
                "proveedor": "Quizlet",
                "descripcion": "Tarjetas de memoria para repasar conceptos clave.",
                "url": "https://quizlet.com/subject/cism/"
            },
            {
                "titulo": "CISM Study Guide",
                "autor": "Thor Pedersen",
                "descripcion": "Guía de estudio gratuita con resúmenes de los dominios.",
                "url": "https://thorteaches.com/cism-study-guide/"
            }
        ]
    },
    "ceh": {
        "libros": [
            {
                "titulo": "CEH Certified Ethical Hacker All-in-One Exam Guide",
                "autor": "Matt Walker",
                "descripcion": "Guía completa que cubre todos los dominios del CEH.",
                "nivel": "Intermedio",
                "url": "https://www.amazon.com/Certified-Ethical-Hacker-All-Guide/dp/1260454550"
            },
            {
                "titulo": "CEH v11 Certified Ethical Hacker Study Guide",
                "autor": "Ric Messier",
                "descripcion": "Guía de estudio actualizada para la versión 11 del CEH.",
                "nivel": "Intermedio",
                "url": "https://www.amazon.com/Certified-Ethical-Hacker-Study-Guide/dp/1119800536"
            }
        ],
        "cursos": [
            {
                "titulo": "CEH - Certified Ethical Hacker",
                "proveedor": "EC-Council",
                "descripcion": "Curso oficial de preparación para el examen CEH.",
                "duracion": "40 horas",
                "formato": "Presencial/Virtual",
                "url": "https://www.eccouncil.org/train-certify/certified-ethical-hacker-ceh/"
            },
            {
                "titulo": "Complete Ethical Hacking Course",
                "proveedor": "Udemy",
                "descripcion": "Curso práctico que cubre técnicas de hacking ético.",
                "duracion": "25 horas",
                "formato": "Virtual",
                "url": "https://www.udemy.com/course/complete-ethical-hacking-course/"
            },
            {
                "titulo": "Practical Ethical Hacking",
                "proveedor": "TCM Security",
                "descripcion": "Curso práctico enfocado en habilidades reales de hacking ético.",
                "duracion": "30 horas",
                "formato": "Virtual",
                "url": "https://academy.tcm-sec.com/p/practical-ethical-hacking-the-complete-course"
            }
        ],
        "practica": [
            {
                "titulo": "CEH Practice Exams",
                "proveedor": "Boson",
                "descripcion": "Simuladores de examen de alta calidad con explicaciones detalladas.",
                "cantidad": "600 preguntas",
                "url": "https://www.boson.com/practice-exam/ethical-hacking-practice-exam"
            },
            {
                "titulo": "TryHackMe",
                "proveedor": "TryHackMe",
                "descripcion": "Plataforma de aprendizaje práctico con laboratorios de hacking.",
                "url": "https://tryhackme.com/"
            },
            {
                "titulo": "HackTheBox",
                "proveedor": "HackTheBox",
                "descripcion": "Plataforma de pentesting con máquinas vulnerables para practicar.",
                "url": "https://www.hackthebox.eu/"
            }
        ],
        "herramientas": [
            {
                "titulo": "Kali Linux",
                "descripcion": "Distribución Linux especializada en pruebas de penetración.",
                "url": "https://www.kali.org/"
            },
            {
                "titulo": "Metasploit Framework",
                "descripcion": "Framework de pruebas de penetración para explotar vulnerabilidades.",
                "url": "https://www.metasploit.com/"
            },
            {
                "titulo": "Wireshark",
                "descripcion": "Analizador de protocolos de red para capturar y analizar tráfico.",
                "url": "https://www.wireshark.org/"
            },
            {
                "titulo": "Burp Suite",
                "descripcion": "Herramienta para pruebas de seguridad en aplicaciones web.",
                "url": "https://portswigger.net/burp"
            }
        ]
    },
    "itil": {
        "libros": [
            {
                "titulo": "ITIL 4 Foundation",
                "autor": "AXELOS",
                "descripcion": "Guía oficial para la certificación ITIL 4 Foundation.",
                "nivel": "Principiante",
                "url": "https://www.axelos.com/store/book/itil-foundation-itil-4-edition"
            },
            {
                "titulo": "ITIL 4 Foundation Exam Study Guide",
                "autor": "Liz Gallacher y Helen Morris",
                "descripcion": "Guía de estudio completa para la certificación ITIL 4 Foundation.",
                "nivel": "Principiante",
                "url": "https://www.amazon.com/ITIL-Foundation-Exam-Study-Guide/dp/1119533198"
            }
        ],
        "cursos": [
            {
                "titulo": "ITIL 4 Foundation Certification Training",
                "proveedor": "AXELOS",
                "descripcion": "Curso oficial de preparación para el examen ITIL 4 Foundation.",
                "duracion": "16 horas",
                "formato": "Presencial/Virtual",
                "url": "https://www.axelos.com/certifications/itil-certifications/itil-foundation"
            },
            {
                "titulo": "ITIL 4 Foundation",
                "proveedor": "Udemy",
                "descripcion": "Curso completo que cubre todos los conceptos de ITIL 4 Foundation.",
                "duracion": "10 horas",
                "formato": "Virtual",
                "url": "https://www.udemy.com/course/itil-4-foundation/"
            }
        ],
        "practica": [
            {
                "titulo": "ITIL 4 Foundation Practice Exams",
                "proveedor": "AXELOS",
                "descripcion": "Exámenes de práctica oficiales para ITIL 4 Foundation.",
                "cantidad": "300 preguntas",
                "url": "https://www.axelos.com/store/book/itil-4-foundation-practice-exams"
            },
            {
                "titulo": "ITIL 4 Foundation Practice Tests",
                "proveedor": "Udemy",
                "descripcion": "Exámenes de práctica con explicaciones detalladas.",
                "cantidad": "200 preguntas",
                "url": "https://www.udemy.com/course/itil-4-foundation-practice-tests/"
            }
        ],
        "herramientas": [
            {
                "titulo": "ITIL 4 Flashcards",
                "proveedor": "Quizlet",
                "descripcion": "Tarjetas de memoria para repasar conceptos clave.",
                "url": "https://quizlet.com/subject/itil-4/"
            },
            {
                "titulo": "ITIL 4 Mind Maps",
                "autor": "IT Process Maps",
                "descripcion": "Mapas mentales que cubren los conceptos de ITIL 4.",
                "url": "https://en.it-processmaps.com/products/itil-4-mind-maps.html"
            }
        ]
    }
}

class PlanEstudio:
    def __init__(self, certificacion, experiencia, horas_semanales, fecha_examen=None, areas_debiles=None):
        """
        Inicializa el generador de plan de estudio.
        
        Args:
            certificacion: Nombre de la certificación (cissp, cism, ceh, itil)
            experiencia: Años de experiencia en el campo
            horas_semanales: Horas disponibles para estudio por semana
            fecha_examen: Fecha objetivo para el examen (opcional)
            areas_debiles: Lista de dominios en los que el usuario necesita enfocarse más (opcional)
        """
        if certificacion not in CERTIFICACIONES:
            print(f"Error: Certificación '{certificacion}' no reconocida.")
            print(f"Certificaciones disponibles: {', '.join(CERTIFICACIONES.keys())}")
            sys.exit(1)
            
        self.certificacion = certificacion
        self.experiencia = experiencia
        self.horas_semanales = horas_semanales
        self.fecha_examen = fecha_examen
        self.areas_debiles = areas_debiles if areas_debiles else []
        
        # Validar áreas débiles
        dominios_validos = list(CERTIFICACIONES[certificacion]["dominios"].keys())
        for area in self.areas_debiles:
            if area not in dominios_validos:
                print(f"Advertencia: Área débil '{area}' no reconocida para la certificación {certificacion}.")
                print(f"Áreas válidas: {', '.join(dominios_validos)}")
                self.areas_debiles.remove(area)
                
        # Calcular duración recomendada del estudio
        self.calcular_duracion_estudio()
        
    def calcular_duracion_estudio(self):
        """Calcula la duración recomendada del estudio basada en la experiencia y la certificación."""
        # Base de tiempo recomendado en semanas según la certificación
        base_tiempo = {
            "cissp": 16,  # 16 semanas (4 meses)
            "cism": 12,   # 12 semanas (3 meses)
            "ceh": 8,     # 8 semanas (2 meses)
            "itil": 4     # 4 semanas (1 mes)
        }
        
        # Ajustar según la experiencia
        factor_experiencia = max(0.5, 1 - (self.experiencia * 0.05))  # Reduce el tiempo necesario con más experiencia
        
        # Ajustar según las horas semanales disponibles
        factor_horas = max(0.5, 10 / self.horas_semanales)  # Base: 10 horas semanales
        
        # Calcular semanas recomendadas
        self.semanas_recomendadas = math.ceil(base_tiempo[self.certificacion] * factor_experiencia * factor_horas)
        
        # Calcular fecha de examen si no se proporcionó
        if not self.fecha_examen:
            hoy = datetime.date.today()
            self.fecha_examen = hoy + datetime.timedelta(weeks=self.semanas_recomendadas)
        else:
            # Si se proporcionó fecha de examen, calcular semanas disponibles
            hoy = datetime.date.today()
            dias_hasta_examen = (self.fecha_examen - hoy).days
            self.semanas_disponibles = max(1, dias_hasta_examen // 7)
            
            # Advertir si el tiempo es insuficiente
            if self.semanas_disponibles < self.semanas_recomendadas:
                print(f"Advertencia: El tiempo disponible ({self.semanas_disponibles} semanas) es menor que el recomendado ({self.semanas_recomendadas} semanas).")
                print("El plan de estudio se ajustará, pero podría ser intensivo.")
                self.semanas_recomendadas = self.semanas_disponibles
        
    def generar_plan(self):
        """Genera el plan de estudio personalizado."""
        # Obtener información de la certificación
        cert_info = CERTIFICACIONES[self.certificacion]
        cert_nombre = cert_info["nombre"]
        dominios = cert_info["dominios"]
        pesos = cert_info["pesos"]
        
        # Calcular horas totales de estudio
        horas_totales = self.semanas_recomendadas * self.horas_semanales
        
        # Distribuir horas por dominio según pesos y áreas débiles
        horas_por_dominio = {}
        factor_area_debil = 1.5  # Factor de multiplicación para áreas débiles
        
        # Primero, calcular la distribución base según pesos
        total_pesos = sum(pesos.values())
        for dominio, peso in pesos.items():
            horas_por_dominio[dominio] = (peso / total_pesos) * horas_totales
            
        # Luego, ajustar para áreas débiles
        if self.areas_debiles:
            # Calcular cuántas horas adicionales asignar a áreas débiles
            horas_adicionales = sum(horas_por_dominio[area] * (factor_area_debil - 1) for area in self.areas_debiles)
            
            # Reducir proporcionalmente las horas de áreas no débiles
            areas_no_debiles = [d for d in dominios.keys() if d not in self.areas_debiles]
            if areas_no_debiles:
                reduccion_por_area = horas_adicionales / len(areas_no_debiles)
                for area in areas_no_debiles:
                    horas_por_dominio[area] -= reduccion_por_area
                    
            # Aumentar horas para áreas débiles
            for area in self.areas_debiles:
                horas_por_dominio[area] *= factor_area_debil
        
        # Crear cronograma semanal
        cronograma = []
        fecha_inicio = datetime.date.today()
        
        # Distribuir el estudio a lo largo de las semanas
        dominios_ordenados = sorted(
            dominios.keys(),
            key=lambda d: (d not in self.areas_debiles, -pesos[d])  # Priorizar áreas débiles y luego por peso
        )
        
        # Crear semanas
        for semana in range(1, self.semanas_recomendadas + 1):
            fecha_semana = fecha_inicio + datetime.timedelta(weeks=semana - 1)
            
            # Determinar qué dominios estudiar esta semana
            dominios_semana = []
            
            # En las primeras semanas, enfocarse en áreas débiles y dominios con mayor peso
            if semana <= len(dominios) / 2:
                # Primera mitad: enfoque en dominios prioritarios
                idx_inicio = (semana - 1) * 2
                idx_fin = min(idx_inicio + 2, len(dominios_ordenados))
                dominios_semana = dominios_ordenados[idx_inicio:idx_fin]
            else:
                # Segunda mitad: repaso y enfoque en áreas menos dominadas
                # Alternar entre todos los dominios para repaso
                idx = (semana - 1) % len(dominios_ordenados)
                dominios_semana = [dominios_ordenados[idx]]
                
                # Añadir siempre un área débil si existe
                if self.areas_debiles and dominios_semana[0] not in self.areas_debiles:
                    idx_debil = (semana - 1) % len(self.areas_debiles)
                    dominios_semana.append(self.areas_debiles[idx_debil])
            
            # Calcular horas por dominio para esta semana
            horas_semana = {}
            for dominio in dominios_semana:
                # Distribuir las horas totales del dominio a lo largo de las semanas
                horas_dominio_total = horas_por_dominio[dominio]
                semanas_para_dominio = self.semanas_recomendadas / 2  # Cada dominio se estudia aproximadamente en la mitad de las semanas
                horas_semana[dominio] = horas_dominio_total / semanas_para_dominio
            
            # Ajustar para no exceder las horas semanales
            total_horas_asignadas = sum(horas_semana.values())
            if total_horas_asignadas > self.horas_semanales:
                factor_ajuste = self.horas_semanales / total_horas_asignadas
                for dominio in horas_semana:
                    horas_semana[dominio] *= factor_ajuste
            
            # Crear actividades para la semana
            actividades = []
            for dominio in dominios_semana:
                # Determinar recursos recomendados para este dominio
                recursos_dominio = self.seleccionar_recursos(dominio)
                
                # Crear actividades específicas
                actividades.append({
                    "dominio": dominio,
                    "nombre_dominio": dominios[dominio],
                    "horas": round(horas_semana[dominio], 1),
                    "actividades": [
                        f"Estudio de conceptos clave de {dominios[dominio]}",
                        f"Lectura de {recursos_dominio['libro']['titulo']}",
                        f"Práctica con {recursos_dominio['practica']['titulo']}"
                    ],
                    "recursos": recursos_dominio
                })
            
            # Añadir semana al cronograma
            cronograma.append({
                "semana": semana,
                "fecha_inicio": fecha_semana.strftime("%Y-%m-%d"),
                "fecha_fin": (fecha_semana + datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
                "actividades": actividades
            })
        
        # Añadir semana final de repaso intensivo
        fecha_ultima_semana = fecha_inicio + datetime.timedelta(weeks=self.semanas_recomendadas)
        cronograma.append({
            "semana": self.semanas_recomendadas + 1,
            "fecha_inicio": fecha_ultima_semana.strftime("%Y-%m-%d"),
            "fecha_fin": (fecha_ultima_semana + datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
            "actividades": [{
                "dominio": "repaso",
                "nombre_dominio": "Repaso General y Preparación Final",
                "horas": self.horas_semanales,
                "actividades": [
                    "Repaso de todos los dominios",
                    "Exámenes de práctica completos",
                    "Revisión de áreas débiles identificadas",
                    "Preparación logística para el examen"
                ],
                "recursos": {
                    "practica": RECURSOS[self.certificacion]["practica"][0]
                }
            }]
        })
        
        # Crear el plan completo
        plan = {
            "certificacion": self.certificacion,
            "nombre_certificacion": cert_nombre,
            "experiencia": self.experiencia,
            "horas_semanales": self.horas_semanales,
            "semanas_recomendadas": self.semanas_recomendadas,
            "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
            "fecha_examen": self.fecha_examen.strftime("%Y-%m-%d"),
            "horas_totales": horas_totales,
            "areas_debiles": [dominios[area] for area in self.areas_debiles],
            "cronograma": cronograma,
            "recursos_recomendados": RECURSOS[self.certificacion]
        }
        
        return plan
    
    def seleccionar_recursos(self, dominio):
        """Selecciona recursos recomendados para un dominio específico."""
        recursos = RECURSOS[self.certificacion]
        
        # Seleccionar un libro (preferir nivel intermedio si hay experiencia, avanzado si es área débil)
        nivel_preferido = "Avanzado" if dominio in self.areas_debiles else "Intermedio" if self.experiencia >= 3 else "Principiante"
        libro = next(
            (l for l in recursos["libros"] if l.get("nivel") == nivel_preferido),
            recursos["libros"][0]  # Default al primero si no hay match
        )
        
        # Seleccionar un curso (preferir formato virtual si hay pocas horas semanales)
        formato_preferido = "Virtual" if self.horas_semanales < 15 else "Presencial/Virtual"
        curso = next(
            (c for c in recursos["cursos"] if c.get("formato") == formato_preferido),
            recursos["cursos"][0]  # Default al primero si no hay match
        )
        
        # Seleccionar recursos de práctica y herramientas
        practica = recursos["practica"][0] if recursos["practica"] else None
        herramienta = recursos["herramientas"][0] if recursos["herramientas"] else None
        
        return {
            "libro": libro,
            "curso": curso,
            "practica": practica,
            "herramienta": herramienta
        }
    
    def generar_markdown(self, plan):
        """Genera el plan de estudio en formato Markdown."""
        md = f"# Plan de Estudio: {plan['nombre_certificacion']}\n\n"
        
        # Información general
        md += "## Información General\n\n"
        md += f"- **Certificación**: {plan['nombre_certificacion']}\n"
        md += f"- **Fecha de inicio**: {plan['fecha_inicio']}\n"
        md += f"- **Fecha objetivo del examen**: {plan['fecha_examen']}\n"
        md += f"- **Duración**: {plan['semanas_recomendadas']} semanas\n"
        md += f"- **Horas semanales**: {plan['horas_semanales']} horas\n"
        md += f"- **Horas totales estimadas**: {int(plan['horas_totales'])} horas\n"
        
        if plan['areas_debiles']:
            md += f"- **Áreas de enfoque especial**: {', '.join(plan['areas_debiles'])}\n"
        
        # Cronograma semanal
        md += "\n## Cronograma Semanal\n\n"
        
        for semana in plan['cronograma']:
            md += f"### Semana {semana['semana']}: {semana['fecha_inicio']} al {semana['fecha_fin']}\n\n"
            
            for actividad in semana['actividades']:
                md += f"#### {actividad['nombre_dominio']} ({actividad['horas']} horas)\n\n"
                
                md += "**Actividades:**\n\n"
                for act in actividad['actividades']:
                    md += f"- {act}\n"
                
                md += "\n**Recursos recomendados:**\n\n"
                
                if 'libro' in actividad['recursos'] and actividad['recursos']['libro']:
                    libro = actividad['recursos']['libro']
                    md += f"- 📚 **Libro**: [{libro['titulo']}]({libro['url']}) - {libro['autor']}\n"
                
                if 'curso' in actividad['recursos'] and actividad['recursos']['curso']:
                    curso = actividad['recursos']['curso']
                    md += f"- 🎓 **Curso**: [{curso['titulo']}]({curso['url']}) - {curso['proveedor']} ({curso['duracion']})\n"
                
                if 'practica' in actividad['recursos'] and actividad['recursos']['practica']:
                    practica = actividad['recursos']['practica']
                    md += f"- 🧪 **Práctica**: [{practica['titulo']}]({practica['url']})\n"
                
                if 'herramienta' in actividad['recursos'] and actividad['recursos']['herramienta']:
                    herramienta = actividad['recursos']['herramienta']
                    md += f"- 🛠️ **Herramienta**: [{herramienta['titulo']}]({herramienta['url']})\n"
                
                md += "\n"
        
        # Recursos adicionales
        md += "## Recursos Adicionales Recomendados\n\n"
        
        md += "### Libros\n\n"
        for libro in plan['recursos_recomendados']['libros']:
            md += f"- [{libro['titulo']}]({libro['url']}) - {libro['autor']}\n"
            md += f"  - {libro['descripcion']}\n"
        
        md += "\n### Cursos\n\n"
        for curso in plan['recursos_recomendados']['cursos']:
            md += f"- [{curso['titulo']}]({curso['url']}) - {curso['proveedor']}\n"
            md += f"  - {curso['descripcion']}\n"
            md += f"  - Duración: {curso['duracion']}\n"
        
        md += "\n### Recursos de Práctica\n\n"
        for practica in plan['recursos_recomendados']['practica']:
            md += f"- [{practica['titulo']}]({practica['url']})\n"
            md += f"  - {practica['descripcion']}\n"
        
        md += "\n### Herramientas\n\n"
        for herramienta in plan['recursos_recomendados']['herramientas']:
            md += f"- [{herramienta['titulo']}]({herramienta['url']})\n"
            md += f"  - {herramienta['descripcion']}\n"
        
        # Consejos finales
        md += "\n## Consejos para el Éxito\n\n"
        md += "1. **Consistencia**: Estudiar regularmente es más efectivo que sesiones intensivas ocasionales.\n"
        md += "2. **Práctica activa**: No solo leas, practica con ejercicios y exámenes de simulación.\n"
        md += "3. **Grupos de estudio**: Considera unirte a un grupo de estudio o foro en línea.\n"
        md += "4. **Descansos**: Toma descansos regulares para mantener la concentración.\n"
        md += "5. **Revisión espaciada**: Revisa periódicamente el material que ya has estudiado.\n"
        md += "6. **Preparación para el examen**: Familiarízate con el formato del examen y las estrategias para responder preguntas.\n"
        md += "7. **Salud**: Mantén buenos hábitos de sueño, alimentación y ejercicio durante tu preparación.\n"
        
        return md
    
    def generar_html(self, plan):
        """Genera el plan de estudio en formato HTML."""
        # Convertir el Markdown a HTML usando una biblioteca externa o implementar la conversión
        # Para este ejemplo, implementamos una conversión básica
        markdown = self.generar_markdown(plan)
        
        # Conversión muy básica de Markdown a HTML (en un caso real, usar una biblioteca como markdown2)
        html = "<!DOCTYPE html>\n<html lang='es'>\n<head>\n"
        html += "<meta charset='UTF-8'>\n"
        html += f"<title>Plan de Estudio: {plan['nombre_certificacion']}</title>\n"
        html += "<style>\n"
        html += "body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }\n"
        html += "h1 { color: #2c3e50; }\n"
        html += "h2 { color: #3498db; border-bottom: 1px solid #eee; padding-bottom: 5px; }\n"
        html += "h3 { color: #2980b9; }\n"
        html += "h4 { color: #16a085; }\n"
        html += "a { color: #3498db; text-decoration: none; }\n"
        html += "a:hover { text-decoration: underline; }\n"
        html += "ul { padding-left: 20px; }\n"
        html += ".week { background-color: #f9f9f9; padding: 15px; margin-bottom: 20px; border-radius: 5px; }\n"
        html += ".activity { background-color: #fff; padding: 10px; margin: 10px 0; border-left: 3px solid #3498db; }\n"
        html += "</style>\n"
        html += "</head>\n<body>\n"
        
        # Convertir encabezados
        lines = markdown.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('# '):
                lines[i] = f"<h1>{line[2:]}</h1>"
            elif line.startswith('## '):
                lines[i] = f"<h2>{line[3:]}</h2>"
            elif line.startswith('### '):
                lines[i] = f"<div class='week'><h3>{line[4:]}</h3>"
                # Cerrar el div al final de la semana
                for j in range(i+1, len(lines)):
                    if lines[j].startswith('### ') or j == len(lines)-1:
                        lines[j-1] += "</div>"
                        break
            elif line.startswith('#### '):
                lines[i] = f"<div class='activity'><h4>{line[5:]}</h4>"
                # Cerrar el div al final de la actividad
                for j in range(i+1, len(lines)):
                    if lines[j].startswith('####') or lines[j].startswith('###') or j == len(lines)-1:
                        if not lines[j-1].endswith("</div>"):
                            lines[j-1] += "</div>"
                        break
            elif line.startswith('- '):
                lines[i] = f"<li>{line[2:]}</li>"
                if i > 0 and not lines[i-1].startswith('<ul>') and not lines[i-1].endswith('</li>'):
                    lines[i] = f"<ul>{lines[i]}"
                if i < len(lines)-1 and not lines[i+1].startswith('- '):
                    lines[i] += "</ul>"
            elif line.startswith('  - '):
                lines[i] = f"<li>{line[4:]}</li>"
                if i > 0 and not lines[i-1].startswith('<ul>') and not lines[i-1].endswith('</li>'):
                    lines[i] = f"<ul>{lines[i]}"
                if i < len(lines)-1 and not lines[i+1].startswith('  - '):
                    lines[i] += "</ul>"
            elif line.startswith('**'):
                lines[i] = f"<strong>{line.strip('*')}</strong>"
            elif line == '':
                lines[i] = '<p></p>'
        
        html += '\n'.join(lines)
        html += "\n</body>\n</html>"
        
        return html
    
def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Herramienta de Generación de Plan de Estudio para Certificaciones de Ciberseguridad')
    parser.add_argument('--certificacion', required=True, choices=['cissp', 'cism', 'ceh', 'itil'],
                        help='Certificación para la que se generará el plan de estudio')
    parser.add_argument('--experiencia', required=True, type=int,
                        help='Años de experiencia en el campo')
    parser.add_argument('--horas_semanales', required=True, type=int,
                        help='Horas disponibles para estudio por semana')
    parser.add_argument('--fecha_examen', help='Fecha objetivo para el examen (formato: YYYY-MM-DD)')
    parser.add_argument('--areas_debiles', help='Áreas en las que el usuario necesita enfocarse más (separadas por comas)')
    parser.add_argument('--formato', choices=['markdown', 'html', 'pdf'], default='markdown',
                        help='Formato de salida del plan')
    parser.add_argument('--salida', help='Archivo para guardar el plan de estudio')
    
    args = parser.parse_args()
    
    # Procesar fecha de examen
    fecha_examen = None
    if args.fecha_examen:
        try:
            fecha_examen = datetime.datetime.strptime(args.fecha_examen, "%Y-%m-%d").date()
        except ValueError:
            print(f"Error: Formato de fecha inválido. Use YYYY-MM-DD.")
            sys.exit(1)
    
    # Procesar áreas débiles
    areas_debiles = []
    if args.areas_debiles:
        areas_debiles = args.areas_debiles.split(',')
    
    # Crear generador de plan de estudio
    generador = PlanEstudio(
        certificacion=args.certificacion,
        experiencia=args.experiencia,
        horas_semanales=args.horas_semanales,
        fecha_examen=fecha_examen,
        areas_debiles=areas_debiles
    )
    
    # Generar plan
    plan = generador.generar_plan()
    
    # Generar salida en el formato especificado
    if args.formato == 'markdown':
        output = generador.generar_markdown(plan)
    elif args.formato == 'html':
        output = generador.generar_html(plan)
    else:  # pdf
        # Para PDF, primero generamos HTML y luego lo convertimos a PDF
        # Esto requeriría una biblioteca externa como weasyprint o pdfkit
        print("Error: La generación de PDF no está implementada en este ejemplo.")
        print("Por favor, use 'markdown' o 'html' como formato de salida.")
        sys.exit(1)
    
    # Guardar o mostrar el resultado
    if args.salida:
        try:
            with open(args.salida, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Plan de estudio guardado en: {args.salida}")
        except Exception as e:
            print(f"Error al guardar el plan de estudio: {e}")
    else:
        print(output)
    
if __name__ == "__main__":
    main()

