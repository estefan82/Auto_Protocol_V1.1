import customtkinter as ctk
import pyautogui
import keyboard
import time
import configparser
import os

CONFIG_FILE = "config.ini"

class MouseGridApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Auto Protocol V1")
        self.geometry("400x500")

        # Variables
        self.base_pos = None
        self.dy = None
        self.celdas = []

        # Configuración
        self.config = configparser.ConfigParser()
        self.cargar_config()

        if not self.config.has_section("APP"):
            self.config.add_section("APP")
            self.config["APP"]["cantidad"] = str(10)
            self.config["APP"]["option"] = "N/A"
            self.config["APP"]["delay"] = str(0.2)
            self.config["APP"]["posibles"] = "Si, No o N/A"
            with open(CONFIG_FILE, "w") as f:
                self.config.write(f)

        # Cargar valores siempre, ya exista o no la sección

        self.cantidad = self.config.getint("APP", "cantidad")
        self.option = self.config.get("APP", "option")
        self.delay = self.config.getfloat("APP", "delay")
        self.num_celdas = ctk.StringVar(value=str(self.cantidad))

        # UI
        self.label_info = ctk.CTkLabel(self, text="SHIFT = marcar base (usa calibración previa para offset)")
        self.label_info.pack(pady=10)

        # Mostrar offset actual
        self.label_offset = ctk.CTkLabel(self, text=self.get_offset_text())
        self.label_offset.pack(pady=5)

        # Frame principal centrado
        frame_central = ctk.CTkFrame(self)
        frame_central.pack(pady=20)

        # Configurar columnas (col0=labels, col1=entries/combobox)
        ancho_label = 100
        ancho_entry = 150

        # -------- Entry: Número de celdas --------
        lbl_celdas = ctk.CTkLabel(frame_central, text="Número de celdas:", width=ancho_label, anchor="e")
        lbl_celdas.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_celdas = ctk.CTkEntry(frame_central, width=ancho_entry, textvariable=self.num_celdas)
        self.entry_celdas.grid(row=0, column=1, padx=5, pady=5)

        # -------- Combo: Tecla --------
        lbl_tecla = ctk.CTkLabel(frame_central, text="Opción:", width=ancho_label, anchor="e")
        lbl_tecla.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.combo_tecla = ctk.CTkComboBox(frame_central, width=ancho_entry, values=["Si", "No", "N/A"])
        self.combo_tecla.grid(row=1, column=1, padx=5, pady=5)
        self.combo_tecla.set(self.option)

        # -------- Entry: Delay --------
        lbl_delay = ctk.CTkLabel(frame_central, text="Delay (ms):", width=ancho_label, anchor="e")
        lbl_delay.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.entry_delay = ctk.CTkEntry(frame_central, width=ancho_entry, placeholder_text="Tiempo (delay) en ms")
        self.entry_delay.grid(row=2, column=1, padx=5, pady=5)
        self.entry_delay.insert(0, self.delay)

        # -------- Botones (centrados debajo) --------
        self.btn_ir = ctk.CTkButton(self, text="Escribir en todas las celdas", command=self.escribir_en_todas, width=200)
        self.btn_ir.pack(pady=20)

        self.btn_borrar_base = ctk.CTkButton(self, text="Borrar Base", command=self.borrar_base, width=200)
        self.btn_borrar_base.pack(pady=5)

        self.btn_calibrar = ctk.CTkButton(self, text="Calibrar Offset", command=self.iniciar_calibracion, width=200)
        self.btn_calibrar.pack(pady=5)

        self.btn_reset_offset = ctk.CTkButton(self, text="Resetear Offset", command=self.resetear_offset, width=200)
        self.btn_reset_offset.pack(pady=5)


        # Bind shift
        keyboard.on_press_key("shift", self.marcar_base)

        # Estado de calibración
        self.calibrando = False
        self.temp_pos = None

    def get_offset_text(self):
        """Devuelve el texto que muestra el offset actual"""
        if self.dy:
            return f"Offset actual: dy={self.dy}"
        else:
            return "Offset no calibrado aún"

    def cargar_config(self):
        """Carga offset desde config.ini si existe"""
        if os.path.exists(CONFIG_FILE):
            self.config.read(CONFIG_FILE)
            if "GRID" in self.config and "dy" in self.config["GRID"]:
                self.dy = int(self.config["GRID"]["dy"])
                print(f"Offset cargado desde config.ini: dy={self.dy}")

    def set_config(self):
        self.config["APP"]["cantidad"]  = str(self.entry_celdas.get())
        self.config["APP"]["option"]    = str(self.combo_tecla.get())
        self.config["APP"]["delay"]     = str(self.entry_delay.get())
        with open(CONFIG_FILE, "w") as f:
            self.config.write(f)

    def guardar_config(self):
        """Guarda offset en config.ini"""
        if not self.config.has_section("GRID"):
            self.config.add_section("GRID")
        self.config["GRID"]["dy"] = str(self.dy)
        with open(CONFIG_FILE, "w") as f:
            self.config.write(f)
        print(f"Offset guardado en config.ini: dy={self.dy}")
        self.label_offset.configure(text=self.get_offset_text())

    def resetear_offset(self):
        """Elimina offset de config.ini"""
        if self.config.has_section("GRID"):
            self.config.remove_section("GRID")
            with open(CONFIG_FILE, "w") as f:
                self.config.write(f)
        self.dy = None
        self.label_offset.configure(text=self.get_offset_text())
        self.label_info.configure(text="Offset reseteado. Vuelve a calibrar.")

    def borrar_base(self):
        """Borra la posición base guardada"""
        self.base_pos = None
        self.celdas = []
        self.label_info.configure(text="Base borrada. Marca una nueva con SHIFT.")
        print("Base borrada.")
        self.cargar_config()
        self.label_offset.configure(text=self.get_offset_text())

    def iniciar_calibracion(self):
        """Activa modo calibración (se necesitan 2 clics en SHIFT)"""
        self.calibrando = True
        self.temp_pos = None
        self.label_info.configure(text="Calibración: presiona SHIFT en celda 1, luego en celda 2")

    def marcar_base(self, e):
        pos = pyautogui.position()
        if self.calibrando:
            if self.temp_pos is None:
                self.temp_pos = pos
                self.label_info.configure(text=f"Calibración: primera posición guardada {pos}")
            else:
                # calcular solo dy
                self.dy = pos.y - self.temp_pos.y
                self.guardar_config()
                self.calibrando = False
                self.label_info.configure(text=f"Calibración completa. dy={self.dy}")
                print("dy:", self.dy)
        else:
            # Uso normal → marcar base
            self.base_pos = pos
            self.actualizar_celdas()
            self.label_info.configure(text=f"Base guardada: {pos}")

    def actualizar_celdas(self):
        if self.base_pos and self.dy:
            #total = self.num_celdas.get()
            total = int(self.num_celdas.get() or 0)

            self.celdas = []

            for i in range(total):
                x = self.base_pos.x
                y = self.base_pos.y + i * self.dy
                self.celdas.append((round(x), round(y)))

            self.label_info.configure(text=f"{total} celdas calculadas.")

    def escribir_en_todas(self):
        if not self.celdas:
            self.label_info.configure(text="Primero marca base con SHIFT")
            return
        if self.combo_tecla.get() == "Si":
            tecla = "s"
        elif self.combo_tecla.get() == "No":
            tecla = "n"
        elif self.combo_tecla.get() == "N/A":
            tecla = "nn"

        self.delay = float(self.entry_delay.get())

        if tecla == "s" or tecla == "n":
            for x, y in self.celdas:
                time.sleep(self.delay)
                pyautogui.click(x, y)
                time.sleep(self.delay)
                keyboard.send(tecla)
                time.sleep(self.delay)
                keyboard.send("tab")
        else:
            for x, y in self.celdas:
                time.sleep(self.delay)
                pyautogui.click(x, y)
                time.sleep(self.delay)
                keyboard.send("n")
                time.sleep(self.delay)
                keyboard.send("n")
                time.sleep(self.delay)
                keyboard.send("tab")

        self.borrar_base()
        self.set_config()

if __name__ == "__main__":
    app = MouseGridApp()
    app.mainloop()
