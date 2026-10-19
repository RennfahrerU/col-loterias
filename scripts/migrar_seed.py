"""Genera loterias/data/seed.db a partir del CSV histórico.

Uso (desde la raíz del proyecto):
    pipenv run python scripts/migrar_seed.py

Es un script de desarrollo de un solo uso; no se empaqueta con la app.
"""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CSV = RAIZ / "data_loterias_completo.csv"
SEED = RAIZ / "loterias" / "data" / "seed.db"

# Esquema único, importado del módulo de la app para no duplicarlo.
import sys

sys.path.insert(0, str(RAIZ))
from loterias.config import LOTERIAS  # noqa: E402
from loterias.data.db import ESQUEMA  # noqa: E402


def main() -> None:
    if not CSV.exists():
        raise SystemExit(f"No se encontró el CSV: {CSV}")

    filas = []
    with CSV.open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r.get("slug") in LOTERIAS:
                filas.append(
                    (
                        r["slug"],
                        r["date"],
                        r["lottery"],
                        str(r["result"]),
                        r.get("series"),
                    )
                )

    if SEED.exists():
        SEED.unlink()
    con = sqlite3.connect(str(SEED))
    con.executescript(ESQUEMA)
    con.executemany(
        "INSERT OR IGNORE INTO resultados (slug, date, lottery, result, series) "
        "VALUES (?, ?, ?, ?, ?)",
        filas,
    )
    con.commit()

    total = con.execute("SELECT COUNT(*) FROM resultados").fetchone()[0]
    rango = con.execute("SELECT MIN(date), MAX(date) FROM resultados").fetchone()
    por_loteria = con.execute(
        "SELECT slug, COUNT(*) FROM resultados GROUP BY slug ORDER BY slug"
    ).fetchall()
    con.close()

    print(f"Leídas del CSV (loterías objetivo): {len(filas)}")
    print(f"Filas únicas en seed.db: {total}  (duplicados ignorados: {len(filas) - total})")
    print(f"Rango de fechas: {rango[0]} -> {rango[1]}")
    for slug, n in por_loteria:
        print(f"  {slug}: {n}")
    print(f"seed.db generado en: {SEED}")


if __name__ == "__main__":
    main()
