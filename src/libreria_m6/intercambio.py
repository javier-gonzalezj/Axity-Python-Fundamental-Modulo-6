"""Intercambio de libros con archivos externos (importar y exportar).

Aquí van los formatos que no son el catálogo principal: por ahora, exportar a CSV.
El JSON propio de la librería se maneja en almacenamiento.py.
"""

import csv
from pathlib import Path
from typing import Any

from libreria_m6.excepciones import PermisoArchivoError
from libreria_m6.modelos import Libro
from libreria_m6.utilidades import escritura_atomica

COLUMNAS_CSV = [
    "isbn",
    "titulo",
    "autor",
    "nacionalidad_autor",
    "genero",
    "año_publicacion",
    "precio",
    "en_stock",
    "cantidad_disponible",
    "editorial",
]


def _libro_a_fila(libro: Libro) -> dict[str, Any]:
    """Aplana un Libro en una fila de CSV (solo valores simples, sin anidar)."""
    return {
        "isbn": libro.isbn,
        "titulo": libro.titulo,
        "autor": libro.autor.nombre,
        "nacionalidad_autor": libro.autor.nacionalidad,
        "genero": "; ".join(libro.genero),
        "año_publicacion": libro.año_publicacion,
        "precio": f"{libro.precio:.2f}",
        "en_stock": "sí" if libro.en_stock else "no",
        "cantidad_disponible": libro.cantidad_disponible,
        "editorial": libro.editorial,
    }


def exportar_csv(libros: list[Libro], ruta: str | Path) -> Path:
    """Guarda una lista de libros en un archivo CSV y devuelve la ruta final.

    Usa utf-8-sig para que Excel muestre bien los acentos y la ñ.
    """
    ruta = Path(ruta).with_suffix(".csv")
    ruta.parent.mkdir(parents=True, exist_ok=True)

    try:
        # newline="" es obligatorio con el módulo csv: evita líneas en blanco en Windows
        with escritura_atomica(ruta, encoding="utf-8-sig", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=COLUMNAS_CSV)
            escritor.writeheader()
            escritor.writerows(_libro_a_fila(libro) for libro in sorted(libros))
    except PermissionError:
        raise PermisoArchivoError(
            f"Sin permisos para escribir {ruta}. ¿Está abierto en Excel?"
        ) from None

    return ruta
