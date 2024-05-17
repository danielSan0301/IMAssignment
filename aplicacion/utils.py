from django.core.mail import send_mail, EmailMessage
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def enviarcorreo(email:str,subject:str, body:str, attach_file:str):
    #generar el correo
    original_email = 'evaristogarcia288@gmail.com'
    email = EmailMessage(
        subject,
        body,
        original_email,
        [email],
    )
    if attach_file:
        email.attach_file(attach_file)
    email.send(fail_silently= False)
        
# Función que representa el contador
def contador():
    tiempo_restante = 60
    while tiempo_restante > 0:
        print("Tiempo restante:", tiempo_restante, "segundos")
        time.sleep(1)  # Esperar 1 segundo
        tiempo_restante -= 1
    print("El tiempo ha expirado.")
    

def dividir_lista(lista, tamaño_sublista):
    sublistas = []
    for i in range(0, len(lista), tamaño_sublista):
        sublistas.append(lista[i:i+tamaño_sublista])

    return sublistas


def cifrar(key:bytes, plaintext: bytes):
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    iv = cipher.iv
    return ciphertext, iv

def descifrar(ciphertext:bytes, key:bytes, iv:bytes):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext