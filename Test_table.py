import customtkinter as ctk

class TablaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Tabla 2x30")
        self.geometry("600x1200")

        # Frame para contener la tabla
        frame_tabla = ctk.CTkFrame(self)
        frame_tabla.pack(pady=20, padx=20, fill="both", expand=True)

        self.entries = []  # Para guardar todas las entradas

        # Crear 30 filas × 2 columnas
        for fila in range(30):
            fila_entries = []
            for col in range(2):
                entry = ctk.CTkEntry(frame_tabla, width=200, placeholder_text=f"Fila {fila+1}, Col {col+1}")
                entry.grid(row=fila, column=col, padx=5, pady=2, sticky="ew")
                fila_entries.append(entry)
            self.entries.append(fila_entries)

        # Botón para limpiar todo
        boton_limpiar = ctk.CTkButton(self, text="Limpiar Todo", command=self.limpiar_tabla)
        boton_limpiar.pack(pady=10)

    def limpiar_tabla(self):
        """Vacía todas las celdas de la tabla"""
        for fila in self.entries:
            for entry in fila:
                entry.delete(0, "end")


if __name__ == "__main__":
    ctk.set_appearance_mode("light")  # Opcional: "dark"
    app = TablaApp()
    app.mainloop()
