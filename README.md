dependences:
pip install paramiko
execute:
python ssh_conn.py


Este script es una herramienta automatizada para la gestión de conexiones SSH y la ejecución de comandos tanto en máquinas remotas como locales. Está diseñado para facilitar tareas como la encriptación/desencriptación de archivos, la transferencia de archivos, la visualización de directorios, y la verificación de privilegios en una máquina remota. También tiene la capacidad de ejecutar comandos en la consola local de Windows, aunque esta función está comentada en el código.

Funciones Principales
Conexión SSH desde un archivo de credenciales:

ssh_connect_from_file(file_path, timeout=1): Establece conexiones SSH iterando sobre una lista de credenciales almacenadas en un archivo. Despliega un menú interactivo con opciones para ejecutar diferentes comandos y tareas en la máquina remota.
Generación de clave de encriptación:

generate_key(): Genera una clave simétrica utilizando la librería cryptography y la guarda en un archivo.
Listado y acceso a directorios remotos:

print_directories(client): Lista los directorios y archivos en el directorio actual de la máquina remota.
access_directory(client, path): Accede y muestra el contenido de un directorio específico en la máquina remota.
Transferencia de archivos:

transfer_file(client, local_path, password): Transfiere archivos desde la máquina local a la máquina remota, ajustando los permisos del archivo transferido.
Encriptación y desencriptación de archivos:

encrypt_files(client, path_to_encrypt): Ejecuta un script remoto para encriptar archivos o directorios en la máquina remota.
decrypt_files(client, path_to_decrypt): Ejecuta un script remoto para desencriptar archivos o directorios en la máquina remota.
Ejecución de comandos remotos:

execute_remote_command(client): Permite ejecutar comandos en la máquina remota e imprime la salida en tiempo real.
Verificación de privilegios en la máquina remota:

check_remote_privileges(client): Verifica si el usuario tiene privilegios root en la máquina remota y ejecuta comandos con esos privilegios si es posible.
(Comentado) Ejecución de comandos locales:

execute_local_command(): Ejecuta comandos en la consola local de Windows (esta función está comentada en el código).
