"""Intercambio de libros con archivos externos (importar y exportar).

Aquí van los archivos que no son el catálogo principal: por ahora, exportar
una selección de libros a JSON. El catálogo de la librería se maneja en
almacenamiento.py.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from libreria_m6.excepciones import PermisoArchivoError
from libreria_m6.modelos import Libro
from libreria_m6.utilidades import escritura_atomica

log = logging.getLogger(__name__)


def exportar_json(libros: list[Libro], ruta: str | Path) -> Path:
    """Guarda una lista de libros en un archivo JSON y devuelve la ruta final.

    Los libros se guardan bajo la clave "libros", con la misma forma que en el
    catálogo, para poder leerlos después con Libro.desde_dict.
    """
    ruta = Path(ruta).with_suffix(".json")
    ruta.parent.mkdir(parents=True, exist_ok=True)

    # Serialización: cada Libro se vuelve dict, igual que en guardar_datos
    contenido: dict[str, Any] = {
        "exportado": datetime.now().isoformat(timespec="seconds"),
        "total": len(libros),
        "libros": [libro.a_dict() for libro in sorted(libros)],
    }

    try:
        with escritura_atomica(ruta) as f:
            json.dump(contenido, f, ensure_ascii=False, indent=2)
    except PermissionError:
        raise PermisoArchivoError(f"Sin permisos para escribir el archivo: {ruta}") from None

    log.info("Exportados %d libros a %s", len(libros), ruta)

    return ruta
