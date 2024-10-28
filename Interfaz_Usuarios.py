import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import face_recognition
import mysql.connector
import pickle

# Database connection
conexion = mysql.connector.connect(
    host="localhost", user="root", password="221102", database="db_proyecto"
)
cursor = conexion.cursor()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestion de estudiantes")
        self.geometry("400x300")
        
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.frames = {}
        for F in (MainMenu, IngresoFrame, BusquedaFrame, EliminarFrame, ActualizarEstatusFrame):
            frame = F(self.main_frame, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(MainMenu)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class MainMenu(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        ttk.Button(self, text="Ingresar Alumno", command=lambda: self.controller.show_frame(IngresoFrame)).pack(pady=10)
        ttk.Button(self, text="Buscar alumno", command=lambda: self.controller.show_frame(BusquedaFrame)).pack(pady=10)
        ttk.Button(self, text="Eliminar alumno", command=lambda: self.controller.show_frame(EliminarFrame)).pack(pady=10)
        ttk.Button(self, text="Actualizar Estatus", command=lambda: self.controller.show_frame(ActualizarEstatusFrame)).pack(pady=10)
class IngresoFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Ingreso del alumno").pack(pady=10)
        
        fields = [("Expediente", "expediente"), ("Nombre", "nombre"), ("Apellido", "apellido")]
        self.entries = {}
        for label, field in fields:
            frame = ttk.Frame(self)
            frame.pack(pady=5)
            ttk.Label(frame, text=f"{label}:").pack(side=tk.LEFT)
            self.entries[field] = ttk.Entry(frame)
            self.entries[field].pack(side=tk.LEFT)
        
        ttk.Button(self, text="Consultar", command=self.consultar).pack(pady=10)
        ttk.Button(self, text="Volver", command=lambda: self.controller.show_frame(MainMenu)).pack(pady=10)

    def consultar(self):
        expediente = self.entries['expediente'].get()
        nombre = self.entries['nombre'].get()
        apellido = self.entries['apellido'].get()

        cursor.execute("SELECT * FROM alumnos WHERE EXP = %s", (expediente,))
        if cursor.fetchone():
            messagebox.showwarning("Advertencia", "Estudiante ya existente en la base de datos")
            return

        self.capturar_imagen(expediente, nombre, apellido)

    def capturar_imagen(self, expediente, nombre, apellido):
        captura = cv2.VideoCapture(0)
        while captura.isOpened():
            ret, frame = captura.read()
            cv2.imshow('Frame', frame)
            
            key = cv2.waitKey(1)
            if key == 27:  # Esc
                break
            elif key == ord('q'):
                codigoCara = face_recognition.face_encodings(frame)
                if len(codigoCara) == 1:
                    self.guardar_alumno(expediente, nombre, apellido, codigoCara[0], frame)
                    break
                else:
                    messagebox.showwarning("Advertencia", "No se detectó una cara o se detectaron múltiples caras")

        captura.release()
        cv2.destroyAllWindows()

    def guardar_alumno(self, expediente, nombre, apellido, codigoCara, frame):
        caraBin = pickle.dumps(codigoCara)
        cursor.execute("INSERT INTO alumnos (EXP, NOM, AP, codigo_facial) VALUES (%s, %s, %s, %s)",
                       (expediente, nombre, apellido, caraBin))
        conexion.commit()
        
        cv2.imwrite(f"C:/Users/Gabriel/Documents/Imagenes alumnos/{expediente}.jpg", frame)
        messagebox.showinfo("Éxito", "Alumno registrado correctamente")

class BusquedaFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Búsqueda de alumno").pack(pady=10)
        
        self.search_type = tk.StringVar()
        self.search_type.set("EXP")
        
        ttk.Radiobutton(self, text="Por número de expediente", variable=self.search_type, value="EXP").pack()
        ttk.Radiobutton(self, text="Por Nombre", variable=self.search_type, value="NOM").pack()
        ttk.Radiobutton(self, text="Por Apellido", variable=self.search_type, value="AP").pack()
        
        self.search_entry = ttk.Entry(self)
        self.search_entry.pack(pady=10)
        
        ttk.Button(self, text="Buscar", command=self.realizar_busqueda).pack(pady=10)
        ttk.Button(self, text="Volver", command=lambda: self.controller.show_frame(MainMenu)).pack(pady=10)

    def realizar_busqueda(self):
        field = self.search_type.get()
        valor = self.search_entry.get()
        cursor.execute(f"SELECT * FROM alumnos WHERE {field} = %s", (valor,))
        resultados = cursor.fetchall()
        if resultados:
            for resultado in resultados:
                messagebox.showinfo("Resultado", f"EXP: {resultado[0]}, NOM: {resultado[1]}, AP: {resultado[2]}")
        else:
            messagebox.showinfo("Resultado", "No se encontraron alumnos")

class EliminarFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Eliminar alumno").pack(pady=10)
        ttk.Label(self, text="Expediente del alumno a eliminar:").pack(pady=5)
        self.entry = ttk.Entry(self)
        self.entry.pack(pady=5)
        ttk.Button(self, text="Eliminar", command=self.eliminar_alumno).pack(pady=10)
        ttk.Button(self, text="Volver", command=lambda: self.controller.show_frame(MainMenu)).pack(pady=10)

    def eliminar_alumno(self):
        expediente = self.entry.get()
        cursor.execute("SELECT * FROM alumnos WHERE EXP = %s", (expediente,))
        if cursor.fetchone():
            cursor.execute("DELETE FROM alumnos WHERE EXP = %s", (expediente,))
            conexion.commit()
            messagebox.showinfo("Éxito", f"Se eliminó el alumno con expediente {expediente}")
        else:
            messagebox.showinfo("Resultado", "No se encontró el alumno")

class ActualizarEstatusFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Actualizar Estatus del Alumno").pack(pady=10)
        ttk.Label(self, text="Expediente del alumno:").pack(pady=5)
        self.expediente_entry = ttk.Entry(self)
        self.expediente_entry.pack(pady=5)
        
        ttk.Button(self, text="Activo", command=lambda: self.actualizar_estatus("Si")).pack(pady=5)
        ttk.Button(self, text="Inactivo", command=lambda: self.actualizar_estatus("No")).pack(pady=5)
        ttk.Button(self, text="Volver", command=lambda: self.controller.show_frame(MainMenu)).pack(pady=10)

    def actualizar_estatus(self, estatus):
        expediente = self.expediente_entry.get()
        if not expediente:
            messagebox.showwarning("Advertencia", "Por favor, ingrese un número de expediente.")
            return
        
        cursor.execute("SELECT * FROM alumnos WHERE EXP = %s", (expediente,))
        if cursor.fetchone():
            cursor.execute("UPDATE alumnos SET Estatus = %s WHERE EXP = %s", (estatus, expediente))
            conexion.commit()
            messagebox.showinfo("Éxito", f"Se actualizó el estatus del alumno con expediente {expediente} a {estatus}")
        else:
            messagebox.showinfo("Error", "No se encontró el alumno con ese expediente")

if __name__ == "__main__":
    app = App()
    app.mainloop()

# Cerrar la conexión a la base de datos al salir
conexion.close()