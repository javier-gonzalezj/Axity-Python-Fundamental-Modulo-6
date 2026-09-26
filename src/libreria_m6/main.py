import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Final

from libreria_m6.almacenamiento import cargar_datos, guardar_datos
from libreria_m6.captura import capturar_filtros, capturar_libro
from libreria_m6.catalogo import agregar_libro
from libreria_m6.excepciones import LibreriaError
from libreria_m6.intercambio import ResultadoImportacion, exportar_json, importar_csv
from libreria_m6.modelos import Libreria, Libro
from libreria_m6.registro import configurar_logging
from libreria_m6.utilidades import cronometro
from libreria_m6.vista import mostrar_libreria, mostrar_libros

log = logging.getLogger(__name__)


def _importar_desde_csv(data: Libreria) -> ResultadoImportacion | None:
    """Pide la ruta de un CSV, importa sus libros a `data` y muestra el resumen.

    Devuelve None si el archivo no se pudo leer. No guarda el catálogo.
    """
    # "Copiar como ruta" en Windows agrega comillas; se quitan
    texto_ruta = input("Ruta del archivo CSV: ").strip().strip('"')
    try:
        resultado = importar_csv(data, texto_ruta)
    except LibreriaError as e:
        log.exception("Error al importar el archivo CSV")
        print(f"❌ No se pudo importar: {e}")
        return None

    print(f"\n✅ {len(resultado.agregados)} libro(s) agregado(s).")
    if resultado.rechazados:
        print(f"⚠️  {len(resultado.rechazados)} fila(s) rechazada(s):")
        for motivo in resultado.rechazados:
            print("   - " + motivo.replace("\n", "\n     "))
    return resultado


def main() -> None:
    os.system("cls" if os.name == "nt" else "clear")

    LIBROS_POR_PAGINA: Final = 3
    raiz_proyecto = Path(__file__).parent.parent.parent
    ruta_json = raiz_proyecto / "data" / "libreria.json"

    configurar_logging(raiz_proyecto / "logs")
    log.info("Inicio del programa")
    print("\nSCRIPT DE MANEJO DE CATALOGO DE LIBROS (MODULO 6)\n")

    try:
        with cronometro("Cargar catálogo"):
            # Se incluye el context manager de temporizacion
            data = cargar_datos(ruta_json)

    except LibreriaError as e:
        log.exception("Error al cargar el catálogo")
        print(f"❌ Error al cargar la librería: {e}")
        return

    mostrar_libreria(data, por_pagina=LIBROS_POR_PAGINA)

    respuesta = input("\n¿Deseas agregar un nuevo libro? (s/n): ").strip().lower()
    if respuesta == "s":
        try:
            nuevo_libro = Libro.desde_dict(capturar_libro(data))
            data = agregar_libro(data, nuevo_libro)
            with cronometro("Guardar catalogo"):
                guardar_datos(ruta_json, data)
        except LibreriaError as e:
            log.exception("Error al agregar un libro")
            print(f"❌ No se pudo agregar el libro: {e}")
            return
        print(f"\n✅ '{nuevo_libro.titulo}' agregado correctamente.")
        mostrar_libreria(data, por_pagina=LIBROS_POR_PAGINA)

    respuesta_importar = input("\n¿Deseas importar libros desde un CSV? (s/n): ").strip().lower()
    if respuesta_importar == "s":
        resultado = _importar_desde_csv(data)
        if resultado is not None and resultado.agregados:
            try:
                with cronometro("Guardar catalogo"):
                    guardar_datos(ruta_json, data)
            except LibreriaError as e:
                log.exception("Error al guardar los libros importados")
                print(f"❌ No se pudo guardar el catálogo: {e}")
                return
            mostrar_libreria(data, por_pagina=LIBROS_POR_PAGINA)

    respuesta_filtro = input("\n¿Deseas filtrar el catálogo? (s/n): ").strip().lower()
    if respuesta_filtro == "s":
        resultados = capturar_filtros(data)
        print(f"\n🔍 {len(resultados)} resultado(s) encontrado(s):")
        mostrar_libros(resultados)

        if resultados:
            respuesta_exportar = input("\n¿Deseas exportar el resultado a JSON? (s/n): ")
            if respuesta_exportar.strip().lower() == "s":
                nombre_defecto = f"filtro_{datetime.now():%Y%m%d_%H%M%S}"
                nombre = input(f"Nombre del archivo [{nombre_defecto}]: ").strip()
                ruta_exportacion = ruta_json.parent / "exportaciones" / (nombre or nombre_defecto)
                try:
                    ruta_final = exportar_json(resultados, ruta_exportacion)
                    print(f"\n✅ Resultado exportado a: {ruta_final}")
                except LibreriaError as e:
                    log.exception("Error al exportar el archivo JSON")
                    print(f"❌ No se pudo exportar: {e}")

    log.info("--- Fin del programa ---")
    print("\n¡HASTA LUEGO!\n")


if __name__ == "__main__":
    main()
