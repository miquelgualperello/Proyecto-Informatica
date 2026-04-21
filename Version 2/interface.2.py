

import os
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from airport import (
    Airport,
    AddAirport,
    ERROR_EMPTY_LIST,
    ERROR_NOT_FOUND,
    FilterAirports,
    LoadAirports,
    MapAirports,
    ModifyAirport,
    PlotAirports,
    RemoveAirport,
    SaveSchengenAirports,
    SearchAirport,
    SetSchengen,
)

from aircraft import (
    LoadArrivals,
    PlotArrivals,
    SaveFlights,
    LongDistanceArrivals,
    PlotAirlines,
    PlotFlightsType,
    MapFlights,
)

airports = []
aircrafts = []

root = None
tree = None
details = None
code_var = None
lat_var = None
lon_var = None
year_var = None
capacity_var = None
autoschengen_var = None
col_min_var = None
col_max_var = None
col_min_capacity = None
col_max_capacity = None
tree = None
aircraft_tree = None
v2_notebook = None
arrivals_figure = None
arrivals_axes = None
arrivals_canvas = None
airlines_figure = None
airlines_axes = None
airlines_canvas = None
flights_type_figure = None
flights_type_axes = None
flights_type_canvas = None
notebook = None
v2_notebook = None
info_text_v2 = None


def apply_styles():
    """Aplica estilo visual moderno profesional."""
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Main.TFrame", background="#ffeaea")
    style.configure("Panel.TLabelframe", background="#ffd9d9")
    style.configure(
        "Panel.TLabelframe.Label",
        background="#ffd9d9",
        foreground="#8b2020",
    )
    style.configure("Custom.TLabel", background="#ffeaea", foreground="#8b2020")
    style.configure("Custom.TButton", padding=8, background="#ffb3b3", relief="raised")
    style.configure("Selected.TButton", padding=8, background="#ff6666", relief="sunken")
    style.configure("Treeview", rowheight=26, background="#fff0f0")
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"), background="#ffb3b3")
    style.configure("TNotebook", background="#ffeaea")
    style.configure("TNotebook.Tab", background="#ffd9d9", foreground="#8b2020", padding=[12, 6])
    style.map(
        "TNotebook.Tab",
        background=[("selected", "#ffeaea")],
    )
    style.map(
        "Custom.TButton",
        background=[("active", "#ff9999")],
    )


def build_interface():
    """Construye la ventana principal del sistema."""
    global root

    root.title("Sistema de Gestión de Tráfico Aéreo")
    root.geometry("1200x800")
    root.minsize(1020, 700)
    root.configure(bg="#ffeaea")

    apply_styles()

    container = ttk.Frame(root, padding=12, style="Main.TFrame")
    container.pack(fill=tk.BOTH, expand=True)

    global notebook
    notebook = ttk.Notebook(container)
    notebook.pack(fill=tk.BOTH, expand=True)

    v1_frame = ttk.Frame(notebook, style="Main.TFrame")
    v2_frame = ttk.Frame(notebook, style="Main.TFrame")

    notebook.add(v1_frame, text="Panel de Control - Aeropuertos")
    notebook.add(v2_frame, text="Panel de Control - Vuelos")

    build_version1(v1_frame)
    build_version2(v2_frame)


def build_version1(parent):
    """Construye los componentes del panel de aeropuertos."""
    main_container = ttk.Frame(parent, style="Main.TFrame")
    main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    left_column = ttk.Frame(main_container, style="Main.TFrame")
    left_column.pack(side=tk.LEFT, fill=tk.BOTH)

    right_column = ttk.Frame(main_container, style="Main.TFrame")
    right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

    top_right = ttk.Frame(right_column, style="Main.TFrame")
    top_right.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))
    build_plot_area(top_right)

    bottom_right = ttk.Frame(right_column, style="Main.TFrame")
    bottom_right.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(5, 0))
    build_table(bottom_right)

    build_form(left_column)
    build_buttons(left_column)
    build_log(left_column)


def build_version2(parent):
    """Construye los componentes del panel de vuelos."""
    global v2_notebook

    right_panel = ttk.Frame(parent, padding=(0, 0, 12, 0), style="Main.TFrame")
    right_panel.pack(side=tk.RIGHT, fill=tk.Y)

    left_panel = ttk.Frame(parent, style="Main.TFrame")
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    build_flight_buttons(right_panel)
    build_aircraft_table(left_panel)

    v2_notebook = ttk.Notebook(left_panel)
    v2_notebook.pack(fill=tk.BOTH, expand=True)

    arrivals_plot_frame = ttk.Frame(v2_notebook, style="Main.TFrame")
    airlines_plot_frame = ttk.Frame(v2_notebook, style="Main.TFrame")
    flights_type_plot_frame = ttk.Frame(v2_notebook, style="Main.TFrame")

    v2_notebook.add(arrivals_plot_frame, text="Horario de Llegadas")
    v2_notebook.add(airlines_plot_frame, text="Por Aerolínea")
    v2_notebook.add(flights_type_plot_frame, text="Tipo de Zona")

    build_arrivals_plot_area(arrivals_plot_frame)
    build_airlines_plot_area(airlines_plot_frame)
    build_flights_type_plot_area(flights_type_plot_frame)


