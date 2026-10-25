"""Vista "Cruz de la suerte": elegir una fecha y ver las 8 sumas en cruz.

El usuario elige una fecha en el calendario; la fecha se descompone en 6 dígitos
(dd mm aa) y se muestran las 8 raíces digitales dispuestas en forma de cruz.
Funciona totalmente offline.
"""

from __future__ import annotations

import math
from datetime import date, datetime

import flet as ft

from loterias.core.cruz import ResultadoCruz, calcular_cruz, digitos_desde_fecha

LIENZO = 330           # lado del área de la cruz
NODO = 64              # diámetro de cada nodo
_H = NODO / 2

# Posición (centro) de cada etiqueta dentro del lienzo.
# Exteriores en las esquinas (puntas de la X); interiores sobre los ejes.
_C = LIENZO / 2
_OFF_EXT = _C - _H - 6   # distancia del centro a las esquinas
_OFF_INT = 62            # distancia del centro a los nodos interiores
POSICIONES: dict[str, tuple[float, float]] = {
    # esquinas exteriores
    "r": (_C - _OFF_EXT, _C - _OFF_EXT),   # arriba-izquierda
    "s": (_C + _OFF_EXT, _C - _OFF_EXT),   # arriba-derecha
    "y": (_C - _OFF_EXT, _C + _OFF_EXT),   # abajo-izquierda
    "z": (_C + _OFF_EXT, _C + _OFF_EXT),   # abajo-derecha
    # ejes interiores
    "t": (_C, _C - _OFF_INT),              # arriba
    "x": (_C, _C + _OFF_INT),              # abajo
    "u": (_C - _OFF_INT, _C),              # izquierda
    "v": (_C + _OFF_INT, _C),              # derecha
}


def _nodo(res: ResultadoCruz, cx: float, cy: float) -> ft.Container:
    """Círculo con la raíz digital y la operación, posicionado por su centro."""
    return ft.Container(
        width=NODO,
        height=NODO,
        left=cx - _H,
        top=cy - _H,
        border_radius=NODO / 2,
        bgcolor=ft.Colors.PRIMARY_CONTAINER,
        alignment=ft.Alignment.CENTER,
        content=ft.Column(
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(str(res.raiz), size=26, weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ON_PRIMARY_CONTAINER),
                ft.Text(res.etiqueta, size=12,
                        color=ft.Colors.ON_PRIMARY_CONTAINER),
            ],
        ),
    )


def _aspa(angulo: float) -> ft.Container:
    """Una de las dos diagonales de la X (barra fina rotada sobre su centro)."""
    largo = _OFF_EXT * 2 * math.sqrt(2)
    return ft.Container(
        width=largo,
        height=4,
        left=_C - largo / 2,
        top=_C - 2,
        border_radius=2,
        bgcolor=ft.Colors.with_opacity(0.35, ft.Colors.PRIMARY),
        rotate=ft.Rotate(angulo),
    )


def _cruz(resultados: list[ResultadoCruz]) -> ft.Control:
    """Dispone los 8 nodos sobre una X: 4 esquinas exteriores + 4 ejes interiores."""
    r = {res.etiqueta: res for res in resultados}
    controles: list[ft.Control] = [_aspa(math.pi / 4), _aspa(-math.pi / 4)]
    controles += [_nodo(r[etq], cx, cy) for etq, (cx, cy) in POSICIONES.items()]
    return ft.Stack(width=LIENZO, height=LIENZO, controls=controles)


def _chip_formula(res: ResultadoCruz) -> ft.Container:
    """Una fórmula: la simbólica (a+c=r) y el cálculo real (2+0 → 2)."""
    return ft.Container(
        padding=8,
        border_radius=8,
        bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.SECONDARY_CONTAINER),
        content=ft.Row(
            spacing=8,
            tight=True,
            controls=[
                ft.Text(f"{res.izq}+{res.der}={res.etiqueta}", size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(f"{res.valor_izq}+{res.valor_der} → {res.raiz}", size=12,
                        weight=ft.FontWeight.BOLD, color=ft.Colors.ON_SECONDARY_CONTAINER),
            ],
        ),
    )


def _leyenda_digitos(digitos: dict[str, int]) -> ft.Control:
    """Muestra qué dígitos salieron de la fecha (día/mes/año)."""
    def par(etiqueta: str, a: str, b: str) -> ft.Row:
        return ft.Row(
            spacing=4,
            tight=True,
            controls=[
                ft.Text(etiqueta, size=11, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(f"{digitos[a]}{digitos[b]}", size=13, weight=ft.FontWeight.BOLD),
            ],
        )

    return ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=18,
        controls=[par("Día", "a", "b"), par("Mes", "c", "d"), par("Año", "e", "f")],
    )


def _formulas(resultados: list[ResultadoCruz], digitos: dict[str, int]) -> ft.Control:
    """Inciso plegable: cómo se llega a cada número."""
    chips = [_chip_formula(r) for r in resultados]
    cuerpo = ft.Column(
        spacing=10,
        controls=[
            _leyenda_digitos(digitos),
            ft.Divider(height=1),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.START,
                spacing=10,
                controls=[
                    ft.Column(spacing=6, controls=chips[0::2]),  # r, t, v, y
                    ft.Column(spacing=6, controls=chips[1::2]),  # s, u, x, z
                ],
            ),
        ],
    )
    return ft.ExpansionTile(
        title=ft.Text("Fórmulas", weight=ft.FontWeight.BOLD),
        expanded=True,
        controls_padding=12,
        controls=[cuerpo],
    )


def crear_vista_cruz(page: ft.Page) -> ft.Control:
    """Construye la vista de la cruz y devuelve su control raíz."""
    fecha_sel = ft.Text(size=16, weight=ft.FontWeight.BOLD)
    contenedor = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    contenedor_formulas = ft.Container()

    def mostrar(fecha: date) -> None:
        fecha_sel.value = fecha.strftime("%d/%m/%Y")
        digitos = digitos_desde_fecha(fecha)
        resultados = calcular_cruz(digitos)
        contenedor.controls = [_cruz(resultados)]
        contenedor_formulas.content = _formulas(resultados, digitos)

    def on_cambio_fecha(e: ft.Event[ft.DatePicker]) -> None:
        valor = e.control.value
        if isinstance(valor, datetime):
            valor = valor.date()
        if valor is not None:
            mostrar(valor)

    def abrir_calendario(e) -> None:
        page.show_dialog(
            ft.DatePicker(
                first_date=date(2000, 1, 1),
                last_date=date(2100, 12, 31),
                current_date=date.today(),
                on_change=on_cambio_fecha,
            )
        )

    mostrar(date.today())

    return ft.Container(
        expand=True,
        padding=20,
        content=ft.Column(
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Text("Cruz de la suerte", size=24, weight=ft.FontWeight.BOLD),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.CALENDAR_MONTH),
                        fecha_sel,
                        ft.Button("Cambiar fecha", icon=ft.Icons.EDIT_CALENDAR,
                                  on_click=abrir_calendario),
                    ],
                ),
                contenedor,
                contenedor_formulas,
            ],
        ),
    )
