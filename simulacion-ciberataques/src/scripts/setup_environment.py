#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para configurar un entorno de simulación de ciberataques.

Este script configura un entorno controlado para la simulación de ciberataques,
incluyendo la creación de máquinas virtuales, configuración de redes, instalación
de herramientas y preparación de escenarios de ataque.

Uso:
    python setup_environment.py --config <archivo_configuracion>
    
Opciones:
    --config ARCHIVO     Archivo YAML con la configuración del entorno
    --verbose            Mostrar información detallada durante la ejecución
    --dry-run            Mostrar acciones sin ejecutarlas
    --force              Forzar la recreación del entorno si ya existe
"""

import argparse
import logging
import os
import subprocess
import sys
import time
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('setup_environment')

class EnvironmentSetup:
    """Clase para configurar el entorno de simulación de ciberataques."""
    
    def __init__(self, config_file: str, verbose: bool = False, dry_run: bool = False, force: bool = False):
        """
        Inicializa la configuración del entorno.
        
        Args:
            config_file: Ruta al archivo de configuración YAML
            verbose: Si se debe mostrar información detallada
            dry_run: Si se deben mostrar acciones sin ejecutarlas
            force: Si se debe forzar la recreación del entorno
        """
        self.config_file = config_file
        self.verbose = verbose
        self.dry_run = dry_run
        self.force = force
        self.config = {}
        
        if verbose:
            logger.setLevel(logging.DEBUG)
            
        self._load_config()
        
    def _load_config(self) -> None:
        """Carga la configuración desde el archivo YAML."""
        try:
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.debug(f"Configuración cargada desde {self.config_file}")
        except FileNotFoundError:
            logger.error(f"Archivo de configuración no encontrado: {self.config_file}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Error al parsear el archivo YAML: {e}")
            sys.exit(1)
            
    def _run_command(self, command: List[str], cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        """
        Ejecuta un comando del sistema.
        
        Args:
            command: Lista con el comando y sus argumentos
            cwd: Directorio de trabajo para el comando
            
        Returns:
            Resultado de la ejecución del comando
        """
        cmd_str = ' '.join(command)
        logger.debug(f"Ejecutando: {cmd_str}")
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Comando: {cmd_str}")
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                check=True,
                capture_output=True,
                text=True
            )
            if self.verbose:
                logger.debug(f"Salida: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Error al ejecutar comando: {cmd_str}")
            logger.error(f"Código de salida: {e.returncode}")
            logger.error(f"Salida de error: {e.stderr}")
            raise
            
    def check_prerequisites(self) -> bool:
        """
        Verifica que se cumplan los prerrequisitos para la configuración.
        
        Returns:
            True si se cumplen todos los prerrequisitos, False en caso contrario
        """
        logger.info("Verificando prerrequisitos...")
        
        # Verificar que se ejecuta como root o con sudo
        if os.geteuid() != 0 and not self.dry_run:
            logger.error("Este script debe ejecutarse como root o con sudo")
            return False
            
        # Verificar herramientas requeridas
        required_tools = ['docker', 'vagrant', 'virtualbox', 'ansible']
        missing_tools = []
        
        for tool in required_tools:
            try:
                self._run_command(['which', tool])
            except subprocess.CalledProcessError:
                missing_tools.append(tool)
                
        if missing_tools:
            logger.error(f"Herramientas requeridas no encontradas: {', '.join(missing_tools)}")
            logger.error("Por favor, instale las herramientas faltantes e intente nuevamente")
            return False
            
        # Verificar espacio en disco
        try:
            result = self._run_command(['df', '-h', '--output=avail', '/'])
            available = result.stdout.strip().split('\n')[1]
            logger.debug(f"Espacio disponible: {available}")
            
            # Extraer el número y convertir a GB
            if 'G' in available:
                available_gb = float(available.replace('G', ''))
                if available_gb < 20:  # Requerir al menos 20GB
                    logger.warning(f"Espacio en disco bajo: {available_gb}GB. Se recomiendan al menos 20GB.")
        except Exception as e:
            logger.warning(f"No se pudo verificar el espacio en disco: {e}")
            
        logger.info("Todos los prerrequisitos cumplidos")
        return True
        
    def setup_network(self) -> bool:
        """
        Configura la red para el entorno de simulación.
        
        Returns:
            True si la configuración fue exitosa, False en caso contrario
        """
        logger.info("Configurando red para el entorno de simulación...")
        
        network_config = self.config.get('network', {})
        network_name = network_config.get('name', 'cyberattack_sim')
        subnet = network_config.get('subnet', '192.168.56.0/24')
        
        try:
            # Crear red Docker
            self._run_command([
                'docker', 'network', 'create',
                '--subnet', subnet,
                network_name
            ])
            
            # Configurar reglas de firewall si es necesario
            if network_config.get('isolate', True):
                logger.info("Configurando reglas de firewall para aislar la red...")
                # Aquí irían comandos para configurar iptables o ufw
                
            logger.info(f"Red {network_name} configurada correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al configurar la red: {e}")
            return False
            
    def setup_virtual_machines(self) -> bool:
        """
        Configura las máquinas virtuales para el entorno de simulación.
        
        Returns:
            True si la configuración fue exitosa, False en caso contrario
        """
        logger.info("Configurando máquinas virtuales...")
        
        vms = self.config.get('virtual_machines', [])
        if not vms:
            logger.warning("No se encontraron definiciones de máquinas virtuales en la configuración")
            return True
            
        # Crear directorio para Vagrantfile
        vagrant_dir = Path(self.config.get('workspace_dir', '.')) / 'vagrant'
        os.makedirs(vagrant_dir, exist_ok=True)
        
        # Generar Vagrantfile
        vagrantfile_content = self._generate_vagrantfile(vms)
        vagrantfile_path = vagrant_dir / 'Vagrantfile'
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Se generaría el siguiente Vagrantfile en {vagrantfile_path}:")
            logger.info(vagrantfile_content)
        else:
            with open(vagrantfile_path, 'w') as f:
                f.write(vagrantfile_content)
                
        # Iniciar las máquinas virtuales
        try:
            self._run_command(['vagrant', 'up'], cwd=str(vagrant_dir))
            logger.info("Máquinas virtuales configuradas correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al configurar las máquinas virtuales: {e}")
            return False
            
    def _generate_vagrantfile(self, vms: List[Dict[str, Any]]) -> str:
        """
        Genera el contenido del Vagrantfile para las máquinas virtuales.
        
        Args:
            vms: Lista de configuraciones de máquinas virtuales
            
        Returns:
            Contenido del Vagrantfile
        """
        vagrantfile = [
            '# -*- mode: ruby -*-',
            '# vi: set ft=ruby :',
            '',
            'Vagrant.configure("2") do |config|'
        ]
        
        for vm in vms:
            name = vm.get('name', 'default')
            box = vm.get('box', 'ubuntu/focal64')
            ip = vm.get('ip', '')
            memory = vm.get('memory', 1024)
            cpus = vm.get('cpus', 1)
            provisioning = vm.get('provisioning', [])
            
            vagrantfile.extend([
                f'  config.vm.define "{name}" do |{name}|',
                f'    {name}.vm.box = "{box}"',
                f'    {name}.vm.hostname = "{name}"'
            ])
            
            if ip:
                vagrantfile.append(f'    {name}.vm.network "private_network", ip: "{ip}"')
                
            vagrantfile.extend([
                f'    {name}.vm.provider "virtualbox" do |vb|',
                f'      vb.memory = {memory}',
                f'      vb.cpus = {cpus}',
                '    end'
            ])
            
            # Agregar provisioning
            for provision in provisioning:
                prov_type = provision.get('type', '')
                if prov_type == 'shell':
                    script = provision.get('script', '')
                    inline = provision.get('inline', '')
                    
                    if script:
                        vagrantfile.append(f'    {name}.vm.provision "shell", path: "{script}"')
                    elif inline:
                        inline_escaped = inline.replace('"', '\\"')
                        vagrantfile.append(f'    {name}.vm.provision "shell", inline: "{inline_escaped}"')
                elif prov_type == 'ansible':
                    playbook = provision.get('playbook', '')
                    if playbook:
                        vagrantfile.append(f'    {name}.vm.provision "ansible" do |ansible|')
                        vagrantfile.append(f'      ansible.playbook = "{playbook}"')
                        vagrantfile.append('    end')
                        
            vagrantfile.append('  end')
            
        vagrantfile.append('end')
        return '\n'.join(vagrantfile)
        
    def install_tools(self) -> bool:
        """
        Instala las herramientas necesarias para la simulación de ciberataques.
        
        Returns:
            True si la instalación fue exitosa, False en caso contrario
        """
        logger.info("Instalando herramientas para simulación de ciberataques...")
        
        tools = self.config.get('tools', [])
        if not tools:
            logger.warning("No se encontraron herramientas para instalar en la configuración")
            return True
            
        for tool in tools:
            name = tool.get('name', '')
            install_method = tool.get('install_method', '')
            
            if not name or not install_method:
                continue
                
            logger.info(f"Instalando {name}...")
            
            try:
                if install_method == 'apt':
                    packages = tool.get('packages', [])
                    if packages:
                        self._run_command(['apt-get', 'update'])
                        self._run_command(['apt-get', 'install', '-y'] + packages)
                elif install_method == 'pip':
                    packages = tool.get('packages', [])
                    if packages:
                        self._run_command(['pip', 'install'] + packages)
                elif install_method == 'git':
                    repo = tool.get('repo', '')
                    dest = tool.get('destination', '')
                    if repo and dest:
                        self._run_command(['git', 'clone', repo, dest])
                        
                        # Ejecutar comandos post-instalación si existen
                        post_install = tool.get('post_install', [])
                        for cmd in post_install:
                            self._run_command(cmd.split(), cwd=dest)
                elif install_method == 'docker':
                    image = tool.get('image', '')
                    if image:
                        self._run_command(['docker', 'pull', image])
                elif install_method == 'custom':
                    commands = tool.get('commands', [])
                    for cmd in commands:
                        self._run_command(cmd.split())
            except Exception as e:
                logger.error(f"Error al instalar {name}: {e}")
                if tool.get('required', False):
                    return False
                    
        logger.info("Herramientas instaladas correctamente")
        return True
        
    def configure_scenarios(self) -> bool:
        """
        Configura los escenarios de ataque para la simulación.
        
        Returns:
            True si la configuración fue exitosa, False en caso contrario
        """
        logger.info("Configurando escenarios de ataque...")
        
        scenarios = self.config.get('scenarios', [])
        if not scenarios:
            logger.warning("No se encontraron escenarios para configurar en la configuración")
            return True
            
        scenarios_dir = Path(self.config.get('workspace_dir', '.')) / 'escenarios'
        os.makedirs(scenarios_dir, exist_ok=True)
        
        for scenario in scenarios:
            name = scenario.get('name', '')
            description = scenario.get('description', '')
            techniques = scenario.get('techniques', [])
            
            if not name:
                continue
                
            logger.info(f"Configurando escenario: {name}")
            
            # Crear archivo YAML para el escenario
            scenario_file = scenarios_dir / f"{name.lower().replace(' ', '_')}.yaml"
            
            scenario_data = {
                'name': name,
                'description': description,
                'techniques': techniques,
                'targets': scenario.get('targets', []),
                'prerequisites': scenario.get('prerequisites', []),
                'steps': scenario.get('steps', [])
            }
            
            if self.dry_run:
                logger.info(f"[DRY RUN] Se generaría el archivo de escenario en {scenario_file}")
            else:
                with open(scenario_file, 'w') as f:
                    yaml.dump(scenario_data, f, default_flow_style=False)
                    
        logger.info("Escenarios configurados correctamente")
        return True
        
    def setup(self) -> bool:
        """
        Configura el entorno completo de simulación.
        
        Returns:
            True si la configuración fue exitosa, False en caso contrario
        """
        logger.info("Iniciando configuración del entorno de simulación...")
        
        # Verificar si el entorno ya existe
        workspace_dir = Path(self.config.get('workspace_dir', '.'))
        if workspace_dir.exists() and not self.force:
            logger.error(f"El directorio de trabajo {workspace_dir} ya existe. Use --force para recrearlo.")
            return False
            
        # Crear directorio de trabajo
        os.makedirs(workspace_dir, exist_ok=True)
        
        # Ejecutar pasos de configuración
        steps = [
            self.check_prerequisites,
            self.setup_network,
            self.setup_virtual_machines,
            self.install_tools,
            self.configure_scenarios
        ]
        
        for step in steps:
            if not step():
                logger.error("Configuración fallida")
                return False
                
        logger.info("Entorno de simulación configurado correctamente")
        return True
        
def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description='Configurar entorno de simulación de ciberataques')
    parser.add_argument('--config', required=True, help='Archivo YAML con la configuración del entorno')
    parser.add_argument('--verbose', action='store_true', help='Mostrar información detallada durante la ejecución')
    parser.add_argument('--dry-run', action='store_true', help='Mostrar acciones sin ejecutarlas')
    parser.add_argument('--force', action='store_true', help='Forzar la recreación del entorno si ya existe')
    
    args = parser.parse_args()
    
    setup = EnvironmentSetup(
        config_file=args.config,
        verbose=args.verbose,
        dry_run=args.dry_run,
        force=args.force
    )
    
    success = setup.setup()
    sys.exit(0 if success else 1)
    
if __name__ == "__main__":
    main()