def build_form(parent):
    """Crea el formulario para nuevos aeropuertos."""
    form = ttk.LabelFrame(parent, text="Datos del Aeropuerto", padding=12, style="Panel.TLabelframe")
    form.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(form, text="Código ICAO:", style="Custom.TLabel").grid(
        row=0, column=0, sticky=tk.W, padx=5, pady=5
    )
    ttk.Entry(form, textvariable=code_var, width=12).grid(
        row=0, column=1, sticky=tk.W, padx=5, pady=5
    )

    ttk.Label(form, text="Latitud:", style="Custom.TLabel").grid(
        row=1, column=0, sticky=tk.W, padx=5, pady=5
    )
    ttk.Entry(form, textvariable=lat_var, width=14).grid(
        row=1, column=1, sticky=tk.W, padx=5, pady=5
    )

    ttk.Label(form, text="Longitud:", style="Custom.TLabel").grid(
        row=2, column=0, sticky=tk.W, padx=5, pady=5
    )
    ttk.Entry(form, textvariable=lon_var, width=14).grid(
        row=2, column=1, sticky=tk.W, padx=5, pady=5
    )

    ttk.Label(form, text="Año apertura:", style="Custom.TLabel").grid(
        row=3, column=0, sticky=tk.W, padx=5, pady=5
    )
    ttk.Entry(form, textvariable=year_var, width=14).grid(
        row=3, column=1, sticky=tk.W, padx=5, pady=5
    )

    ttk.Label(form, text="Capacidad:", style="Custom.TLabel").grid(
        row=4, column=0, sticky=tk.W, padx=5, pady=5
    )
    ttk.Entry(form, textvariable=capacity_var, width=14).grid(
        row=4, column=1, sticky=tk.W, padx=5, pady=5
    )

    ttk.Checkbutton(
        form,
        text="Detectar Schengen automáticamente",
        variable=autoschengen_var,
    ).grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=8)

    ttk.Button(
        form,
        text="Agregar",
        command=add_airport,
        style="Custom.TButton",
    ).grid(row=6, column=0, sticky=tk.EW, padx=5, pady=(8, 3))

    ttk.Button(
        form,
        text="Actualizar",
        command=modify_selected,
        style="Custom.TButton",
    ).grid(row=6, column=1, sticky=tk.EW, padx=5, pady=(8, 3))

    form.columnconfigure(1, weight=1)


def build_buttons(parent):
    """Crea el panel de acciones principales."""
    buttons = ttk.LabelFrame(parent, text="Acciones Disponibles", padding=12, style="Panel.TLabelframe")
    buttons.pack(fill=tk.X)

    ttk.Button(buttons, text="Cargar Archivo", command=load_file, style="Custom.TButton").grid(
        row=0, column=0, padx=5, pady=5, sticky=tk.EW
    )
    ttk.Button(
        buttons,
        text="Borrar",
        command=remove_selected,
        style="Custom.TButton",
    ).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Verificar Schengen",
        command=detect_schengen,
        style="Custom.TButton",
    ).grid(row=1, column=0, padx=5, pady=5, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Exportar Schengen",
        command=save_schengen,
        style="Custom.TButton",
    ).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Ver Listado",
        command=show_all,
        style="Custom.TButton",
    ).grid(row=2, column=0, padx=5, pady=5, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Ver Gráfico",
        command=plot_airports_interface,
        style="Custom.TButton",
    ).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Ver Mapa",
        command=map_airports,
        style="Custom.TButton",
    ).grid(row=3, column=0, padx=5, pady=5, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Actualizar",
        command=refresh_list,
        style="Custom.TButton",
    ).grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)

    ttk.Label(buttons, text="Filtrar por año:", style="Custom.TLabel").grid(
        row=4, column=0, columnspan=2, padx=5, pady=3, sticky=tk.W
    )
    
    ttk.Label(buttons, text="Desde:", style="Custom.TLabel").grid(
        row=5, column=0, padx=5, pady=2, sticky=tk.E
    )
    ttk.Entry(buttons, textvariable=col_min_var, width=10).grid(
        row=5, column=1, padx=5, pady=2, sticky=tk.W
    )

    ttk.Label(buttons, text="Hasta:", style="Custom.TLabel").grid(
        row=6, column=0, padx=5, pady=2, sticky=tk.E
    )
    ttk.Entry(buttons, textvariable=col_max_var, width=10).grid(
        row=6, column=1, padx=5, pady=2, sticky=tk.W
    )

    ttk.Label(buttons, text="Filtrar por capacidad:", style="Custom.TLabel").grid(
        row=7, column=0, columnspan=2, padx=5, pady=3, sticky=tk.W
    )
    
    ttk.Label(buttons, text="Mín:", style="Custom.TLabel").grid(
        row=8, column=0, padx=5, pady=2, sticky=tk.E
    )
    ttk.Entry(buttons, textvariable=col_min_capacity, width=10).grid(
        row=8, column=1, padx=5, pady=2, sticky=tk.W
    )

    ttk.Label(buttons, text="Máx:", style="Custom.TLabel").grid(
        row=9, column=0, padx=5, pady=2, sticky=tk.E
    )
    ttk.Entry(buttons, textvariable=col_max_capacity, width=10).grid(
        row=9, column=1, padx=5, pady=2, sticky=tk.W
    )

    ttk.Button(
        buttons,
        text="Aplicar Filtro",
        command=filter_airports,
        style="Custom.TButton",
    ).grid(row=10, column=0, padx=5, pady=5, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Limpiar Filtros",
        command=show_all_airports,
        style="Custom.TButton",
    ).grid(row=10, column=1, padx=5, pady=5, sticky=tk.EW)

    for column in range(2):
        buttons.columnconfigure(column, weight=1)


