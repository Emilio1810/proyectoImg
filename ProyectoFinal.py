import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageEnhance, ImageOps, ImageFilter, ImageDraw
from tkinter import Canvas

class EditorDeImagenes:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Imágenes")
        self.root.geometry("1920x1080")

        #variables
        self.historial_deshacer = []
        self.historial_rehacer = []
        self.imagen_original = None  
        self.imagen_editada = None  
        self.imagen_temporal = None  
        self.zoom_factor = 1.0  
        self.imagen_invertida_x = False  
        self.imagen_invertida_y = False  
        self.dibujando_pluma = False  
        self.recorte_inicio = None  
        self.rect = None  

        self.crear_interfaz()

    def crear_interfaz(self):
        # Crear el frame izquierdo (pantalla 1) para los controles (15% del ancho)
        pantalla_1 = ctk.CTkFrame(self.root, fg_color="lightgray")
        pantalla_1.place(relwidth=0.15, relheight=1.0, x=0, y=0)  # 15% del ancho, 100% de la altura

        # Crear el frame derecho (pantalla 2) para la imagen (85% del ancho)
        pantalla_2 = ctk.CTkFrame(self.root, fg_color="gray")  
        pantalla_2.place(relwidth=0.85, relheight=1.0, relx=0.15, y=0)

        # Frame para los botones de deshacer y rehacer (junto al Notebook)
        botones_frame = ttk.Frame(pantalla_1)
        botones_frame.pack(side="top", fill="x")

        # Añadir los botones de deshacer y rehacer como botones normales pero con estilo
        boton_deshacer = ttk.Button(botones_frame, text="⟲", command=self.deshacer_cambio)
        boton_deshacer.pack(side="left", padx=5, pady=5)

        boton_rehacer = ttk.Button(botones_frame, text="⟳", command=self.rehacer_cambio)
        boton_rehacer.pack(side="left", padx=5, pady=5)

        # Configurar el Notebook en la pantalla 1
        tab_control = ttk.Notebook(pantalla_1)
        tab_control.bind("<<NotebookTabChanged>>", lambda e: self.desactivar_recorte())  # Desactivar recorte al cambiar de pestaña
        tab_control.bind("<<NotebookTabChanged>>", lambda e: self.desactivar_pluma())  # Desactivar pluma al cambiar de pestaña
        tab_control.pack(expand=1, fill="both")

        # Crear pestañas en el Notebook
        tab_posicion = ctk.CTkFrame(tab_control)
        tab_colores = ctk.CTkFrame(tab_control)
        tab_efectos = ctk.CTkFrame(tab_control)
        tab_exportar = ctk.CTkFrame(tab_control)

        tab_control.add(tab_posicion, text="Posición")
        tab_control.add(tab_colores, text="Colores")
        tab_control.add(tab_efectos, text="Efectos")
        tab_control.add(tab_exportar, text="Exportar")

        # Añadir elementos a la pestaña de Posición
        ctk.CTkLabel(tab_posicion, text="Rotación").pack(pady=10)
        self.rotation_slider = ctk.CTkSlider(tab_posicion, from_=0, to=360, command=self.aplicar_transformaciones)
        self.rotation_slider.set(0)
        self.rotation_slider.pack(fill="x", padx=10, pady=5)

        # Vincular la actualización del historial al soltar el slider de rotación
        self.rotation_slider.bind("<ButtonRelease-1>", self.actualizar_historial_deshacer)

        # Subir los botones de inversión de ejes
        self.boton_invertir_x = ctk.CTkButton(tab_posicion, text="Invertir X", command=lambda: self.invertir_imagen('x'))
        self.boton_invertir_x.pack(pady=5, padx=10, fill="x")
        self.boton_invertir_y = ctk.CTkButton(tab_posicion, text="Invertir Y", command=lambda: self.invertir_imagen('y'))
        self.boton_invertir_y.pack(pady=5, padx=10, fill="x")

        # Botón para activar recorte
        self.boton_recortar = ctk.CTkButton(tab_posicion, text="Recortar Imagen", command=self.activar_recorte)
        self.boton_recortar.pack(pady=5, padx=10, fill="x")

        # Botón para abrir imagen
        self.boton_abrir_imagen = ctk.CTkButton(tab_posicion, text="Abrir Imagen", command=self.cargar_imagen)
        self.boton_abrir_imagen.place(relx=0.5, rely=0.95, anchor="center", relwidth=0.6)

        # Añadir elementos a la pestaña de Colores
        ctk.CTkLabel(tab_colores, text="Brillo").pack(pady=10)
        self.brillo_slider = ctk.CTkSlider(tab_colores, from_=0, to=2, command=self.aplicar_transformaciones)
        self.brillo_slider.pack(fill="x", padx=10, pady=5)
        self.brillo_slider.bind("<ButtonRelease-1>", self.actualizar_historial_deshacer)

        ctk.CTkLabel(tab_colores, text="Contraste").pack(pady=10)
        self.contraste_slider = ctk.CTkSlider(tab_colores, from_=0, to=2, command=self.aplicar_transformaciones)
        self.contraste_slider.pack(fill="x", padx=10, pady=5)
        self.contraste_slider.bind("<ButtonRelease-1>", self.actualizar_historial_deshacer)

        ctk.CTkLabel(tab_colores, text="Saturación").pack(pady=10)
        self.saturacion_slider = ctk.CTkSlider(tab_colores, from_=0, to=2, command=self.aplicar_transformaciones)
        self.saturacion_slider.pack(fill="x", padx=10, pady=5)
        self.saturacion_slider.bind("<ButtonRelease-1>", self.actualizar_historial_deshacer)

        # Añadir elementos a la pestaña de Efectos
        ctk.CTkLabel(tab_efectos, text="Desenfoque").pack(pady=10)
        self.blur_slider = ctk.CTkSlider(tab_efectos, from_=0, to=10, command=self.aplicar_transformaciones)
        self.blur_slider.set(0)  # Ajustar el valor inicial a 0
        self.blur_slider.pack(fill="x", padx=10, pady=5)
        self.blur_slider.bind("<ButtonRelease-1>", self.actualizar_historial_deshacer)

        # Añadir el slider de transparencia
        ctk.CTkLabel(tab_efectos, text="Transparencia").pack(pady=10)
        self.transparencia_slider = ctk.CTkSlider(tab_efectos, from_=255, to=0, command=self.aplicar_transformaciones)
        self.transparencia_slider.set(255)  # Valor inicial (sin transparencia)
        self.transparencia_slider.pack(fill="x", padx=10, pady=5)
        self.transparencia_slider.bind("<ButtonRelease-1>", self.actualizar_historial_deshacer)

        self.boton_pluma = ctk.CTkButton(tab_efectos, text="Pluma", command=self.activar_pluma)
        self.boton_pluma.pack(pady=10)

        # Añadir elementos a la pestaña de Exportar
        ctk.CTkLabel(tab_exportar, text="Formato de archivo:").pack(pady=10)
        self.tipo_archivo_var = ctk.StringVar(value="png")
        formatos = [("PNG", "png"), ("BMP", "bmp")]
        for formato, valor in formatos:
            ctk.CTkRadioButton(tab_exportar, text=formato, variable=self.tipo_archivo_var, value=valor).pack(anchor='w')

        self.boton_guardar_imagen = ctk.CTkButton(tab_exportar, text="Guardar Imagen", command=self.guardar_imagen)
        self.boton_guardar_imagen.pack(pady=10)

        # Ajustar botones de zoom y el % en la esquina inferior derecha de pantalla 2
        self.boton_zoom_menos = ctk.CTkButton(pantalla_2, text="-", width=30, command=self.zoom_menos)
        self.boton_zoom_menos.place(relx=0.85, rely=0.93, anchor="se")
        self.zoom_label = ctk.CTkLabel(pantalla_2, text="100%")
        self.zoom_label.place(relx=0.91, rely=0.93, anchor="se")
        self.boton_zoom_mas = ctk.CTkButton(pantalla_2, text="+", width=30, command=self.zoom_mas)
        self.boton_zoom_mas.place(relx=0.97, rely=0.93, anchor="se")

        self.canvas = Canvas(pantalla_2, bg="gray")
        self.canvas.place(relwidth=1.0, relheight=0.88, x=0, y=0)





    def aplicar_transformaciones(self, event=None):
        self.desactivar_pluma()  # Desactivar la pluma al aplicar otras transformaciones
        if self.imagen_original:
            self.imagen_editada = self.imagen_original.copy()

            # Rotación
            angulo = self.rotation_slider.get()
            self.imagen_editada = self.imagen_editada.rotate(angulo, expand=True)

            # Inversiones de ejes
            if self.imagen_invertida_x:
                self.imagen_editada = ImageOps.mirror(self.imagen_editada)
            if self.imagen_invertida_y:
                self.imagen_editada = ImageOps.flip(self.imagen_editada)

            # Brillo, saturación, y contraste
            enhancer = ImageEnhance.Brightness(self.imagen_editada)
            self.imagen_editada = enhancer.enhance(self.brillo_slider.get())

            enhancer = ImageEnhance.Color(self.imagen_editada)
            self.imagen_editada = enhancer.enhance(self.saturacion_slider.get())

            enhancer = ImageEnhance.Contrast(self.imagen_editada)
            self.imagen_editada = enhancer.enhance(self.contraste_slider.get())

            # Desenfoque
            blur_cantidad = self.blur_slider.get()
            if blur_cantidad > 0:
                self.imagen_editada = self.imagen_editada.filter(ImageFilter.GaussianBlur(blur_cantidad))

            # Transparencia
            transparencia_valor = self.transparencia_slider.get()
            alpha = self.imagen_editada.getchannel("A")
            alpha = alpha.point(lambda p: p * (transparencia_valor / 255))
            self.imagen_editada.putalpha(alpha)

            self.mostrar_imagen(self.imagen_editada)
            self.actualizar_historial_deshacer()

    def actualizar_historial_deshacer(self, event=None):
        """
        Al soltar el slider o realizar un cambio, actualiza el historial de deshacer.
        """
        if self.imagen_editada:
            estado_actual = {
                'imagen': self.imagen_editada.copy(),
                'brillo': self.brillo_slider.get(),
                'contraste': self.contraste_slider.get(),
                'saturacion': self.saturacion_slider.get(),
                'rotacion': self.rotation_slider.get(),
                'desenfoque': self.blur_slider.get(),
                'transparencia': self.transparencia_slider.get(),
                'invertida_x': self.imagen_invertida_x,
                'invertida_y': self.imagen_invertida_y
            }
            self.historial_deshacer.append(estado_actual)
            self.historial_rehacer.clear()  # Limpiar el historial de rehacer al hacer un nuevo cambio

    def deshacer_cambio(self):
        """
        Deshacer el último cambio.
        """
        if self.historial_deshacer:
            estado_actual = {
                'imagen': self.imagen_editada.copy(),
                'brillo': self.brillo_slider.get(),
                'contraste': self.contraste_slider.get(),
                'saturacion': self.saturacion_slider.get(),
                'rotacion': self.rotation_slider.get(),
                'desenfoque': self.blur_slider.get(),
                'transparencia': self.transparencia_slider.get(),
                'invertida_x': self.imagen_invertida_x,
                'invertida_y': self.imagen_invertida_y
            }
            self.historial_rehacer.append(estado_actual)
            estado_anterior = self.historial_deshacer.pop()
            self.restaurar_estado(estado_anterior)

    def rehacer_cambio(self):
        """
        Rehacer el último cambio deshecho.
        """
        if self.historial_rehacer:
            estado_actual = {
                'imagen': self.imagen_editada.copy(),
                'brillo': self.brillo_slider.get(),
                'contraste': self.contraste_slider.get(),
                'saturacion': self.saturacion_slider.get(),
                'rotacion': self.rotation_slider.get(),
                'desenfoque': self.blur_slider.get(),
                'transparencia': self.transparencia_slider.get(),
                'invertida_x': self.imagen_invertida_x,
                'invertida_y': self.imagen_invertida_y
            }
            self.historial_deshacer.append(estado_actual)
            estado_posterior = self.historial_rehacer.pop()
            self.restaurar_estado(estado_posterior)

    def restaurar_estado(self, estado):
        """
        Restaura la imagen y los valores de los sliders al estado proporcionado.
        """
        self.imagen_editada = estado['imagen']
        self.brillo_slider.set(estado['brillo'])
        self.contraste_slider.set(estado['contraste'])
        self.saturacion_slider.set(estado['saturacion'])
        self.rotation_slider.set(estado['rotacion'])
        self.blur_slider.set(estado['desenfoque'])
        self.transparencia_slider.set(estado['transparencia'])
        self.imagen_invertida_x = estado['invertida_x']
        self.imagen_invertida_y = estado['invertida_y']
        self.mostrar_imagen(self.imagen_editada)

    def activar_recorte(self):
        """
        Activar o desactivar la herramienta de recorte.
        """
        if not hasattr(self, 'recorte_activo') or not self.recorte_activo:
            # Activar recorte
            self.recorte_activo = True
            self.boton_recortar.configure(fg_color="#1E3C72")  # Cambiar a azul oscuro para indicar que está activo
            self.canvas.bind("<Button-1>", self.iniciar_recorte)  # Iniciar recorte al hacer clic
            self.canvas.bind("<B1-Motion>", self.dibujar_recorte)  # Dibujar recorte mientras se arrastra
            self.canvas.bind("<ButtonRelease-1>", self.finalizar_recorte)  # Finalizar recorte al soltar el clic
        else:
            self.desactivar_recorte()

    def desactivar_recorte(self):
        """
        Desactivar la herramienta de recorte.
        """
        if hasattr(self, 'recorte_activo') and self.recorte_activo:
            self.recorte_activo = False
            self.boton_recortar.configure(fg_color="#007BFF")  # Volver a azul claro para indicar que está desactivado
            self.canvas.unbind("<Button-1>")
            self.canvas.unbind("<B1-Motion>")
            self.canvas.unbind("<ButtonRelease-1>")

    def iniciar_recorte(self, event):
        """
        Iniciar el área de recorte cuando se presiona el mouse.
        """
        self.recorte_inicio = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        self.rect = self.canvas.create_rectangle(self.recorte_inicio[0], self.recorte_inicio[1], self.recorte_inicio[0], self.recorte_inicio[1], outline="red", width=2)

    def dibujar_recorte(self, event):
        """
        Dibujar el área de recorte mientras se arrastra el mouse.
        """
        if self.recorte_inicio:
            x1, y1 = self.recorte_inicio
            x2, y2 = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            self.canvas.coords(self.rect, x1, y1, x2, y2)

    def finalizar_recorte(self, event):
        """
        Finalizar el área de recorte cuando se suelta el mouse.
        """
        if self.recorte_inicio and self.rect:
            x1, y1 = self.recorte_inicio
            x2, y2 = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

            # Limitar las coordenadas dentro del rango de la imagen actual
            width, height = self.imagen_editada.size
            x1, x2 = max(0, min(width, x1)), max(0, min(width, x2))
            y1, y2 = max(0, min(height, y1)), max(0, min(height, y2))

            if x1 < x2 and y1 < y2:  # Asegurar que el recorte tenga un área válida
                crop_box = (int(x1), int(y1), int(x2), int(y2))
                self.imagen_editada = self.imagen_editada.crop(crop_box)
                # Actualizar la imagen original con la recortada
                self.imagen_original = self.imagen_editada.copy()
                self.mostrar_imagen(self.imagen_editada)

            self.canvas.delete(self.rect)  # Eliminar el rectángulo de recorte
            self.recorte_inicio = None
            self.desactivar_recorte()  # Desactivar recorte después de aplicar

    def cargar_imagen(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if self.image_path:
            try:
                self.imagen_original = Image.open(self.image_path).convert("RGBA")
                self.imagen_editada = self.imagen_original.copy()
                self.zoom_factor = 1.0
                self.actualizar_zoom_label()
                self.imagen_invertida_x = False
                self.imagen_invertida_y = False

                # Reiniciar sliders
                self.brillo_slider.set(1.0)
                self.contraste_slider.set(1.0)
                self.saturacion_slider.set(1.0)
                self.rotation_slider.set(0)
                self.blur_slider.set(0)
                self.transparencia_slider.set(255)

                self.mostrar_imagen(self.imagen_editada)
                self.historial_deshacer.clear()
                self.historial_rehacer.clear()
                self.actualizar_historial_deshacer()  # Registrar el estado inicial
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")

    def mostrar_imagen(self, imagen):
        width, height = imagen.size
        zoomed_image = imagen.resize((int(width * self.zoom_factor), int(height * self.zoom_factor)), Image.LANCZOS)
        self.image_tk = ImageTk.PhotoImage(zoomed_image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=self.image_tk)
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def invertir_imagen(self, direccion):
        if self.imagen_editada:
            if direccion == 'x':
                self.imagen_invertida_x = not self.imagen_invertida_x
                self.imagen_editada = ImageOps.mirror(self.imagen_editada)
            elif direccion == 'y':
                self.imagen_invertida_y = not self.imagen_invertida_y
                self.imagen_editada = ImageOps.flip(self.imagen_editada)

            self.mostrar_imagen(self.imagen_editada)
            self.actualizar_historial_deshacer()  # Registrar el cambio

    def zoom_mas(self):
        self.zoom_factor += 0.05
        self.actualizar_zoom_label()
        self.mostrar_imagen(self.imagen_editada)

    def zoom_menos(self):
        if self.zoom_factor > 0.1:
            self.zoom_factor -= 0.05
            self.actualizar_zoom_label()
            self.mostrar_imagen(self.imagen_editada)

    def actualizar_zoom_label(self):
        porcentaje_zoom = int(self.zoom_factor * 100)
        self.zoom_label.configure(text=f"Zoom: {porcentaje_zoom}%")

    def activar_pluma(self):
        """
        Activar la herramienta de pluma para dibujar sobre la imagen.
        """
        if not hasattr(self, 'pluma_activa') or not self.pluma_activa:
            # Activar la pluma
            self.pluma_activa = True
            self.boton_pluma.configure(fg_color="#1E3C72")  # Indicar que la pluma está activa
            self.imagen_temporal = self.imagen_editada.copy()  # Crear una copia temporal de la imagen editada
            self.pluma_draw = ImageDraw.Draw(self.imagen_temporal)  # Inicializar herramienta de dibujo
            self.root.bind('<B1-Motion>', self.dibujar_pluma)  # Dibujar mientras se arrastra el mouse
            self.root.bind('<ButtonRelease-1>', self.liberar_pluma)  # Liberar la pluma al soltar el clic
        else:
            self.desactivar_pluma()  # Si la pluma está activa, desactívala al hacer clic nuevamente

    def dibujar_pluma(self, event):
        """
        Dibujar usando la herramienta de pluma mientras se arrastra el mouse.
        """
        if self.pluma_activa:
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            if self.ultima_posicion:
                # Dibujar una línea entre la última posición y la posición actual del mouse
                self.pluma_draw.line([self.ultima_posicion, (x, y)], fill="black", width=3)
            self.ultima_posicion = (x, y)
            self.mostrar_imagen(self.imagen_temporal)  # Actualizar la imagen en el canvas


    def liberar_pluma(self, event):
        """
        Finalizar el trazo con la pluma al soltar el mouse.
        """
        self.ultima_posicion = None  # Reiniciar la posición del mouse para el siguiente trazo
        if self.imagen_temporal:
            # Al soltar el clic, actualizar el historial de deshacer
            self.imagen_editada = self.imagen_temporal.copy()
            self.actualizar_historial_deshacer()


    def desactivar_pluma(self):
        """
        Desactivar la herramienta de pluma y aplicar los cambios realizados con la pluma a la imagen original.
        """
        if hasattr(self, 'pluma_activa') and self.pluma_activa:
            self.pluma_activa = False
            self.boton_pluma.configure(fg_color="#007BFF")  # Restablecer el color del botón de pluma

            if self.imagen_temporal:
                # Al desactivar la pluma, aplicar los trazos a la imagen original
                self.imagen_original = self.imagen_temporal.copy()
                self.imagen_editada = self.imagen_original.copy()
                self.imagen_temporal = None  # Reiniciar la imagen temporal

            # Desvincular los eventos de pluma
            self.root.unbind('<B1-Motion>')
            self.root.unbind('<ButtonRelease-1>')
            self.actualizar_historial_deshacer()  # Guardar el estado en el historial de deshacer

    def guardar_imagen(self):
        if self.imagen_editada:
            ruta_guardar = filedialog.asksaveasfilename(defaultextension=f".{self.tipo_archivo_var.get()}", filetypes=[(f"{self.tipo_archivo_var.get().upper()} files", f"*.{self.tipo_archivo_var.get()}")])
            if ruta_guardar:
                self.imagen_editada.save(ruta_guardar)


if __name__ == "__main__":
    root = ctk.CTk()
    app = EditorDeImagenes(root)
    root.mainloop()
