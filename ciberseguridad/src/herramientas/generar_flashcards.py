#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Herramienta para Generar Flashcards de Estudio para Certificaciones de Ciberseguridad

Esta herramienta genera flashcards (tarjetas de memoria) para ayudar en el estudio de
certificaciones de ciberseguridad (CISSP, CISM, CEH, ITIL). Las flashcards pueden
generarse en diferentes formatos y organizarse por dominios.

Uso:
    python generar_flashcards.py --certificacion [cissp|cism|ceh|itil] --dominio NOMBRE_DOMINIO
    
Opciones adicionales:
    --formato [txt|csv|anki|html|pdf]  Formato de salida de las flashcards
    --cantidad NUM                     Número de flashcards a generar
    --salida ARCHIVO                   Archivo para guardar las flashcards
    --incluir_ejemplos                 Incluir ejemplos prácticos en las flashcards
"""

import argparse
import csv
import json
import os
import sys
import random
import datetime
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
            }
        },
        "cism": {
            "nombre": "Certified Information Security Manager",
            "dominios": {
                "gobierno_seguridad": "Gobierno de la Seguridad de la Información",
                "gestion_riesgos": "Gestión de Riesgos de la Información",
                "programa_seguridad": "Desarrollo y Gestión del Programa de Seguridad",
                "gestion_incidentes": "Gestión de Incidentes de Seguridad"
            }
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
            }
        },
        "itil": {
            "nombre": "Information Technology Infrastructure Library",
            "dominios": {
                "conceptos_clave": "Conceptos Clave de ITIL",
                "cuatro_dimensiones": "Las Cuatro Dimensiones de la Gestión de Servicios",
                "sistema_valor": "El Sistema de Valor del Servicio ITIL",
                "practicas_gestion": "Prácticas de Gestión de ITIL",
                "mejora_continua": "Mejora Continua"
            }
        }
    }

# Base de conocimientos para flashcards
# Formato: {certificacion: {dominio: [lista de flashcards]}}
FLASHCARDS_DB = {
    "cissp": {
        "seguridad_riesgos": [
            {
                "pregunta": "¿Qué es la tríada CIA?",
                "respuesta": "La tríada CIA se refiere a los tres principios fundamentales de la seguridad de la información: Confidencialidad, Integridad y Disponibilidad.",
                "ejemplo": "Confidencialidad: cifrado de datos. Integridad: firmas digitales. Disponibilidad: sistemas redundantes."
            },
            {
                "pregunta": "¿Qué es un BIA (Análisis de Impacto al Negocio)?",
                "respuesta": "Un BIA es un proceso que identifica y evalúa los efectos potenciales de una interrupción en las operaciones críticas del negocio.",
                "ejemplo": "Un BIA determina que el sistema de procesamiento de pagos tiene un RTO de 4 horas porque cada hora de inactividad cuesta $50,000."
            },
            {
                "pregunta": "Explique la diferencia entre riesgo, amenaza y vulnerabilidad.",
                "respuesta": "Amenaza: Cualquier circunstancia o evento con el potencial de causar daño. Vulnerabilidad: Debilidad que puede ser explotada. Riesgo: Probabilidad de que una amenaza explote una vulnerabilidad, causando daño.",
                "ejemplo": "Amenaza: hacker. Vulnerabilidad: software sin parches. Riesgo: probabilidad de que el hacker explote el software sin parches."
            },
            {
                "pregunta": "¿Qué es la gestión de riesgos?",
                "respuesta": "La gestión de riesgos es el proceso de identificar, evaluar y mitigar riesgos para la organización, incluyendo la implementación de controles para reducir el riesgo a un nivel aceptable.",
                "ejemplo": "Una organización identifica el riesgo de pérdida de datos, evalúa su impacto como alto, y decide implementar cifrado y copias de seguridad como controles."
            },
            {
                "pregunta": "Describa los cuatro tipos de controles de seguridad.",
                "respuesta": "1. Preventivos: evitan que ocurran incidentes. 2. Detectivos: identifican cuando ha ocurrido un incidente. 3. Correctivos: mitigan el impacto de un incidente. 4. Disuasivos: desalientan a los atacantes.",
                "ejemplo": "Preventivo: firewall. Detectivo: IDS. Correctivo: backup. Disuasivo: cámaras visibles."
            }
        ],
        "seguridad_activos": [
            {
                "pregunta": "¿Qué es la clasificación de datos?",
                "respuesta": "La clasificación de datos es el proceso de categorizar los datos según su sensibilidad, criticidad y valor para la organización, para determinar los controles de seguridad apropiados.",
                "ejemplo": "Clasificaciones comunes: Público, Interno, Confidencial, Restringido."
            },
            {
                "pregunta": "¿Qué es el ciclo de vida de la información?",
                "respuesta": "El ciclo de vida de la información describe las fases por las que pasan los datos desde su creación hasta su eliminación: creación/recepción, distribución, uso, mantenimiento, y disposición.",
                "ejemplo": "Un documento confidencial se crea, se distribuye a un equipo, se utiliza para un proyecto, se archiva por 7 años y luego se destruye."
            },
            {
                "pregunta": "¿Qué es la sanitización de datos?",
                "respuesta": "La sanitización de datos es el proceso de eliminar información sensible de medios de almacenamiento de manera que no pueda ser recuperada.",
                "ejemplo": "Métodos de sanitización: borrado seguro, desmagnetización, destrucción física."
            }
        ],
        # Más dominios...
    },
    "cism": {
        "gobierno_seguridad": [
            {
                "pregunta": "¿Qué es el gobierno de seguridad de la información?",
                "respuesta": "El gobierno de seguridad de la información es el sistema mediante el cual se dirigen y controlan las actividades de seguridad de la información, alineándolas con los objetivos estratégicos de la organización.",
                "ejemplo": "Un comité de seguridad de la información que reporta al consejo directivo y establece políticas alineadas con los objetivos de negocio."
            },
            {
                "pregunta": "¿Cuáles son los componentes clave del gobierno de seguridad?",
                "respuesta": "Los componentes clave incluyen: liderazgo y compromiso ejecutivo, estructura organizativa, roles y responsabilidades, políticas y estándares, gestión de riesgos, y medición del desempeño.",
                "ejemplo": "Un CISO que reporta al CEO, un comité de seguridad, políticas documentadas, un marco de gestión de riesgos y métricas de seguridad."
            }
        ],
        # Más dominios...
    },
    # Más certificaciones...
}

class GeneradorFlashcards:
    def __init__(self, certificacion, dominio=None, formato="txt", cantidad=None, incluir_ejemplos=False):
        """
        Inicializa el generador de flashcards.
        
        Args:
            certificacion: Nombre de la certificación (cissp, cism, ceh, itil)
            dominio: Dominio específico para generar flashcards (opcional)
            formato: Formato de salida (txt, csv, anki, html, pdf)
            cantidad: Número de flashcards a generar (opcional)
            incluir_ejemplos: Si se deben incluir ejemplos prácticos en las flashcards
        """
        if certificacion not in CERTIFICACIONES:
            print(f"Error: Certificación '{certificacion}' no reconocida.")
            print(f"Certificaciones disponibles: {', '.join(CERTIFICACIONES.keys())}")
            sys.exit(1)
            
        self.certificacion = certificacion
        self.dominio = dominio
        self.formato = formato
        self.cantidad = cantidad
        self.incluir_ejemplos = incluir_ejemplos
        
        # Validar dominio si se especificó
        if dominio and dominio not in CERTIFICACIONES[certificacion]["dominios"]:
            print(f"Error: Dominio '{dominio}' no reconocido para la certificación {certificacion}.")
            print(f"Dominios disponibles:")
            for key, value in CERTIFICACIONES[certificacion]["dominios"].items():
                print(f"  - {key}: {value}")
            sys.exit(1)
            
    def seleccionar_flashcards(self):
        """Selecciona las flashcards según los criterios especificados."""
        flashcards_seleccionadas = []
        
        # Obtener flashcards disponibles
        if self.dominio:
            # Seleccionar flashcards de un dominio específico
            dominios = [self.dominio]
        else:
            # Seleccionar flashcards de todos los dominios
            dominios = CERTIFICACIONES[self.certificacion]["dominios"].keys()
            
        # Recopilar flashcards de los dominios seleccionados
        for dominio in dominios:
            if dominio in FLASHCARDS_DB.get(self.certificacion, {}):
                flashcards_dominio = FLASHCARDS_DB[self.certificacion][dominio]
                
                # Añadir metadatos del dominio
                for flashcard in flashcards_dominio:
                    flashcard_con_meta = flashcard.copy()
                    flashcard_con_meta["dominio"] = dominio
                    flashcard_con_meta["nombre_dominio"] = CERTIFICACIONES[self.certificacion]["dominios"][dominio]
                    flashcards_seleccionadas.append(flashcard_con_meta)
        
        # Si no hay flashcards disponibles, generar algunas básicas
        if not flashcards_seleccionadas:
            flashcards_seleccionadas = self.generar_flashcards_basicas(dominios)
            
        # Limitar cantidad si se especificó
        if self.cantidad and len(flashcards_seleccionadas) > self.cantidad:
            flashcards_seleccionadas = random.sample(flashcards_seleccionadas, self.cantidad)
            
        return flashcards_seleccionadas
    
    def generar_flashcards_basicas(self, dominios):
        """Genera flashcards básicas para los dominios especificados."""
        flashcards = []
        
        for dominio in dominios:
            nombre_dominio = CERTIFICACIONES[self.certificacion]["dominios"][dominio]
            
            # Generar flashcards básicas para este dominio
            flashcards.append({
                "dominio": dominio,
                "nombre_dominio": nombre_dominio,
                "pregunta": f"¿Qué es {nombre_dominio}?",
                "respuesta": f"{nombre_dominio} es un área clave de conocimiento en la certificación {CERTIFICACIONES[self.certificacion]['nombre']}.",
                "ejemplo": f"Estudiar este dominio es esencial para comprender los conceptos fundamentales de {CERTIFICACIONES[self.certificacion]['nombre']}."
            })
            
            flashcards.append({
                "dominio": dominio,
                "nombre_dominio": nombre_dominio,
                "pregunta": f"Mencione tres conceptos clave de {nombre_dominio}.",
                "respuesta": f"Los conceptos clave varían según el dominio específico, pero generalmente incluyen principios fundamentales, mejores prácticas y estándares relacionados con {nombre_dominio}.",
                "ejemplo": "Consulte la documentación oficial de la certificación para obtener información detallada sobre este dominio."
            })
            
        return flashcards
    
    def generar_txt(self, flashcards):
        """Genera flashcards en formato de texto plano."""
        output = f"FLASHCARDS: {CERTIFICACIONES[self.certificacion]['nombre']}\n"
        output += f"Fecha de generación: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        if self.dominio:
            output += f"Dominio: {CERTIFICACIONES[self.certificacion]['dominios'][self.dominio]}\n"
        
        output += f"Cantidad: {len(flashcards)}\n"
        output += "=" * 80 + "\n\n"
        
        for i, flashcard in enumerate(flashcards, 1):
            output += f"FLASHCARD #{i}\n"
            output += f"Dominio: {flashcard['nombre_dominio']}\n"
            output += f"Pregunta: {flashcard['pregunta']}\n"
            output += f"Respuesta: {flashcard['respuesta']}\n"
            
            if self.incluir_ejemplos and "ejemplo" in flashcard:
                output += f"Ejemplo: {flashcard['ejemplo']}\n"
                
            output += "\n" + "-" * 40 + "\n\n"
            
        return output
    
    def generar_csv(self, flashcards):
        """Genera flashcards en formato CSV."""
        import io
        import csv
        
        output = io.StringIO()
        fieldnames = ["Dominio", "Pregunta", "Respuesta"]
        
        if self.incluir_ejemplos:
            fieldnames.append("Ejemplo")
            
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for flashcard in flashcards:
            row = {
                "Dominio": flashcard["nombre_dominio"],
                "Pregunta": flashcard["pregunta"],
                "Respuesta": flashcard["respuesta"]
            }
            
            if self.incluir_ejemplos and "ejemplo" in flashcard:
                row["Ejemplo"] = flashcard["ejemplo"]
                
            writer.writerow(row)
            
        return output.getvalue()
    
    def generar_anki(self, flashcards):
        """Genera flashcards en formato compatible con Anki."""
        # Anki usa un formato específico para importar tarjetas
        # Aquí generamos un archivo de texto con campos separados por tabulaciones
        output = ""
        
        for flashcard in flashcards:
            # Formato básico: pregunta<tab>respuesta
            line = f"{flashcard['pregunta']}\t{flashcard['respuesta']}"
            
            # Añadir campos adicionales si es necesario
            if self.incluir_ejemplos and "ejemplo" in flashcard:
                line += f"\t{flashcard['ejemplo']}"
                
            line += f"\t{flashcard['nombre_dominio']}"
            output += line + "\n"
            
        return output
    
    def generar_html(self, flashcards):
        """Genera flashcards en formato HTML."""
        html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flashcards de Estudio</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1, h2 {
            color: #333;
            text-align: center;
        }
        .flashcard {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            overflow: hidden;
        }
        .flashcard-header {
            background-color: #4285f4;
            color: white;
            padding: 10px 15px;
            font-weight: bold;
        }
        .flashcard-body {
            padding: 15px;
        }
        .flashcard-question {
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 1.1em;
        }
        .flashcard-answer {
            display: none;
            background-color: #f9f9f9;
            padding: 10px;
            border-left: 3px solid #4285f4;
            margin-top: 10px;
        }
        .flashcard-example {
            display: none;
            background-color: #e8f0fe;
            padding: 10px;
            border-left: 3px solid #34a853;
            margin-top: 10px;
            font-style: italic;
        }
        .flashcard-toggle {
            background-color: #4285f4;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 10px;
        }
        .flashcard-toggle:hover {
            background-color: #3367d6;
        }
        .info {
            background-color: #e8f0fe;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>Flashcards de Estudio</h1>
    <div class="info">
        <p><strong>Certificación:</strong> """ + CERTIFICACIONES[self.certificacion]['nombre'] + """</p>
"""
        
        if self.dominio:
            html += f"        <p><strong>Dominio:</strong> {CERTIFICACIONES[self.certificacion]['dominios'][self.dominio]}</p>\n"
            
        html += f"""        <p><strong>Cantidad:</strong> {len(flashcards)}</p>
        <p><strong>Fecha de generación:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <h2>Instrucciones</h2>
    <p>Haga clic en "Mostrar Respuesta" para ver la respuesta a cada pregunta. Intente responder mentalmente antes de ver la respuesta.</p>
    
"""

        for i, flashcard in enumerate(flashcards, 1):
            html += f"""    <div class="flashcard">
        <div class="flashcard-header">Flashcard #{i} - {flashcard['nombre_dominio']}</div>
        <div class="flashcard-body">
            <div class="flashcard-question">{flashcard['pregunta']}</div>
            <button class="flashcard-toggle" onclick="toggleAnswer(this)">Mostrar Respuesta</button>
            <div class="flashcard-answer">{flashcard['respuesta']}</div>
"""
            
            if self.incluir_ejemplos and "ejemplo" in flashcard:
                html += f"""            <button class="flashcard-toggle" onclick="toggleExample(this)" style="background-color: #34a853;">Mostrar Ejemplo</button>
            <div class="flashcard-example">{flashcard['ejemplo']}</div>
"""
                
            html += """        </div>
    </div>
"""
            
        html += """    <script>
        function toggleAnswer(button) {
            const answer = button.nextElementSibling;
            if (answer.style.display === "block") {
                answer.style.display = "none";
                button.textContent = "Mostrar Respuesta";
            } else {
                answer.style.display = "block";
                button.textContent = "Ocultar Respuesta";
            }
        }
        
        function toggleExample(button) {
            const example = button.nextElementSibling;
            if (example.style.display === "block") {
                example.style.display = "none";
                button.textContent = "Mostrar Ejemplo";
            } else {
                example.style.display = "block";
                button.textContent = "Ocultar Ejemplo";
            }
        }
    </script>
</body>
</html>"""
        
        return html
    
    def generar_pdf(self, flashcards):
        """Genera flashcards en formato PDF."""
        # Para generar PDF, primero generamos HTML y luego lo convertimos
        # Esto requeriría una biblioteca externa como weasyprint o pdfkit
        print("Error: La generación de PDF no está implementada en este ejemplo.")
        print("Por favor, use otro formato de salida.")
        sys.exit(1)
    
    def generar(self, archivo_salida=None):
        """Genera las flashcards en el formato especificado y las guarda o muestra."""
        # Seleccionar flashcards
        flashcards = self.seleccionar_flashcards()
        
        # Generar contenido según el formato
        if self.formato == "txt":
            output = self.generar_txt(flashcards)
        elif self.formato == "csv":
            output = self.generar_csv(flashcards)
        elif self.formato == "anki":
            output = self.generar_anki(flashcards)
        elif self.formato == "html":
            output = self.generar_html(flashcards)
        elif self.formato == "pdf":
            output = self.generar_pdf(flashcards)
        else:
            print(f"Error: Formato '{self.formato}' no soportado.")
            sys.exit(1)
        
        # Guardar o mostrar el resultado
        if archivo_salida:
            try:
                with open(archivo_salida, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"Flashcards guardadas en: {archivo_salida}")
            except Exception as e:
                print(f"Error al guardar las flashcards: {e}")
        else:
            print(output)
            
        return len(flashcards)
    