def build_flight_buttons(parent):
    """Crea el panel de controles de vuelos."""
    buttons = ttk.LabelFrame(parent, text="Panel de Control de Vuelos", padding=12, style="Panel.TLabelframe")
    buttons.pack(fill=tk.X)

    ttk.Button(buttons, text="Importar Datos", command=load_arrivals, style="Custom.TButton").grid(
        row=0, column=0, padx=5, pady=5, sticky=tk.EW
    )
    ttk.Button(
        buttons,
        text="Análisis Horario",
        command=plot_arrivals_interface,
        style="Custom.TButton",
    ).grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Exportar Datos",
        command=save_flights,
        style="Custom.TButton",
    ).grid(row=1, column=0, padx=5, pady=5, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Estadísticas Aerolíneas",
        command=plot_airlines_interface,
        style="Custom.TButton",
    ).grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Análisis Schengen",
        command=plot_flights_type_interface,
        style="Custom.TButton",
    ).grid(row=2, column=0, padx=5, pady=5, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Vuelos Larga Distancia",
        command=show_long_distance,
        style="Custom.TButton",
    ).grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)

    ttk.Button(
        buttons,
        text="Generar Mapa Completo",
        command=map_flights_interface,
        style="Custom.TButton",
    ).grid(row=3, column=0, padx=5, pady=5, sticky=tk.EW)
    ttk.Button(
        buttons,
        text="Mapa Larga Distancia",
        command=map_long_distance_interface,
        style="Custom.TButton",
    ).grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)

    global info_text_v2
    info_text_v2 = tk.Text(
        buttons,
        height=12,
        width=30,
        bg="#fff0f0",
        fg="#8b2020",
        relief="solid",
        borderwidth=1,
    )
    info_text_v2.grid(row=4, column=0, columnspan=2, padx=5, pady=10, sticky=tk.EW)

    buttons.columnconfigure(0, weight=1)
    buttons.columnconfigure(1, weight=1)


def build_table(parent):
    """Crea el listado de aeropuertos."""
    ttk.Label(parent, text="Listado de Aeropuertos Registrados", style="Custom.TLabel").pack(anchor=tk.W)

    columns = ("code", "lat", "lon", "year", "capacity", "schengen")

    global tree
    tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)

    tree.heading("code", text="Código")
    tree.heading("lat", text="Latitud")
    tree.heading("lon", text="Longitud")
    tree.heading("year", text="Año")
    tree.heading("capacity", text="Capacidad")
    tree.heading("schengen", text="Zona")

    tree.column("code", width=70, anchor=tk.CENTER)
    tree.column("lat", width=100, anchor=tk.CENTER)
    tree.column("lon", width=100, anchor=tk.CENTER)
    tree.column("year", width=60, anchor=tk.CENTER)
    tree.column("capacity", width=80, anchor=tk.CENTER)
    tree.column("schengen", width=80, anchor=tk.CENTER)

    tree.pack(fill=tk.BOTH, expand=False)
    tree.bind("<<TreeviewSelect>>", show_selected)


def build_aircraft_table(parent):
    """Crea el listado de vuelos."""
    ttk.Label(parent, text="Registro de Vuelos", style="Custom.TLabel").pack(anchor=tk.W)

    columns = ("id", "origin", "arrival", "airline")

    global aircraft_tree
    aircraft_tree = ttk.Treeview(parent, columns=columns, show="headings", height=10)

    aircraft_tree.heading("id", text="IDENTIFICADOR")
    aircraft_tree.heading("origin", text="AEROPUERTO")
    aircraft_tree.heading("arrival", text="HORARIO")
    aircraft_tree.heading("airline", text="AEROLÍNEA")

    aircraft_tree.column("id", width=100, anchor=tk.CENTER)
    aircraft_tree.column("origin", width=100, anchor=tk.CENTER)
    aircraft_tree.column("arrival", width=100, anchor=tk.CENTER)
    aircraft_tree.column("airline", width=100, anchor=tk.CENTER)

    aircraft_tree.pack(fill=tk.BOTH, expand=False)


