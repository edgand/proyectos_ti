#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generador de Roadmap Tecnológico

Este script genera un roadmap tecnológico en formato HTML a partir de un archivo CSV
que contiene iniciativas estratégicas de TI.

Uso:
    python generar_roadmap.py --input iniciativas.csv --output roadmap_tecnologico.html

Formato del CSV de entrada:
    id,nombre,descripcion,categoria,inicio,fin,dependencias,responsable,prioridad,estado

Ejemplo:
    ID1,Migración a Cloud,Migrar infraestructura a AWS,Infraestructura,2025-01,2025-06,,,Alta,No iniciado
    ID2,Implementación CRM,Implementar Salesforce,Aplicaciones,2025-03,2025-09,ID1,Dept. Ventas,Alta,No iniciado
"""

import argparse
import csv
import datetime
import sys
from collections import defaultdict
import os

def parse_arguments():
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description='Genera un roadmap tecnológico a partir de un archivo CSV.')
    parser.add_argument('--input', required=True, help='Archivo CSV de entrada con las iniciativas')
    parser.add_argument('--output', required=True, help='Archivo HTML de salida para el roadmap')
    parser.add_argument('--periodo', default='2025-2027', help='Periodo del roadmap (formato: AAAA-AAAA)')
    parser.add_argument('--titulo', default='Roadmap Tecnológico', help='Título del roadmap')
    parser.add_argument('--organizacion', default='Mi Organización', help='Nombre de la organización')
    return parser.parse_args()

def leer_iniciativas(archivo_csv):
    """Lee las iniciativas desde un archivo CSV."""
    iniciativas = []
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                iniciativas.append(row)
        return iniciativas
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {archivo_csv}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        sys.exit(1)

def parse_fecha(fecha_str):
    """Convierte una fecha en formato AAAA-MM a un objeto datetime."""
    try:
        return datetime.datetime.strptime(fecha_str, '%Y-%m')
    except ValueError:
        print(f"Error: Formato de fecha incorrecto: {fecha_str}. Use el formato AAAA-MM.")
        sys.exit(1)

def calcular_periodo(iniciativas, periodo_arg):
    """Calcula el periodo del roadmap basado en las iniciativas o el argumento proporcionado."""
    inicio_arg, fin_arg = periodo_arg.split('-')
    inicio_arg = datetime.datetime(int(inicio_arg), 1, 1)
    fin_arg = datetime.datetime(int(fin_arg), 12, 31)
    
    # Si hay iniciativas, ajustar el periodo según las fechas de las iniciativas
    if iniciativas:
        fechas_inicio = [parse_fecha(i['inicio']) for i in iniciativas if 'inicio' in i and i['inicio']]
        fechas_fin = [parse_fecha(i['fin']) for i in iniciativas if 'fin' in i and i['fin']]
        
        if fechas_inicio and fechas_fin:
            min_inicio = min(fechas_inicio)
            max_fin = max(fechas_fin)
            
            # Ajustar al periodo proporcionado si es necesario
            inicio = min(min_inicio, inicio_arg)
            fin = max(max_fin, fin_arg)
            
            # Ajustar a años completos
            inicio = datetime.datetime(inicio.year, 1, 1)
            fin = datetime.datetime(fin.year, 12, 31)
            
            return inicio, fin
    
    return inicio_arg, fin_arg

def generar_meses(fecha_inicio, fecha_fin):
    """Genera una lista de todos los meses en el periodo."""
    meses = []
    mes_actual = datetime.datetime(fecha_inicio.year, fecha_inicio.month, 1)
    
    while mes_actual <= fecha_fin:
        meses.append(mes_actual)
        # Avanzar al siguiente mes
        if mes_actual.month == 12:
            mes_actual = datetime.datetime(mes_actual.year + 1, 1, 1)
        else:
            mes_actual = datetime.datetime(mes_actual.year, mes_actual.month + 1, 1)
    
    return meses

def generar_html_roadmap(iniciativas, archivo_salida, fecha_inicio, fecha_fin, titulo, organizacion):
    """Genera un archivo HTML con el roadmap."""
    meses = generar_meses(fecha_inicio, fecha_fin)
    
    # Agrupar iniciativas por categoría
    iniciativas_por_categoria = defaultdict(list)
    for iniciativa in iniciativas:
        categoria = iniciativa.get('categoria', 'Sin categoría')
        iniciativas_por_categoria[categoria].append(iniciativa)
    
    # Generar colores para las categorías
    colores = {
        'Infraestructura': '#4285F4',  # Azul
        'Aplicaciones': '#34A853',     # Verde
        'Datos': '#FBBC05',            # Amarillo
        'Seguridad': '#EA4335',        # Rojo
        'Procesos': '#9C27B0',         # Púrpura
        'Personas': '#FF9800',         # Naranja
        'Sin categoría': '#9E9E9E'     # Gris
    }
    
    # Asignar colores a categorías no predefinidas
    colores_base = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#d35400', '#34495e']
    color_index = 0
    for categoria in iniciativas_por_categoria.keys():
        if categoria not in colores:
            colores[categoria] = colores_base[color_index % len(colores_base)]
            color_index += 1
    
    # Generar HTML
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo} - {organizacion}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            border-radius: 5px;
        }}
        h1, h2 {{
            color: #2c3e50;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #7f8c8d;
            margin-top: 0;
            margin-bottom: 30px;
        }}
        .roadmap {{
            overflow-x: auto;
            margin-top: 30px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }}
        th {{
            background-color: #f2f2f2;
            position: sticky;
            top: 0;
        }}
        .year-header {{
            background-color: #2c3e50;
            color: white;
        }}
        .month-header {{
            background-color: #34495e;
            color: white;
            font-size: 0.8em;
        }}
        .category {{
            text-align: left;
            font-weight: bold;
            background-color: #ecf0f1;
        }}
        .initiative {{
            text-align: left;
            padding-left: 20px;
        }}
        .bar {{
            height: 20px;
            border-radius: 3px;
            margin: 2px 0;
        }}
        .tooltip {{
            position: relative;
            display: inline-block;
        }}
        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 200px;
            background-color: #555;
            color: #fff;
            text-align: left;
            border-radius: 6px;
            padding: 5px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -100px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.8em;
        }}
        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}
        .legend {{
            margin-top: 20px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 5px 15px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            margin-right: 5px;
            border-radius: 3px;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 0.8em;
            color: #7f8c8d;
        }}
        @media print {{
            body {{
                background-color: white;
            }}
            .container {{
                box-shadow: none;
                padding: 0;
            }}
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{titulo}</h1>
        <p class="subtitle">{organizacion} | Periodo: {fecha_inicio.strftime('%Y')} - {fecha_fin.strftime('%Y')}</p>
        
        <div class="roadmap">
            <table>
                <thead>
                    <tr>
                        <th rowspan="2">Iniciativa</th>
"""
    
    # Generar encabezados de años
    año_actual = None
    for mes in meses:
        if año_actual != mes.year:
            año_actual = mes.year
            colspan = sum(1 for m in meses if m.year == año_actual)
            html += f'<th colspan="{colspan}" class="year-header">{año_actual}</th>\n'
    
    html += '</tr>\n<tr>\n'
    
    # Generar encabezados de meses
    for mes in meses:
        nombre_mes = mes.strftime('%b')
        html += f'<th class="month-header">{nombre_mes}</th>\n'
    
    html += '</tr>\n</thead>\n<tbody>\n'
    
    # Generar filas para cada categoría e iniciativa
    for categoria, iniciativas_cat in iniciativas_por_categoria.items():
        html += f'<tr><td class="category" colspan="{len(meses) + 1}">{categoria}</td></tr>\n'
        
        for iniciativa in iniciativas_cat:
            id_iniciativa = iniciativa.get('id', '')
            nombre = iniciativa.get('nombre', 'Sin nombre')
            descripcion = iniciativa.get('descripcion', '')
            inicio = parse_fecha(iniciativa.get('inicio', '')) if iniciativa.get('inicio') else None
            fin = parse_fecha(iniciativa.get('fin', '')) if iniciativa.get('fin') else None
            dependencias = iniciativa.get('dependencias', '')
            responsable = iniciativa.get('responsable', '')
            prioridad = iniciativa.get('prioridad', '')
            estado = iniciativa.get('estado', '')
            
            # Información para el tooltip
            tooltip_info = f"""
                <b>ID:</b> {id_iniciativa}<br>
                <b>Descripción:</b> {descripcion}<br>
                <b>Periodo:</b> {inicio.strftime('%b %Y') if inicio else '?'} - {fin.strftime('%b %Y') if fin else '?'}<br>
                <b>Responsable:</b> {responsable}<br>
                <b>Prioridad:</b> {prioridad}<br>
                <b>Estado:</b> {estado}<br>
                <b>Dependencias:</b> {dependencias}
            """
            
            html += f'<tr>\n<td class="initiative tooltip">{nombre}<span class="tooltiptext">{tooltip_info}</span></td>\n'
            
            # Generar celdas para cada mes
            for mes in meses:
                if inicio and fin and inicio <= mes <= fin:
                    # Determinar si es el primer o último mes para redondear los bordes
                    es_primero = mes.year == inicio.year and mes.month == inicio.month
                    es_ultimo = mes.year == fin.year and mes.month == fin.month
                    
                    border_radius = ""
                    if es_primero and es_ultimo:
                        border_radius = "border-radius: 3px;"
                    elif es_primero:
                        border_radius = "border-radius: 3px 0 0 3px;"
                    elif es_ultimo:
                        border_radius = "border-radius: 0 3px 3px 0;"
                    
                    html += f'<td><div class="bar tooltip" style="background-color: {colores[categoria]}; {border_radius}"><span class="tooltiptext">{tooltip_info}</span></div></td>\n'
                else:
                    html += '<td></td>\n'
            
            html += '</tr>\n'
    
    html += '</tbody>\n</table>\n</div>\n'
    
    # Generar leyenda
    html += '<div class="legend">\n'
    for categoria, color in colores.items():
        if categoria in iniciativas_por_categoria:
            html += f'<div class="legend-item"><div class="legend-color" style="background-color: {color};"></div>{categoria}</div>\n'
    html += '</div>\n'
    
    # Pie de página
    html += f"""
        <div class="footer">
            Generado el {datetime.datetime.now().strftime('%d/%m/%Y')} | Plan Estratégico de TI
        </div>
    </div>
</body>
</html>
"""
    
    # Escribir el archivo HTML
    try:
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Roadmap generado exitosamente: {archivo_salida}")
    except Exception as e:
        print(f"Error al escribir el archivo HTML: {e}")
        sys.exit(1)

def main():
    """Función principal."""
    args = parse_arguments()
    
    # Verificar que el directorio de salida existe
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except Exception as e:
            print(f"Error al crear el directorio de salida: {e}")
            sys.exit(1)
    
    # Leer iniciativas
    iniciativas = leer_iniciativas(args.input)
    
    # Calcular periodo
    fecha_inicio, fecha_fin = calcular_periodo(iniciativas, args.periodo)
    
    # Generar roadmap
    generar_html_roadmap(iniciativas, args.output, fecha_inicio, fecha_fin, args.titulo, args.organizacion)

if __name__ == "__main__":
    main()