def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Herramienta para Generar Flashcards de Estudio para Certificaciones de Ciberseguridad')
    parser.add_argument('--certificacion', required=True, choices=['cissp', 'cism', 'ceh', 'itil'],
                        help='Certificación para la que se generarán las flashcards')
    parser.add_argument('--dominio', help='Dominio específico para generar flashcards')
    parser.add_argument('--formato', choices=['txt', 'csv', 'anki', 'html', 'pdf'], default='txt',
                        help='Formato de salida de las flashcards')
    parser.add_argument('--cantidad', type=int, help='Número de flashcards a generar')
    parser.add_argument('--salida', help='Archivo para guardar las flashcards')
    parser.add_argument('--incluir_ejemplos', action='store_true',
                        help='Incluir ejemplos prácticos en las flashcards')
    
    args = parser.parse_args()
    
    # Crear generador de flashcards
    generador = GeneradorFlashcards(
        certificacion=args.certificacion,
        dominio=args.dominio,
        formato=args.formato,
        cantidad=args.cantidad,
        incluir_ejemplos=args.incluir_ejemplos
    )
    
    # Generar flashcards
    num_flashcards = generador.generar(args.salida)
    
    print(f"Se generaron {num_flashcards} flashcards para la certificación {args.certificacion}.")
    
if __name__ == "__main__":
    main()