def build_log(parent):
    """Crea el panel de mensajes del sistema."""
    ttk.Label(parent, text="Panel de Notificaciones", style="Custom.TLabel").pack(anchor=tk.W, pady=(10, 0))

    global details
    details = tk.Text(
        parent,
        height=7,
        wrap="word",
        bg="#fff0f0",
        fg="#8b2020",
        relief="solid",
        borderwidth=1,
    )
    details.pack(fill=tk.BOTH, expand=False, pady=(0, 6))


def build_plot_area(parent):
    """Crea el área de visualización de datos."""
    ttk.Label(parent, text="Distribución por Zona", style="Custom.TLabel").pack(
        anchor=tk.W, pady=(10, 0)
    )

    plot_frame = ttk.Frame(parent, style="Main.TFrame")
    plot_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    global figure
    global axes
    global canvas

    figure = Figure(figsize=(6.5, 4.5), dpi=100)
    axes = figure.add_subplot(111)
    axes.set_title("Distribución de Aeropuertos por Zona")
    axes.set_ylabel("Cantidad de Aeropuertos")

    figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)

    canvas = FigureCanvasTkAgg(figure, master=plot_frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()


def build_arrivals_plot_area(parent):
    """Crea el área de análisis horario."""
    ttk.Label(parent, text="Análisis de Llegadas por Hora", style="Custom.TLabel").pack(
        anchor=tk.W, pady=(10, 0)
    )

    plot_frame = ttk.Frame(parent, style="Main.TFrame")
    plot_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    global arrivals_figure
    global arrivals_axes
    global arrivals_canvas

    arrivals_figure = Figure(figsize=(6.5, 4.5), dpi=100)
    arrivals_axes = arrivals_figure.add_subplot(111)
    arrivals_axes.set_title("Frecuencia de Llegadas por Hora")
    arrivals_axes.set_xlabel("Hora del Día")
    arrivals_axes.set_ylabel("Cantidad de Llegadas")

    arrivals_figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)

    arrivals_canvas = FigureCanvasTkAgg(arrivals_figure, master=plot_frame)
    arrivals_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    arrivals_canvas.draw()


def build_airlines_plot_area(parent):
    """Crea el área de estadísticas de aerolíneas."""
    ttk.Label(parent, text="Estadísticas por Aerolínea", style="Custom.TLabel").pack(
        anchor=tk.W, pady=(10, 0)
    )

    plot_frame = ttk.Frame(parent, style="Main.TFrame")
    plot_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    global airlines_figure
    global airlines_axes
    global airlines_canvas

    airlines_figure = Figure(figsize=(6.5, 4.5), dpi=100)
    airlines_axes = airlines_figure.add_subplot(111)
    airlines_axes.set_title("Vuelos por Aerolínea")
    airlines_axes.set_ylabel("Cantidad de Vuelos")

    airlines_figure.subplots_adjust(left=0.08, right=0.97, top=0.85, bottom=0.35)

    airlines_canvas = FigureCanvasTkAgg(airlines_figure, master=plot_frame)
    airlines_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    airlines_canvas.draw()


def build_flights_type_plot_area(parent):
    """Crea el área de análisis de zonas."""
    ttk.Label(parent, text="Análisis por Tipo de Zona", style="Custom.TLabel").pack(
        anchor=tk.W, pady=(10, 0)
    )

    plot_frame = ttk.Frame(parent, style="Main.TFrame")
    plot_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    global flights_type_figure
    global flights_type_axes
    global flights_type_canvas

    flights_type_figure = Figure(figsize=(6.5, 4.5), dpi=100)
    flights_type_axes = flights_type_figure.add_subplot(111)
    flights_type_axes.set_title("Llegadas por Zona")
    flights_type_axes.set_ylabel("Cantidad de Vuelos")

    flights_type_figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)

    flights_type_canvas = FigureCanvasTkAgg(flights_type_figure, master=plot_frame)
    flights_type_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    flights_type_canvas.draw()


def log_message(message):
    """Escribe un mensaje en la zona de información."""
    details.insert(tk.END, message + "\n")
    details.see(tk.END)


def clear_log():
    """Borra el contenido de la zona de información."""
    details.delete("1.0", tk.END)


def clear_input_fields():
    """Limpia los campos del formulaire."""
    code_var.set("")
    lat_var.set("")
    lon_var.set("")
    year_var.set("")
    capacity_var.set("")


def apply_schengen_flags():
    """Actualiza el atributo Schengen de todos los aeropuertos."""
    i = 0
    while i < len(airports):
        SetSchengen(airports[i])
        i += 1


def selected_index():
    """Devuelve el índice del aeropuerto seleccionado."""
    selection = tree.selection()
    index = -1

    if selection:
        iid = selection[0]
        if str(iid).isdigit():
            possible_index = int(iid)
            if 0 <= possible_index < len(airports):
                index = possible_index

    return index


def selected_airport():
    """Devuelve el aeropuerto seleccionado."""
    airport = None
    index = selected_index()

    if index != -1:
        airport = airports[index]

    return airport


