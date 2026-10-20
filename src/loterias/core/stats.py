"""Cálculos estadísticos sobre los resultados (puro, sin pandas ni UI).

Trabaja sobre filas tal como las devuelve `data.repository.obtener` (objetos
tipo sqlite3.Row o dicts con 'date' y 'result'). Cada resultado se normaliza a 4
cifras y se analizan las 4 posiciones por separado, como en la versión anterior.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date

N_POSICIONES = 4


@dataclass(frozen=True)
class Registro:
    fecha: date
    dia_semana: int                 # 0 = lunes ... 6 = domingo
    digitos: tuple[int, int, int, int]
    suma: int


def _cifras(result: str) -> tuple[int, int, int, int]:
    """Normaliza un resultado a 4 cifras (rellena con ceros a la izquierda)."""
    solo = "".join(c for c in str(result) if c.isdigit()).zfill(N_POSICIONES)
    solo = solo[-N_POSICIONES:]
    return tuple(int(c) for c in solo)  # type: ignore[return-value]


def preparar(filas) -> list[Registro]:
    """Convierte filas de la DB en registros listos para analizar."""
    regs: list[Registro] = []
    for f in filas:
        d = f["date"] if not isinstance(f["date"], date) else f["date"].isoformat()
        fecha = date.fromisoformat(d)
        cifras = _cifras(f["result"])
        regs.append(
            Registro(
                fecha=fecha,
                dia_semana=fecha.weekday(),
                digitos=cifras,
                suma=sum(cifras),
            )
        )
    return regs


def frecuencias_por_posicion(regs: list[Registro]) -> list[list[int]]:
    """Para cada posición (0-3), conteo de cada dígito 0-9. Devuelve 4 listas de 10."""
    matriz = [[0] * 10 for _ in range(N_POSICIONES)]
    for r in regs:
        for p in range(N_POSICIONES):
            matriz[p][r.digitos[p]] += 1
    return matriz


def numero_caliente(regs: list[Registro]) -> str:
    """Dígito más frecuente en cada posición, concatenado (desempate: menor dígito)."""
    if not regs:
        return ""
    freqs = frecuencias_por_posicion(regs)
    cifras = []
    for conteos in freqs:
        mejor = max(range(10), key=lambda d: (conteos[d], -d))
        cifras.append(str(mejor))
    return "".join(cifras)


def suma_promedio(regs: list[Registro]) -> float | None:
    if not regs:
        return None
    return sum(r.suma for r in regs) / len(regs)


def matriz_dia_digito(regs: list[Registro], posicion: int) -> list[list[int]]:
    """Conteo día de semana (7) x dígito (10) para una posición dada."""
    matriz = [[0] * 10 for _ in range(7)]
    for r in regs:
        matriz[r.dia_semana][r.digitos[posicion]] += 1
    return matriz


def atrasos(regs: list[Registro]) -> list[list[int]]:
    """Atraso posicional: sorteos desde la última aparición de cada dígito.

    Devuelve 4 listas de 10. 0 = salió en el sorteo más reciente; un valor mayor
    = más atrasado. Si un dígito nunca apareció, su atraso es len(regs).
    """
    orden = sorted(regs, key=lambda r: r.fecha, reverse=True)
    total = len(orden)
    resultado = [[total] * 10 for _ in range(N_POSICIONES)]
    for p in range(N_POSICIONES):
        vistos = set()
        for i, r in enumerate(orden):
            d = r.digitos[p]
            if d not in vistos:
                resultado[p][d] = i
                vistos.add(d)
                if len(vistos) == 10:
                    break
    return resultado
