"""Funciones básicas para la versión 2 de ProjectoAeropuerto - Gestión de vuelos."""

import os
import math
import webbrowser

ERROR_EMPTY_LIST = -1
ERROR_NOT_FOUND = -2
ERROR_FILE = -3

LEBL_LAT = 41.297445
LEBL_LON = 2.083294

SCHENGEN_PREFIXES = [
    "LO", "EB", "LK", "LC", "EK", "EE", "EF", "LF", "ED", "LG", "EH",
    "LH", "BI", "LI", "EV", "EY", "EL", "LM", "EN", "EP", "LP", "LZ",
    "LJ", "LE", "ES", "LS",
]

AIRPORT_COORDS_CACHE = {}


def _is_schengen_airport(code):
    """Devuelve True si el airport pertenece a Schengen."""
    code = str(code).strip().upper()
    is_schengen = False

    if code != "":
        prefix = code[:2]
        index = 0
        while index < len(SCHENGEN_PREFIXES):
            if prefix == SCHENGEN_PREFIXES[index]:
                is_schengen = True
            index += 1

    return is_schengen


def Aircraft(id_code, origin, arrival_time, airline):
    """Crea un avión como diccionario simple."""
    aircraft = {
        "id": str(id_code).strip().upper(),
        "origin": str(origin).strip().upper(),
        "arrival_time": str(arrival_time).strip(),
        "airline": str(airline).strip().upper(),
        "distance": 0,
    }
    return aircraft


def GetId(aircraft):
    """Devuelve el ID del avión."""
    aircraft_id = ""

    if aircraft is not None:
        aircraft_id = aircraft["id"]

    return aircraft_id


def GetOrigin(aircraft):
    """Devuelve el aeropuerto de origen del avión."""
    origin = ""

    if aircraft is not None:
        origin = aircraft["origin"]

    return origin


def GetArrivalTime(aircraft):
    """Devuelve la hora de llegada del avión."""
    arrival_time = ""

    if aircraft is not None:
        arrival_time = aircraft["arrival_time"]

    return arrival_time


def GetAirline(aircraft):
    """Devuelve la compañía aérea del avión."""
    airline = ""

    if aircraft is not None:
        airline = aircraft["airline"]

    return airline


def SetOrigin(aircraft, origin):
    """Actualiza el aeropuerto de origen del avión."""
    if aircraft is not None:
        aircraft["origin"] = str(origin).strip().upper()


def SetArrivalTime(aircraft, arrival_time):
    """Actualiza la hora de llegada del avión."""
    if aircraft is not None:
        aircraft["arrival_time"] = str(arrival_time).strip()


def SetAirline(aircraft, airline):
    """Actualiza la compañía aérea del avión."""
    if aircraft is not None:
        aircraft["airline"] = str(airline).strip().upper()


def AircraftToString(aircraft):
    """Devuelve una cadena con la información del avión."""
    result = ""

    if aircraft is not None:
        result = (
            f"{aircraft['id']} | "
            f"Origen: {aircraft['origin']} | "
            f"Llegada: {aircraft['arrival_time']} | "
            f"Compañía: {aircraft['airline']}"
        )

    return result


def PrintAircraft(aircraft):
    """Imprime por consola la información del avión."""
    if aircraft is None:
        print("Aircraft: None")
    else:
        print(
            f"ID: {aircraft['id']} | "
            f"Origin: {aircraft['origin']} | "
            f"Arrival: {aircraft['arrival_time']} | "
            f"Airline: {aircraft['airline']}"
        )


def _parse_time_to_hours(time_str):
    """Convierte una hora en formato HH:MM a horas decimales."""
    hours = 0

    if time_str != "":
        parts = time_str.split(":")
        if len(parts) == 2:
            try:
                hours = int(parts[0]) + int(parts[1]) / 60.0
            except ValueError:
                hours = 0

    return hours


