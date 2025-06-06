#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para ejecutar un escenario de simulación de ciberataques.

Este script ejecuta un escenario de simulación de ciberataques definido en un archivo YAML,
siguiendo las técnicas y pasos especificados en el marco MITRE ATT&CK.

Uso:
    python run_scenario.py --scenario <archivo_escenario>
    
Opciones:
    --scenario ARCHIVO   Archivo YAML con la definición del escenario
    --verbose            Mostrar información detallada durante la ejecución
    --dry-run            Mostrar acciones sin ejecutarlas
    --output DIRECTORIO  Directorio para guardar los resultados
"""

import argparse
import datetime
import json
import logging
import os
import subprocess
import sys
import time
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('run_scenario')

class ScenarioRunner:
    """Clase para ejecutar escenarios de simulación de ciberataques."""
    
    def __init__(self, scenario_file: str, verbose: bool = False, dry_run: bool = False, output_dir: Optional[str] = None):
        """
        Inicializa el ejecutor de escenarios.
        
        Args:
            scenario_file: Ruta al archivo YAML con la definición del escenario
            verbose: Si se debe mostrar información detallada
            dry_run: Si se deben mostrar acciones sin ejecutarlas
            output_dir: Directorio para guardar los resultados
        """
        self.scenario_file = scenario_file
        self.verbose = verbose
        self.dry_run = dry_run
        self.output_dir = output_dir or f"results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.scenario = {}
        self.results = {
            "scenario": "",
            "start_time": "",
            "end_time": "",
            "status": "not_started",
            "techniques": [],
            "steps": []
        }
        
        if verbose:
            logger.setLevel(logging.DEBUG)
            
        self._load_scenario()
        
    def _load_scenario(self) -> None:
        """Carga el escenario desde el archivo YAML."""
        try:
            with open(self.scenario_file, 'r') as f:
                self.scenario = yaml.safe_load(f)
            logger.debug(f"Escenario cargado desde {self.scenario_file}")
            
            # Actualizar información básica en resultados
            self.results["scenario"] = self.scenario.get("name", "Unknown")
            
        except FileNotFoundError:
            logger.error(f"Archivo de escenario no encontrado: {self.scenario_file}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error al parsear el archivo YAML: {e}")
            sys.exit(1)
            
    def _run_command(self, command: List[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
        """
        Ejecuta un comando del sistema.
        
        Args:
            command: Lista con el comando y sus argumentos
            cwd: Directorio de trabajo para el comando
            
        Returns:
            Tupla con (código de salida, salida estándar, salida de error)
        """
        cmd_str = ' '.join(command)
        logger.debug(f"Ejecutando: {cmd_str}")
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Comando: {cmd_str}")
            return 0, "[DRY RUN] Salida simulada", ""
        
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if self.verbose:
                logger.debug(f"Salida: {stdout}")
                if stderr:
                    logger.debug(f"Error: {stderr}")
                    
            return process.returncode, stdout, stderr
        except Exception as e:
            logger.error(f"Error al ejecutar comando: {cmd_str}")
            logger.error(f"Excepción: {e}")
            return -1, "", str(e)
            
    def check_prerequisites(self) -> bool:
        """
        Verifica que se cumplan los prerrequisitos para ejecutar el escenario.
        
        Returns:
            True si se cumplen todos los prerrequisitos, False en caso contrario
        """
        logger.info("Verificando prerrequisitos para el escenario...")
        
        prerequisites = self.scenario.get("prerequisites", [])
        if not prerequisites:
            logger.info("No se especificaron prerrequisitos para este escenario")
            return True
            
        all_met = True
        
        for prereq in prerequisites:
            prereq_type = prereq.get("type", "")
            prereq_value = prereq.get("value", "")
            
            if not prereq_type or not prereq_value:
                continue
                
            logger.debug(f"Verificando prerrequisito: {prereq_type} - {prereq_value}")
            
            if prereq_type == "command":
                returncode, _, _ = self._run_command(["which", prereq_value])
                if returncode != 0:
                    logger.error(f"Prerrequisito no cumplido: comando '{prereq_value}' no encontrado")
                    all_met = False
            elif prereq_type == "file":
                if not os.path.exists(prereq_value):
                    logger.error(f"Prerrequisito no cumplido: archivo '{prereq_value}' no encontrado")
                    all_met = False
            elif prereq_type == "directory":
                if not os.path.isdir(prereq_value):
                    logger.error(f"Prerrequisito no cumplido: directorio '{prereq_value}' no encontrado")
                    all_met = False
            elif prereq_type == "environment":
                if prereq_value not in os.environ:
                    logger.error(f"Prerrequisito no cumplido: variable de entorno '{prereq_value}' no definida")
                    all_met = False
            elif prereq_type == "python_module":
                try:
                    __import__(prereq_value)
                except ImportError:
                    logger.error(f"Prerrequisito no cumplido: módulo Python '{prereq_value}' no instalado")
                    all_met = False
                    
        if all_met:
            logger.info("Todos los prerrequisitos cumplidos")
        else:
            logger.error("No se cumplen todos los prerrequisitos para ejecutar este escenario")
            
        return all_met
        
    def prepare_environment(self) -> bool:
        """
        Prepara el entorno para la ejecución del escenario.
        
        Returns:
            True si la preparación fue exitosa, False en caso contrario
        """
        logger.info("Preparando entorno para la ejecución del escenario...")
        
        # Crear directorio de salida
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            logger.debug(f"Directorio de salida creado: {self.output_dir}")
        except Exception as e:
            logger.error(f"Error al crear directorio de salida: {e}")
            return False
            
        # Preparar objetivos
        targets = self.scenario.get("targets", [])
        if not targets:
            logger.warning("No se especificaron objetivos para este escenario")
            return True
            
        for target in targets:
            target_type = target.get("type", "")
            target_value = target.get("value", "")
            
            if not target_type or not target_value:
                continue
                
            logger.info(f"Preparando objetivo: {target_type} - {target_value}")
            
            if target_type == "ip":
                # Verificar conectividad
                returncode, _, _ = self._run_command(["ping", "-c", "1", target_value])
                if returncode != 0:
                    logger.warning(f"No se puede alcanzar el objetivo: {target_value}")
            elif target_type == "docker":
                # Verificar si el contenedor está en ejecución
                returncode, stdout, _ = self._run_command(["docker", "ps", "-q", "-f", f"name={target_value}"])
                if not stdout.strip():
                    logger.warning(f"El contenedor Docker '{target_value}' no está en ejecución")
            elif target_type == "vm":
                # Verificar si la máquina virtual está en ejecución
                returncode, stdout, _ = self._run_command(["vagrant", "status", target_value])
                if "running" not in stdout.lower():
                    logger.warning(f"La máquina virtual '{target_value}' no está en ejecución")
                    
        logger.info("Entorno preparado correctamente")
        return True
        
    def execute_technique(self, technique: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta una técnica de ataque específica.
        
        Args:
            technique: Diccionario con la definición de la técnica
            
        Returns:
            Diccionario con los resultados de la ejecución
        """
        technique_id = technique.get("id", "unknown")
        technique_name = technique.get("name", "Unknown Technique")
        
        logger.info(f"Ejecutando técnica: {technique_name} ({technique_id})")
        
        result = {
            "id": technique_id,
            "name": technique_name,
            "status": "failed",
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": "",
            "output": "",
            "error": ""
        }
        
        commands = technique.get("commands", [])
        if not commands:
            logger.warning(f"No se especificaron comandos para la técnica {technique_id}")
            result["error"] = "No commands specified"
            result["end_time"] = datetime.datetime.now().isoformat()
            return result
            
        success = True
        outputs = []
        
        for cmd in commands:
            if isinstance(cmd, str):
                cmd_parts = cmd.split()
            else:
                cmd_parts = cmd
                
            returncode, stdout, stderr = self._run_command(cmd_parts)
            
            cmd_result = {
                "command": ' '.join(cmd_parts),
                "returncode": returncode,
                "stdout": stdout,
                "stderr": stderr
            }
            
            outputs.append(cmd_result)
            
            if returncode != 0:
                success = False
                
        result["status"] = "success" if success else "failed"
        result["output"] = outputs
        result["end_time"] = datetime.datetime.now().isoformat()
        
        return result
        
    def execute_step(self, step: Dict[str, Any], step_index: int) -> Dict[str, Any]:
        """
        Ejecuta un paso del escenario.
        
        Args:
            step: Diccionario con la definición del paso
            step_index: Índice del paso en el escenario
            
        Returns:
            Diccionario con los resultados de la ejecución
        """
        step_name = step.get("name", f"Step {step_index + 1}")
        
        logger.info(f"Ejecutando paso: {step_name}")
        
        result = {
            "name": step_name,
            "status": "failed",
            "start_time": datetime.datetime.now().isoformat(),
            "end_time": "",
            "techniques": []
        }
        
        techniques = step.get("techniques", [])
        if not techniques:
            logger.warning(f"No se especificaron técnicas para el paso {step_name}")
            result["end_time"] = datetime.datetime.now().isoformat()
            return result
            
        success = True
        
        for technique in techniques:
            technique_result = self.execute_technique(technique)
            result["techniques"].append(technique_result)
            
            if technique_result["status"] != "success":
                success = False
                
            # Pausa entre técnicas
            time.sleep(1)
            
        result["status"] = "success" if success else "failed"
        result["end_time"] = datetime.datetime.now().isoformat()
        
        return result
        
    def run(self) -> bool:
        """
        Ejecuta el escenario completo.
        
        Returns:
            True si la ejecución fue exitosa, False en caso contrario
        """
        logger.info(f"Iniciando ejecución del escenario: {self.scenario.get('name', 'Unknown')}")
        
        self.results["start_time"] = datetime.datetime.now().isoformat()
        self.results["status"] = "running"
        
        # Verificar prerrequisitos
        if not self.check_prerequisites():
            self.results["status"] = "failed"
            self.results["end_time"] = datetime.datetime.now().isoformat()
            self._save_results()
            return False
            
        # Preparar entorno
        if not self.prepare_environment():
            self.results["status"] = "failed"
            self.results["end_time"] = datetime.datetime.now().isoformat()
            self._save_results()
            return False
            
        # Ejecutar pasos
        steps = self.scenario.get("steps", [])
        if not steps:
            logger.warning("No se especificaron pasos para este escenario")
            self.results["status"] = "completed"
            self.results["end_time"] = datetime.datetime.now().isoformat()
            self._save_results()
            return True
            
        success = True
        
        for i, step in enumerate(steps):
            step_result = self.execute_step(step, i)
            self.results["steps"].append(step_result)
            
            if step_result["status"] != "success":
                success = False
                if step.get("stop_on_failure", False):
                    logger.error(f"Paso {i+1} falló y está configurado para detener la ejecución")
                    break
                    
            # Pausa entre pasos
            time.sleep(2)
            
        # Recopilar técnicas ejecutadas
        all_techniques = []
        for step_result in self.results["steps"]:
            for technique_result in step_result.get("techniques", []):
                all_techniques.append({
                    "id": technique_result.get("id", ""),
                    "name": technique_result.get("name", ""),
                    "status": technique_result.get("status", "")
                })
                
        self.results["techniques"] = all_techniques
        self.results["status"] = "completed" if success else "failed"
        self.results["end_time"] = datetime.datetime.now().isoformat()
        
        # Guardar resultados
        self._save_results()
        
        logger.info(f"Ejecución del escenario completada con estado: {self.results['status']}")
        return success
        
    def _save_results(self) -> None:
        """Guarda los resultados de la ejecución en un archivo JSON."""
        if self.dry_run:
            logger.info("[DRY RUN] Se guardarían los resultados")
            return
            
        try:
            results_file = os.path.join(self.output_dir, "results.json")
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.debug(f"Resultados guardados en {results_file}")
        except Exception as e:
            logger.error(f"Error al guardar resultados: {e}")
            
def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Ejecutar escenario de simulación de ciberataques')
    parser.add_argument('--scenario', required=True, help='Archivo YAML con la definición del escenario')
    parser.add_argument('--verbose', action='store_true', help='Mostrar información detallada durante la ejecución')
    parser.add_argument('--dry-run', action='store_true', help='Mostrar acciones sin ejecutarlas')
    parser.add_argument('--output', help='Directorio para guardar los resultados')
    
    args = parser.parse_args()
    
    runner = ScenarioRunner(
        scenario_file=args.scenario,
        verbose=args.verbose,
        dry_run=args.dry_run,
        output_dir=args.output
    )
    
    success = runner.run()
    sys.exit(0 if success else 1)
    
if __name__ == "__main__":
    main()

