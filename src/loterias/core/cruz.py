"""Lógica pura de "Cruz de la suerte".

A partir de una fecha (6 dígitos: dd mm aa) se calculan 8 sumas cruzadas y cada
una se reduce a un solo dígito mediante su raíz digital. El resultado se muestra
en forma de cruz en la interfaz.

Este módulo no depende de la UI ni de I/O: funciona offline y es testeable.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

# Las 6 casillas de entrada. a, b son los dos dígitos del día; c..f son los
# cuatro dígitos de mes y año (mm aa). Se conservan los nombres originales
# (a..f) por continuidad con la versión anterior.
CASILLAS = ("a", "b", "c", "d", "e", "f")

# Los 8 pares cruzados y su etiqueta de salida, en el mismo orden que la
# versión original (a+c=r, a+d=s, ... b+f=z).
PARES: tuple[tuple[str, str, str], ...] = (
    ("r", "a", "c"),
    ("s", "a", "d"),
    ("t", "a", "e"),
    ("u", "a", "f"),
    ("v", "b", "c"),
    ("x", "b", "d"),
    ("y", "b", "e"),
    ("z", "b", "f"),
)


@dataclass(frozen=True)
class ResultadoCruz:
    """Una de las 8 sumas de la cruz, lista para mostrar."""

    etiqueta: str   # 'r', 's', ...
    izq: str        # casilla izquierda ('a' o 'b')
    der: str        # casilla derecha ('c'..'f')
    valor_izq: int
    valor_der: int
    suma: int       # valor_izq + valor_der (antes de reducir)
    raiz: int       # raíz digital de la suma (0-9)


def raiz_digital(n: int) -> int:
    """Reduce un entero a un solo dígito sumando sus cifras repetidamente.

    Equivale al algoritmo `sumar1` de la versión original. La raíz digital de 0
    es 0; la de 18 es 9, etc.
    """
    n = abs(n)
    while n > 9:
        n = sum(int(c) for c in str(n))
    return n


def _validar_digito(nombre: str, valor: int) -> int:
    if not isinstance(valor, int):
        raise TypeError(f"La casilla '{nombre}' debe ser un entero, no {type(valor).__name__}.")
    if not 0 <= valor <= 9:
        raise ValueError(f"La casilla '{nombre}' debe ser un dígito 0-9, se recibió {valor}.")
    return valor


def digitos_desde_fecha(fecha: date) -> dict[str, int]:
    """Convierte una fecha en las 6 casillas (dd mm aa), un dígito por casilla.

    a, b = dígitos del día; c, d = dígitos del mes; e, f = dos últimos del año.
    """
    dd = f"{fecha.day:02d}"
    mm = f"{fecha.month:02d}"
    aa = f"{fecha.year % 100:02d}"
    cadena = dd + mm + aa  # 6 dígitos en orden a..f
    return {casilla: int(cadena[i]) for i, casilla in enumerate(CASILLAS)}


def calcular_cruz(digitos: dict[str, int]) -> list[ResultadoCruz]:
    """Calcula las 8 sumas cruzadas a partir de las 6 casillas.

    `digitos` debe tener las claves 'a'..'f' con un dígito (0-9) cada una.
    Lanza ValueError/TypeError si falta una casilla o el valor no es un dígito.
    """
    faltantes = [c for c in CASILLAS if c not in digitos]
    if faltantes:
        raise ValueError(f"Faltan casillas: {', '.join(faltantes)}")

    vals = {c: _validar_digito(c, digitos[c]) for c in CASILLAS}

    resultados: list[ResultadoCruz] = []
    for etiqueta, izq, der in PARES:
        suma = vals[izq] + vals[der]
        resultados.append(
            ResultadoCruz(
                etiqueta=etiqueta,
                izq=izq,
                der=der,
                valor_izq=vals[izq],
                valor_der=vals[der],
                suma=suma,
                raiz=raiz_digital(suma),
            )
        )
    return resultados