def _load_airport_coords_from_file(filename):
    """Carga coordenadas de aeropuertos desde un archivo Airports.txt."""
    coords_dict = {}

    if os.path.exists("Airports.txt"):
        try:
            with open("Airports.txt", "r", encoding="utf-8") as handler:
                first_line = True

                for raw_line in handler:
                    line = raw_line.strip()

                    if line != "":
                        if first_line:
                            first_line = False
                        else:
                            parts = line.split()
                            if len(parts) >= 3:
                                code = parts[0].strip().upper()
                                lat = parts[1].strip()
                                lon = parts[2].strip()

                                if lat.startswith("N") or lat.startswith("S"):
                                    lat = _sexagesimal_to_decimal(lat)
                                else:
                                    try:
                                        lat = float(lat)
                                    except ValueError:
                                        lat = None

                                if lon.startswith("E") or lon.startswith("W"):
                                    lon = _sexagesimal_to_decimal(lon)
                                else:
                                    try:
                                        lon = float(lon)
                                    except ValueError:
                                        lon = None

                                if lat is not None and lon is not None:
                                    coords_dict[code] = (lat, lon)

        except OSError:
            print("Aviso: No se pudo leer Airports.txt para coordenadas.")

    return coords_dict


def _sexagesimal_to_decimal(coord):
    """Convierte coordenadas tipo NDDMMSS o EDDDMMSS a grados decimales."""
    coord = str(coord).strip()
    decimal = None

    if coord != "" and len(coord) >= 2:
        direction = coord[0].upper()
        digits = coord[1:]

        if digits.isdigit():
            if direction in ("N", "S"):
                if len(digits) >= 4:
                    degrees = int(digits[:2])
                    minutes = int(digits[2:4]) if len(digits) >= 4 else 0
                    seconds = int(digits[4:6]) if len(digits) >= 6 else 0
                    decimal = degrees + minutes / 60.0 + seconds / 3600.0

                    if direction == "S":
                        decimal = -decimal

            if direction in ("E", "W"):
                if len(digits) >= 5:
                    if len(digits) >= 7:
                        degrees = int(digits[:3])
                        minutes = int(digits[3:5])
                        seconds = int(digits[5:7])
                    else:
                        degrees = int(digits[:len(digits)-4]) if len(digits) > 4 else 0
                        minutes = int(digits[len(digits)-4:len(digits)-2]) if len(digits) >= 2 else 0
                        seconds = int(digits[len(digits)-2:]) if len(digits) >= 1 else 0
                    decimal = degrees + minutes / 60.0 + seconds / 3600.0

                    if direction == "W":
                        decimal = -decimal

    return decimal


def _haversine_distance(lat1, lon1, lat2, lon2):
    """Calcula la distancia en kilómetros entre dos coordenadas usando Haversine."""
    R = 6371.0

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c

    return distance


def SearchAircraft(aircrafts, aircraft_id):
    """Busca un avión por ID y lo devuelve."""
    aircraft_id = str(aircraft_id).strip().upper()
    result = None
    index = 0
    found = False

    while index < len(aircrafts) and not found:
        if aircrafts[index]["id"] == aircraft_id:
            result = aircrafts[index]
            found = True
        else:
            index += 1

    return result


def LoadArrivals(filename):
    """Abre el ficheo y devuelve una lista de aviones."""
    aircrafts = []

    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as handler:
                first_line = True

                for raw_line in handler:
                    line = raw_line.strip()

                    if line != "":
                        if first_line:
                            first_line = False
                        else:
                            parts = line.split()

                            valid_time = False
                            if len(parts) >= 4:
                                time_str = parts[2]
                                if ":" in time_str:
                                    time_parts = time_str.split(":")
                                    if len(time_parts) == 2:
                                        try:
                                            h = int(time_parts[0])
                                            m = int(time_parts[1])
                                            if 0 <= h <= 23 and 0 <= m <= 59:
                                                valid_time = True
                                        except ValueError:
                                            pass

                            if valid_time and len(parts) >= 4:
                                id_code = parts[0]
                                origin = parts[1]
                                arrival_time = parts[2]
                                airline = parts[3]

                                aircraft = Aircraft(id_code, origin, arrival_time, airline)
                                aircrafts.append(aircraft)

        except OSError:
            print(f"Error al leer el ficheo '{filename}'.")
            aircrafts = []
    else:
        print(f"Error: el ficheo '{filename}' no existe.")

    return aircrafts


