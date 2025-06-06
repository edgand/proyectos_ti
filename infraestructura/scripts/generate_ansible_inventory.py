#!/usr/bin/env python3
# Script para generar un inventario dinámico de Ansible a partir de la salida de Terraform

import json
import sys
import os

def generate_inventory(terraform_output_file, inventory_file):
    """
    Genera un inventario de Ansible a partir de la salida de Terraform.
    
    Args:
        terraform_output_file: Ruta al archivo JSON con la salida de Terraform
        inventory_file: Ruta al archivo de inventario de Ansible a generar
    """
    # Verificar que el archivo de salida de Terraform existe
    if not os.path.isfile(terraform_output_file):
        print(f"Error: El archivo {terraform_output_file} no existe")
        return False
    
    # Cargar la salida de Terraform
    try:
        with open(terraform_output_file, 'r') as f:
            terraform_output = json.load(f)
    except Exception as e:
        print(f"Error al cargar el archivo JSON: {e}")
        return False
    
    # Extraer información de las instancias
    try:
        instance_ids = terraform_output.get('app_instance_ids', {}).get('value', [])
        instance_public_ips = terraform_output.get('app_instance_public_ips', {}).get('value', [])
        instance_private_ips = terraform_output.get('app_instance_private_ips', {}).get('value', [])
        
        # Verificar que tenemos la misma cantidad de IDs, IPs públicas e IPs privadas
        if len(instance_ids) != len(instance_public_ips) or len(instance_ids) != len(instance_private_ips):
            print("Error: La cantidad de IDs, IPs públicas e IPs privadas no coincide")
            return False
        
        # Crear el contenido del inventario
        inventory_content = "# Inventario generado automáticamente a partir de la salida de Terraform\n\n"
        
        # Grupo de webservers
        inventory_content += "[webservers]\n"
        for i in range(len(instance_ids)):
            instance_id = instance_ids[i]
            public_ip = instance_public_ips[i]
            private_ip = instance_private_ips[i]
            inventory_content += f"web{i+1:02d} ansible_host={public_ip} private_ip={private_ip} instance_id={instance_id}\n"
        
        inventory_content += "\n"
        
        # Extraer información del balanceador de carga
        lb_dns_name = terraform_output.get('app_lb_dns_name', {}).get('value', '')
        
        # Grupo de loadbalancers
        if lb_dns_name:
            inventory_content += "[loadbalancers]\n"
            inventory_content += f"lb01 ansible_host={lb_dns_name}\n\n"
        
        # Grupo de all
        inventory_content += "[all:children]\n"
        inventory_content += "webservers\n"
        if lb_dns_name:
            inventory_content += "loadbalancers\n"
        
        inventory_content += "\n"
        
        # Variables para todos los hosts
        inventory_content += "[all:vars]\n"
        inventory_content += "ansible_user=ubuntu\n"
        inventory_content += "ansible_ssh_private_key_file=~/.ssh/id_rsa\n"
        inventory_content += "ansible_become=yes\n"
        inventory_content += "ansible_become_method=sudo\n"
        
        # Escribir el inventario
        try:
            # Asegurarse de que el directorio existe
            os.makedirs(os.path.dirname(inventory_file), exist_ok=True)
            
            with open(inventory_file, 'w') as f:
                f.write(inventory_content)
            
            print(f"Inventario generado correctamente en {inventory_file}")
            return True
        except Exception as e:
            print(f"Error al escribir el archivo de inventario: {e}")
            return False
    
    except Exception as e:
        print(f"Error al procesar la salida de Terraform: {e}")
        return False

if __name__ == "__main__":
    # Verificar argumentos
    if len(sys.argv) != 3:
        print("Uso: python3 generate_ansible_inventory.py <terraform_output_file> <inventory_file>")
        sys.exit(1)
    
    terraform_output_file = sys.argv[1]
    inventory_file = sys.argv[2]
    
    # Generar inventario
    if not generate_inventory(terraform_output_file, inventory_file):
        sys.exit(1)
    
    sys.exit(0)

