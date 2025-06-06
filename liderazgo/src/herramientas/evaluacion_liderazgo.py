#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Herramienta de Evaluación de Madurez de Liderazgo en TI

Esta herramienta permite evaluar la madurez del liderazgo en equipos y organizaciones de TI,
basándose en múltiples dimensiones y modelos de liderazgo. Genera un informe detallado
con resultados, recomendaciones y un plan de desarrollo.

Uso:
    python evaluacion_liderazgo.py [--output informe_liderazgo.json] [--interactive]
"""

import argparse
import json
import os
import sys
import datetime
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Definición de las dimensiones de liderazgo
DIMENSIONES_LIDERAZGO = {
    "vision_estrategica": {
        "nombre": "Visión Estratégica",
        "descripcion": "Capacidad para desarrollar y comunicar una visión clara y convincente que inspire y guíe al equipo.",
        "preguntas": [
            "¿El líder desarrolla y comunica una visión clara para el equipo?",
            "¿La visión está alineada con los objetivos estratégicos de la organización?",
            "¿El líder involucra al equipo en el desarrollo y refinamiento de la visión?",
            "¿El líder traduce la visión en objetivos y metas concretas?",
            "¿El líder adapta la visión según los cambios en el entorno?"
        ]
    },
    "liderazgo_servicial": {
        "nombre": "Liderazgo Servicial",
        "descripcion": "Enfoque en servir primero a los miembros del equipo, ayudándoles a desarrollarse y desempeñarse al máximo nivel.",
        "preguntas": [
            "¿El líder prioriza las necesidades del equipo sobre las propias?",
            "¿El líder elimina obstáculos que impiden al equipo realizar su trabajo?",
            "¿El líder proporciona los recursos necesarios para que el equipo tenga éxito?",
            "¿El líder fomenta el desarrollo profesional y personal de los miembros del equipo?",
            "¿El líder escucha activamente y responde a las preocupaciones del equipo?"
        ]
    },
    "liderazgo_tecnico": {
        "nombre": "Liderazgo Técnico",
        "descripcion": "Capacidad para proporcionar dirección técnica, mentoría y tomar decisiones técnicas sólidas.",
        "preguntas": [
            "¿El líder posee conocimientos técnicos relevantes para el trabajo del equipo?",
            "¿El líder proporciona mentoría técnica a los miembros del equipo?",
            "¿El líder establece estándares técnicos y mejores prácticas?",
            "¿El líder toma decisiones técnicas sólidas y las justifica adecuadamente?",
            "¿El líder se mantiene actualizado con las tendencias y avances tecnológicos?"
        ]
    },
    "gestion_equipos": {
        "nombre": "Gestión de Equipos",
        "descripcion": "Habilidad para formar, desarrollar y gestionar equipos efectivos y de alto rendimiento.",
        "preguntas": [
            "¿El líder forma equipos con las habilidades y diversidad adecuadas?",
            "¿El líder establece roles y responsabilidades claras dentro del equipo?",
            "¿El líder fomenta la colaboración y el trabajo en equipo?",
            "¿El líder gestiona y resuelve conflictos de manera efectiva?",
            "¿El líder reconoce y celebra los logros del equipo?"
        ]
    },
    "comunicacion": {
        "nombre": "Comunicación",
        "descripcion": "Capacidad para comunicarse de manera clara, efectiva y adaptada a diferentes audiencias.",
        "preguntas": [
            "¿El líder comunica información de manera clara y concisa?",
            "¿El líder adapta su comunicación a diferentes audiencias?",
            "¿El líder escucha activamente y busca comprender antes de responder?",
            "¿El líder proporciona retroalimentación constructiva y oportuna?",
            "¿El líder fomenta la comunicación abierta y honesta dentro del equipo?"
        ]
    },
    "toma_decisiones": {
        "nombre": "Toma de Decisiones",
        "descripcion": "Capacidad para tomar decisiones oportunas, informadas y efectivas, involucrando a las personas adecuadas.",
        "preguntas": [
            "¿El líder toma decisiones oportunas y evita la parálisis por análisis?",
            "¿El líder basa sus decisiones en datos e información relevante?",
            "¿El líder involucra a las personas adecuadas en el proceso de toma de decisiones?",
            "¿El líder comunica claramente las decisiones y sus razones?",
            "¿El líder evalúa y aprende de los resultados de sus decisiones?"
        ]
    },
    "gestion_cambio": {
        "nombre": "Gestión del Cambio",
        "descripcion": "Habilidad para liderar al equipo a través del cambio, fomentando la adaptabilidad y la resiliencia.",
        "preguntas": [
            "¿El líder comunica claramente la necesidad y los beneficios del cambio?",
            "¿El líder involucra al equipo en la planificación e implementación del cambio?",
            "¿El líder proporciona apoyo y recursos durante períodos de cambio?",
            "¿El líder gestiona la resistencia al cambio de manera efectiva?",
            "¿El líder celebra los éxitos y aprende de los desafíos durante el cambio?"
        ]
    },
    "innovacion": {
        "nombre": "Innovación",
        "descripcion": "Capacidad para fomentar la creatividad, la experimentación y la innovación en el equipo.",
        "preguntas": [
            "¿El líder fomenta la generación de nuevas ideas y enfoques?",
            "¿El líder crea un entorno seguro para la experimentación y el aprendizaje de los errores?",
            "¿El líder asigna tiempo y recursos para la innovación?",
            "¿El líder reconoce y recompensa la innovación y la creatividad?",
            "¿El líder implementa procesos para convertir ideas en soluciones prácticas?"
        ]
    },
    "desarrollo_talento": {
        "nombre": "Desarrollo de Talento",
        "descripcion": "Enfoque en el desarrollo continuo de las habilidades y capacidades del equipo.",
        "preguntas": [
            "¿El líder identifica las fortalezas y áreas de desarrollo de cada miembro del equipo?",
            "¿El líder proporciona oportunidades de aprendizaje y desarrollo?",
            "¿El líder ofrece coaching y mentoría regular?",
            "¿El líder crea planes de desarrollo individualizados?",
            "¿El líder fomenta una cultura de aprendizaje continuo?"
        ]
    },
    "inteligencia_emocional": {
        "nombre": "Inteligencia Emocional",
        "descripcion": "Capacidad para reconocer y gestionar las propias emociones y las de los demás.",
        "preguntas": [
            "¿El líder demuestra autoconciencia de sus emociones y su impacto en los demás?",
            "¿El líder gestiona efectivamente sus emociones, especialmente en situaciones de estrés?",
            "¿El líder muestra empatía y comprensión hacia los demás?",
            "¿El líder construye relaciones positivas basadas en la confianza y el respeto?",
            "¿El líder gestiona conflictos de manera constructiva?"
        ]
    }
}

# Definición de los niveles de madurez
NIVELES_MADUREZ = {
    1: "Inicial - Liderazgo reactivo y ad hoc",
    2: "En desarrollo - Liderazgo consciente con algunas prácticas establecidas",
    3: "Definido - Liderazgo estructurado con prácticas estandarizadas",
    4: "Gestionado - Liderazgo medido y adaptativo",
    5: "Optimizado - Liderazgo innovador y de mejora continua"
}

# Descripción detallada de los niveles de madurez por dimensión
DESCRIPCIONES_NIVELES = {
    "vision_estrategica": {
        1: "El líder se enfoca principalmente en objetivos a corto plazo sin una visión clara.",
        2: "El líder tiene una visión básica pero no está completamente alineada o comunicada.",
        3: "El líder desarrolla y comunica una visión clara alineada con los objetivos organizacionales.",
        4: "El líder involucra al equipo en el desarrollo de la visión y la adapta según el feedback.",
        5: "El líder crea una visión inspiradora que impulsa la innovación y se adapta proactivamente."
    },
    "liderazgo_servicial": {
        1: "El líder se enfoca principalmente en sus propias necesidades o las de la gerencia.",
        2: "El líder muestra cierta preocupación por el equipo pero de manera inconsistente.",
        3: "El líder regularmente prioriza las necesidades del equipo y elimina obstáculos.",
        4: "El líder consistentemente sirve al equipo y fomenta activamente su desarrollo.",
        5: "El líder crea una cultura de servicio donde todos se apoyan mutuamente."
    },
    "liderazgo_tecnico": {
        1: "El líder tiene conocimientos técnicos limitados o desactualizados.",
        2: "El líder tiene conocimientos técnicos básicos pero proporciona poca dirección.",
        3: "El líder proporciona dirección técnica sólida y establece estándares.",
        4: "El líder proporciona mentoría técnica efectiva y fomenta la excelencia técnica.",
        5: "El líder impulsa la innovación técnica y es reconocido como referente en su campo."
    },
    "gestion_equipos": {
        1: "El líder gestiona individuos más que un equipo cohesionado.",
        2: "El líder forma equipos básicos pero con roles poco claros o desequilibrados.",
        3: "El líder forma equipos efectivos con roles claros y fomenta la colaboración.",
        4: "El líder desarrolla equipos de alto rendimiento que trabajan con autonomía.",
        5: "El líder crea una cultura de equipo excepcional que atrae y retiene talento."
    },
    "comunicacion": {
        1: "La comunicación del líder es inconsistente, poco clara o unidireccional.",
        2: "El líder comunica información básica pero con efectividad variable.",
        3: "El líder comunica de manera clara y fomenta el diálogo abierto.",
        4: "El líder adapta su comunicación a diferentes audiencias y situaciones.",
        5: "El líder es un comunicador excepcional que inspira y conecta a todos los niveles."
    },
    "toma_decisiones": {
        1: "El líder toma decisiones reactivas, sin un proceso claro o sin involucrar a otros.",
        2: "El líder tiene un proceso básico de toma de decisiones pero inconsistente.",
        3: "El líder toma decisiones informadas e involucra a las personas adecuadas.",
        4: "El líder tiene un proceso sólido de toma de decisiones basado en datos.",
        5: "El líder equilibra perfectamente datos, intuición y participación en decisiones."
    },
    "gestion_cambio": {
        1: "El líder impone cambios sin preparación o apoyo adecuado.",
        2: "El líder comunica cambios pero proporciona apoyo limitado durante la transición.",
        3: "El líder planifica e implementa cambios de manera estructurada con apoyo.",
        4: "El líder involucra al equipo en el cambio y gestiona efectivamente la resistencia.",
        5: "El líder crea una cultura que abraza el cambio como oportunidad de mejora."
    },
    "innovacion": {
        1: "El líder se enfoca en mantener el status quo, con poca innovación.",
        2: "El líder está abierto a nuevas ideas pero proporciona poco apoyo para implementarlas.",
        3: "El líder fomenta activamente la innovación y proporciona recursos para ella.",
        4: "El líder crea un entorno seguro para experimentar y aprender de los errores.",
        5: "El líder impulsa una cultura de innovación continua que genera ventajas competitivas."
    },
    "desarrollo_talento": {
        1: "El líder proporciona poco o ningún desarrollo para el equipo.",
        2: "El líder ofrece algunas oportunidades de desarrollo pero sin un plan estructurado.",
        3: "El líder implementa planes de desarrollo para los miembros del equipo.",
        4: "El líder proporciona coaching regular y crea oportunidades de crecimiento.",
        5: "El líder crea una cultura de aprendizaje continuo y desarrollo mutuo."
    },
    "inteligencia_emocional": {
        1: "El líder muestra poca conciencia o gestión de las emociones propias o ajenas.",
        2: "El líder tiene cierta conciencia emocional pero respuestas inconsistentes.",
        3: "El líder demuestra autoconciencia y empatía en la mayoría de situaciones.",
        4: "El líder gestiona efectivamente las emociones y construye relaciones sólidas.",
        5: "El líder utiliza la inteligencia emocional para inspirar y transformar el equipo."
    }
}

# Recomendaciones por dimensión y nivel
RECOMENDACIONES = {
    "vision_estrategica": {
        1: [
            "Desarrollar una visión clara para el equipo alineada con los objetivos organizacionales",
            "Participar en talleres de planificación estratégica",
            "Solicitar mentoría de líderes con fuerte visión estratégica"
        ],
        2: [
            "Refinar la visión para hacerla más clara y alineada con los objetivos organizacionales",
            "Mejorar la comunicación de la visión al equipo",
            "Establecer metas específicas que apoyen la visión"
        ],
        3: [
            "Involucrar más al equipo en el refinamiento de la visión",
            "Implementar revisiones regulares de la visión para mantenerla relevante",
            "Conectar más explícitamente el trabajo diario con la visión"
        ],
        4: [
            "Desarrollar la capacidad del equipo para contribuir a la visión",
            "Implementar mecanismos para adaptar la visión según cambios en el entorno",
            "Compartir la visión más ampliamente en la organización"
        ],
        5: [
            "Mentorizar a otros líderes en el desarrollo de visión estratégica",
            "Participar en la definición de la visión organizacional",
            "Explorar visiones más ambiciosas e innovadoras"
        ]
    },
    "liderazgo_servicial": {
        1: [
            "Aprender los principios básicos del liderazgo servicial",
            "Comenzar a preguntar regularmente al equipo qué necesitan para tener éxito",
            "Identificar y eliminar al menos un obstáculo que enfrenta el equipo"
        ],
        2: [
            "Establecer check-ins regulares con los miembros del equipo",
            "Desarrollar un enfoque más consistente para apoyar al equipo",
            "Priorizar la eliminación de obstáculos para el equipo"
        ],
        3: [
            "Implementar prácticas formales de liderazgo servicial",
            "Desarrollar un plan para el crecimiento de cada miembro del equipo",
            "Solicitar feedback regular sobre cómo servir mejor al equipo"
        ],
        4: [
            "Mentorizar a otros en prácticas de liderazgo servicial",
            "Crear sistemas que faciliten el apoyo continuo al equipo",
            "Fomentar una cultura de servicio mutuo en el equipo"
        ],
        5: [
            "Liderar iniciativas organizacionales de liderazgo servicial",
            "Desarrollar nuevas prácticas innovadoras de liderazgo servicial",
            "Crear una comunidad de práctica de liderazgo servicial"
        ]
    },
    "liderazgo_tecnico": {
        1: [
            "Identificar áreas técnicas clave para desarrollo personal",
            "Establecer un plan de aprendizaje técnico continuo",
            "Buscar mentoría de líderes técnicos experimentados"
        ],
        2: [
            "Desarrollar mayor profundidad en áreas técnicas relevantes",
            "Comenzar a proporcionar dirección técnica básica al equipo",
            "Establecer algunos estándares técnicos básicos"
        ],
        3: [
            "Formalizar estándares y mejores prácticas técnicas",
            "Implementar revisiones técnicas regulares",
            "Desarrollar un programa de mentoría técnica"
        ],
        4: [
            "Establecer una comunidad de práctica técnica",
            "Implementar procesos para mantenerse actualizado con tendencias tecnológicas",
            "Desarrollar un plan de excelencia técnica para el equipo"
        ],
        5: [
            "Contribuir al avance del campo técnico (conferencias, publicaciones)",
            "Liderar iniciativas de innovación técnica",
            "Mentorizar a otros líderes técnicos"
        ]
    },
    "gestion_equipos": {
        1: [
            "Aprender principios básicos de formación y desarrollo de equipos",
            "Definir roles y responsabilidades claras para el equipo",
            "Implementar reuniones regulares de equipo"
        ],
        2: [
            "Evaluar y mejorar la composición del equipo",
            "Implementar actividades básicas de team building",
            "Desarrollar procesos para gestionar conflictos"
        ],
        3: [
            "Implementar prácticas formales de desarrollo de equipos",
            "Establecer métricas para evaluar la efectividad del equipo",
            "Fomentar mayor autonomía en el equipo"
        ],
        4: [
            "Desarrollar al equipo hacia la auto-organización",
            "Implementar prácticas avanzadas de colaboración",
            "Crear un plan de desarrollo para el equipo como unidad"
        ],
        5: [
            "Desarrollar enfoques innovadores para la gestión de equipos",
            "Mentorizar a otros líderes en desarrollo de equipos",
            "Crear una cultura de equipo que sea referente en la organización"
        ]
    },
    "comunicacion": {
        1: [
            "Desarrollar habilidades básicas de comunicación clara y concisa",
            "Implementar check-ins regulares con el equipo",
            "Practicar la escucha activa"
        ],
        2: [
            "Solicitar feedback sobre la efectividad de la comunicación",
            "Adaptar la comunicación a diferentes miembros del equipo",
            "Mejorar la estructura y claridad de las comunicaciones escritas"
        ],
        3: [
            "Implementar múltiples canales de comunicación según necesidades",
            "Desarrollar habilidades para comunicar temas complejos",
            "Establecer normas de comunicación para el equipo"
        ],
        4: [
            "Desarrollar habilidades avanzadas de comunicación persuasiva",
            "Implementar procesos para mejorar la comunicación en el equipo",
            "Mentorizar a otros en habilidades de comunicación"
        ],
        5: [
            "Desarrollar una estrategia de comunicación integral",
            "Liderar iniciativas para mejorar la comunicación organizacional",
            "Innovar en prácticas de comunicación efectiva"
        ]
    },
    "toma_decisiones": {
        1: [
            "Aprender modelos básicos de toma de decisiones",
            "Documentar decisiones importantes y sus razones",
            "Comenzar a involucrar al equipo en algunas decisiones"
        ],
        2: [
            "Implementar un proceso básico para decisiones importantes",
            "Mejorar el uso de datos en la toma de decisiones",
            "Clarificar qué decisiones se toman a qué nivel"
        ],
        3: [
            "Formalizar procesos de toma de decisiones",
            "Implementar revisiones post-decisión para aprendizaje",
            "Desarrollar marcos para diferentes tipos de decisiones"
        ],
        4: [
            "Implementar herramientas avanzadas de análisis de decisiones",
            "Optimizar el balance entre decisiones individuales y grupales",
            "Desarrollar la capacidad de toma de decisiones del equipo"
        ],
        5: [
            "Innovar en procesos de toma de decisiones",
            "Mentorizar a otros en toma de decisiones efectiva",
            "Liderar iniciativas para mejorar la toma de decisiones organizacional"
        ]
    },
    "gestion_cambio": {
        1: [
            "Aprender principios básicos de gestión del cambio",
            "Mejorar la comunicación durante períodos de cambio",
            "Identificar y abordar resistencias básicas al cambio"
        ],
        2: [
            "Desarrollar planes básicos de gestión del cambio",
            "Involucrar al equipo en la planificación de cambios",
            "Proporcionar más apoyo durante transiciones"
        ],
        3: [
            "Implementar metodologías formales de gestión del cambio",
            "Desarrollar champions del cambio dentro del equipo",
            "Establecer métricas para evaluar la efectividad del cambio"
        ],
        4: [
            "Implementar prácticas avanzadas de gestión del cambio",
            "Desarrollar la resiliencia del equipo ante el cambio",
            "Liderar cambios complejos que afectan a múltiples equipos"
        ],
        5: [
            "Desarrollar enfoques innovadores para la gestión del cambio",
            "Mentorizar a otros líderes en gestión del cambio",
            "Liderar transformaciones organizacionales significativas"
        ]
    },
    "innovacion": {
        1: [
            "Dedicar tiempo específico para la generación de ideas",
            "Implementar una caja de sugerencias para el equipo",
            "Comenzar a celebrar intentos de innovación, incluso si fallan"
        ],
        2: [
            "Establecer sesiones regulares de brainstorming",
            "Asignar pequeños recursos para experimentación",
            "Implementar un proceso básico para evaluar nuevas ideas"
        ],
        3: [
            "Implementar metodologías formales de innovación",
            "Establecer tiempo protegido para innovación (ej. 20% time)",
            "Desarrollar métricas para evaluar la innovación"
        ],
        4: [
            "Crear un programa estructurado de innovación",
            "Implementar procesos para escalar ideas exitosas",
            "Fomentar la colaboración interdisciplinaria para innovación"
        ],
        5: [
            "Desarrollar un ecosistema de innovación",
            "Liderar iniciativas de innovación organizacional",
            "Establecer asociaciones externas para impulsar la innovación"
        ]
    },
    "desarrollo_talento": {
        1: [
            "Identificar fortalezas y áreas de desarrollo para cada miembro del equipo",
            "Implementar check-ins regulares de desarrollo",
            "Proporcionar oportunidades básicas de aprendizaje"
        ],
        2: [
            "Crear planes de desarrollo individuales básicos",
            "Implementar sesiones regulares de feedback",
            "Proporcionar más oportunidades de aprendizaje y crecimiento"
        ],
        3: [
            "Implementar un programa formal de desarrollo de talento",
            "Establecer planes de carrera para miembros del equipo",
            "Desarrollar un programa de mentoría"
        ],
        4: [
            "Personalizar planes de desarrollo para maximizar potencial",
            "Implementar rotaciones y asignaciones para desarrollo",
            "Crear oportunidades de liderazgo para miembros del equipo"
        ],
        5: [
            "Desarrollar un programa integral de desarrollo de talento",
            "Mentorizar a otros líderes en desarrollo de talento",
            "Crear una cultura de aprendizaje continuo y desarrollo mutuo"
        ]
    },
    "inteligencia_emocional": {
        1: [
            "Desarrollar mayor autoconciencia emocional",
            "Practicar técnicas básicas de gestión emocional",
            "Comenzar a practicar la empatía activamente"
        ],
        2: [
            "Solicitar feedback sobre impacto emocional en otros",
            "Desarrollar técnicas más avanzadas de gestión emocional",
            "Mejorar la capacidad de reconocer emociones en otros"
        ],
        3: [
            "Implementar prácticas regulares de reflexión emocional",
            "Desarrollar habilidades para gestionar conversaciones difíciles",
            "Fomentar un entorno emocionalmente seguro"
        ],
        4: [
            "Utilizar la inteligencia emocional para desarrollar relaciones más profundas",
            "Implementar prácticas para fomentar bienestar emocional en el equipo",
            "Mentorizar a otros en inteligencia emocional"
        ],
        5: [
            "Utilizar la inteligencia emocional como herramienta transformacional",
            "Liderar iniciativas de bienestar emocional organizacional",
            "Desarrollar enfoques innovadores para el desarrollo de inteligencia emocional"
        ]
    }
}

def parse_arguments():
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description='Herramienta de Evaluación de Madurez de Liderazgo en TI')
    parser.add_argument('--output', default='informe_liderazgo.json', help='Archivo de salida para el informe de evaluación')
    parser.add_argument('--interactive', action='store_true', help='Ejecutar en modo interactivo')
    parser.add_argument('--organizacion', default='Mi Organización', help='Nombre de la organización')
    parser.add_argument('--generar-graficos', action='store_true', help='Generar gráficos de resultados')
    return parser.parse_args()

def solicitar_info_organizacion():
    """Solicita información básica de la organización."""
    print("\n=== INFORMACIÓN DE LA ORGANIZACIÓN ===")
    organizacion = input("Nombre de la organización: ")
    responsable = input("Responsable de la evaluación: ")
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    equipo = input("Nombre del equipo o área evaluada: ")
    
    return {
        "organizacion": organizacion,
        "responsable": responsable,
        "fecha": fecha,
        "equipo": equipo
    }

def evaluar_dimension_interactiva(dimension_id, dimension_info):
    """Solicita la evaluación de una dimensión específica en modo interactivo."""
    print(f"\n=== EVALUACIÓN DE DIMENSIÓN: {dimension_info['nombre']} ===")
    print(f"Descripción: {dimension_info['descripcion']}")
    print("\nPor favor, evalúe las siguientes afirmaciones en una escala de 1 a 5:")
    print("1: Totalmente en desacuerdo / Nunca")
    print("2: En desacuerdo / Raramente")
    print("3: Neutral / A veces")
    print("4: De acuerdo / Frecuentemente")
    print("5: Totalmente de acuerdo / Siempre")
    
    respuestas = []
    for i, pregunta in enumerate(dimension_info['preguntas']):
        while True:
            try:
                valor = int(input(f"\n{i+1}. {pregunta} (1-5): "))
                if 1 <= valor <= 5:
                    respuestas.append(valor)
                    break
                print("Error: El valor debe estar entre 1 y 5.")
            except ValueError:
                print("Error: Ingrese un número entero.")
    
    # Calcular nivel de madurez basado en las respuestas
    promedio = sum(respuestas) / len(respuestas)
    nivel_madurez = round(promedio)
    
    # Solicitar evidencias y observaciones
    print("\nPor favor, proporcione información adicional:")
    evidencias = input("Evidencias que respaldan esta evaluación: ")
    observaciones = input("Observaciones adicionales: ")
    
    return {
        "nivel_madurez": nivel_madurez,
        "respuestas_detalladas": respuestas,
        "promedio": round(promedio, 2),
        "evidencias": evidencias,
        "observaciones": observaciones
    }

def evaluar_dimensiones_interactivo():
    """Realiza la evaluación de todas las dimensiones en modo interactivo."""
    resultados = {}
    
    for dimension_id, dimension_info in DIMENSIONES_LIDERAZGO.items():
        resultados[dimension_id] = evaluar_dimension_interactiva(dimension_id, dimension_info)
    
    return resultados

def generar_datos_ejemplo():
    """Genera datos de ejemplo para la evaluación."""
    resultados = {}
    
    for dimension_id, dimension_info in DIMENSIONES_LIDERAZGO.items():
        # Generar nivel de madurez aleatorio pero realista
        nivel_madurez = np.random.choice([2, 3, 4], p=[0.3, 0.5, 0.2])
        
        # Generar respuestas detalladas consistentes con el nivel de madurez
        respuestas = []
        for _ in range(len(dimension_info['preguntas'])):
            # Añadir algo de variación aleatoria alrededor del nivel de madurez
            respuesta = max(1, min(5, int(nivel_madurez + np.random.choice([-1, 0, 1], p=[0.2, 0.6, 0.2]))))
            respuestas.append(respuesta)
        
        promedio = sum(respuestas) / len(respuestas)
        
        resultados[dimension_id] = {
            "nivel_madurez": int(nivel_madurez),
            "respuestas_detalladas": respuestas,
            "promedio": round(promedio, 2),
            "evidencias": f"Evidencias de ejemplo para {dimension_info['nombre']}",
            "observaciones": f"Observaciones de ejemplo para {dimension_info['nombre']}"
        }
    
    return resultados

def calcular_promedios(resultados):
    """Calcula el promedio general de madurez de liderazgo."""
    niveles = [r["nivel_madurez"] for r in resultados.values()]
    promedio = sum(niveles) / len(niveles)
    
    return {
        "promedio_general": round(promedio, 2),
        "nivel_general": round(promedio)
    }

def identificar_fortalezas_debilidades(resultados):
    """Identifica las principales fortalezas y áreas de mejora."""
    items = [(dimension_id, datos["nivel_madurez"]) for dimension_id, datos in resultados.items()]
    items.sort(key=lambda x: x[1], reverse=True)
    
    fortalezas = []
    for dimension_id, nivel in items[:3]:  # Top 3 fortalezas
        fortalezas.append({
            "dimension_id": dimension_id,
            "nombre": DIMENSIONES_LIDERAZGO[dimension_id]["nombre"],
            "nivel_madurez": nivel,
            "descripcion": DESCRIPCIONES_NIVELES[dimension_id][nivel]
        })
    
    items.sort(key=lambda x: x[1])
    areas_mejora = []
    for dimension_id, nivel in items[:3]:  # Top 3 áreas de mejora
        areas_mejora.append({
            "dimension_id": dimension_id,
            "nombre": DIMENSIONES_LIDERAZGO[dimension_id]["nombre"],
            "nivel_madurez": nivel,
            "descripcion": DESCRIPCIONES_NIVELES[dimension_id][nivel]
        })
    
    return {
        "fortalezas": fortalezas,
        "areas_mejora": areas_mejora
    }

def generar_recomendaciones(resultados):
    """Genera recomendaciones basadas en los resultados de la evaluación."""
    recomendaciones = []
    
    # Ordenar dimensiones por nivel de madurez (ascendente)
    items = [(dimension_id, datos["nivel_madurez"]) for dimension_id, datos in resultados.items()]
    items.sort(key=lambda x: x[1])
    
    # Generar recomendaciones para las 5 dimensiones con menor nivel de madurez
    for dimension_id, nivel in items[:5]:
        if dimension_id in RECOMENDACIONES and nivel in RECOMENDACIONES[dimension_id]:
            recomendaciones.append({
                "dimension_id": dimension_id,
                "nombre": DIMENSIONES_LIDERAZGO[dimension_id]["nombre"],
                "nivel_actual": nivel,
                "nivel_objetivo": min(5, nivel + 1),
                "acciones": RECOMENDACIONES[dimension_id][nivel]
            })
    
    return recomendaciones

def generar_plan_desarrollo(recomendaciones):
    """Genera un plan de desarrollo basado en las recomendaciones."""
    plan = []
    
    # Ordenar recomendaciones por nivel actual (ascendente)
    recomendaciones_ordenadas = sorted(recomendaciones, key=lambda x: x["nivel_actual"])
    
    for i, recomendacion in enumerate(recomendaciones_ordenadas):
        # Calcular fechas objetivo (ejemplo: 2 meses por cada recomendación, escalonadas)
        fecha_inicio = datetime.datetime.now()
        meses_adicionales = i * 2
        fecha_objetivo = (fecha_inicio + datetime.timedelta(days=30 * meses_adicionales)).strftime("%Y-%m-%d")
        
        plan.append({
            "dimension_id": recomendacion["dimension_id"],
            "nombre": recomendacion["nombre"],
            "nivel_actual": recomendacion["nivel_actual"],
            "nivel_objetivo": recomendacion["nivel_objetivo"],
            "acciones": recomendacion["acciones"],
            "fecha_objetivo": fecha_objetivo,
            "recursos_sugeridos": generar_recursos_sugeridos(recomendacion["dimension_id"])
        })
    
    return plan

def generar_recursos_sugeridos(dimension_id):
    """Genera recursos sugeridos para el desarrollo en una dimensión específica."""
    recursos = {
        "vision_estrategica": [
            "Libro: 'Strategic Leadership: The General's Art' por Mark Grandstaff y Georgia Sorenson",
            "Curso: 'Developing Strategic Vision' en LinkedIn Learning",
            "Artículo: 'Strategic Leadership: The Essential Skills' en Harvard Business Review"
        ],
        "liderazgo_servicial": [
            "Libro: 'Servant Leadership: A Journey into the Nature of Legitimate Power and Greatness' por Robert K. Greenleaf",
            "Curso: 'Servant Leadership: Leading with Others in Mind' en Udemy",
            "Artículo: 'Why Servant Leadership Is the Future of Leadership' en Forbes"
        ],
        "liderazgo_tecnico": [
            "Libro: 'The Manager's Path: A Guide for Tech Leaders Navigating Growth and Change' por Camille Fournier",
            "Curso: 'Technical Leadership Masterclass' en Pluralsight",
            "Comunidad: 'Tech Leadership Community' en Slack"
        ],
        "gestion_equipos": [
            "Libro: 'The Five Dysfunctions of a Team' por Patrick Lencioni",
            "Curso: 'Leading High-Performance Teams' en Coursera",
            "Herramienta: 'Team Canvas' para sesiones de alineación de equipo"
        ],
        "comunicacion": [
            "Libro: 'Crucial Conversations: Tools for Talking When Stakes Are High' por Kerry Patterson",
            "Curso: 'Communication Foundations' en LinkedIn Learning",
            "Taller: 'Effective Communication for Technical Leaders'"
        ],
        "toma_decisiones": [
            "Libro: 'Thinking, Fast and Slow' por Daniel Kahneman",
            "Curso: 'Critical Thinking and Decision Making' en edX",
            "Herramienta: 'WRAP Framework' de Chip y Dan Heath"
        ],
        "gestion_cambio": [
            "Libro: 'Switch: How to Change Things When Change Is Hard' por Chip y Dan Heath",
            "Curso: 'Leading Organizational Change' en Coursera",
            "Certificación: 'Prosci Change Management Certification'"
        ],
        "innovacion": [
            "Libro: 'The Innovator's Dilemma' por Clayton Christensen",
            "Curso: 'Design Thinking for Innovation' en Coursera",
            "Taller: 'Innovation Sprint Workshop'"
        ],
        "desarrollo_talento": [
            "Libro: 'Radical Candor' por Kim Scott",
            "Curso: 'Coaching for Results' en LinkedIn Learning",
            "Certificación: 'International Coaching Federation (ICF) Certification'"
        ],
        "inteligencia_emocional": [
            "Libro: 'Emotional Intelligence 2.0' por Travis Bradberry y Jean Greaves",
            "Curso: 'Developing Emotional Intelligence' en LinkedIn Learning",
            "Evaluación: 'EQ-i 2.0 Assessment'"
        ]
    }
    
    return recursos.get(dimension_id, ["No hay recursos específicos disponibles para esta dimensión"])

def generar_graficos(resultados, info_organizacion, directorio_salida="graficos"):
    """Genera gráficos visuales de los resultados de la evaluación."""
    # Crear directorio si no existe
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)
    
    # 1. Gráfico de radar de niveles de madurez por dimensión
    generar_grafico_radar(resultados, os.path.join(directorio_salida, "radar_dimensiones.png"), info_organizacion)
    
    # 2. Gráfico de barras comparando niveles actuales con objetivos
    generar_grafico_comparativo(resultados, os.path.join(directorio_salida, "comparativo_niveles.png"), info_organizacion)
    
    return [
        os.path.join(directorio_salida, "radar_dimensiones.png"),
        os.path.join(directorio_salida, "comparativo_niveles.png")
    ]

def generar_grafico_radar(resultados, archivo_salida, info_organizacion):
    """Genera un gráfico de radar de los niveles de madurez por dimensión."""
    dimensiones = []
    niveles = []
    
    for dimension_id, datos in resultados.items():
        dimensiones.append(DIMENSIONES_LIDERAZGO[dimension_id]["nombre"])
        niveles.append(datos["nivel_madurez"])
    
    # Convertir a formato radar (cerrar el polígono)
    dimensiones = dimensiones + [dimensiones[0]]
    niveles = niveles + [niveles[0]]
    
    # Crear figura
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, polar=True)
    
    # Configurar ejes
    angles = np.linspace(0, 2*np.pi, len(dimensiones), endpoint=False).tolist()
    angles += angles[:1]  # Cerrar el polígono
    
    # Dibujar niveles
    ax.plot(angles, niveles, 'o-', linewidth=2)
    ax.fill(angles, niveles, alpha=0.25)
    
    # Configurar etiquetas y título
    ax.set_thetagrids(np.degrees(angles[:-1]), dimensiones[:-1])
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'])
    ax.set_title(f'Niveles de Madurez de Liderazgo - {info_organizacion["organizacion"]}', size=15, y=1.1)
    ax.grid(True)
    
    # Guardar figura
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=300, bbox_inches='tight')
    plt.close()

def generar_grafico_comparativo(resultados, archivo_salida, info_organizacion):
    """Genera un gráfico de barras comparando niveles actuales con objetivos."""
    dimensiones = []
    niveles_actuales = []
    niveles_objetivo = []
    
    for dimension_id, datos in resultados.items():
        dimensiones.append(DIMENSIONES_LIDERAZGO[dimension_id]["nombre"])
        niveles_actuales.append(datos["nivel_madurez"])
        niveles_objetivo.append(min(5, datos["nivel_madurez"] + 1))  # Nivel objetivo es actual + 1, máximo 5
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Configurar posiciones de barras
    x = np.arange(len(dimensiones))
    width = 0.35
    
    # Dibujar barras
    rects1 = ax.bar(x - width/2, niveles_actuales, width, label='Nivel Actual')
    rects2 = ax.bar(x + width/2, niveles_objetivo, width, label='Nivel Objetivo')
    
    # Añadir etiquetas y título
    ax.set_xlabel('Dimensiones de Liderazgo')
    ax.set_ylabel('Nivel de Madurez')
    ax.set_title(f'Comparación de Niveles Actuales y Objetivos - {info_organizacion["organizacion"]}')
    ax.set_xticks(x)
    ax.set_xticklabels(dimensiones, rotation=45, ha='right')
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.legend()
    
    # Añadir valores sobre las barras
    for rect in rects1:
        height = rect.get_height()
        ax.annotate(f'{height}',
                    xy=(rect.get_x() + rect.get_width()/2, height),
                    xytext=(0, 3),  # 3 puntos de desplazamiento vertical
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    for rect in rects2:
        height = rect.get_height()
        ax.annotate(f'{height}',
                    xy=(rect.get_x() + rect.get_width()/2, height),
                    xytext=(0, 3),  # 3 puntos de desplazamiento vertical
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    # Guardar figura
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=300)
    plt.close()

def generar_informe(info_organizacion, resultados, archivo_salida):
    """Genera un informe completo con los resultados de la evaluación."""
    # Calcular promedios
    promedios = calcular_promedios(resultados)
    
    # Identificar fortalezas y áreas de mejora
    analisis = identificar_fortalezas_debilidades(resultados)
    
    # Generar recomendaciones
    recomendaciones = generar_recomendaciones(resultados)
    
    # Generar plan de desarrollo
    plan_desarrollo = generar_plan_desarrollo(recomendaciones)
    
    # Estructura del informe
    informe = {
        "info_organizacion": info_organizacion,
        "fecha_generacion": datetime.datetime.now().strftime("%Y-%m-%d"),
        "resultados_detallados": {
            dimension_id: {
                "nombre": DIMENSIONES_LIDERAZGO[dimension_id]["nombre"],
                "descripcion": DIMENSIONES_LIDERAZGO[dimension_id]["descripcion"],
                "nivel_madurez": datos["nivel_madurez"],
                "descripcion_nivel": DESCRIPCIONES_NIVELES[dimension_id][datos["nivel_madurez"]],
                "promedio": datos["promedio"],
                "respuestas_detalladas": datos["respuestas_detalladas"],
                "evidencias": datos["evidencias"],
                "observaciones": datos["observaciones"]
            }
            for dimension_id, datos in resultados.items()
        },
        "promedios": promedios,
        "analisis": analisis,
        "recomendaciones": recomendaciones,
        "plan_desarrollo": plan_desarrollo
    }
    
    # Guardar informe
    try:
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(informe, f, ensure_ascii=False, indent=4)
        print(f"\nInforme generado exitosamente: {archivo_salida}")
    except Exception as e:
        print(f"\nError al guardar el informe: {e}")
        sys.exit(1)
    
    return informe

def main():
    """Función principal."""
    args = parse_arguments()
    
    print("\n=== HERRAMIENTA DE EVALUACIÓN DE MADUREZ DE LIDERAZGO EN TI ===")
    
    # Verificar que el directorio de salida existe
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"Error al crear el directorio de salida: {e}")
            sys.exit(1)
    
    # Obtener información de la organización
    if args.interactive:
        info_organizacion = solicitar_info_organizacion()
    else:
        info_organizacion = {
            "organizacion": args.organizacion,
            "responsable": "Usuario Ejemplo",
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d"),
            "equipo": "Equipo de TI"
        }
    
    # Realizar evaluación
    if args.interactive:
        print("\nIniciando evaluación interactiva de dimensiones de liderazgo...")
        resultados = evaluar_dimensiones_interactivo()
    else:
        print("\nGenerando datos de ejemplo para la evaluación...")
        resultados = generar_datos_ejemplo()
    
    # Generar informe
    informe = generar_informe(info_organizacion, resultados, args.output)
    
    # Generar gráficos si se solicita
    if args.generar_graficos:
        print("\nGenerando gráficos de resultados...")
        graficos = generar_graficos(resultados, info_organizacion)
        print(f"Gráficos generados: {', '.join(graficos)}")
    
    print("\n=== RESUMEN DE RESULTADOS ===")
    print(f"Nivel de madurez promedio: {informe['promedios']['promedio_general']} ({NIVELES_MADUREZ[informe['promedios']['nivel_general']]})")
    
    print("\nPrincipales fortalezas:")
    for i, fortaleza in enumerate(informe['analisis']['fortalezas']):
        print(f"{i+1}. {fortaleza['nombre']} (Nivel {fortaleza['nivel_madurez']})")
    
    print("\nPrincipales áreas de mejora:")
    for i, area in enumerate(informe['analisis']['areas_mejora']):
        print(f"{i+1}. {area['nombre']} (Nivel {area['nivel_madurez']})")
    
    print(f"\nPara más detalles, consulte el informe completo: {args.output}")

if __name__ == "__main__":
    main()