def PlotArrivals(aircrafts):
    """Muestra un gráfico de la frecuencia de llegadas por hora."""
    if len(aircrafts) == 0:
        print("Error: no hay aviones para representar.")
        return None

    hourly_counts = []
    hour = 0
    while hour < 24:
        hourly_counts.append(0)
        hour += 1

    for aircraft in aircrafts:
        arrival_hour = _parse_time_to_hours(aircraft["arrival_time"])
        hour_index = int(arrival_hour)
        if 0 <= hour_index < 24:
            hourly_counts[hour_index] += 1

    return hourly_counts


def SaveFlights(aircrafts, filename):
    """Escribe la información de los aviones en un ficheo."""
    result = len(aircrafts)

    if result == 0:
        print("Error: no hay aviones para guardar.")
        result = ERROR_EMPTY_LIST
    else:
        try:
            with open(filename, "w", encoding="utf-8") as handler:
                handler.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")

                for aircraft in aircrafts:
                    id_val = aircraft["id"] if aircraft["id"] != "" else "-"
                    origin_val = aircraft["origin"] if aircraft["origin"] != "" else "-"
                    time_val = aircraft["arrival_time"] if aircraft["arrival_time"] != "" else "0"
                    airline_val = aircraft["airline"] if aircraft["airline"] != "" else "-"

                    handler.write(
                        f"{id_val} {origin_val} {time_val} {airline_val}\n"
                    )

        except OSError:
            print(f"Error al escribir el ficheo '{filename}'.")
            result = ERROR_FILE

    return result


def PlotAirlines(aircrafts):
    """Recibe una lista de aircrafts y muestra un gráfico de barras del número de vuelos por compañía."""
    if len(aircrafts) == 0:
        print("Error: no hay aviones para representar.")
        return None

    airline_counts = {}
    index = 0
    while index < len(aircrafts):
        airline = aircrafts[index]["airline"]
        if airline == "":
            airline = "-"

        if airline not in airline_counts:
            airline_counts[airline] = 0

        airline_counts[airline] += 1
        index += 1

    return airline_counts


def PlotFlightsType(aircrafts):
    """Muestra un gráfico apilado de vuelos Schengen vs no-Schengen."""
    if len(aircrafts) == 0:
        print("Error: no hay aviones para representar.")
        return None

    schengen_count = 0
    non_schengen_count = 0

    index = 0
    while index < len(aircrafts):
        origin = aircrafts[index]["origin"]
        if _is_schengen_airport(origin):
            schengen_count += 1
        else:
            non_schengen_count += 1
        index += 1

    return (schengen_count, non_schengen_count)


