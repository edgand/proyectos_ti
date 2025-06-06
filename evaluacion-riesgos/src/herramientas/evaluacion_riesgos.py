#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Herramienta de Evaluación de Riesgos de Seguridad de la Información

Esta herramienta permite realizar evaluaciones de riesgos de seguridad de la información
utilizando diferentes metodologías como OCTAVE Allegro, FAIR y NIST SP 800-30.
Genera un informe detallado con los resultados de la evaluación.

Uso:
    python evaluacion_riesgos.py --metodologia <octave|fair|nist> [--output informe_riesgos.json] [--interactive]
"""

import argparse
import json
import os
import sys
import datetime
import random
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# --- Definiciones Comunes ---
NIVELES_IMPACTO = {
    1: "Muy Bajo",
    2: "Bajo",
    3: "Moderado",
    4: "Alto",
    5: "Muy Alto"
}

NIVELES_PROBABILIDAD = {
    1: "Muy Baja",
    2: "Baja",
    3: "Moderada",
    4: "Alta",
    5: "Muy Alta"
}

NIVELES_RIESGO = {
    "Muy Bajo": "El riesgo es insignificante y puede ser aceptado sin tratamiento adicional.",
    "Bajo": "El riesgo es bajo y puede requerir monitoreo o tratamiento de bajo costo.",
    "Moderado": "El riesgo es moderado y requiere consideración para tratamiento.",
    "Alto": "El riesgo es alto y requiere tratamiento prioritario.",
    "Muy Alto": "El riesgo es muy alto y requiere acción inmediata para tratamiento."
}

MATRIZ_RIESGO_5X5 = [
    # Probabilidad \ Impacto -> Muy Bajo, Bajo, Moderado, Alto, Muy Alto
    ["Muy Bajo", "Bajo",     "Moderado", "Alto",     "Muy Alto"], # Muy Alta
    ["Muy Bajo", "Bajo",     "Moderado", "Alto",     "Alto"    ], # Alta
    ["Muy Bajo", "Bajo",     "Bajo",     "Moderado", "Alto"    ], # Moderada
    ["Muy Bajo", "Muy Bajo", "Bajo",     "Moderado", "Moderado"], # Baja
    ["Muy Bajo", "Muy Bajo", "Muy Bajo", "Bajo",     "Moderado"]  # Muy Baja
]

# --- Metodología OCTAVE Allegro ---

AREAS_IMPACTO_OCTAVE = [
    "Reputación y Confianza del Cliente",
    "Financiero",
    "Productividad",
    "Seguridad y Bienestar (Vida y Salud)",
    "Multas y Sanciones Legales"
]

CONTENEDORES_OCTAVE = {
    "tecnico": "Sistemas, aplicaciones, redes, dispositivos",
    "fisico": "Instalaciones, hardware, documentos físicos",
    "personas": "Empleados, contratistas, clientes con acceso"
}

def evaluar_octave_allegro_interactivo():
    """Realiza la evaluación de riesgos utilizando OCTAVE Allegro en modo interactivo."""
    print("\n=== EVALUACIÓN DE RIESGOS - OCTAVE ALLEGRO ===")
    
    # 1. Establecer Criterios de Medición de Riesgo
    print("\n--- Fase 1: Establecer Criterios de Medición de Riesgo ---")
    criterios_riesgo = {}
    for area in AREAS_IMPACTO_OCTAVE:
        while True:
            try:
                prioridad = int(input(f"Prioridad para 	\"{area}\" (1-5, 5=más alta): "))
                if 1 <= prioridad <= 5:
                    criterios_riesgo[area] = prioridad
                    break
                print("Error: Ingrese un número entre 1 y 5.")
            except ValueError:
                print("Error: Ingrese un número entero.")

    # 2. Desarrollar Perfiles de Activos de Información
    print("\n--- Fase 2: Desarrollar Perfiles de Activos de Información ---")
    activos = []
    num_activos = int(input("Número de activos de información críticos a perfilar: "))
    for i in range(num_activos):
        print(f"\n--- Perfilando Activo #{i+1} ---")
        nombre_activo = input("Nombre del activo: ")
        descripcion_activo = input("Descripción del activo: ")
        propietario_activo = input("Propietario del activo: ")
        requisitos_seguridad = input("Requisitos de seguridad (Confidencialidad, Integridad, Disponibilidad): ")
        
        contenedores_seleccionados = []
        print("Seleccione los contenedores para este activo (separados por coma):")
        for c_id, c_desc in CONTENEDORES_OCTAVE.items():
            print(f"- {c_id}: {c_desc}")
        seleccion = input("Contenedores: ").split(",")
        contenedores_seleccionados = [s.strip() for s in seleccion if s.strip() in CONTENEDORES_OCTAVE]
        
        activos.append({
            "nombre": nombre_activo,
            "descripcion": descripcion_activo,
            "propietario": propietario_activo,
            "requisitos_seguridad": requisitos_seguridad,
            "contenedores": contenedores_seleccionados
        })

    # 3. Identificar Amenazas
    print("\n--- Fase 3: Identificar Amenazas ---")
    amenazas_octave = []
    num_amenazas = int(input("Número de escenarios de amenaza a identificar: "))
    for i in range(num_amenazas):
        print(f"\n--- Identificando Amenaza #{i+1} ---")
        descripcion_amenaza = input("Descripción del escenario de amenaza: ")
        activo_afectado = input(f"Activo afectado (de los perfilados anteriormente): ")
        fuente_amenaza = input("Fuente de la amenaza (ej. Interna, Externa, Accidental, Deliberada): ")
        resultado_no_deseado = input("Resultado no deseado: ")
        
        amenazas_octave.append({
            "descripcion": descripcion_amenaza,
            "activo_afectado": activo_afectado,
            "fuente": fuente_amenaza,
            "resultado_no_deseado": resultado_no_deseado
        })

    # 4. Identificar y Mitigar Riesgos
    print("\n--- Fase 4: Identificar y Mitigar Riesgos ---")
    riesgos_octave = []
    for i, amenaza in enumerate(amenazas_octave):
        print(f"\n--- Evaluando Riesgo para Amenaza: {amenaza["descripcion"]} ---")
        impacto_total = 0
        print("Evalúe el impacto en cada área (1-5, 5=más alto):")
        impactos_detalle = {}
        for area, prioridad_area in criterios_riesgo.items():
            while True:
                try:
                    valor_impacto = int(input(f"Impacto en 	\"{area}\" (Prioridad {prioridad_area}): "))
                    if 1 <= valor_impacto <= 5:
                        impacto_total += valor_impacto * prioridad_area
                        impactos_detalle[area] = valor_impacto
                        break
                    print("Error: Ingrese un número entre 1 y 5.")
                except ValueError:
                    print("Error: Ingrese un número entero.")
        
        # Normalizar impacto total a una escala de 1-5 (aproximado)
        # Max impacto posible: 5 * sum(prioridades)
        # Min impacto posible: 1 * sum(prioridades)
        max_prioridad_sum = sum(criterios_riesgo.values())
        if max_prioridad_sum == 0: max_prioridad_sum = 1 # Evitar división por cero
        
        # Simple normalización, se puede mejorar
        nivel_impacto_octave = round(np.clip((impacto_total / (max_prioridad_sum * 5)) * 5, 1, 5))
        
        while True:
            try:
                probabilidad_octave = int(input("Probabilidad de ocurrencia de la amenaza (1-5, 5=más alta): "))
                if 1 <= probabilidad_octave <= 5:
                    break
                print("Error: Ingrese un número entre 1 y 5.")
            except ValueError:
                print("Error: Ingrese un número entero.")
        
        # Usar matriz de riesgo para determinar nivel de riesgo
        # Ajustar índices para la matriz (0-4)
        nivel_riesgo_str = MATRIZ_RIESGO_5X5[5 - probabilidad_octave][nivel_impacto_octave - 1]
        
        estrategia_mitigacion = input("Estrategia de mitigación propuesta: ")
        
        riesgos_octave.append({
            "amenaza": amenaza["descripcion"],
            "activo_afectado": amenaza["activo_afectado"],
            "impacto_detalle": impactos_detalle,
            "impacto_total_ponderado": impacto_total,
            "nivel_impacto_calculado": nivel_impacto_octave,
            "probabilidad_ocurrencia": probabilidad_octave,
            "nivel_riesgo": nivel_riesgo_str,
            "descripcion_nivel_riesgo": NIVELES_RIESGO.get(nivel_riesgo_str, "N/A"),
            "estrategia_mitigacion": estrategia_mitigacion
        })

    return {
        "metodologia": "OCTAVE Allegro",
        "criterios_riesgo": criterios_riesgo,
        "activos": activos,
        "amenazas": amenazas_octave,
        "riesgos": riesgos_octave
    }

# --- Metodología FAIR ---

FACTORES_FAIR = {
    "frecuencia_evento_amenaza": "Frecuencia con la que los actores de amenaza actúan de manera que podrían causar una pérdida.",
    "vulnerabilidad": "Probabilidad de que un activo sea incapaz de resistir las acciones de un actor de amenaza.",
    "capacidad_amenaza": "Nivel de fuerza que un actor de amenaza es capaz de aplicar contra un activo.",
    "resistencia_control": "Fuerza de un control en comparación con un nivel específico de capacidad de amenaza.",
    "perdida_primaria": "Pérdidas directas resultantes de un evento (ej. costo de reemplazo, costo de respuesta).",
    "perdida_secundaria": "Pérdidas indirectas (ej. daño reputacional, multas regulatorias)."
}

def evaluar_fair_interactivo():
    """Realiza la evaluación de riesgos utilizando FAIR en modo interactivo."""
    print("\n=== EVALUACIÓN DE RIESGOS - FAIR ===")
    print("FAIR se enfoca en la cuantificación del riesgo. Esta versión interactiva simplificará la estimación.")
    
    riesgos_fair = []
    num_escenarios = int(input("Número de escenarios de riesgo a analizar: "))
    
    for i in range(num_escenarios):
        print(f"\n--- Analizando Escenario de Riesgo #{i+1} ---")
        descripcion_escenario = input("Descripción del escenario de riesgo (ej. Ransomware en servidor de archivos): ")
        activo_principal = input("Activo principal afectado: ")
        actor_amenaza = input("Actor de amenaza principal (ej. Cibercriminales, Insider malicioso): ")
        
        print("\nEstime los siguientes factores (rangos o valores puntuales donde sea posible):")
        
        # Frecuencia de Evento de Amenaza (Loss Event Frequency - LEF)
        print(f"\nFactor: Frecuencia de Evento de Amenaza ({FACTORES_FAIR["frecuencia_evento_amenaza"]})")
        lef_min = float(input("Estimación mínima de eventos por año (ej. 0.1 para 1 vez cada 10 años): "))
        lef_max = float(input("Estimación máxima de eventos por año (ej. 2 para 2 veces al año): "))
        lef_probable = float(input("Estimación más probable de eventos por año: "))
        
        # Vulnerabilidad
        print(f"\nFactor: Vulnerabilidad ({FACTORES_FAIR["vulnerabilidad"]})")
        vulnerabilidad_min = float(input("Probabilidad mínima de que la amenaza tenga éxito (0.0 - 1.0): "))
        vulnerabilidad_max = float(input("Probabilidad máxima de que la amenaza tenga éxito (0.0 - 1.0): "))
        vulnerabilidad_probable = float(input("Probabilidad más probable de que la amenaza tenga éxito (0.0 - 1.0): "))
        
        # Magnitud de Pérdida (Loss Magnitude - LM)
        print(f"\nFactor: Magnitud de Pérdida Primaria ({FACTORES_FAIR["perdida_primaria"]})")
        lm_primaria_min = float(input("Estimación mínima de pérdida primaria (en USD): "))
        lm_primaria_max = float(input("Estimación máxima de pérdida primaria (en USD): "))
        lm_primaria_probable = float(input("Estimación más probable de pérdida primaria (en USD): "))
        
        print(f"\nFactor: Magnitud de Pérdida Secundaria ({FACTORES_FAIR["perdida_secundaria"]})")
        lm_secundaria_min = float(input("Estimación mínima de pérdida secundaria (en USD): "))
        lm_secundaria_max = float(input("Estimación máxima de pérdida secundaria (en USD): "))
        lm_secundaria_probable = float(input("Estimación más probable de pérdida secundaria (en USD): "))
        
        # Simulación Monte Carlo simplificada (usando valores probables para demostración)
        # En una implementación real, se usarían distribuciones y múltiples iteraciones
        frecuencia_perdida_probable = lef_probable * vulnerabilidad_probable
        magnitud_perdida_total_probable = lm_primaria_probable + lm_secundaria_probable
        riesgo_anualizado_probable = frecuencia_perdida_probable * magnitud_perdida_total_probable
        
        riesgos_fair.append({
            "escenario": descripcion_escenario,
            "activo_principal": activo_principal,
            "actor_amenaza": actor_amenaza,
            "frecuencia_evento_amenaza": {"min": lef_min, "max": lef_max, "probable": lef_probable},
            "vulnerabilidad": {"min": vulnerabilidad_min, "max": vulnerabilidad_max, "probable": vulnerabilidad_probable},
            "perdida_primaria": {"min": lm_primaria_min, "max": lm_primaria_max, "probable": lm_primaria_probable},
            "perdida_secundaria": {"min": lm_secundaria_min, "max": lm_secundaria_max, "probable": lm_secundaria_probable},
            "frecuencia_perdida_anual_probable": round(frecuencia_perdida_probable, 2),
            "magnitud_perdida_total_probable_usd": round(magnitud_perdida_total_probable, 2),
            "riesgo_anualizado_probable_usd": round(riesgo_anualizado_probable, 2)
        })
        
    return {
        "metodologia": "FAIR",
        "riesgos": riesgos_fair
    }

# --- Metodología NIST SP 800-30 ---

FUENTES_AMENAZA_NIST = [
    "Adversario (ej. Cibercriminal, Estado-Nación, Insider)",
    "No Adversario (ej. Error humano, Falla de sistema, Desastre natural)"
]

EVENTOS_AMENAZA_NIST = [
    "Acceso no autorizado", "Uso indebido de información", "Denegación de servicio", 
    "Modificación no autorizada", "Destrucción de información/sistemas"
]

def evaluar_nist_interactivo():
    """Realiza la evaluación de riesgos utilizando NIST SP 800-30 en modo interactivo."""
    print("\n=== EVALUACIÓN DE RIESGOS - NIST SP 800-30 ===")
    
    riesgos_nist = []
    num_riesgos = int(input("Número de riesgos a identificar y evaluar: "))
    
    for i in range(num_riesgos):
        print(f"\n--- Evaluando Riesgo #{i+1} ---")
        
        # Identificar Amenazas
        print("\nIdentificación de Amenazas:")
        fuente_amenaza_nist = input(f"Fuente de amenaza ({ ", ".join(FUENTES_AMENAZA_NIST) }): ")
        evento_amenaza_nist = input(f"Evento de amenaza ({ ", ".join(EVENTOS_AMENAZA_NIST) }): ")
        descripcion_amenaza_nist = input("Descripción adicional de la amenaza: ")
        
        # Identificar Vulnerabilidades
        print("\nIdentificación de Vulnerabilidades:")
        descripcion_vulnerabilidad_nist = input("Descripción de la vulnerabilidad preexistente o condición explotable: ")
        
        # Determinar Probabilidad de Ocurrencia
        print("\nProbabilidad de Ocurrencia:")
        while True:
            try:
                probabilidad_nist = int(input(f"Probabilidad de que la amenaza explote la vulnerabilidad (1-5, 1={NIVELES_PROBABILIDAD[1]} ... 5={NIVELES_PROBABILIDAD[5]}): "))
                if 1 <= probabilidad_nist <= 5:
                    break
                print("Error: Ingrese un número entre 1 y 5.")
            except ValueError:
                print("Error: Ingrese un número entero.")
        
        # Determinar Impacto
        print("\nImpacto (si la amenaza se materializa):")
        while True:
            try:
                impacto_nist = int(input(f"Impacto en la organización (1-5, 1={NIVELES_IMPACTO[1]} ... 5={NIVELES_IMPACTO[5]}): "))
                if 1 <= impacto_nist <= 5:
                    break
                print("Error: Ingrese un número entre 1 y 5.")
            except ValueError:
                print("Error: Ingrese un número entero.")
        
        # Determinar Riesgo
        # Ajustar índices para la matriz (0-4)
        nivel_riesgo_str_nist = MATRIZ_RIESGO_5X5[5 - probabilidad_nist][impacto_nist - 1]
        
        controles_existentes = input("Controles de seguridad existentes relevantes: ")
        recomendaciones_nist = input("Recomendaciones para tratamiento del riesgo: ")
        
        riesgos_nist.append({
            "fuente_amenaza": fuente_amenaza_nist,
            "evento_amenaza": evento_amenaza_nist,
            "descripcion_amenaza": descripcion_amenaza_nist,
            "vulnerabilidad": descripcion_vulnerabilidad_nist,
            "probabilidad_ocurrencia": probabilidad_nist,
            "probabilidad_descripcion": NIVELES_PROBABILIDAD[probabilidad_nist],
            "impacto": impacto_nist,
            "impacto_descripcion": NIVELES_IMPACTO[impacto_nist],
            "nivel_riesgo": nivel_riesgo_str_nist,
            "descripcion_nivel_riesgo": NIVELES_RIESGO.get(nivel_riesgo_str_nist, "N/A"),
            "controles_existentes": controles_existentes,
            "recomendaciones": recomendaciones_nist
        })
        
    return {
        "metodologia": "NIST SP 800-30",
        "riesgos": riesgos_nist
    }

# --- Funciones Auxiliares ---

def generar_datos_ejemplo_octave():
    """Genera datos de ejemplo para OCTAVE Allegro."""
    criterios_riesgo = {area: random.randint(3, 5) for area in AREAS_IMPACTO_OCTAVE}
    activos = [
        {"nombre": "Servidor de Base de Datos Clientes", "descripcion": "Almacena información sensible de clientes", "propietario": "Equipo de TI", "requisitos_seguridad": "Alta C, Alta I, Media A", "contenedores": ["tecnico", "fisico"]},
        {"nombre": "Aplicación Web de Ventas", "descripcion": "Plataforma de e-commerce", "propietario": "Equipo de Ventas", "requisitos_seguridad": "Media C, Alta I, Alta A", "contenedores": ["tecnico"]}
    ]
    amenazas_octave = [
        {"descripcion": "Acceso no autorizado a la base de datos de clientes", "activo_afectado": "Servidor de Base de Datos Clientes", "fuente": "Externa Deliberada", "resultado_no_deseado": "Fuga de datos de clientes"},
        {"descripcion": "Ataque de Denegación de Servicio a la aplicación web", "activo_afectado": "Aplicación Web de Ventas", "fuente": "Externa Deliberada", "resultado_no_deseado": "Interrupción del servicio de ventas"}
    ]
    riesgos_octave = []
    for amenaza in amenazas_octave:
        impactos_detalle = {area: random.randint(2, 5) for area in AREAS_IMPACTO_OCTAVE}
        impacto_total = sum(impactos_detalle[area] * criterios_riesgo[area] for area in AREAS_IMPACTO_OCTAVE)
        max_prioridad_sum = sum(criterios_riesgo.values())
        if max_prioridad_sum == 0: max_prioridad_sum = 1
        nivel_impacto_octave = round(np.clip((impacto_total / (max_prioridad_sum * 5)) * 5, 1, 5))
        probabilidad_octave = random.randint(2, 4)
        nivel_riesgo_str = MATRIZ_RIESGO_5X5[5 - probabilidad_octave][nivel_impacto_octave - 1]
        riesgos_octave.append({
            "amenaza": amenaza["descripcion"],
            "activo_afectado": amenaza["activo_afectado"],
            "impacto_detalle": impactos_detalle,
            "impacto_total_ponderado": impacto_total,
            "nivel_impacto_calculado": nivel_impacto_octave,
            "probabilidad_ocurrencia": probabilidad_octave,
            "nivel_riesgo": nivel_riesgo_str,
            "descripcion_nivel_riesgo": NIVELES_RIESGO.get(nivel_riesgo_str, "N/A"),
            "estrategia_mitigacion": "Implementar controles de acceso más robustos y monitoreo."
        })
    return {
        "metodologia": "OCTAVE Allegro",
        "criterios_riesgo": criterios_riesgo,
        "activos": activos,
        "amenazas": amenazas_octave,
        "riesgos": riesgos_octave
    }

def generar_datos_ejemplo_fair():
    """Genera datos de ejemplo para FAIR."""
    riesgos_fair = [
        {
            "escenario": "Exfiltración de datos de clientes por malware en estación de trabajo de soporte",
            "activo_principal": "Datos de Clientes",
            "actor_amenaza": "Cibercriminales (externos)",
            "frecuencia_evento_amenaza": {"min": 0.5, "max": 2, "probable": 1},
            "vulnerabilidad": {"min": 0.2, "max": 0.6, "probable": 0.4},
            "perdida_primaria": {"min": 5000, "max": 20000, "probable": 10000},
            "perdida_secundaria": {"min": 20000, "max": 100000, "probable": 50000},
            "frecuencia_perdida_anual_probable": 0.4,
            "magnitud_perdida_total_probable_usd": 60000,
            "riesgo_anualizado_probable_usd": 24000
        },
        {
            "escenario": "Interrupción de servicio de producción por error de configuración de firewall",
            "activo_principal": "Servicio de Producción XYZ",
            "actor_amenaza": "Personal Interno (error accidental)",
            "frecuencia_evento_amenaza": {"min": 1, "max": 4, "probable": 2},
            "vulnerabilidad": {"min": 0.1, "max": 0.3, "probable": 0.2},
            "perdida_primaria": {"min": 100000, "max": 500000, "probable": 250000},
            "perdida_secundaria": {"min": 50000, "max": 200000, "probable": 100000},
            "frecuencia_perdida_anual_probable": 0.4,
            "magnitud_perdida_total_probable_usd": 350000,
            "riesgo_anualizado_probable_usd": 140000
        }
    ]
    return {
        "metodologia": "FAIR",
        "riesgos": riesgos_fair
    }

def generar_datos_ejemplo_nist():
    """Genera datos de ejemplo para NIST SP 800-30."""
    riesgos_nist = []
    for i in range(3):
        probabilidad_nist = random.randint(2, 4)
        impacto_nist = random.randint(2, 5)
        nivel_riesgo_str_nist = MATRIZ_RIESGO_5X5[5 - probabilidad_nist][impacto_nist - 1]
        riesgos_nist.append({
            "fuente_amenaza": random.choice(FUENTES_AMENAZA_NIST),
            "evento_amenaza": random.choice(EVENTOS_AMENAZA_NIST),
            "descripcion_amenaza": f"Amenaza de ejemplo #{i+1}",
            "vulnerabilidad": f"Vulnerabilidad de ejemplo #{i+1} (ej. Software desactualizado, configuración incorrecta)",
            "probabilidad_ocurrencia": probabilidad_nist,
            "probabilidad_descripcion": NIVELES_PROBABILIDAD[probabilidad_nist],
            "impacto": impacto_nist,
            "impacto_descripcion": NIVELES_IMPACTO[impacto_nist],
            "nivel_riesgo": nivel_riesgo_str_nist,
            "descripcion_nivel_riesgo": NIVELES_RIESGO.get(nivel_riesgo_str_nist, "N/A"),
            "controles_existentes": "Firewall, Antivirus, Políticas de contraseñas",
            "recomendaciones": "Aplicar parches, mejorar configuraciones, implementar MFA"
        })
    return {
        "metodologia": "NIST SP 800-30",
        "riesgos": riesgos_nist
    }

def generar_informe_riesgos(resultados, archivo_salida, info_organizacion):
    """Genera un informe JSON con los resultados de la evaluación."""
    informe = {
        "info_organizacion": info_organizacion,
        "fecha_generacion": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "metodologia_utilizada": resultados["metodologia"],
        "resultados_evaluacion": resultados
    }
    
    # Añadir resumen de riesgos para OCTAVE y NIST
    if resultados["metodologia"] in ["OCTAVE Allegro", "NIST SP 800-30"]:
        resumen = defaultdict(int)
        for riesgo in resultados["riesgos"]:
            resumen[riesgo["nivel_riesgo"]] += 1
        informe["resumen_niveles_riesgo"] = dict(resumen)
    
    # Añadir resumen de riesgos para FAIR
    if resultados["metodologia"] == "FAIR":
        total_riesgo_anualizado = sum(r["riesgo_anualizado_probable_usd"] for r in resultados["riesgos"])
        informe["resumen_riesgo_fair"] = {
            "numero_escenarios_analizados": len(resultados["riesgos"]),
            "total_riesgo_anualizado_probable_usd": round(total_riesgo_anualizado, 2)
        }

    try:
        with open(archivo_salida, "w", encoding="utf-8") as f:
            json.dump(informe, f, ensure_ascii=False, indent=4)
        print(f"\nInforme de riesgos generado exitosamente: {archivo_salida}")
    except Exception as e:
        print(f"\nError al guardar el informe: {e}")
        sys.exit(1)
    
    return informe

def generar_grafico_distribucion_riesgos(informe, archivo_salida):
    """Genera un gráfico de barras de la distribución de niveles de riesgo (para OCTAVE/NIST)."""
    if "resumen_niveles_riesgo" not in informe:
        print("No hay datos de resumen de niveles de riesgo para graficar.")
        return

    niveles = list(informe["resumen_niveles_riesgo"].keys())
    conteos = list(informe["resumen_niveles_riesgo"].values())
    
    # Ordenar por severidad (aproximado, se puede mejorar)
    orden_severidad = {"Muy Bajo": 0, "Bajo": 1, "Moderado": 2, "Alto": 3, "Muy Alto": 4}
    sorted_data = sorted(zip(niveles, conteos), key=lambda x: orden_severidad.get(x[0], 99))
    niveles_sorted = [d[0] for d in sorted_data]
    conteos_sorted = [d[1] for d in sorted_data]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(niveles_sorted, conteos_sorted, color=["green", "yellowgreen", "gold", "coral", "red"])
    plt.xlabel("Nivel de Riesgo")
    plt.ylabel("Número de Riesgos Identificados")
    plt.title(f"Distribución de Niveles de Riesgo ({informe["metodologia_utilizada"]}) - {informe["info_organizacion"]["organizacion"]}")
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va=\


'center', ha='center')
    
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=300)
    plt.close()
    print(f"Gráfico de distribución de riesgos generado: {archivo_salida}")

def generar_grafico_riesgo_fair(informe, archivo_salida):
    """Genera un gráfico de barras del riesgo anualizado para escenarios FAIR."""
    if informe["metodologia_utilizada"] != "FAIR":
        print("Este gráfico solo es aplicable para la metodología FAIR.")
        return
    
    escenarios = [r["escenario"] for r in informe["resultados_evaluacion"]["riesgos"]]
    riesgos_anualizados = [r["riesgo_anualizado_probable_usd"] for r in informe["resultados_evaluacion"]["riesgos"]]
    
    # Truncar nombres de escenarios largos
    escenarios_truncados = [s[:30] + "..." if len(s) > 30 else s for s in escenarios]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(escenarios_truncados, riesgos_anualizados, color="cornflowerblue")
    plt.xlabel("Escenario de Riesgo")
    plt.ylabel("Riesgo Anualizado Probable (USD)")
    plt.title(f"Riesgo Anualizado por Escenario (FAIR) - {informe["info_organizacion"]["organizacion"]}")
    plt.xticks(rotation=45, ha="right")
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f"${int(yval):,}", va='bottom', ha='center')
    
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=300)
    plt.close()
    print(f"Gráfico de riesgo anualizado FAIR generado: {archivo_salida}")

def solicitar_info_organizacion():
    """Solicita información básica de la organización."""
    print("\n=== INFORMACIÓN DE LA ORGANIZACIÓN ===")
    organizacion = input("Nombre de la organización: ")
    responsable = input("Responsable de la evaluación: ")
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    departamento = input("Departamento o área evaluada: ")
    
    return {
        "organizacion": organizacion,
        "responsable": responsable,
        "fecha": fecha,
        "departamento": departamento
    }

def parse_arguments():
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description='Herramienta de Evaluación de Riesgos de Seguridad de la Información')
    parser.add_argument('--metodologia', choices=['octave', 'fair', 'nist'], required=True, help='Metodología de evaluación de riesgos a utilizar')
    parser.add_argument('--output', default='informe_riesgos.json', help='Archivo de salida para el informe de evaluación')
    parser.add_argument('--interactive', action='store_true', help='Ejecutar en modo interactivo')
    parser.add_argument('--organizacion', default='Mi Organización', help='Nombre de la organización')
    parser.add_argument('--generar-graficos', action='store_true', help='Generar gráficos de resultados')
    return parser.parse_args()

def main():
    """Función principal."""
    args = parse_arguments()
    
    print("\n=== HERRAMIENTA DE EVALUACIÓN DE RIESGOS DE SEGURIDAD DE LA INFORMACIÓN ===")
    
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
            "departamento": "Departamento de TI"
        }
    
    # Realizar evaluación según la metodología seleccionada
    if args.metodologia == 'octave':
        if args.interactive:
            resultados = evaluar_octave_allegro_interactivo()
        else:
            print("\nGenerando datos de ejemplo para OCTAVE Allegro...")
            resultados = generar_datos_ejemplo_octave()
    elif args.metodologia == 'fair':
        if args.interactive:
            resultados = evaluar_fair_interactivo()
        else:
            print("\nGenerando datos de ejemplo para FAIR...")
            resultados = generar_datos_ejemplo_fair()
    elif args.metodologia == 'nist':
        if args.interactive:
            resultados = evaluar_nist_interactivo()
        else:
            print("\nGenerando datos de ejemplo para NIST SP 800-30...")
            resultados = generar_datos_ejemplo_nist()
    
    # Generar informe
    informe = generar_informe_riesgos(resultados, args.output, info_organizacion)
    
    # Generar gráficos si se solicita
    if args.generar_graficos:
        print("\nGenerando gráficos de resultados...")
        graficos_dir = os.path.join(os.path.dirname(args.output), "graficos")
        if not os.path.exists(graficos_dir):
            os.makedirs(graficos_dir)
        
        if args.metodologia in ['octave', 'nist']:
            grafico_distribucion = os.path.join(graficos_dir, f"distribucion_riesgos_{args.metodologia}.png")
            generar_grafico_distribucion_riesgos(informe, grafico_distribucion)
        
        if args.metodologia == 'fair':
            grafico_fair = os.path.join(graficos_dir, "riesgo_anualizado_fair.png")
            generar_grafico_riesgo_fair(informe, grafico_fair)
    
    print("\n=== RESUMEN DE RESULTADOS ===")
    if args.metodologia in ['octave', 'nist']:
        if "resumen_niveles_riesgo" in informe:
            print("Distribución de niveles de riesgo:")
            for nivel, conteo in informe["resumen_niveles_riesgo"].items():
                print(f"- {nivel}: {conteo} riesgos")
    
    if args.metodologia == 'fair':
        if "resumen_riesgo_fair" in informe:
            print(f"Número de escenarios analizados: {informe["resumen_riesgo_fair"]["numero_escenarios_analizados"]}")
            print(f"Riesgo anualizado total (probable): ${informe["resumen_riesgo_fair"]["total_riesgo_anualizado_probable_usd"]:,.2f}")
    
    print(f"\nPara más detalles, consulte el informe completo: {args.output}")

if __name__ == "__main__":
    main()

