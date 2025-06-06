#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para generar informes de simulaciones de ciberataques.

Este script genera informes detallados a partir de los resultados de simulaciones
de ciberataques, incluyendo gráficos, estadísticas y recomendaciones.

Uso:
    python generate_report.py --input <directorio_resultados> --output <archivo_informe>
    
Opciones:
    --input DIRECTORIO    Directorio con los resultados de la simulación
    --output ARCHIVO      Archivo de salida para el informe (PDF o HTML)
    --template ARCHIVO    Plantilla personalizada para el informe
    --logo ARCHIVO        Logo para incluir en el informe
"""

import argparse
import datetime
import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

import matplotlib
matplotlib.use('Agg')  # Usar backend no interactivo
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import pdfkit
import markdown

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('generate_report')

class ReportGenerator:
    """Clase para generar informes de simulaciones de ciberataques."""
    
    def __init__(self, input_dir: str, output_file: str, template_file: Optional[str] = None, logo_file: Optional[str] = None):
        """
        Inicializa el generador de informes.
        
        Args:
            input_dir: Directorio con los resultados de la simulación
            output_file: Archivo de salida para el informe
            template_file: Plantilla personalizada para el informe
            logo_file: Logo para incluir en el informe
        """
        self.input_dir = input_dir
        self.output_file = output_file
        self.template_file = template_file
        self.logo_file = logo_file
        self.results = {}
        self.report_data = {}
        
        # Determinar formato de salida
        self.output_format = os.path.splitext(output_file)[1].lower()
        if self.output_format not in ['.pdf', '.html']:
            logger.warning(f"Formato de salida no reconocido: {self.output_format}. Se usará HTML.")
            self.output_format = '.html'
            
        self._load_results()
        
    def _load_results(self) -> None:
        """Carga los resultados de la simulación."""
        results_file = os.path.join(self.input_dir, "results.json")
        try:
            with open(results_file, 'r') as f:
                self.results = json.load(f)
            logger.debug(f"Resultados cargados desde {results_file}")
        except FileNotFoundError:
            logger.error(f"Archivo de resultados no encontrado: {results_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear el archivo JSON: {e}")
            sys.exit(1)
            
    def _generate_charts(self) -> Dict[str, str]:
        """
        Genera gráficos para el informe.
        
        Returns:
            Diccionario con rutas a los archivos de gráficos generados
        """
        logger.info("Generando gráficos para el informe...")
        
        charts_dir = os.path.join(self.input_dir, "charts")
        os.makedirs(charts_dir, exist_ok=True)
        
        charts = {}
        
        # Gráfico de técnicas por estado
        try:
            techniques = self.results.get("techniques", [])
            if techniques:
                status_counts = {"success": 0, "failed": 0}
                for technique in techniques:
                    status = technique.get("status", "unknown")
                    if status in status_counts:
                        status_counts[status] += 1
                    else:
                        status_counts[status] = 1
                        
                # Crear gráfico de barras
                plt.figure(figsize=(8, 6))
                bars = plt.bar(
                    status_counts.keys(),
                    status_counts.values(),
                    color=['green', 'red']
                )
                
                # Añadir etiquetas
                plt.title('Resultado de Técnicas de Ataque')
                plt.xlabel('Estado')
                plt.ylabel('Cantidad')
                
                # Añadir valores en las barras
                for bar in bars:
                    height = bar.get_height()
                    plt.text(
                        bar.get_x() + bar.get_width()/2.,
                        height,
                        f'{height}',
                        ha='center',
                        va='bottom'
                    )
                    
                # Guardar gráfico
                techniques_chart_path = os.path.join(charts_dir, "techniques_status.png")
                plt.savefig(techniques_chart_path)
                plt.close()
                
                charts["techniques_status"] = techniques_chart_path
                logger.debug(f"Gráfico de técnicas generado: {techniques_chart_path}")
        except Exception as e:
            logger.error(f"Error al generar gráfico de técnicas: {e}")
            
        # Gráfico de línea de tiempo
        try:
            steps = self.results.get("steps", [])
            if steps:
                step_names = []
                durations = []
                
                for step in steps:
                    name = step.get("name", "Unknown")
                    start_time = datetime.datetime.fromisoformat(step.get("start_time", ""))
                    end_time = datetime.datetime.fromisoformat(step.get("end_time", ""))
                    duration = (end_time - start_time).total_seconds() / 60  # Duración en minutos
                    
                    step_names.append(name)
                    durations.append(duration)
                    
                # Crear gráfico de barras horizontales
                plt.figure(figsize=(10, 6))
                bars = plt.barh(step_names, durations)
                
                # Añadir etiquetas
                plt.title('Duración de Pasos de Ataque')
                plt.xlabel('Duración (minutos)')
                plt.ylabel('Paso')
                
                # Añadir valores en las barras
                for bar in bars:
                    width = bar.get_width()
                    plt.text(
                        width + 0.1,
                        bar.get_y() + bar.get_height()/2.,
                        f'{width:.2f} min',
                        ha='left',
                        va='center'
                    )
                    
                # Guardar gráfico
                timeline_chart_path = os.path.join(charts_dir, "steps_timeline.png")
                plt.savefig(timeline_chart_path)
                plt.close()
                
                charts["steps_timeline"] = timeline_chart_path
                logger.debug(f"Gráfico de línea de tiempo generado: {timeline_chart_path}")
        except Exception as e:
            logger.error(f"Error al generar gráfico de línea de tiempo: {e}")
            
        # Gráfico de mapa de calor de técnicas MITRE ATT&CK
        try:
            techniques = self.results.get("techniques", [])
            if techniques:
                # Agrupar técnicas por tácticas (primeros caracteres del ID)
                tactics = {}
                for technique in techniques:
                    technique_id = technique.get("id", "")
                    if technique_id.startswith("T"):
                        tactic = technique_id[:4]  # Tomar los primeros 4 caracteres (ej: T1078)
                        if tactic in tactics:
                            tactics[tactic] += 1
                        else:
                            tactics[tactic] = 1
                            
                if tactics:
                    # Crear gráfico de barras
                    plt.figure(figsize=(12, 6))
                    bars = plt.bar(
                        tactics.keys(),
                        tactics.values(),
                        color='blue'
                    )
                    
                    # Añadir etiquetas
                    plt.title('Técnicas MITRE ATT&CK Utilizadas')
                    plt.xlabel('ID de Técnica')
                    plt.ylabel('Frecuencia')
                    plt.xticks(rotation=45)
                    
                    # Añadir valores en las barras
                    for bar in bars:
                        height = bar.get_height()
                        plt.text(
                            bar.get_x() + bar.get_width()/2.,
                            height,
                            f'{height}',
                            ha='center',
                            va='bottom'
                        )
                        
                    plt.tight_layout()
                    
                    # Guardar gráfico
                    mitre_chart_path = os.path.join(charts_dir, "mitre_techniques.png")
                    plt.savefig(mitre_chart_path)
                    plt.close()
                    
                    charts["mitre_techniques"] = mitre_chart_path
                    logger.debug(f"Gráfico de técnicas MITRE generado: {mitre_chart_path}")
        except Exception as e:
            logger.error(f"Error al generar gráfico de técnicas MITRE: {e}")
            
        return charts
        
    def _generate_statistics(self) -> Dict[str, Any]:
        """
        Genera estadísticas para el informe.
        
        Returns:
            Diccionario con estadísticas calculadas
        """
        logger.info("Generando estadísticas para el informe...")
        
        stats = {}
        
        # Estadísticas generales
        stats["scenario_name"] = self.results.get("scenario", "Unknown")
        stats["status"] = self.results.get("status", "unknown")
        
        # Calcular duración total
        try:
            start_time = datetime.datetime.fromisoformat(self.results.get("start_time", ""))
            end_time = datetime.datetime.fromisoformat(self.results.get("end_time", ""))
            duration = end_time - start_time
            stats["duration"] = {
                "seconds": duration.total_seconds(),
                "formatted": str(duration).split('.')[0]  # Formato HH:MM:SS
            }
        except Exception:
            stats["duration"] = {"seconds": 0, "formatted": "00:00:00"}
            
        # Estadísticas de técnicas
        techniques = self.results.get("techniques", [])
        stats["techniques"] = {
            "total": len(techniques),
            "success": sum(1 for t in techniques if t.get("status") == "success"),
            "failed": sum(1 for t in techniques if t.get("status") == "failed"),
            "success_rate": 0
        }
        
        if stats["techniques"]["total"] > 0:
            stats["techniques"]["success_rate"] = (stats["techniques"]["success"] / stats["techniques"]["total"]) * 100
            
        # Estadísticas de pasos
        steps = self.results.get("steps", [])
        stats["steps"] = {
            "total": len(steps),
            "success": sum(1 for s in steps if s.get("status") == "success"),
            "failed": sum(1 for s in steps if s.get("status") == "failed"),
            "success_rate": 0
        }
        
        if stats["steps"]["total"] > 0:
            stats["steps"]["success_rate"] = (stats["steps"]["success"] / stats["steps"]["total"]) * 100
            
        return stats
        
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """
        Genera recomendaciones basadas en los resultados.
        
        Returns:
            Lista de recomendaciones
        """
        logger.info("Generando recomendaciones para el informe...")
        
        recommendations = []
        
        # Analizar técnicas fallidas
        techniques = self.results.get("techniques", [])
        failed_techniques = [t for t in techniques if t.get("status") == "failed"]
        
        if failed_techniques:
            recommendations.append({
                "title": "Mejorar detección de técnicas",
                "description": "Se recomienda mejorar la detección de las técnicas que fallaron durante la simulación. Esto podría indicar que estas técnicas son más difíciles de detectar o que los controles actuales son efectivos.",
                "priority": "Alta"
            })
            
        # Analizar técnicas exitosas
        successful_techniques = [t for t in techniques if t.get("status") == "success"]
        
        if successful_techniques:
            recommendations.append({
                "title": "Fortalecer controles de seguridad",
                "description": "Se recomienda fortalecer los controles de seguridad para las técnicas que tuvieron éxito durante la simulación. Estas representan vulnerabilidades potenciales que podrían ser explotadas por atacantes reales.",
                "priority": "Alta"
            })
            
        # Recomendaciones generales
        recommendations.append({
            "title": "Realizar simulaciones periódicas",
            "description": "Se recomienda realizar simulaciones de ciberataques de forma periódica para evaluar continuamente la postura de seguridad y la efectividad de los controles implementados.",
            "priority": "Media"
        })
        
        recommendations.append({
            "title": "Actualizar procedimientos de respuesta",
            "description": "Actualizar los procedimientos de respuesta a incidentes basándose en los hallazgos de esta simulación, especialmente para las técnicas que tuvieron éxito.",
            "priority": "Media"
        })
        
        recommendations.append({
            "title": "Capacitación del personal",
            "description": "Proporcionar capacitación adicional al personal de seguridad sobre las técnicas utilizadas en esta simulación, especialmente aquellas que no fueron detectadas o mitigadas correctamente.",
            "priority": "Media"
        })
        
        return recommendations
        
    def _prepare_report_data(self) -> None:
        """Prepara los datos para el informe."""
        logger.info("Preparando datos para el informe...")
        
        # Generar gráficos
        charts = self._generate_charts()
        
        # Generar estadísticas
        stats = self._generate_statistics()
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations()
        
        # Preparar datos del informe
        self.report_data = {
            "title": f"Informe de Simulación de Ciberataques: {stats['scenario_name']}",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "logo": self.logo_file,
            "scenario": stats["scenario_name"],
            "status": stats["status"],
            "duration": stats["duration"]["formatted"],
            "start_time": self.results.get("start_time", "").replace("T", " ").split(".")[0],
            "end_time": self.results.get("end_time", "").replace("T", " ").split(".")[0],
            "statistics": stats,
            "charts": charts,
            "recommendations": recommendations,
            "techniques": self.results.get("techniques", []),
            "steps": self.results.get("steps", [])
        }
        
    def _generate_html_report(self) -> str:
        """
        Genera el informe en formato HTML.
        
        Returns:
            Ruta al archivo HTML generado
        """
        logger.info("Generando informe HTML...")
        
        # Determinar plantilla a utilizar
        if self.template_file and os.path.exists(self.template_file):
            template_path = os.path.dirname(self.template_file)
            template_file = os.path.basename(self.template_file)
        else:
            # Usar plantilla predeterminada
            template_path = os.path.join(os.path.dirname(__file__), "templates")
            template_file = "report_template.html"
            
            # Si no existe la plantilla predeterminada, crear una básica
            if not os.path.exists(os.path.join(template_path, template_file)):
                os.makedirs(template_path, exist_ok=True)
                with open(os.path.join(template_path, template_file), 'w') as f:
                    f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #ddd;
        }
        .logo {
            max-height: 100px;
            margin-bottom: 20px;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        h2 {
            color: #3498db;
            margin-top: 30px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        h3 {
            color: #2980b9;
        }
        .summary {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        .summary-item {
            margin-bottom: 10px;
        }
        .summary-label {
            font-weight: bold;
            display: inline-block;
            width: 150px;
        }
        .chart {
            margin: 20px 0;
            text-align: center;
        }
        .chart img {
            max-width: 100%;
            height: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .success {
            color: green;
        }
        .failed {
            color: red;
        }
        .recommendations {
            margin-top: 30px;
        }
        .recommendation {
            background-color: #f8f9fa;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #3498db;
        }
        .high-priority {
            border-left-color: #e74c3c;
        }
        .medium-priority {
            border-left-color: #f39c12;
        }
        .low-priority {
            border-left-color: #2ecc71;
        }
        .footer {
            margin-top: 50px;
            text-align: center;
            font-size: 0.9em;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {% if logo %}
            <img src="{{ logo }}" alt="Logo" class="logo">
            {% endif %}
            <h1>{{ title }}</h1>
            <p>Fecha: {{ date }}</p>
        </div>

        <div class="summary">
            <h2>Resumen de la Simulación</h2>
            <div class="summary-item">
                <span class="summary-label">Escenario:</span>
                <span>{{ scenario }}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Estado:</span>
                <span class="{% if status == 'completed' %}success{% else %}failed{% endif %}">{{ status }}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Inicio:</span>
                <span>{{ start_time }}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Fin:</span>
                <span>{{ end_time }}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Duración:</span>
                <span>{{ duration }}</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Técnicas Exitosas:</span>
                <span>{{ statistics.techniques.success }} de {{ statistics.techniques.total }} ({{ statistics.techniques.success_rate|round(1) }}%)</span>
            </div>
            <div class="summary-item">
                <span class="summary-label">Pasos Exitosos:</span>
                <span>{{ statistics.steps.success }} de {{ statistics.steps.total }} ({{ statistics.steps.success_rate|round(1) }}%)</span>
            </div>
        </div>

        <h2>Resultados Gráficos</h2>
        {% if charts.techniques_status %}
        <div class="chart">
            <h3>Estado de las Técnicas</h3>
            <img src="{{ charts.techniques_status }}" alt="Estado de las Técnicas">
        </div>
        {% endif %}
        
        {% if charts.steps_timeline %}
        <div class="chart">
            <h3>Duración de los Pasos</h3>
            <img src="{{ charts.steps_timeline }}" alt="Duración de los Pasos">
        </div>
        {% endif %}
        
        {% if charts.mitre_techniques %}
        <div class="chart">
            <h3>Técnicas MITRE ATT&CK</h3>
            <img src="{{ charts.mitre_techniques }}" alt="Técnicas MITRE ATT&CK">
        </div>
        {% endif %}

        <h2>Técnicas Ejecutadas</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Nombre</th>
                    <th>Estado</th>
                </tr>
            </thead>
            <tbody>
                {% for technique in techniques %}
                <tr>
                    <td>{{ technique.id }}</td>
                    <td>{{ technique.name }}</td>
                    <td class="{% if technique.status == 'success' %}success{% else %}failed{% endif %}">{{ technique.status }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <h2>Pasos Ejecutados</h2>
        <table>
            <thead>
                <tr>
                    <th>Nombre</th>
                    <th>Estado</th>
                    <th>Duración</th>
                </tr>
            </thead>
            <tbody>
                {% for step in steps %}
                <tr>
                    <td>{{ step.name }}</td>
                    <td class="{% if step.status == 'success' %}success{% else %}failed{% endif %}">{{ step.status }}</td>
                    <td>
                        {% set start = step.start_time|replace("T", " ")|replace("Z", "")|trim %}
                        {% set end = step.end_time|replace("T", " ")|replace("Z", "")|trim %}
                        {{ (end|string|to_datetime - start|string|to_datetime)|string|split('.')[0] }}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <h2>Recomendaciones</h2>
        <div class="recommendations">
            {% for rec in recommendations %}
            <div class="recommendation {% if rec.priority == 'Alta' %}high-priority{% elif rec.priority == 'Media' %}medium-priority{% else %}low-priority{% endif %}">
                <h3>{{ rec.title }} <small>({{ rec.priority }})</small></h3>
                <p>{{ rec.description }}</p>
            </div>
            {% endfor %}
        </div>

        <div class="footer">
            <p>Informe generado automáticamente el {{ date }}</p>
        </div>
    </div>
</body>
</html>""")
                
        # Configurar entorno Jinja2
        env = Environment(loader=FileSystemLoader(template_path))
        
        # Añadir filtro para convertir strings a datetime
        def to_datetime(value):
            return datetime.datetime.fromisoformat(value)
        env.filters['to_datetime'] = to_datetime
        
        # Cargar plantilla
        template = env.get_template(template_file)
        
        # Renderizar HTML
        html_content = template.render(**self.report_data)
        
        # Guardar HTML
        html_output = self.output_file
        if not html_output.endswith('.html'):
            html_output = f"{os.path.splitext(html_output)[0]}.html"
            
        with open(html_output, 'w') as f:
            f.write(html_content)
            
        logger.debug(f"Informe HTML generado: {html_output}")
        return html_output
        
    def _generate_pdf_report(self) -> str:
        """
        Genera el informe en formato PDF.
        
        Returns:
            Ruta al archivo PDF generado
        """
        logger.info("Generando informe PDF...")
        
        # Primero generar HTML
        html_file = self._generate_html_report()
        
        # Convertir HTML a PDF
        pdf_output = self.output_file
        if not pdf_output.endswith('.pdf'):
            pdf_output = f"{os.path.splitext(pdf_output)[0]}.pdf"
            
        try:
            pdfkit.from_file(html_file, pdf_output)
            logger.debug(f"Informe PDF generado: {pdf_output}")
            return pdf_output
        except Exception as e:
            logger.error(f"Error al generar PDF: {e}")
            logger.warning(f"Se utilizará el informe HTML: {html_file}")
            return html_file
            
    def generate(self) -> str:
        """
        Genera el informe completo.
        
        Returns:
            Ruta al archivo de informe generado
        """
        logger.info("Generando informe completo...")
        
        # Preparar datos
        self._prepare_report_data()
        
        # Generar informe según formato
        if self.output_format == '.pdf':
            return self._generate_pdf_report()
        else:
            return self._generate_html_report()
            
def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Generar informe de simulación de ciberataques')
    parser.add_argument('--input', required=True, help='Directorio con los resultados de la simulación')
    parser.add_argument('--output', required=True, help='Archivo de salida para el informe (PDF o HTML)')
    parser.add_argument('--template', help='Plantilla personalizada para el informe')
    parser.add_argument('--logo', help='Logo para incluir en el informe')
    
    args = parser.parse_args()
    
    generator = ReportGenerator(
        input_dir=args.input,
        output_file=args.output,
        template_file=args.template,
        logo_file=args.logo
    )
    
    output_file = generator.generate()
    logger.info(f"Informe generado correctamente: {output_file}")
    
if __name__ == "__main__":
    main()

