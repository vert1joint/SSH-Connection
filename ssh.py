import paramiko
import socket
import time

def ssh_connect_from_file(file_path, timeout=7):
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