def refresh_list():
    """Actualiza la tabla con la lista actual."""
    apply_schengen_flags()

    for item in tree.get_children():
        tree.delete(item)

    i = 0
    while i < len(airports):
        tree.insert(
            "",
            tk.END,
            iid=str(i),
            values=(
                airports[i]["code"],
                f"{airports[i]['latitude']:.6f}",
                f"{airports[i]['longitude']:.6f}",
                airports[i]["year"],
                airports[i]["capacity"],
                "Schengen" if airports[i]["schengen"] else "No-Schengen"
            )
        )
        i += 1


def refresh_aircraft_list():
    """Actualiza la tabla de vuelos."""
    for item in aircraft_tree.get_children():
        aircraft_tree.delete(item)

    i = 0
    while i < len(aircrafts):
        aircraft_tree.insert(
            "",
            tk.END,
            iid=str(i),
            values=(
                aircrafts[i]["id"],
                aircrafts[i]["origin"],
                aircrafts[i]["arrival_time"],
                aircrafts[i]["airline"],
            ),
        )
        i += 1


def load_file():
    """Carga una lista de aeropuertos desde un fichier."""
    global airports

    filename = filedialog.askopenfilename(
        title="Selecciona un fichier de aeropuertos",
        filetypes=[("Text files", "*.txt"), ("Todos los archivos", "*.*")],
    )

    if filename != "":
        airports = LoadAirports(filename)
        refresh_list()

        clear_log()
        log_message(f"Fichero cargado: {filename}")
        log_message(f"Aeropuertos cargados: {len(airports)}")

        if len(airports) == 0:
            messagebox.showwarning(
                "Aviso",
                "No se ha cargado ningún aeropuerto. Revisa el fichier seleccionado.",
            )


def show_selected(_event=None):
    """Muestra en el panel inferior la información del aeropuerto seleccionado."""
    airport = selected_airport()

    if airport:
        clear_log()
        log_message(f"Código ICAO: {airport['code']}")
        log_message(f"Latitud: {airport['latitude']:.6f}")
        log_message(f"Longitud: {airport['longitude']:.6f}")
        log_message(f"Año: {airport['year']}")
        log_message(f"Capacidad: {airport['capacity']}")
        log_message(f"Schengen: {'Sí' if airport['schengen'] else 'No'}")


def show_all():
    """Muestra en el panel inferior todos los aeropuertos cargados."""
    apply_schengen_flags()
    clear_log()

    if len(airports) == 0:
        log_message("No hay aeropuertos cargados.")
    else:
        log_message("Lista actual de aeropuertos:")
        log_message("")

        i = 0
        while i < len(airports):
            log_message(
                f"{airports[i]['code']} | "
                f"Lat: {airports[i]['latitude']:.6f} | "
                f"Lon: {airports[i]['longitude']:.6f} | "
                f"Año: {airports[i]['year']} | "
                f"Cap: {airports[i]['capacity']} | "
                f"Schengen: {'Sí' if airports[i]['schengen'] else 'No'}"
            )
            i += 1


def add_airport():
    """Añade un aeropuerto a partir de los datos del formulaire."""
    code = code_var.get().strip()
    valid_data = True
    latitude = 0.0
    longitude = 0.0
    year = 0
    capacity = 0

    if code == "":
        valid_data = False
        messagebox.showerror("Error", "El código ICAO no puede estar vacío.")

    if valid_data:
        try:
            latitude = float(lat_var.get())
            longitude = float(lon_var.get())
        except ValueError:
            valid_data = False
            messagebox.showerror("Error", "Latitud y longitud deben ser números reales.")

    if valid_data:
        year_text = year_var.get().strip()
        if year_text != "":
            year = int(year_text) if year_text.isdigit() else 0

        capacity_text = capacity_var.get().strip()
        if capacity_text != "":
            capacity = int(capacity_text) if capacity_text.isdigit() else 0

    if valid_data:
        airport = Airport(code, latitude, longitude, year, capacity)

        if autoschengen_var.get():
            SetSchengen(airport)

        added = AddAirport(airports, airport)

        if added:
            refresh_list()
            clear_input_fields()
            clear_log()
            log_message(f"Aeropuerto añadido correctamente: {airport['code']}")
        else:
            messagebox.showwarning("Aviso", "Ese aeropuerto ya existe en la lista.")


def remove_selected():
    """Elimina de la lista el aeropuerto seleccionado."""
    airport = selected_airport()

    if airport is None:
        messagebox.showinfo("Información", "Selecciona un aeropuerto en la tabla.")
    else:
        result = RemoveAirport(airports, airport["code"])

        if result == ERROR_NOT_FOUND:
            messagebox.showwarning("Aviso", "No se encontró el aeropuerto a eliminar.")
        else:
            refresh_list()
            clear_log()
            log_message(f"Aeropuerto eliminado: {airport['code']}")


def detect_schengen():
    """Actualiza el atributo Schengen del aeropuerto seleccionado o de todos."""
    airport = selected_airport()

    if airport is not None:
        SetSchengen(airport)
        refresh_list()
        clear_log()
        log_message(f"Atributo Schengen actualizado para: {airport['code']}")
    else:
        apply_schengen_flags()
        refresh_list()
        clear_log()
        log_message("Atributo Schengen actualizado para toda la lista.")


