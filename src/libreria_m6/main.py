import os
from pathlib import Path
from typing import Final

from libreria_m6.captura import capturar_filtros, capturar_libro
from libreria_m6.excepciones import LibreriaError
from libreria_m6.lector import (
    agregar_libro,
    cargar_datos,
    guardar_datos,
    mostrar_libreria,
    mostrar_libros,
)
from libreria_m6.modelos import Libro
from libreria_m6.utilidades import cronometro


def main() -> None:
    os.system("cls" if os.name == "nt" else "clear")

    LIBROS_POR_PAGINA: Final = 3
    ruta_json = Path(__file__).parent.parent.parent / "data" / "libreria.json"

    print("\nSCRIPT DE MANEJO DE CATALOGO DE LIBROS (MODULO 6)\n")

    try:
        with cronometro("Cargar catálogo"):
            # Se incluye el context manager de temporizacion
            data = cargar_datos(ruta_json)

    except LibreriaError as e:
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
            print(f"❌ No se pudo agregar el libro: {e}")
            return
        print(f"\n✅ '{nuevo_libro.titulo}' agregado correctamente.")
        mostrar_libreria(data, por_pagina=LIBROS_POR_PAGINA)

    respuesta_filtro = input("\n¿Deseas filtrar el catálogo? (s/n): ").strip().lower()
    if respuesta_filtro == "s":
        resultados = capturar_filtros(data)
        print(f"\n🔍 {len(resultados)} resultado(s) encontrado(s):")
        mostrar_libros(resultados)

    print("\n¡HASTA LUEGO!\n")


if __name__ == "__main__":
    main()
