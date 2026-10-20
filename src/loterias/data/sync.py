"""Sincronización incremental con la API de resultados.

Al abrir con internet, baja solo los días nuevos desde la última fecha guardada
(menos una ventana de re-fetch, por resultados publicados tarde). Sin internet,
la primera petición falla y el sync se aborta en silencio: la app sigue con lo
que ya tiene almacenado.
"""

from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass
from datetime import date, timedelta

import requests

from loterias import config
from loterias.data import repository


@dataclass
class ResultadoSync:
    insertados: int = 0      # filas nuevas guardadas
    dias_consultados: int = 0
    error: str | None = None  # None si todo fue bien; texto si hubo fallo (p.ej. offline)


def _fecha_inicio(con: sqlite3.Connection, hoy: date) -> date:
    ultima = repository.ultima_fecha(con)
    if ultima:
        return date.fromisoformat(ultima) - timedelta(days=config.REFETCH_DIAS)
    return hoy - timedelta(days=config.DIAS_INICIAL)


def _resultados_del_dia(dia: date) -> list[dict]:
    """Pide un día a la API y devuelve solo las loterías objetivo."""
    resp = requests.get(f"{config.API_BASE}/{dia.isoformat()}", timeout=10)
    resp.raise_for_status()
    datos = resp.json()
    if datos.get("status") != "success" or not datos.get("data"):
        return []
    filas = []
    for item in datos["data"]:
        if item.get("slug") in config.LOTERIAS:
            filas.append(
                {
                    "slug": item["slug"],
                    "date": item["date"],
                    "lottery": item["lottery"],
                    "result": str(item["result"]),
                    "series": item.get("series"),
                }
            )
    return filas


def sincronizar(con: sqlite3.Connection, hoy: date | None = None) -> ResultadoSync:
    """Ejecuta el sync incremental. Pensado para correr fuera del hilo de UI."""
    hoy = hoy or date.today()
    resultado = ResultadoSync()
    dia = _fecha_inicio(con, hoy)

    while dia <= hoy:
        try:
            filas = _resultados_del_dia(dia)
        except requests.RequestException as e:
            # Muy probablemente sin conexión: abortamos sin romper la app.
            resultado.error = str(e)
            break
        resultado.insertados += repository.insertar(con, filas)
        resultado.dias_consultados += 1
        dia += timedelta(days=1)
        if dia <= hoy:
            time.sleep(config.PAUSA_PETICION_S)

    return resultado