def save_schengen():
    """Guarda en fichier solo los aeropuertos Schengen."""
    if len(airports) == 0:
        messagebox.showinfo("Información", "No hay aeropuertos para guardar.")
    else:
        apply_schengen_flags()

        filename = filedialog.asksaveasfilename(
            title="Guardar aeropuertos Schengen",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
        )

        if filename != "":
            result = SaveSchengenAirports(airports, filename)

            if result == ERROR_EMPTY_LIST:
                messagebox.showwarning("Aviso", "No hay aeropuertos Schengen en la lista.")
            elif result < 0:
                messagebox.showerror("Error", "No se pudo guardar el fichier de salida.")
            else:
                clear_log()
                log_message(f"Fichero guardado: {filename}")
                log_message(f"Aeropuertos Schengen guardados: {result}")
                messagebox.showinfo("Correcto", f"Se guardaron {result} aeropuertos.")


def plot_airports_interface():
    """Muestra el gráfico integrado dentro de la propia interfaz."""
    if len(airports) == 0:
        messagebox.showinfo("Información", "Carga o añade aeropuertos primero.")
    else:
        apply_schengen_flags()
        drawn = PlotAirports(airports, axes)

        if drawn:
            figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)
            canvas.draw()
            clear_log()
            log_message("Gráfico actualizado dentro de la interfaz.")
        else:
            messagebox.showwarning("Aviso", "No se pudo dibujar el gráfico.")


def map_airports():
    """Genera el fichier KML y trata de abrirlo."""
    if len(airports) == 0:
        messagebox.showinfo("Información", "Carga o añade aeropuertos primero.")
    else:
        apply_schengen_flags()
        filename = MapAirports(airports)

        if filename is None:
            messagebox.showerror("Error", "No se pudo generar el fichier KML.")
        else:
            clear_log()
            log_message(f"Fichero KML generado: {filename}")
            log_message("Ábrelo con Google Earth si no se muestra automáticamente.")


def modify_selected():
    """Modifica el aeropuerto seleccionado con los datos del formulaire."""
    airport = selected_airport()

    if airport is None:
        messagebox.showinfo("Información", "Selecciona un aeropuerto en la tabla.")
    else:
        code = code_var.get().strip()
        if code == "":
            code = airport["code"]

        latitude = airport["latitude"]
        longitude = airport["longitude"]
        year = airport["year"]
        capacity = airport["capacity"]

        lat_text = lat_var.get().strip()
        if lat_text != "":
            latitude = float(lat_text) if lat_text.replace(".", "").replace("-", "").isdigit() else airport["latitude"]

        lon_text = lon_var.get().strip()
        if lon_text != "":
            longitude = float(lon_text) if lon_text.replace(".", "").replace("-", "").isdigit() else airport["longitude"]

        year_text = year_var.get().strip()
        if year_text != "":
            year = int(year_text) if year_text.isdigit() else airport["year"]

        capacity_text = capacity_var.get().strip()
        if capacity_text != "":
            capacity = int(capacity_text) if capacity_text.isdigit() else airport["capacity"]

        ModifyAirport(airport, code, latitude, longitude, year, capacity)

        if autoschengen_var.get():
            SetSchengen(airport)

        refresh_list()
        clear_input_fields()
        clear_log()
        log_message(f"Aeropuerto modificado: {airport['code']}")


def filter_airports():
    """Filtra los aeropuertos según los criterios especificados."""
    if len(airports) == 0:
        messagebox.showinfo("Información", "No hay aeropuertos para filtrar.")
    else:
        min_year = 0
        max_year = 0
        min_capacity = 0
        max_capacity = 0

        min_text = col_min_var.get().strip()
        if min_text != "":
            min_year = int(min_text) if min_text.isdigit() else 0

        max_text = col_max_var.get().strip()
        if max_text != "":
            max_year = int(max_text) if max_text.isdigit() else 0

        min_cap_text = col_min_capacity.get().strip()
        if min_cap_text != "":
            min_capacity = int(min_cap_text) if min_cap_text.isdigit() else 0

        max_cap_text = col_max_capacity.get().strip()
        if max_cap_text != "":
            max_capacity = int(max_cap_text) if max_cap_text.isdigit() else 0

        filtered = FilterAirports(airports, min_year, max_year, min_capacity, max_capacity)

        if len(filtered) == 0:
            messagebox.showinfo("Información", "No hay aeropuertos que coincidan con los filtros.")
        else:
            clear_log()
            log_message(f"Aeropuertos encontrados: {len(filtered)}")
            log_message("")

            i = 0
            while i < len(filtered):
                log_message(
                    f"{filtered[i]['code']} | "
                    f"Lat: {filtered[i]['latitude']:.6f} | "
                    f"Lon: {filtered[i]['longitude']:.6f} | "
                    f"Año: {filtered[i]['year']} | "
                    f"Cap: {filtered[i]['capacity']} | "
                    f"Schengen: {'Sí' if filtered[i]['schengen'] else 'No'}"
                )
                i += 1


