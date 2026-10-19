"""Consultas y escrituras sobre la tabla `resultados`."""

from __future__ import annotations

import sqlite3


def ultima_fecha(con: sqlite3.Connection) -> str | None:
    """Fecha ISO más reciente almacenada (sobre cualquier lotería), o None."""
    fila = con.execute("SELECT MAX(date) AS m FROM resultados").fetchone()
    return fila["m"] if fila and fila["m"] else None


def insertar(con: sqlite3.Connection, filas: list[dict]) -> int:
    """Inserta resultados con INSERT OR IGNORE (dedup por slug+date).

    Devuelve cuántas filas nuevas se insertaron realmente.
    """
    if not filas:
        return 0
    antes = con.total_changes
    con.executemany(
        """
        INSERT OR IGNORE INTO resultados (slug, date, lottery, result, series)
        VALUES (:slug, :date, :lottery, :result, :series)
        """,
        filas,
    )
    con.commit()
    return con.total_changes - antes


def obtener(
    con: sqlite3.Connection,
    slug: str | None = None,
    desde: str | None = None,
    hasta: str | None = None,
) -> list[sqlite3.Row]:
    """Devuelve resultados filtrados por lotería y rango de fechas (ISO), ordenados."""
    sql = "SELECT slug, date, lottery, result, series FROM resultados WHERE 1=1"
    params: list[str] = []
    if slug:
        sql += " AND slug = ?"
        params.append(slug)
    if desde:
        sql += " AND date >= ?"
        params.append(desde)
    if hasta:
        sql += " AND date <= ?"
        params.append(hasta)
    sql += " ORDER BY date"
    return con.execute(sql, params).fetchall()