def MapFlights(aircrafts, long_distance_only=False):
    """Muestra en Google Earth las trayectorias de todos los vuelos."""
    if len(aircrafts) == 0:
        print("Error: no hay aviones para representar en el mapa.")
        return None

    coords_dict = _load_airport_coords_from_file("Airports.txt")

    if len(coords_dict) == 0:
        print("Error: No se encontraron coordenadas en Airports.txt.")
        return None

    output_filename = "flights_map.kml"
    if long_distance_only:
        output_filename = "flights_long_distance.kml"

    kml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        "  <Document>",
        "    <name>Flights to LEBL</name>",
        "    <Style id=\"schengen_line\">",
        "      <LineStyle>",
        "        <color>ff33cc33</color>",
        "        <width>3</width>",
        "      </LineStyle>",
        "    </Style>",
        "    <Style id=\"nonschengen_line\">",
        "      <LineStyle>",
        "        <color>ff3366ff</color>",
        "        <width>3</width>",
        "      </LineStyle>",
        "    </Style>",
    ]

    index = 0
    while index < len(aircrafts):
        aircraft = aircrafts[index]
        origin_code = aircraft["origin"]

        origin_coords = coords_dict.get(origin_code)

        if origin_coords is not None:
            distance = _haversine_distance(
                LEBL_LAT, LEBL_LON, origin_coords[0], origin_coords[1]
            )
            aircraft["distance"] = distance

            should_include = True
            if long_distance_only:
                should_include = distance > 2000

            if should_include:
                is_schengen = _is_schengen_airport(origin_code)
                style_name = "schengen_line" if is_schengen else "nonschengen_line"

                kml_lines.append("    <Placemark>")
                kml_lines.append(f"      <name>{aircraft['id']}</name>")
                kml_lines.append(f"      <styleUrl>#{style_name}</styleUrl>")
                kml_lines.append(
                    f"      <description>From: {origin_code} | Distance: {distance:.0f} km | Airline: {aircraft['airline']} | Arrival: {aircraft['arrival_time']}</description>"
                )
                kml_lines.append("      <LineString>")
                kml_lines.append("        <tessellate>1</tessellate>")
                kml_lines.append(
                    f"        <coordinates>{origin_coords[1]},{origin_coords[0]},0 {LEBL_LON},{LEBL_LAT},0</coordinates>"
                )
                kml_lines.append("      </LineString>")
                kml_lines.append("    </Placemark>")

        index += 1

    kml_lines.append("  </Document>")
    kml_lines.append("</kml>")

    result = None

    try:
        with open(output_filename, "w", encoding="utf-8") as handler:
            handler.write("\n".join(kml_lines))
        result = output_filename

    except OSError:
        print(f"Error al escribir el archivo KML '{output_filename}'.")

    return result


def LongDistanceArrivals(aircrafts):
    """Devuelve una lista con los aviones que vienen de más de 2000 km."""
    long_distance = []

    coords_dict = _load_airport_coords_from_file("Airports.txt")

    if len(coords_dict) == 0:
        print("Aviso: No hay archivo Airports.txt con coordenadas. No se pueden calcular distancias.")
        return long_distance

    index = 0
    while index < len(aircrafts):
        aircraft = aircrafts[index]
        origin_code = aircraft["origin"]
        origin_coords = coords_dict.get(origin_code)

        if origin_coords is not None:
            distance = _haversine_distance(
                LEBL_LAT, LEBL_LON, origin_coords[0], origin_coords[1]
            )

            if distance > 2000:
                aircraft["distance"] = distance
                long_distance.append(aircraft)

        index += 1

    return long_distance


if __name__ == "__main__":
    aircrafts = LoadArrivals("Arrivals.txt")
    print(f"Aeronaves cargadas: {len(aircrafts)}")

    if len(aircrafts) > 0:
        print("\nPrimera aeronave:")
        PrintAircraft(aircrafts[0])

        hourly = PlotArrivals(aircrafts)
        if hourly is not None:
            print("\nLlegadas por hora:")
            hour = 0
            while hour < 24:
                print(f"Hora {hour:02d}: {hourly[hour]}")
                hour += 1

        print("\n--- Test PlotAirlines ---")
        airlines = PlotAirlines(aircrafts)
        if airlines is not None:
            print("Vuelos por compañía:")
            for airline, count in airlines.items():
                print(f"  {airline}: {count}")

        print("\n--- Test PlotFlightsType ---")
        schengen_data = PlotFlightsType(aircrafts)
        if schengen_data is not None:
            print(f"Schengen: {schengen_data[0]}, No-Schengen: {schengen_data[1]}")

        print("\n--- Test LongDistanceArrivals ---")
        long_dist = LongDistanceArrivals(aircrafts)
        print(f"Vuelos de larga distancia (>2000 km): {len(long_dist)}")
        i = 0
        while i < len(long_dist) and i < 5:
            print(f"  {long_dist[i]['id']} | {long_dist[i]['origin']} | {long_dist[i].get('distance', 0):.0f} km")
            i += 1

        print("\n--- Test MapFlights ---")
        map_result = MapFlights(aircrafts)
        if map_result is not None:
            print(f"Mapa generado: {map_result}")