def show_all_airports():
    """Muestra todos los aeropuertos sin aplicar filtros."""
    if len(airports) == 0:
        messagebox.showinfo("Información", "No hay aeropuertos para mostrar.")
    else:
        clear_log()
        log_message(f"Total de aeropuertos: {len(airports)}")
        log_message("")

        i = 0
        while i < len(airports):
            log_message(
                f"{airports[i]['code']} | "
                f"Lat: {airports[i]['latitude']:.6f} | "
                f"Lon: {airports[i]['longitude']:.6f} | "
                f"Año: {airports[i]['year']} | "
                f"Cap: {airports[i]['capacity']} | "
                f"Schengen: {'Sí' if airports[i]['schengen'] else 'No'}"
            )
            i += 1


def load_arrivals():
    """Carga una lista de vuelos desde un fichier."""
    global aircrafts

    filename = filedialog.askopenfilename(
        title="Selecciona un fichier de vuelos",
        filetypes=[("Text files", "*.txt"), ("Todos los archivos", "*.*")],
    )

    if filename != "":
        aircrafts = LoadArrivals(filename)
        refresh_aircraft_list()

        clear_log()
        log_message(f"Fichero cargado: {filename}")
        log_message(f"Vuelos cargados: {len(aircrafts)}")

        if len(aircrafts) == 0:
            messagebox.showwarning(
                "Aviso",
                "No se ha cargado ningún vuelo. Revisa el fichier seleccionado.",
            )


def plot_arrivals_interface():
    """Muestra el gráfico de llegadas por hora."""
    if len(aircrafts) == 0:
        messagebox.showinfo("Información", "Carga o añade vuelos primero.")
    else:
        hourly_data = PlotArrivals(aircrafts)

        if hourly_data:
            arrivals_axes.clear()
            hours = []
            counts = []
            hour = 0
            while hour < 24:
                hours.append(hour)
                counts.append(hourly_data[hour])
                hour += 1

            arrivals_axes.bar(hours, counts, color="#e05555")
            arrivals_axes.set_xlabel("Hora del Día")
            arrivals_axes.set_ylabel("Cantidad de Llegadas")
            arrivals_axes.set_title("Frecuencia de Llegadas por Hora")
            arrivals_axes.set_xticks(range(0, 24, 2))

            arrivals_figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)
            arrivals_canvas.draw()
            clear_log()
            log_message("Gráfico de llegadas actualizado.")
        else:
            messagebox.showwarning("Aviso", "No se pudo dibujar el gráfico.")


def save_flights():
    """Guarda los vuelos en un fichier."""
    if len(aircrafts) == 0:
        messagebox.showinfo("Información", "No hay vuelos para guardar.")
    else:
        filename = filedialog.asksaveasfilename(
            title="Guardar vuelos",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
        )

        if filename != "":
            result = SaveFlights(aircrafts, filename)

            if result < 0:
                messagebox.showerror("Error", "No se pudo guardar el fichier de salida.")
            else:
                clear_log()
                log_message(f"Fichero guardado: {filename}")
                log_message(f"Vuelos guardados: {result}")
                messagebox.showinfo("Correcto", f"Se guardaron {result} vuelos.")


def log_message_v2(message):
    """Escribe un mensaje en la zona de información de la pestaña 2."""
    info_text_v2.insert(tk.END, message + "\n")
    info_text_v2.see(tk.END)


def clear_log_v2():
    """Borra el contenido de la zona de información de la pestaña 2."""
    info_text_v2.delete("1.0", tk.END)


def show_long_distance():
    """Muestra los vuelos de larga distancia (>2000 km)."""
    if len(aircrafts) == 0:
        messagebox.showinfo("Información", "Carga o añade vuelos primero.")
    else:
        if len(airports) == 0:
            messagebox.showwarning(
                "Aviso",
                "Carga primero los aeropuertos para calcular distancias.",
            )
        else:
            from aircraft import _load_airport_coords_from_file, _haversine_distance, LEBL_LAT, LEBL_LON

            coords_dict = _load_airport_coords_from_file("Airports.txt")

            if len(coords_dict) == 0:
                messagebox.showerror("Error", "No se encontró Airports.txt con coordenadas.")
            else:
                long_distance = []
                i = 0
                while i < len(aircrafts):
                    aircraft = aircrafts[i]
                    origin_code = aircraft["origin"]
                    origin_coords = coords_dict.get(origin_code)

                    if origin_coords is not None:
                        distance = _haversine_distance(
                            LEBL_LAT, LEBL_LON, origin_coords[0], origin_coords[1]
                        )
                        aircraft["distance"] = distance

                        if distance > 2000:
                            long_distance.append(aircraft)

                    i += 1

                clear_log_v2()
                log_message_v2(f"Vuelos de larga distancia (>2000 km): {len(long_distance)}")
                log_message_v2("")

                i = 0
                while i < len(long_distance):
                    dist = long_distance[i].get("distance", 0)
                    log_message_v2(
                        f"{long_distance[i]['id']} | {long_distance[i]['origin']} | "
                        f"{long_distance[i]['arrival_time']} | {dist:.0f} km"
                    )
                    i += 1


