from cryptography.fernet import Fernet
import os
import sys

def cargar_key():
    try:
        with open('/tmp/encryption_key.key', 'rb') as key_file:
            key = key_file.read()
        print(f"Clave cargada: {key}")
        return key
    except FileNotFoundError:
        print("Error: No se encontró el archivo de clave.")
        return None

def decrypt(items, key):
    f = Fernet(key)
    for item in items:
        try:
            with open(item, 'rb') as file:
                encrypted_data = file.read()
            decrypted_data = f.decrypt(encrypted_data)
            with open(item, 'wb') as file:
                file.write(decrypted_data)
            print(f"Archivo desencriptado: {item}")
        except Exception as e:
            print(f"Error al desencriptar {item}: {str(e)}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Error: Se requiere la ruta del directorio a desencriptar.")
        sys.exit(1)

    path_to_decrypt = sys.argv[1]

    if not os.path.exists(path_to_decrypt):
        print("La ruta especificada no existe.")
        sys.exit(1)

    if not os.path.isdir(path_to_decrypt):
        print("La ruta especificada no es un directorio.")
        sys.exit(1)

    items = os.listdir(path_to_decrypt)
    full_path = [os.path.join(path_to_decrypt, item) for item in items if os.path.isfile(os.path.join(path_to_decrypt, item)) and item != 'readme.txt']

    key = cargar_key()
    if key:
        decrypt(full_path, key)
        print("Proceso de desencriptación completado.")
    else:
        print("No se pudo cargar la clave. Desencriptación cancelada.")

    readme_path = os.path.join(path_to_decrypt, 'readme.txt')
    if os.path.exists(readme_path):
        os.remove(readme_path)
        print("Archivo readme.txt eliminado.")