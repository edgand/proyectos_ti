#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Herramienta de Evaluación de Madurez de TI basada en COBIT

Este script permite realizar una evaluación de madurez de los procesos de TI
según el marco de referencia COBIT, generando un informe con los resultados
y recomendaciones.

Uso:
    python evaluacion_madurez.py [--output informe_madurez.json] [--interactive]
"""

import argparse
import json
import os
import sys
import datetime
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict

# Definición de los procesos COBIT por dominio
PROCESOS_COBIT = {
    "EDM": {
        "EDM01": "Asegurar el Establecimiento y Mantenimiento del Marco de Gobernanza",
        "EDM02": "Asegurar la Entrega de Beneficios",
        "EDM03": "Asegurar la Optimización del Riesgo",
        "EDM04": "Asegurar la Optimización de Recursos",
        "EDM05": "Asegurar la Transparencia hacia las Partes Interesadas"
    },
    "APO": {
        "APO01": "Gestionar el Marco de Gestión de TI",
        "APO02": "Gestionar la Estrategia",
        "APO03": "Gestionar la Arquitectura Empresarial",
        "APO04": "Gestionar la Innovación",
        "APO05": "Gestionar el Portafolio",
        "APO06": "Gestionar el Presupuesto y los Costos",
        "APO07": "Gestionar los Recursos Humanos",
        "APO08": "Gestionar las Relaciones",
        "APO09": "Gestionar los Acuerdos de Servicio",
        "APO10": "Gestionar los Proveedores",
        "APO11": "Gestionar la Calidad",
        "APO12": "Gestionar el Riesgo",
        "APO13": "Gestionar la Seguridad"
    },
    "BAI": {
        "BAI01": "Gestionar Programas y Proyectos",
        "BAI02": "Gestionar la Definición de Requisitos",
        "BAI03": "Gestionar la Identificación y Construcción de Soluciones",
        "BAI04": "Gestionar la Disponibilidad y la Capacidad",
        "BAI05": "Gestionar la Facilitación del Cambio Organizativo",
        "BAI06": "Gestionar los Cambios",
        "BAI07": "Gestionar la Aceptación del Cambio y la Transición",
        "BAI08": "Gestionar el Conocimiento",
        "BAI09": "Gestionar los Activos",
        "BAI10": "Gestionar la Configuración"
    },
    "DSS": {
        "DSS01": "Gestionar Operaciones",
        "DSS02": "Gestionar Peticiones e Incidentes de Servicio",
        "DSS03": "Gestionar Problemas",
        "DSS04": "Gestionar la Continuidad",
        "DSS05": "Gestionar Servicios de Seguridad",
        "DSS06": "Gestionar Controles de Procesos de Negocio"
    },
    "MEA": {
        "MEA01": "Monitorear, Evaluar y Valorar el Rendimiento y la Conformidad",
        "MEA02": "Monitorear, Evaluar y Valorar el Sistema de Control Interno",
        "MEA03": "Monitorear, Evaluar y Valorar la Conformidad con los Requerimientos Externos"
    }
}

# Descripción de los niveles de madurez
NIVELES_MADUREZ = {
    0: "Inexistente - El proceso no está implementado o no logra su propósito",
    1: "Inicial - El proceso se ejecuta de manera ad hoc",
    2: "Repetible - El proceso sigue un patrón regular",
    3: "Definido - El proceso está documentado y comunicado",
    4: "Gestionado - El proceso es monitoreado y medido",
    5: "Optimizado - El proceso se mejora continuamente"
}

def parse_arguments():
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description='Herramienta de Evaluación de Madurez de TI basada en COBIT')
    parser.add_argument('--output', default='informe_madurez.json', help='Archivo de salida para el informe de madurez')
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
    periodo = input("Periodo evaluado (ej. 2025): ")
    
    return {
        "organizacion": organizacion,
        "responsable": responsable,
        "fecha": fecha,
        "periodo": periodo
    }

def evaluar_proceso_interactivo(dominio, proceso, descripcion):
    """Solicita la evaluación de un proceso específico en modo interactivo."""
    print(f"\n=== EVALUACIÓN DE PROCESO: {proceso} - {descripcion} ===")
    print("Niveles de madurez:")
    for nivel, desc in NIVELES_MADUREZ.items():
        print(f"{nivel}: {desc}")
    
    while True:
        try:
            nivel_actual = int(input(f"\nNivel actual de madurez para {proceso} (0-5): "))
            if 0 <= nivel_actual <= 5:
                break
            print("Error: El nivel debe estar entre 0 y 5.")
        except ValueError:
            print("Error: Ingrese un número entero.")
    
    while True:
        try:
            nivel_objetivo = int(input(f"Nivel objetivo de madurez para {proceso} (0-5): "))
            if 0 <= nivel_objetivo <= 5:
                break
            print("Error: El nivel debe estar entre 0 y 5.")
        except ValueError:
            print("Error: Ingrese un número entero.")
    
    evidencias = input("Evidencias que respaldan el nivel asignado: ")
    observaciones = input("Observaciones sobre el estado actual: ")
    acciones = input("Acciones recomendadas para cerrar la brecha: ")
    
    return {
        "nivel_actual": nivel_actual,
        "nivel_objetivo": nivel_objetivo,
        "evidencias": evidencias,
        "observaciones": observaciones,
        "acciones": acciones
    }

def evaluar_procesos_interactivo():
    """Realiza la evaluación de todos los procesos en modo interactivo."""
    resultados = {}
    
    for dominio, procesos in PROCESOS_COBIT.items():
        print(f"\n=== DOMINIO: {dominio} ===")
        resultados[dominio] = {}
        
        for codigo, descripcion in procesos.items():
            resultados[dominio][codigo] = evaluar_proceso_interactivo(dominio, codigo, descripcion)
    
    return resultados

def generar_datos_ejemplo():
    """Genera datos de ejemplo para la evaluación."""
    resultados = {}
    
    for dominio, procesos in PROCESOS_COBIT.items():
        resultados[dominio] = {}
        
        for codigo, descripcion in procesos.items():
            # Generar niveles aleatorios pero realistas
            nivel_actual = np.random.choice([1, 2, 3], p=[0.3, 0.5, 0.2])
            nivel_objetivo = min(5, nivel_actual + np.random.choice([1, 2], p=[0.7, 0.3]))
            
            resultados[dominio][codigo] = {
                "nivel_actual": int(nivel_actual),
                "nivel_objetivo": int(nivel_objetivo),
                "evidencias": "Evidencias de ejemplo para " + codigo,
                "observaciones": "Observaciones de ejemplo para " + codigo,
                "acciones": "Acciones recomendadas de ejemplo para " + codigo
            }
    
    return resultados

def calcular_promedios(resultados):
    """Calcula los promedios de madurez por dominio y general."""
    promedios = {"dominios": {}, "general": {}}
    
    # Calcular promedios por dominio
    for dominio, procesos in resultados.items():
        niveles_actuales = [p["nivel_actual"] for p in procesos.values()]
        niveles_objetivo = [p["nivel_objetivo"] for p in procesos.values()]
        
        promedio_actual = sum(niveles_actuales) / len(niveles_actuales)
        promedio_objetivo = sum(niveles_objetivo) / len(niveles_objetivo)
        brecha = promedio_objetivo - promedio_actual
        
        promedios["dominios"][dominio] = {
            "actual": round(promedio_actual, 2),
            "objetivo": round(promedio_objetivo, 2),
            "brecha": round(brecha, 2)
        }
    
    # Calcular promedio general
    todos_actuales = []
    todos_objetivo = []
    
    for dominio, procesos in resultados.items():
        todos_actuales.extend([p["nivel_actual"] for p in procesos.values()])
        todos_objetivo.extend([p["nivel_objetivo"] for p in procesos.values()])
    
    promedio_general_actual = sum(todos_actuales) / len(todos_actuales)
    promedio_general_objetivo = sum(todos_objetivo) / len(todos_objetivo)
    brecha_general = promedio_general_objetivo - promedio_general_actual
    
    promedios["general"] = {
        "actual": round(promedio_general_actual, 2),
        "objetivo": round(promedio_general_objetivo, 2),
        "brecha": round(brecha_general, 2)
    }
    
    return promedios

def identificar_procesos_criticos(resultados, top_n=5):
    """Identifica los procesos con mayor brecha entre nivel actual y objetivo."""
    procesos_con_brecha = []
    
    for dominio, procesos in resultados.items():
        for codigo, datos in procesos.items():
            brecha = datos["nivel_objetivo"] - datos["nivel_actual"]
            if brecha > 0:
                procesos_con_brecha.append({
                    "dominio": dominio,
                    "codigo": codigo,
                    "descripcion": PROCESOS_COBIT[dominio][codigo],
                    "nivel_actual": datos["nivel_actual"],
                    "nivel_objetivo": datos["nivel_objetivo"],
                    "brecha": brecha
                })
    
    # Ordenar por brecha (mayor a menor)
    procesos_con_brecha.sort(key=lambda x: x["brecha"], reverse=True)
    
    return procesos_con_brecha[:top_n]

def generar_recomendaciones(procesos_criticos):
    """Genera recomendaciones basadas en los procesos críticos identificados."""
    recomendaciones = []
    
    for proceso in procesos_criticos:
        dominio = proceso["dominio"]
        codigo = proceso["codigo"]
        descripcion = proceso["descripcion"]
        nivel_actual = proceso["nivel_actual"]
        nivel_objetivo = proceso["nivel_objetivo"]
        
        # Generar recomendación basada en el dominio y nivel actual
        if dominio == "EDM":
            recomendacion = f"Fortalecer la gobernanza de TI en el área de {descripcion} mediante la implementación de un marco formal de toma de decisiones y responsabilidades."
        elif dominio == "APO":
            recomendacion = f"Mejorar los procesos de planificación y organización relacionados con {descripcion} a través de la definición de políticas y procedimientos claros."
        elif dominio == "BAI":
            recomendacion = f"Optimizar los procesos de implementación de soluciones en {descripcion} mediante la adopción de metodologías estructuradas y mejores prácticas."
        elif dominio == "DSS":
            recomendacion = f"Reforzar la entrega y soporte de servicios en {descripcion} a través de la implementación de procesos operativos estandarizados y medibles."
        elif dominio == "MEA":
            recomendacion = f"Mejorar los mecanismos de monitoreo y evaluación de {descripcion} mediante la implementación de métricas claras y procesos de revisión periódicos."
        
        recomendaciones.append({
            "proceso": f"{codigo} - {descripcion}",
            "nivel_actual": nivel_actual,
            "nivel_objetivo": nivel_objetivo,
            "recomendacion": recomendacion
        })
    
    return recomendaciones

def generar_plan_accion(procesos_criticos):
    """Genera un plan de acción basado en los procesos críticos identificados."""
    plan_accion = []
    
    for i, proceso in enumerate(procesos_criticos):
        dominio = proceso["dominio"]
        codigo = proceso["codigo"]
        descripcion = proceso["descripcion"]
        
        # Generar acción basada en el dominio
        if dominio == "EDM":
            accion = f"Implementar un marco formal de gobernanza para {descripcion}"
            responsable = "Director de TI"
        elif dominio == "APO":
            accion = f"Desarrollar políticas y procedimientos para {descripcion}"
            responsable = "Gerente de Planificación de TI"
        elif dominio == "BAI":
            accion = f"Implementar metodología estructurada para {descripcion}"
            responsable = "Gerente de Proyectos"
        elif dominio == "DSS":
            accion = f"Estandarizar procesos operativos para {descripcion}"
            responsable = "Gerente de Operaciones de TI"
        elif dominio == "MEA":
            accion = f"Implementar métricas y procesos de revisión para {descripcion}"
            responsable = "Gerente de Calidad de TI"
        
        # Calcular fecha objetivo (ejemplo: 3 meses por cada acción, escalonadas)
        fecha_inicio = datetime.datetime.now()
        meses_adicionales = (i + 1) * 3
        fecha_objetivo = (fecha_inicio + datetime.timedelta(days=30 * meses_adicionales)).strftime("%Y-%m-%d")
        
        plan_accion.append({
            "accion": accion,
            "proceso": f"{codigo} - {descripcion}",
            "responsable": responsable,
            "fecha_objetivo": fecha_objetivo,
            "recursos": "Por determinar",
            "metricas_exito": f"Alcanzar nivel de madurez {proceso['nivel_objetivo']} en {codigo}"
        })
    
    return plan_accion

def generar_graficos(resultados, promedios, nombre_organizacion, directorio_salida="graficos"):
    """Genera gráficos visuales de los resultados de la evaluación."""
    # Crear directorio si no existe
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)
    
    # 1. Gráfico de radar por dominio
    generar_grafico_radar(promedios, os.path.join(directorio_salida, "radar_dominios.png"), nombre_organizacion)
    
    # 2. Gráfico de barras de brechas por dominio
    generar_grafico_brechas(promedios, os.path.join(directorio_salida, "brechas_dominios.png"), nombre_organizacion)
    
    # 3. Mapa de calor de procesos
    generar_mapa_calor(resultados, os.path.join(directorio_salida, "mapa_calor_procesos.png"), nombre_organizacion)
    
    return [
        os.path.join(directorio_salida, "radar_dominios.png"),
        os.path.join(directorio_salida, "brechas_dominios.png"),
        os.path.join(directorio_salida, "mapa_calor_procesos.png")
    ]

def generar_grafico_radar(promedios, archivo_salida, nombre_organizacion):
    """Genera un gráfico de radar de los niveles de madurez por dominio."""
    dominios = list(promedios["dominios"].keys())
    niveles_actuales = [promedios["dominios"][d]["actual"] for d in dominios]
    niveles_objetivo = [promedios["dominios"][d]["objetivo"] for d in dominios]
    
    # Convertir a formato radar (cerrar el polígono)
    dominios = dominios + [dominios[0]]
    niveles_actuales = niveles_actuales + [niveles_actuales[0]]
    niveles_objetivo = niveles_objetivo + [niveles_objetivo[0]]
    
    # Crear figura
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, polar=True)
    
    # Configurar ejes
    angles = np.linspace(0, 2*np.pi, len(dominios), endpoint=False).tolist()
    angles += angles[:1]  # Cerrar el polígono
    
    # Dibujar niveles
    ax.plot(angles, niveles_actuales, 'o-', linewidth=2, label='Nivel Actual')
    ax.fill(angles, niveles_actuales, alpha=0.25)
    ax.plot(angles, niveles_objetivo, 'o-', linewidth=2, label='Nivel Objetivo')
    ax.fill(angles, niveles_objetivo, alpha=0.25)
    
    # Configurar etiquetas y título
    ax.set_thetagrids(np.degrees(angles[:-1]), dominios[:-1])
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'])
    ax.set_title(f'Niveles de Madurez por Dominio - {nombre_organizacion}', size=15, y=1.1)
    ax.grid(True)
    
    # Leyenda
    ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
    # Guardar figura
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=300, bbox_inches='tight')
    plt.close()

def generar_grafico_brechas(promedios, archivo_salida, nombre_organizacion):
    """Genera un gráfico de barras de las brechas por dominio."""
    dominios = list(promedios["dominios"].keys())
    brechas = [promedios["dominios"][d]["brecha"] for d in dominios]
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Dibujar barras
    bars = ax.bar(dominios, brechas, color='skyblue')
    
    # Añadir valores sobre las barras
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 puntos de desplazamiento vertical
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    # Configurar etiquetas y título
    ax.set_xlabel('Dominios')
    ax.set_ylabel('Brecha (Objetivo - Actual)')
    ax.set_title(f'Brechas de Madurez por Dominio - {nombre_organizacion}')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Añadir línea de brecha promedio
    brecha_promedio = promedios["general"]["brecha"]
    ax.axhline(y=brecha_promedio, color='r', linestyle='-', label=f'Brecha Promedio: {brecha_promedio:.2f}')
    ax.legend()
    
    # Guardar figura
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=300)
    plt.close()

def generar_mapa_calor(resultados, archivo_salida, nombre_organizacion):
    """Genera un mapa de calor de los niveles de madurez de todos los procesos."""
    # Preparar datos para el mapa de calor
    dominios = list(PROCESOS_COBIT.keys())
    max_procesos = max(len(PROCESOS_COBIT[d]) for d in dominios)
    
    # Crear matriz para el mapa de calor
    matriz_niveles = np.zeros((len(dominios), max_procesos))
    matriz_niveles.fill(np.nan)  # Llenar con NaN para celdas vacías
    
    # Etiquetas para los ejes
    etiquetas_y = dominios
    etiquetas_x = []
    
    # Llenar la matriz con los niveles actuales
    for i, dominio in enumerate(dominios):
        procesos = list(PROCESOS_COBIT[dominio].keys())
        if len(etiquetas_x) < len(procesos):
            etiquetas_x = procesos
        
        for j, codigo in enumerate(procesos):
            if codigo in resultados[dominio]:
                matriz_niveles[i, j] = resultados[dominio][codigo]["nivel_actual"]
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Crear mapa de calor
    cmap = plt.cm.RdYlGn  # Red-Yellow-Green colormap
    im = ax.imshow(matriz_niveles, cmap=cmap, vmin=0, vmax=5)
    
    # Configurar ejes
    ax.set_xticks(np.arange(len(etiquetas_x)))
    ax.set_yticks(np.arange(len(etiquetas_y)))
    ax.set_xticklabels(etiquetas_x)
    ax.set_yticklabels(etiquetas_y)
    
    # Rotar etiquetas del eje x
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Añadir valores en las celdas
    for i in range(len(dominios)):
        for j in range(max_procesos):
            if not np.isnan(matriz_niveles[i, j]):
                text = ax.text(j, i, int(matriz_niveles[i, j]),
                               ha="center", va="center", color="black")
    
    # Añadir barra de color
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Nivel de Madurez", rotation=-90, va="bottom")
    
    # Título
    ax.set_title(f"Mapa de Calor de Niveles de Madurez - {nombre_organizacion}")
    
    # Guardar figura
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=300)
    plt.close()

def generar_informe(info_organizacion, resultados, archivo_salida):
    """Genera un informe completo con los resultados de la evaluación."""
    # Calcular promedios
    promedios = calcular_promedios(resultados)
    
    # Identificar procesos críticos
    procesos_criticos = identificar_procesos_criticos(resultados)
    
    # Generar recomendaciones
    recomendaciones = generar_recomendaciones(procesos_criticos)
    
    # Generar plan de acción
    plan_accion = generar_plan_accion(procesos_criticos)
    
    # Estructura del informe
    informe = {
        "info_organizacion": info_organizacion,
        "fecha_generacion": datetime.datetime.now().strftime("%Y-%m-%d"),
        "resultados_detallados": resultados,
        "promedios": promedios,
        "procesos_criticos": procesos_criticos,
        "recomendaciones": recomendaciones,
        "plan_accion": plan_accion
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
    
    print("\n=== HERRAMIENTA DE EVALUACIÓN DE MADUREZ DE TI BASADA EN COBIT ===")
    
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
            "periodo": "2025"
        }
    
    # Realizar evaluación
    if args.interactive:
        print("\nIniciando evaluación interactiva de procesos COBIT...")
        resultados = evaluar_procesos_interactivo()
    else:
        print("\nGenerando datos de ejemplo para la evaluación...")
        resultados = generar_datos_ejemplo()
    
    # Generar informe
    informe = generar_informe(info_organizacion, resultados, args.output)
    
    # Generar gráficos si se solicita
    if args.generar_graficos:
        print("\nGenerando gráficos de resultados...")
        graficos = generar_graficos(resultados, informe["promedios"], info_organizacion["organizacion"])
        print(f"Gráficos generados: {', '.join(graficos)}")
    
    print("\n=== RESUMEN DE RESULTADOS ===")
    print(f"Nivel de madurez promedio actual: {informe['promedios']['general']['actual']}")
    print(f"Nivel de madurez promedio objetivo: {informe['promedios']['general']['objetivo']}")
    print(f"Brecha promedio: {informe['promedios']['general']['brecha']}")
    
    print("\nProcesos críticos identificados:")
    for i, proceso in enumerate(informe['procesos_criticos']):
        print(f"{i+1}. {proceso['codigo']} - {proceso['descripcion']} (Brecha: {proceso['brecha']})")
    
    print(f"\nPara más detalles, consulte el informe completo: {args.output}")

if __name__ == "__main__":
    main()

