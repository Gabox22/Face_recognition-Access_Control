import face_recognition
import cv2
import mysql.connector
import pickle
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import serial
import time

# Configuración del puerto serial
ser = serial.Serial('COM3', 115200, timeout=1)  # Ajusta 'COM3' al puerto correcto de tu ESP32

def enviar_senal_led(estado):
    """
    Envía una señal serial al ESP32 para controlar un LED y el servo.
    
    :param estado: True para encender el LED y abrir el servo, False para apagarlos
    """
    try:
        if estado:
            ser.write(b'1')  # Envía '1' para encender el LED y abrir el servo
            print("Señal enviada para encender el LED y abrir el servo")
        else:
            ser.write(b'0')  # Envía '0' para apagar el LED y cerrar el servo
            print("Señal enviada para apagar el LED y cerrar el servo")
        time.sleep(0.1)  # Pequeña pausa para asegurar que se envíe la señal
    except serial.SerialException as e:
        print(f"Error al conectar con el ESP32: {e}")

# Configuración inicial
Tk().withdraw()  # Ocultar la ventana principal de Tkinter
capture = cv2.VideoCapture(0)  # Iniciar la captura de video

# Configuración de la conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="221102",
    database="db_proyecto"
)
cursor = conexion.cursor(buffered=True)

# Obtener datos de alumnos de la base de datos
cursor.execute("SELECT * FROM alumnos")
datos = cursor.fetchall()

# Función para comparar caras
def comparar_caras(frame, datos):
    caras = face_recognition.face_locations(frame)
    if len(caras) == 0:
        return "Pon una cara"
    elif len(caras) > 1:
        return "Hay más de una cara"
    
    encoding_actual = face_recognition.face_encodings(frame, caras)[0]
    
    for fila in datos:
        codigo_cara_guardada = pickle.loads(fila[3])
        if not isinstance(codigo_cara_guardada, list):
            codigo_cara_guardada = [codigo_cara_guardada]
        
        if np.any(face_recognition.compare_faces(codigo_cara_guardada, encoding_actual)):
            if fila[4] == "Si":  # Asumiendo que la columna Estatus es la quinta columna (índice 4)
                enviar_senal_led(True)
                return f"Coincidencia encontrada: {fila[0]} {fila[1]} {fila[2]}"
            else:
                return "Estudiante inactivo"
    
    return "Sin coincidencias"

# Bucle principal de captura y procesamiento
while capture.isOpened():
    ret, frame = capture.read()
    if not ret:
        break
    
    cv2.imshow('Frame', frame)
    
    # Leer del puerto serial
    if ser.in_waiting > 0:
        received_data = ser.read().decode('ascii')
        if received_data == 'q':
            resultado = comparar_caras(frame, datos)
            print(resultado)
            if "Coincidencia encontrada" not in resultado:
                enviar_senal_led(False)
    
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # Tecla ESC
        enviar_senal_led(False)
        break

# Liberar recursos
capture.release()
cv2.destroyAllWindows()
conexion.close()
ser.close()