def plot_airlines_interface():
    """Muestra el gráfico de vuelos por compañía."""
    if len(aircrafts) == 0:
        messagebox.showinfo("Información", "Carga o añade vuelos primero.")
    else:
        airline_data = PlotAirlines(aircrafts)

        if airline_data:
            airlines_axes.clear()
            airlines = list(airline_data.keys())
            counts = list(airline_data.values())

            airlines_axes.bar(airlines, counts, color="#e05555")
            airlines_axes.set_xlabel("Aerolínea")
            airlines_axes.set_ylabel("Cantidad de Vuelos")
            airlines_axes.set_title("Vuelos por Aerolínea")
            airlines_axes.set_xticks(range(len(airlines)))
            airlines_axes.set_xticklabels(airlines, rotation=90, ha="center", fontsize=7)

            airlines_figure.subplots_adjust(left=0.08, right=0.97, top=0.85, bottom=0.35)
            airlines_canvas.draw()
            clear_log_v2()
            log_message_v2("Gráfico de compañías actualizado.")
        else:
            messagebox.showwarning("Aviso", "No se pudo dibujar el gráfico.")


def plot_flights_type_interface():
    """Muestra el gráfico apilado Schengen vs No-Schengen."""
    if len(aircrafts) == 0:
        messagebox.showinfo("Información", "Carga o añade vuelos primero.")
    else:
        data = PlotFlightsType(aircrafts)

        if data:
            flights_type_axes.clear()
            flights_type_axes.bar(["Llegadas"], [data[0]], label="Zona Schengen", color="#e05555")
            flights_type_axes.bar(["Llegadas"], [data[1]], bottom=[data[0]], label="Zona No Schengen", color="#ff8080")
            flights_type_axes.set_ylabel("Cantidad de Vuelos")
            flights_type_axes.set_title("Llegadas por Zona")
            flights_type_axes.legend()

            flights_type_figure.subplots_adjust(left=0.12, right=0.97, top=0.88, bottom=0.16)
            flights_type_canvas.draw()
            clear_log_v2()
            log_message_v2("Gráfico Schengen/No-Schengen actualizado.")
        else:
            messagebox.showwarning("Aviso", "No se pudo dibujar el gráfico.")


def map_flights_interface():
    """Genera el mapa KML de todos los vuelos."""
    if len(aircrafts) == 0:
        messagebox.showinfo("Información", "Carga o añade vuelos primero.")
    else:
        if len(airports) == 0:
            messagebox.showwarning(
                "Aviso",
                "Carga primero los aeropuertos para el mapa.",
            )
        else:
            filename = MapFlights(aircrafts)

            if filename is None:
                messagebox.showerror("Error", "No se pudo generar el archivo KML.")
            else:
                clear_log_v2()
                log_message_v2(f"Archivo KML generado: {filename}")
                try:
                    full_path = os.path.abspath(filename)
                    url = "file:///" + full_path.replace("\\", "/")
                    webbrowser.open(url)
                    log_message_v2("Abriendo en navegador...")
                except Exception:
                    log_message_v2("Ábrelo con Google Earth manualmente.")
                messagebox.showinfo("Correcto", f"Archivo KML generado: {filename}")


def map_long_distance_interface():
    """Genera el mapa KML solo de vuelos de larga distancia."""
    if len(aircrafts) == 0:
        messagebox.showinfo("Información", "Carga o añade vuelos primero.")
    else:
        if len(airports) == 0:
            messagebox.showwarning(
                "Aviso",
                "Carga primero los aeropuertos para el mapa.",
            )
        else:
            filename = MapFlights(aircrafts, long_distance_only=True)

            if filename is None:
                messagebox.showerror("Error", "No se pudo generar el archivo KML.")
            else:
                clear_log_v2()
                log_message_v2(f"Archivo KML de larga distancia generado: {filename}")
                try:
                    full_path = os.path.abspath(filename)
                    url = "file:///" + full_path.replace("\\", "/")
                    webbrowser.open(url)
                    log_message_v2("Abriendo en navegador...")
                except Exception:
                    log_message_v2("Ábrelo con Google Earth manualmente.")
                messagebox.showinfo("Correcto", f"Archivo KML generado: {filename}")


def main():
    """Punto de entrada principal del programa."""
    global root
    global code_var
    global lat_var
    global lon_var
    global year_var
    global capacity_var
    global autoschengen_var
    global col_min_var
    global col_max_var
    global col_min_capacity
    global col_max_capacity

    root = tk.Tk()

    code_var = tk.StringVar()
    lat_var = tk.StringVar()
    lon_var = tk.StringVar()
    year_var = tk.StringVar()
    capacity_var = tk.StringVar()
    autoschengen_var = tk.BooleanVar(value=True)
    col_min_var = tk.StringVar()
    col_max_var = tk.StringVar()
    col_min_capacity = tk.StringVar()
    col_max_capacity = tk.StringVar()

    build_interface()
    root.mainloop()


if __name__ == "__main__":
    main()