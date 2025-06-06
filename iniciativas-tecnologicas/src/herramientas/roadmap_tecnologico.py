#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Herramienta de Generación de Roadmap Tecnológico

Esta herramienta permite generar un roadmap tecnológico visual a partir de un archivo CSV
que contiene iniciativas tecnológicas. El roadmap puede personalizarse en términos de
horizonte temporal, capas, y formato de visualización.

Uso:
    python roadmap_tecnologico.py --input iniciativas.csv --output roadmap.html
                                  [--organizacion "Mi Empresa"] [--horizonte 3]
                                  [--formato html|png|pdf] [--tema claro|oscuro]
"""

import argparse
import csv
import os
import sys
import datetime
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import webbrowser
from pathlib import Path

# --- Configuración por defecto ---
CONFIG_DEFAULT = {
    "capas": [
        {"id": "mercado", "nombre": "Mercado y Negocio", "color": "#4285F4"},
        {"id": "producto", "nombre": "Producto y Servicio", "color": "#EA4335"},
        {"id": "tecnologia", "nombre": "Tecnología", "color": "#FBBC05"},
        {"id": "capacidades", "nombre": "Capacidades y Recursos", "color": "#34A853"}
    ],
    "estados": {
        "planificado": {"nombre": "Planificado", "color": "#A8A8A8"},
        "en_progreso": {"nombre": "En Progreso", "color": "#FBBC05"},
        "completado": {"nombre": "Completado", "color": "#34A853"},
        "retrasado": {"nombre": "Retrasado", "color": "#EA4335"},
        "cancelado": {"nombre": "Cancelado", "color": "#000000"}
    },
    "periodos": ["Q1", "Q2", "Q3", "Q4"],
    "horizonte_default": 3,  # años
    "formato_default": "html",
    "tema_default": "claro"
}

# --- Funciones de utilidad ---

def cargar_iniciativas(archivo_csv):
    """Carga las iniciativas desde un archivo CSV."""
    try:
        iniciativas = []
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                iniciativas.append(row)
        return iniciativas
    except Exception as e:
        print(f"Error al cargar el archivo CSV: {e}")
        sys.exit(1)

def validar_iniciativas(iniciativas, config):
    """Valida que las iniciativas tengan los campos requeridos y formatos correctos."""
    campos_requeridos = ["id", "nombre", "descripcion", "capa", "fecha_inicio", "fecha_fin", "estado"]
    capas_validas = [capa["id"] for capa in config["capas"]]
    estados_validos = list(config["estados"].keys())
    
    iniciativas_validas = []
    errores = []
    
    for i, iniciativa in enumerate(iniciativas):
        error_iniciativa = False
        
        # Verificar campos requeridos
        for campo in campos_requeridos:
            if campo not in iniciativa or not iniciativa[campo]:
                errores.append(f"Iniciativa #{i+1}: Falta el campo requerido '{campo}'")
                error_iniciativa = True
        
        if error_iniciativa:
            continue
        
        # Verificar valores válidos
        if iniciativa["capa"] not in capas_validas:
            errores.append(f"Iniciativa '{iniciativa['nombre']}': Capa '{iniciativa['capa']}' no válida. Debe ser una de: {', '.join(capas_validas)}")
            error_iniciativa = True
        
        if iniciativa["estado"] not in estados_validos:
            errores.append(f"Iniciativa '{iniciativa['nombre']}': Estado '{iniciativa['estado']}' no válido. Debe ser uno de: {', '.join(estados_validos)}")
            error_iniciativa = True
        
        # Verificar fechas
        try:
            fecha_inicio = datetime.datetime.strptime(iniciativa["fecha_inicio"], "%Y-%m-%d")
            fecha_fin = datetime.datetime.strptime(iniciativa["fecha_fin"], "%Y-%m-%d")
            
            if fecha_fin < fecha_inicio:
                errores.append(f"Iniciativa '{iniciativa['nombre']}': La fecha de fin es anterior a la fecha de inicio")
                error_iniciativa = True
                
            # Convertir fechas a formato datetime
            iniciativa["fecha_inicio_dt"] = fecha_inicio
            iniciativa["fecha_fin_dt"] = fecha_fin
            
        except ValueError:
            errores.append(f"Iniciativa '{iniciativa['nombre']}': Formato de fecha incorrecto. Use YYYY-MM-DD")
            error_iniciativa = True
        
        if not error_iniciativa:
            iniciativas_validas.append(iniciativa)
    
    if errores:
        print("Se encontraron errores en el archivo de iniciativas:")
        for error in errores:
            print(f"- {error}")
        
        if not iniciativas_validas:
            print("No hay iniciativas válidas para procesar. Corrige los errores y vuelve a intentarlo.")
            sys.exit(1)
        else:
            print(f"Se procesarán {len(iniciativas_validas)} iniciativas válidas de {len(iniciativas)} totales.")
    
    return iniciativas_validas

def generar_roadmap_plotly(iniciativas, config, organizacion, horizonte, tema):
    """Genera un roadmap interactivo utilizando Plotly."""
    # Determinar el rango de fechas
    fecha_actual = datetime.datetime.now()
    fecha_inicio_roadmap = fecha_actual - datetime.timedelta(days=90)  # 3 meses atrás
    fecha_fin_roadmap = fecha_actual + datetime.timedelta(days=365 * horizonte)  # N años adelante
    
    # Preparar datos para el gráfico
    df_iniciativas = []
    
    for iniciativa in iniciativas:
        # Solo incluir iniciativas que caen dentro del horizonte
        if iniciativa["fecha_inicio_dt"] <= fecha_fin_roadmap and iniciativa["fecha_fin_dt"] >= fecha_inicio_roadmap:
            capa_info = next((c for c in config["capas"] if c["id"] == iniciativa["capa"]), None)
            estado_info = config["estados"].get(iniciativa["estado"], {"nombre": iniciativa["estado"], "color": "#CCCCCC"})
            
            df_iniciativas.append({
                "ID": iniciativa["id"],
                "Iniciativa": iniciativa["nombre"],
                "Descripción": iniciativa["descripcion"],
                "Capa": capa_info["nombre"] if capa_info else iniciativa["capa"],
                "Capa_ID": iniciativa["capa"],
                "Fecha_Inicio": iniciativa["fecha_inicio_dt"],
                "Fecha_Fin": iniciativa["fecha_fin_dt"],
                "Estado": estado_info["nombre"],
                "Color": estado_info["color"],
                "Responsable": iniciativa.get("responsable", "No asignado"),
                "Prioridad": iniciativa.get("prioridad", "Media")
            })
    
    if not df_iniciativas:
        print("No hay iniciativas dentro del horizonte temporal especificado.")
        sys.exit(1)
    
    df = pd.DataFrame(df_iniciativas)
    
    # Ordenar capas según el orden en la configuración
    capa_orden = {capa["id"]: i for i, capa in enumerate(config["capas"])}
    df["Capa_Orden"] = df["Capa_ID"].map(capa_orden)
    df = df.sort_values(["Capa_Orden", "Fecha_Inicio"])
    
    # Crear figura
    fig = go.Figure()
    
    # Colores para el tema
    if tema == "oscuro":
        bg_color = "#1E1E1E"
        text_color = "#FFFFFF"
        grid_color = "#333333"
    else:  # claro
        bg_color = "#FFFFFF"
        text_color = "#333333"
        grid_color = "#EEEEEE"
    
    # Añadir barras para cada iniciativa
    for i, row in df.iterrows():
        fig.add_trace(go.Bar(
            x=[row["Fecha_Fin"] - row["Fecha_Inicio"]],
            y=[row["Iniciativa"]],
            orientation='h',
            base=[row["Fecha_Inicio"]],
            marker_color=row["Color"],
            customdata=[[
                row["ID"],
                row["Descripción"],
                row["Estado"],
                row["Responsable"],
                row["Prioridad"]
            ]],
            hovertemplate="<b>%{y}</b><br>" +
                          "ID: %{customdata[0]}<br>" +
                          "Descripción: %{customdata[1]}<br>" +
                          "Estado: %{customdata[2]}<br>" +
                          "Responsable: %{customdata[3]}<br>" +
                          "Prioridad: %{customdata[4]}<br>" +
                          "Inicio: %{base|%d %b %Y}<br>" +
                          "Fin: %{x|%d %b %Y}<extra></extra>",
            name=row["Iniciativa"]
        ))
    
    # Añadir línea vertical para la fecha actual
    fig.add_vline(x=fecha_actual, line_width=2, line_dash="dash", line_color="red")
    
    # Configurar el diseño
    fig.update_layout(
        title={
            'text': f"Roadmap Tecnológico - {organizacion}",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24, 'color': text_color}
        },
        xaxis=dict(
            title="Fecha",
            type="date",
            tickformat="%b %Y",
            range=[fecha_inicio_roadmap, fecha_fin_roadmap],
            gridcolor=grid_color,
            linecolor=grid_color,
            tickfont={'color': text_color},
            titlefont={'color': text_color}
        ),
        yaxis=dict(
            title="Iniciativas",
            categoryorder='array',
            categoryarray=df["Iniciativa"].tolist(),
            gridcolor=grid_color,
            linecolor=grid_color,
            tickfont={'color': text_color},
            titlefont={'color': text_color}
        ),
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font={'color': text_color},
        height=max(600, len(df) * 30),  # Altura dinámica basada en el número de iniciativas
        margin=dict(l=150, r=50, t=100, b=100),
        showlegend=False,
        annotations=[
            dict(
                x=fecha_actual,
                y=1.05,
                xref="x",
                yref="paper",
                text="Hoy",
                showarrow=False,
                font=dict(color="red", size=12),
                bgcolor="rgba(255, 255, 255, 0.7)"
            )
        ]
    )
    
    # Añadir anotaciones para las capas
    capas_unicas = df.sort_values("Capa_Orden")["Capa"].unique()
    capa_actual = ""
    capa_inicio_idx = 0
    
    for i, iniciativa in enumerate(df.sort_values("Capa_Orden")["Iniciativa"]):
        capa = df[df["Iniciativa"] == iniciativa]["Capa"].values[0]
        
        if capa != capa_actual:
            # Añadir anotación para la capa anterior si no es la primera
            if capa_actual:
                fig.add_shape(
                    type="rect",
                    xref="paper", yref="y",
                    x0=0, x1=1,
                    y0=capa_inicio_idx - 0.5, y1=i - 0.5,
                    fillcolor=next((c["color"] for c in config["capas"] if c["nombre"] == capa_actual), "#CCCCCC") + "20",
                    line=dict(width=0),
                    layer="below"
                )
                
                fig.add_annotation(
                    x=-0.15,
                    y=(capa_inicio_idx + i - 1) / 2,
                    xref="paper",
                    yref="y",
                    text=capa_actual,
                    showarrow=False,
                    font=dict(size=14, color=text_color),
                    align="center",
                    textangle=-90
                )
            
            capa_actual = capa
            capa_inicio_idx = i
    
    # Añadir la última capa
    if capa_actual:
        fig.add_shape(
            type="rect",
            xref="paper", yref="y",
            x0=0, x1=1,
            y0=capa_inicio_idx - 0.5, y1=len(df) - 0.5,
            fillcolor=next((c["color"] for c in config["capas"] if c["nombre"] == capa_actual), "#CCCCCC") + "20",
            line=dict(width=0),
            layer="below"
        )
        
        fig.add_annotation(
            x=-0.15,
            y=(capa_inicio_idx + len(df) - 1) / 2,
            xref="paper",
            yref="y",
            text=capa_actual,
            showarrow=False,
            font=dict(size=14, color=text_color),
            align="center",
            textangle=-90
        )
    
    # Añadir leyenda de estados
    estados_unicos = list(config["estados"].values())
    for i, estado in enumerate(estados_unicos):
        fig.add_trace(go.Scatter(
            x=[fecha_inicio_roadmap],
            y=[0],
            mode="markers",
            marker=dict(size=10, color=estado["color"]),
            name=estado["nombre"],
            showlegend=True
        ))
    
    return fig

def generar_roadmap_matplotlib(iniciativas, config, organizacion, horizonte, tema):
    """Genera un roadmap utilizando Matplotlib (para exportación a PNG/PDF)."""
    # Determinar el rango de fechas
    fecha_actual = datetime.datetime.now()
    fecha_inicio_roadmap = fecha_actual - datetime.timedelta(days=90)  # 3 meses atrás
    fecha_fin_roadmap = fecha_actual + datetime.timedelta(days=365 * horizonte)  # N años adelante
    
    # Preparar datos para el gráfico
    df_iniciativas = []
    
    for iniciativa in iniciativas:
        # Solo incluir iniciativas que caen dentro del horizonte
        if iniciativa["fecha_inicio_dt"] <= fecha_fin_roadmap and iniciativa["fecha_fin_dt"] >= fecha_inicio_roadmap:
            capa_info = next((c for c in config["capas"] if c["id"] == iniciativa["capa"]), None)
            estado_info = config["estados"].get(iniciativa["estado"], {"nombre": iniciativa["estado"], "color": "#CCCCCC"})
            
            df_iniciativas.append({
                "ID": iniciativa["id"],
                "Iniciativa": iniciativa["nombre"],
                "Descripción": iniciativa["descripcion"],
                "Capa": capa_info["nombre"] if capa_info else iniciativa["capa"],
                "Capa_ID": iniciativa["capa"],
                "Fecha_Inicio": iniciativa["fecha_inicio_dt"],
                "Fecha_Fin": iniciativa["fecha_fin_dt"],
                "Estado": estado_info["nombre"],
                "Color": estado_info["color"],
                "Responsable": iniciativa.get("responsable", "No asignado"),
                "Prioridad": iniciativa.get("prioridad", "Media")
            })
    
    if not df_iniciativas:
        print("No hay iniciativas dentro del horizonte temporal especificado.")
        sys.exit(1)
    
    df = pd.DataFrame(df_iniciativas)
    
    # Ordenar capas según el orden en la configuración
    capa_orden = {capa["id"]: i for i, capa in enumerate(config["capas"])}
    df["Capa_Orden"] = df["Capa_ID"].map(capa_orden)
    df = df.sort_values(["Capa_Orden", "Fecha_Inicio"])
    
    # Configurar el tema
    if tema == "oscuro":
        plt.style.use('dark_background')
        text_color = 'white'
        grid_color = '#333333'
    else:  # claro
        plt.style.use('default')
        text_color = 'black'
        grid_color = '#EEEEEE'
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(12, max(8, len(df) * 0.4)))
    
    # Configurar eje X (fechas)
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.xticks(rotation=45)
    
    # Configurar eje Y (iniciativas)
    iniciativas_list = df["Iniciativa"].tolist()
    ax.set_yticks(range(len(iniciativas_list)))
    ax.set_yticklabels(iniciativas_list)
    
    # Añadir barras para cada iniciativa
    for i, row in df.iterrows():
        start_date = mdates.date2num(row["Fecha_Inicio"])
        end_date = mdates.date2num(row["Fecha_Fin"])
        duration = end_date - start_date
        
        ax.barh(iniciativas_list.index(row["Iniciativa"]), duration, left=start_date, 
                height=0.6, color=row["Color"], alpha=0.8)
    
    # Añadir línea vertical para la fecha actual
    ax.axvline(x=fecha_actual, color='red', linestyle='--', linewidth=1)
    ax.text(fecha_actual, len(iniciativas_list) + 0.5, 'Hoy', 
            color='red', ha='center', va='bottom', fontsize=10)
    
    # Añadir sombreado para las capas
    capas_unicas = df.sort_values("Capa_Orden")["Capa"].unique()
    capa_actual = ""
    capa_inicio_idx = 0
    
    for i, iniciativa in enumerate(df.sort_values("Capa_Orden")["Iniciativa"]):
        capa = df[df["Iniciativa"] == iniciativa]["Capa"].values[0]
        
        if capa != capa_actual:
            # Añadir sombreado para la capa anterior si no es la primera
            if capa_actual:
                capa_color = next((c["color"] for c in config["capas"] if c["nombre"] == capa_actual), "#CCCCCC")
                ax.axhspan(capa_inicio_idx - 0.5, i - 0.5, color=capa_color, alpha=0.1)
                
                # Añadir etiqueta de capa
                ax.text(-0.1, (capa_inicio_idx + i - 1) / 2, capa_actual, 
                        transform=ax.get_yaxis_transform(), ha='right', va='center', 
                        fontsize=12, fontweight='bold', rotation=90, color=text_color)
            
            capa_actual = capa
            capa_inicio_idx = i
    
    # Añadir la última capa
    if capa_actual:
        capa_color = next((c["color"] for c in config["capas"] if c["nombre"] == capa_actual), "#CCCCCC")
        ax.axhspan(capa_inicio_idx - 0.5, len(df) - 0.5, color=capa_color, alpha=0.1)
        
        # Añadir etiqueta de capa
        ax.text(-0.1, (capa_inicio_idx + len(df) - 1) / 2, capa_actual, 
                transform=ax.get_yaxis_transform(), ha='right', va='center', 
                fontsize=12, fontweight='bold', rotation=90, color=text_color)
    
    # Configurar límites y etiquetas
    ax.set_xlim([fecha_inicio_roadmap, fecha_fin_roadmap])
    ax.set_title(f"Roadmap Tecnológico - {organizacion}", fontsize=16, color=text_color)
    ax.set_xlabel("Fecha", fontsize=12, color=text_color)
    ax.set_ylabel("Iniciativas", fontsize=12, color=text_color)
    
    # Añadir leyenda de estados
    estados_unicos = list(config["estados"].values())
    handles = [plt.Rectangle((0,0), 1, 1, color=estado["color"], alpha=0.8) for estado in estados_unicos]
    labels = [estado["nombre"] for estado in estados_unicos]
    ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.15), 
              ncol=len(estados_unicos), frameon=False)
    
    # Ajustar diseño
    plt.grid(axis='x', linestyle='--', alpha=0.3, color=grid_color)
    plt.tight_layout()
    
    return fig

def generar_roadmap(iniciativas, config, organizacion, horizonte, formato, tema, archivo_salida):
    """Genera el roadmap en el formato especificado."""
    print(f"Generando roadmap para {organizacion} con horizonte de {horizonte} años...")
    
    if formato == "html":
        fig = generar_roadmap_plotly(iniciativas, config, organizacion, horizonte, tema)
        fig.write_html(archivo_salida, auto_open=False)
    else:  # png o pdf
        fig = generar_roadmap_matplotlib(iniciativas, config, organizacion, horizonte, tema)
        plt.savefig(archivo_salida, dpi=300, bbox_inches='tight')
        plt.close(fig)
    
    print(f"Roadmap generado exitosamente: {archivo_salida}")
    return archivo_salida

def generar_iniciativas_ejemplo(archivo_salida):
    """Genera un archivo CSV de ejemplo con iniciativas tecnológicas."""
    fecha_actual = datetime.datetime.now()
    
    # Crear iniciativas de ejemplo para diferentes capas
    iniciativas = [
        {
            "id": "MKT-001",
            "nombre": "Análisis de tendencias del mercado",
            "descripcion": "Estudio de tendencias tecnológicas y su impacto en el mercado",
            "capa": "mercado",
            "fecha_inicio": (fecha_actual - datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
            "fecha_fin": (fecha_actual + datetime.timedelta(days=60)).strftime("%Y-%m-%d"),
            "estado": "en_progreso",
            "responsable": "Departamento de Marketing",
            "prioridad": "Alta"
        },
        {
            "id": "MKT-002",
            "nombre": "Análisis de competidores",
            "descripcion": "Evaluación de soluciones tecnológicas de competidores",
            "capa": "mercado",
            "fecha_inicio": (fecha_actual + datetime.timedelta(days=90)).strftime("%Y-%m-%d"),
            "fecha_fin": (fecha_actual + datetime.timedelta(days=180)).strftime("%Y-%m-%d"),
            "estado": "planificado",
            "responsable": "Departamento de Marketing",
            "prioridad": "Media"
        },
        {
            "id": "PROD-001",
            "nombre": "Rediseño de interfaz de usuario",
            "descripcion": "Modernización de la interfaz de usuario de la plataforma principal",
            "capa": "producto",
            "fecha_inicio": (fecha_actual - datetime.timedelta(days=60)).strftime("%Y-%m-%d"),
            "fecha_fin": (fecha_actual + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
            "estado": "en_progreso",
            "responsable": "Equipo de UX/UI",
            "prioridad": "Alta"
        },
        {
            "id": "PROD-002",
            "nombre": "Desarrollo de aplicación móvil",
            "descripcion": "Creación de aplicación móvil para clientes",
            "capa": "producto",
            "fecha_inicio": (fecha_actual + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
            "fecha_fin": (fecha_actual + datetime.timedelta(days=180)).strftime("%Y-%m-%d"),
            "estado": "planificado",
            "responsable": "Equipo de Desarrollo Móvil",
            "prioridad": "Alta"
        },
        {
            "id": "TECH-001",
            "nombre": "Migración a microservicios",
            "descripcion": "Transformación de la arquitectura monolítica a microservicios",
            "capa": "tecnologia",
            "fecha_inicio": (fecha_actual - datetime.timedelta(days=90)).strftime("%Y-%m-%d"),
            "fecha_fin": (fecha_actual + datetime.timedelta(days=275)).strftime("%Y-%m-%d"),
            "estado": "en_progreso",
            "responsable": "Equipo de Arquitectura",
            "prioridad": "Alta"
        },
        {
            "id": "TECH-002",
            "nombre": "Implementación de CI/CD",
            "descripcion": "Configuración de pipeline de integración y despliegue continuo",
            "capa": "tecnologia",
            "fecha_inicio": (fecha_actual - datetime.timedelta(days=45)).strftime("%Y-%m-%d"),
            "fecha_fin": (fecha_actual + datetime.timedelta(days=15)).strftime("%Y-%m-%d"),
            "estado": "completado",
            "responsable": "Equipo DevOps",
            "prioridad": "Media"
        },
        {
            "id": "TECH-003",
            "nombre": "Adopción de contenedores",
            "descripcion": "Migración de aplicaciones a contenedores Docker y Kubernetes",
            "capa": "tecnologia",
            "fecha_inicio": (fecha_actual + datetime.timedelta(days=60)).strftime("%Y-%m-%d"),
            "fecha_fin": (fecha_actual + datetime.timedelta(days=150)).strftime("%Y-%m-%d"),
            "estado": "planificado",
            "responsable": "Equipo de Infraestructura",
            "prioridad": "Alta"
        },
        {
            "id": "CAP-001",
            "nombre": "Capacitación en Cloud Native",
            "descripcion": "Programa de formación en tecnologías cloud native",
            "capa": "capacidades",
            "fecha_inicio": (fecha_actual + datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
            "fecha_fin": (fecha_actual + datetime.timedelta(days=120)).strftime("%Y-%m-%d"),
            "estado": "planificado",
            "responsable": "Departamento de RRHH",
            "prioridad": "Media"
        },
        {
            "id": "CAP-002",
            "nombre": "Contratación especialistas IA",
            "descripcion": "Incorporación de especialistas en inteligencia artificial",
            "capa": "capacidades",
            "fecha_inicio": (fecha_actual + datetime.timedelta(days=180)).strftime("%Y-%m-%d"),
            "fecha_fin": (fecha_actual + datetime.timedelta(days=270)).strftime("%Y-%m-%d"),
            "estado": "planificado",
            "responsable": "Departamento de RRHH",
            "prioridad": "Baja"
        },
        {
            "id": "TECH-004",
            "nombre": "Implementación de IA para análisis predictivo",
            "descripcion": "Desarrollo de modelos de IA para análisis predictivo de datos de clientes",
            "capa": "tecnologia",
            "fecha_inicio": (fecha_actual + datetime.timedelta(days=365)).strftime("%Y-%m-%d"),
            "fecha_fin": (fecha_actual + datetime.timedelta(days=545)).strftime("%Y-%m-%d"),
            "estado": "planificado",
            "responsable": "Equipo de Ciencia de Datos",
            "prioridad": "Media"
        }
    ]
    
    # Escribir al archivo CSV
    try:
        with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=iniciativas[0].keys())
            writer.writeheader()
            writer.writerows(iniciativas)
        print(f"Archivo de iniciativas de ejemplo generado: {archivo_salida}")
        return True
    except Exception as e:
        print(f"Error al generar el archivo de ejemplo: {e}")
        return False

def parse_arguments():
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description='Herramienta de Generación de Roadmap Tecnológico')
    parser.add_argument('--input', help='Archivo CSV con las iniciativas tecnológicas')
    parser.add_argument('--output', default='roadmap_tecnologico.html', help='Archivo de salida para el roadmap')
    parser.add_argument('--organizacion', default='Mi Organización', help='Nombre de la organización')
    parser.add_argument('--horizonte', type=int, default=CONFIG_DEFAULT["horizonte_default"], help='Horizonte temporal en años')
    parser.add_argument('--formato', choices=['html', 'png', 'pdf'], default=CONFIG_DEFAULT["formato_default"], help='Formato de salida')
    parser.add_argument('--tema', choices=['claro', 'oscuro'], default=CONFIG_DEFAULT["tema_default"], help='Tema visual')
    parser.add_argument('--generar-ejemplo', action='store_true', help='Generar un archivo CSV de ejemplo')
    return parser.parse_args()

def main():
    """Función principal."""
    args = parse_arguments()
    
    # Verificar si se solicita generar un ejemplo
    if args.generar_ejemplo:
        ejemplo_path = "iniciativas_ejemplo.csv"
        if generar_iniciativas_ejemplo(ejemplo_path):
            print(f"Puedes usar este archivo como entrada: python {sys.argv[0]} --input {ejemplo_path}")
        return
    
    # Verificar que se proporcionó un archivo de entrada
    if not args.input:
        print("Error: Debe proporcionar un archivo CSV de entrada con las iniciativas.")
        print(f"Para generar un archivo de ejemplo, use: python {sys.argv[0]} --generar-ejemplo")
        sys.exit(1)
    
    # Verificar que el archivo de entrada existe
    if not os.path.exists(args.input):
        print(f"Error: El archivo de entrada '{args.input}' no existe.")
        sys.exit(1)
    
    # Ajustar la extensión del archivo de salida según el formato
    output_path = args.output
    if not output_path.lower().endswith(f'.{args.formato}'):
        output_base = os.path.splitext(output_path)[0]
        output_path = f"{output_base}.{args.formato}"
    
    # Verificar que el directorio de salida existe
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"Error al crear el directorio de salida: {e}")
            sys.exit(1)
    
    # Cargar y validar iniciativas
    iniciativas = cargar_iniciativas(args.input)
    iniciativas_validadas = validar_iniciativas(iniciativas, CONFIG_DEFAULT)
    
    # Generar roadmap
    roadmap_path = generar_roadmap(
        iniciativas_validadas, 
        CONFIG_DEFAULT, 
        args.organizacion, 
        args.horizonte, 
        args.formato, 
        args.tema, 
        output_path
    )
    
    # Abrir el roadmap generado
    if args.formato == "html":
        webbrowser.open(f'file://{os.path.abspath(roadmap_path)}')

if __name__ == "__main__":
    main()

