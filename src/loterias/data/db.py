"""Acceso a la base de datos SQLite local.

La DB vive en el directorio escribible y persistente de la plataforma
(`FLET_APP_STORAGE_DATA`, que Flet define en Android/iOS/desktop). En desarrollo
fuera de Flet se usa una carpeta `.data/` en la raíz del proyecto.

En el primer arranque, si no existe la DB pero sí el `seed.db` empaquetado, se
copia para tener histórico offline desde el inicio.
"""

from __future__ import annotations

import os
import shutil
import sqlite3
from pathlib import Path

# seed.db viaja dentro del paquete, así es legible también en el APK.
SEED = Path(__file__).parent / "seed.db"

ESQUEMA = """
CREATE TABLE IF NOT EXISTS resultados (
    slug    TEXT NOT NULL,
    date    TEXT NOT NULL,
    lottery TEXT NOT NULL,
    result  TEXT NOT NULL,
    series  TEXT,
    PRIMARY KEY (slug, date)
);
CREATE INDEX IF NOT EXISTS idx_resultados_slug_date ON resultados (slug, date);
"""


def ruta_db() -> Path:
    """Devuelve la ruta del archivo de la DB, creando el directorio si falta."""
    base = os.getenv("FLET_APP_STORAGE_DATA")
    if base:
        carpeta = Path(base)
    else:
        # Fallback de desarrollo (fuera de Flet). Raíz del proyecto:
        # src/loterias/data/db.py -> parents[3] = raíz.
        carpeta = Path(__file__).resolve().parents[3] / ".data"
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta / "loterias.db"


def conectar() -> sqlite3.Connection:
    """Abre la DB (copiando el seed si es el primer arranque) y asegura el esquema."""
    ruta = ruta_db()
    if not ruta.exists() and SEED.exists():
        shutil.copy(SEED, ruta)
    con = sqlite3.connect(str(ruta))
    con.row_factory = sqlite3.Row
    con.executescript(ESQUEMA)
    return con
